from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import Date, case, func, literal_column

from config import database as db
from models.Platform import Platform
from models.PlatformOrder import PlatformOrder
from models.PlatformOrderItem import PlatformOrderItem


def _to_float(value):
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return float(value)
    return value


def _rate(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0
    return float(numerator) / float(denominator)


def _date_start(value: date | None) -> datetime | None:
    if value is None:
        return None
    return datetime.combine(value, time.min)


def _date_end_exclusive(value: date | None) -> datetime | None:
    if value is None:
        return None
    return datetime.combine(value + timedelta(days=1), time.min)


def _clean_statuses(order_statuses: list[str] | None) -> list[str]:
    if not order_statuses:
        return []
    return [status.strip() for status in order_statuses if status and status.strip()]


def _year_month_range(year: int | None, month: int | None):
    selected_year = year or datetime.now().year
    selected_month = month if month and 1 <= month <= 12 else None

    if selected_month:
        start_at = datetime(selected_year, selected_month, 1)
        next_month_year = selected_year + 1 if selected_month == 12 else selected_year
        next_month = 1 if selected_month == 12 else selected_month + 1
        end_at = datetime(next_month_year, next_month, 1)
    else:
        start_at = datetime(selected_year, 1, 1)
        end_at = datetime(selected_year + 1, 1, 1)

    return selected_year, selected_month, start_at, end_at


def _format_period(value, group_by: str) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        if group_by == "month":
            return value.strftime("%Y-%m")
        return value.strftime("%Y-%m-%d")

    text = str(value)
    if group_by == "month":
        return text[:7]
    return text[:10]


def _apply_order_filters(
    query,
    *,
    date_from: date | None,
    date_to: date | None,
    platform_ids: list[int] | None,
    order_statuses: list[str] | None,
):
    start_at = _date_start(date_from)
    end_at = _date_end_exclusive(date_to)
    cleaned_statuses = _clean_statuses(order_statuses)

    if start_at is not None:
        query = query.filter(PlatformOrder.OrderCreatedAt >= start_at)
    if end_at is not None:
        query = query.filter(PlatformOrder.OrderCreatedAt < end_at)
    if platform_ids:
        query = query.filter(PlatformOrder.PlatformId.in_(platform_ids))
    if cleaned_statuses:
        query = query.filter(PlatformOrder.OrderStatus.in_(cleaned_statuses))

    return query


def _apply_validity_filters(query, *, include_cancelled: bool, include_returned: bool):
    if not include_cancelled:
        query = query.filter(PlatformOrder.IsCancelled == False)
    if not include_returned:
        query = query.filter(PlatformOrder.IsReturned == False)
    return query


def _base_order_query(
    *,
    date_from: date | None,
    date_to: date | None,
    platform_ids: list[int] | None,
    order_statuses: list[str] | None,
):
    query = db.session.query(PlatformOrder).filter(PlatformOrder.isDeleted == False)
    return _apply_order_filters(
        query,
        date_from=date_from,
        date_to=date_to,
        platform_ids=platform_ids,
        order_statuses=order_statuses,
    )


def _valid_order_query(
    *,
    date_from: date | None,
    date_to: date | None,
    platform_ids: list[int] | None,
    order_statuses: list[str] | None,
    include_cancelled: bool,
    include_returned: bool,
):
    query = _base_order_query(
        date_from=date_from,
        date_to=date_to,
        platform_ids=platform_ids,
        order_statuses=order_statuses,
    )
    return _apply_validity_filters(
        query,
        include_cancelled=include_cancelled,
        include_returned=include_returned,
    )


def get_kpi_summary(
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    platform_ids: list[int] | None = None,
    order_statuses: list[str] | None = None,
    include_cancelled: bool = False,
    include_returned: bool = False,
) -> dict:
    cleaned_statuses = _clean_statuses(order_statuses)
    gross_query = _base_order_query(
        date_from=date_from,
        date_to=date_to,
        platform_ids=platform_ids,
        order_statuses=cleaned_statuses,
    )
    valid_query = _valid_order_query(
        date_from=date_from,
        date_to=date_to,
        platform_ids=platform_ids,
        order_statuses=cleaned_statuses,
        include_cancelled=include_cancelled,
        include_returned=include_returned,
    )

    gross_orders = gross_query.count()
    cancelled_orders = gross_query.filter(PlatformOrder.IsCancelled == True).count()
    returned_orders = gross_query.filter(PlatformOrder.IsReturned == True).count()
    valid_orders = valid_query.count()

    total_sales_value = _to_float(
        valid_query.with_entities(func.coalesce(func.sum(PlatformOrder.SalesValue), 0)).scalar()
    )
    average_order_value = total_sales_value / valid_orders if valid_orders else 0

    quantity_query = (
        db.session.query(func.coalesce(func.sum(PlatformOrderItem.Quantity), 0))
        .join(PlatformOrder, PlatformOrder.PlatformOrderId == PlatformOrderItem.PlatformOrderId)
        .filter(PlatformOrder.isDeleted == False)
        .filter(PlatformOrderItem.isDeleted == False)
    )
    quantity_query = _apply_validity_filters(
        quantity_query,
        include_cancelled=include_cancelled,
        include_returned=include_returned,
    )
    quantity_query = _apply_order_filters(
        quantity_query,
        date_from=date_from,
        date_to=date_to,
        platform_ids=platform_ids,
        order_statuses=cleaned_statuses,
    )
    total_quantity_sold = int(quantity_query.scalar() or 0)

    platform_rows = (
        db.session.query(
            Platform.PlatformId,
            Platform.PlatformName,
            func.count(PlatformOrder.PlatformOrderId).label("OrderCount"),
            func.coalesce(func.sum(PlatformOrder.SalesValue), 0).label("SalesValue"),
        )
        .join(PlatformOrder, PlatformOrder.PlatformId == Platform.PlatformId)
        .filter(Platform.isDeleted == False)
        .filter(PlatformOrder.isDeleted == False)
    )
    platform_rows = _apply_validity_filters(
        platform_rows,
        include_cancelled=include_cancelled,
        include_returned=include_returned,
    )
    platform_rows = _apply_order_filters(
        platform_rows,
        date_from=date_from,
        date_to=date_to,
        platform_ids=platform_ids,
        order_statuses=cleaned_statuses,
    )
    platform_rows = (
        platform_rows
        .group_by(Platform.PlatformId, Platform.PlatformName)
        .order_by(func.coalesce(func.sum(PlatformOrder.SalesValue), 0).desc())
        .all()
    )

    platform_split = []
    for row in platform_rows:
        sales_value = _to_float(row.SalesValue)
        platform_split.append(
            {
                "platformId": row.PlatformId,
                "platformName": row.PlatformName,
                "orderCount": row.OrderCount,
                "salesValue": sales_value,
                "salesShare": _rate(sales_value, total_sales_value),
            }
        )

    return {
        "totalSalesValue": total_sales_value,
        "totalOrders": valid_orders,
        "totalQuantitySold": total_quantity_sold,
        "averageOrderValue": average_order_value,
        "grossOrders": gross_orders,
        "validOrders": valid_orders,
        "cancelledOrders": cancelled_orders,
        "cancelledRate": _rate(cancelled_orders, gross_orders),
        "returnedOrders": returned_orders,
        "returnedRate": _rate(returned_orders, gross_orders),
        "platformSplit": platform_split,
        "filters": {
            "dateFrom": str(date_from) if date_from else None,
            "dateTo": str(date_to) if date_to else None,
            "platformIds": platform_ids or [],
            "orderStatuses": cleaned_statuses,
            "includeCancelled": include_cancelled,
            "includeReturned": include_returned,
        },
    }


def get_sales_by_platform(
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    platform_ids: list[int] | None = None,
    order_statuses: list[str] | None = None,
    include_cancelled: bool = False,
    include_returned: bool = False,
) -> dict:
    cleaned_statuses = _clean_statuses(order_statuses)

    quantity_by_order = (
        db.session.query(
            PlatformOrderItem.PlatformOrderId.label("PlatformOrderId"),
            func.coalesce(func.sum(PlatformOrderItem.Quantity), 0).label("Quantity"),
        )
        .filter(PlatformOrderItem.isDeleted == False)
        .group_by(PlatformOrderItem.PlatformOrderId)
        .subquery()
    )

    query = (
        db.session.query(
            Platform.PlatformId,
            Platform.PlatformName,
            func.count(PlatformOrder.PlatformOrderId).label("OrderCount"),
            func.coalesce(func.sum(quantity_by_order.c.Quantity), 0).label("Quantity"),
            func.coalesce(func.sum(PlatformOrder.SalesValue), 0).label("SalesValue"),
        )
        .join(PlatformOrder, PlatformOrder.PlatformId == Platform.PlatformId)
        .outerjoin(quantity_by_order, quantity_by_order.c.PlatformOrderId == PlatformOrder.PlatformOrderId)
        .filter(Platform.isDeleted == False)
        .filter(PlatformOrder.isDeleted == False)
    )
    query = _apply_validity_filters(
        query,
        include_cancelled=include_cancelled,
        include_returned=include_returned,
    )
    query = _apply_order_filters(
        query,
        date_from=date_from,
        date_to=date_to,
        platform_ids=platform_ids,
        order_statuses=cleaned_statuses,
    )

    rows = (
        query
        .group_by(Platform.PlatformId, Platform.PlatformName)
        .order_by(func.coalesce(func.sum(PlatformOrder.SalesValue), 0).desc())
        .all()
    )

    total_sales_value = sum(_to_float(row.SalesValue) for row in rows)
    total_order_count = sum(int(row.OrderCount or 0) for row in rows)
    total_quantity = sum(int(row.Quantity or 0) for row in rows)

    items = []
    for row in rows:
        order_count = int(row.OrderCount or 0)
        quantity = int(row.Quantity or 0)
        sales_value = _to_float(row.SalesValue)
        items.append(
            {
                "platformId": row.PlatformId,
                "platformName": row.PlatformName,
                "orderCount": order_count,
                "quantity": quantity,
                "salesValue": sales_value,
                "salesShare": _rate(sales_value, total_sales_value),
                "quantityShare": _rate(quantity, total_quantity),
                "orderShare": _rate(order_count, total_order_count),
                "averageOrderValue": sales_value / order_count if order_count else 0,
            }
        )

    return {
        "items": items,
        "totalSalesValue": total_sales_value,
        "totalOrderCount": total_order_count,
        "totalQuantity": total_quantity,
        "filters": {
            "dateFrom": str(date_from) if date_from else None,
            "dateTo": str(date_to) if date_to else None,
            "platformIds": platform_ids or [],
            "orderStatuses": cleaned_statuses,
            "includeCancelled": include_cancelled,
            "includeReturned": include_returned,
        },
    }


def get_sales_trend(
    *,
    platform_ids: list[int] | None = None,
    order_statuses: list[str] | None = None,
    include_cancelled: bool = False,
    include_returned: bool = False,
    year: int | None = None,
    month: int | None = None,
) -> dict:
    cleaned_statuses = _clean_statuses(order_statuses)
    selected_year, selected_month, start_at, end_at = _year_month_range(year, month)
    normalized_group_by = "day" if selected_month else "month"

    if selected_month:
        period_expr = func.cast(PlatformOrder.OrderCreatedAt, Date)
    else:
        period_expr = func.month(PlatformOrder.OrderCreatedAt)

    quantity_by_order = (
        db.session.query(
            PlatformOrderItem.PlatformOrderId.label("PlatformOrderId"),
            func.coalesce(func.sum(PlatformOrderItem.Quantity), 0).label("Quantity"),
        )
        .filter(PlatformOrderItem.isDeleted == False)
        .group_by(PlatformOrderItem.PlatformOrderId)
        .subquery()
    )

    if selected_month:
        day_count = monthrange(selected_year, selected_month)[1]
        periods = [
            date(selected_year, selected_month, day).strftime("%Y-%m-%d")
            for day in range(1, day_count + 1)
        ]
    else:
        periods = list(range(1, 13))

    def build_series(*, key: str, name: str, target_platform_ids: list[int] | None):
        query = (
            db.session.query(
                period_expr.label("Period"),
                func.count(PlatformOrder.PlatformOrderId).label("OrderCount"),
                func.coalesce(func.sum(quantity_by_order.c.Quantity), 0).label("Quantity"),
                func.coalesce(func.sum(PlatformOrder.SalesValue), 0).label("SalesValue"),
            )
            .select_from(PlatformOrder)
            .outerjoin(quantity_by_order, quantity_by_order.c.PlatformOrderId == PlatformOrder.PlatformOrderId)
            .filter(PlatformOrder.isDeleted == False)
            .filter(PlatformOrder.OrderCreatedAt.isnot(None))
            .filter(PlatformOrder.OrderCreatedAt >= start_at)
            .filter(PlatformOrder.OrderCreatedAt < end_at)
        )
        query = _apply_validity_filters(
            query,
            include_cancelled=include_cancelled,
            include_returned=include_returned,
        )
        query = _apply_order_filters(
            query,
            date_from=None,
            date_to=None,
            platform_ids=target_platform_ids,
            order_statuses=cleaned_statuses,
        )

        rows = (
            query
            .group_by(period_expr)
            .order_by(period_expr)
            .all()
        )

        rows_by_period = {}
        for row in rows:
            period_key = _format_period(row.Period, normalized_group_by) if selected_month else int(row.Period or 0)
            sales_value = _to_float(row.SalesValue)
            order_count = int(row.OrderCount or 0)
            quantity = int(row.Quantity or 0)

            rows_by_period[period_key] = {
                "salesValue": sales_value,
                "orderCount": order_count,
                "quantity": quantity,
            }

        items = []
        for period in periods:
            row = rows_by_period.get(period, {"salesValue": 0, "orderCount": 0, "quantity": 0})
            items.append(
                {
                    "period": f"{selected_year}-{period:02d}" if not selected_month else period,
                    "salesValue": row["salesValue"],
                    "orderCount": row["orderCount"],
                    "quantity": row["quantity"],
                }
            )

        totals = {
            "salesValue": sum(item["salesValue"] for item in items),
            "orderCount": sum(item["orderCount"] for item in items),
            "quantity": sum(item["quantity"] for item in items),
        }

        return {
            "key": key,
            "name": name,
            "items": items,
            "totals": totals,
        }

    series = [
        build_series(key="all", name="All Platforms", target_platform_ids=platform_ids),
        build_series(key="shopee", name="Shopee", target_platform_ids=[1]),
        build_series(key="tiktok", name="TikTok", target_platform_ids=[3]),
    ]
    all_series = series[0]

    return {
        "groupBy": normalized_group_by,
        "year": selected_year,
        "month": selected_month,
        "items": all_series["items"],
        "series": series,
        "totals": all_series["totals"],
        "filters": {
            "dateFrom": None,
            "dateTo": None,
            "platformIds": platform_ids or [],
            "orderStatuses": cleaned_statuses,
            "includeCancelled": include_cancelled,
            "includeReturned": include_returned,
        },
    }


def get_top_selling_products(
    *,
    year: int | None = None,
    month: int | None = None,
    platform_ids: list[int] | None = None,
    sort_by: str = "quantity",
    limit: int = 20,
) -> dict:
    selected_year, selected_month, start_at, end_at = _year_month_range(year, month)
    safe_limit = min(max(limit or 20, 1), 100)
    normalized_sort_by = sort_by if sort_by in {"quantity", "salesValue", "orderCount"} else "quantity"

    sku_expr = func.ltrim(
        func.rtrim(
            case(
                (PlatformOrder.PlatformId == literal_column("1"), PlatformOrderItem.PlatformSku),
                else_=PlatformOrderItem.SellerSku,
            )
        )
    )
    query = (
        db.session.query(
            sku_expr.label("Sku"),
            func.min(PlatformOrderItem.ProductName).label("DisplayProductName"),
            func.min(PlatformOrderItem.VariationName).label("VariationName"),
            func.coalesce(func.sum(PlatformOrderItem.Quantity), 0).label("TotalQuantity"),
            func.coalesce(func.sum(PlatformOrderItem.NetSalePrice), 0).label("SalesValue"),
            func.count(func.distinct(PlatformOrder.PlatformOrderId)).label("OrderCount"),
            func.count(func.distinct(PlatformOrder.PlatformId)).label("PlatformCount"),
        )
        .select_from(PlatformOrderItem)
        .join(PlatformOrder, PlatformOrder.PlatformOrderId == PlatformOrderItem.PlatformOrderId)
        .filter(PlatformOrder.isDeleted == False)
        .filter(PlatformOrderItem.isDeleted == False)
        .filter(PlatformOrder.IsCancelled == False)
        .filter(PlatformOrder.IsReturned == False)
        .filter(PlatformOrder.OrderCreatedAt.isnot(None))
        .filter(PlatformOrder.OrderCreatedAt >= start_at)
        .filter(PlatformOrder.OrderCreatedAt < end_at)
        .filter(sku_expr.isnot(None))
        .filter(sku_expr != "")
    )
    if platform_ids:
        query = query.filter(PlatformOrder.PlatformId.in_(platform_ids))

    rows = (
        query
        .group_by(sku_expr)
        .all()
    )

    items = []
    for row in rows:
        total_quantity = int(row.TotalQuantity or 0)
        sales_value = _to_float(row.SalesValue)
        order_count = int(row.OrderCount or 0)
        product_name = row.DisplayProductName or ""
        items.append(
            {
                "sku": row.Sku,
                "displayProductName": product_name,
                "variationName": row.VariationName or "",
                "totalQuantity": total_quantity,
                "salesValue": sales_value,
                "orderCount": order_count,
                "platformCount": int(row.PlatformCount or 0),
                "productNameSamples": [product_name] if product_name else [],
            }
        )

    sort_key_map = {
        "quantity": lambda item: (item["totalQuantity"], item["salesValue"], item["orderCount"]),
        "salesValue": lambda item: (item["salesValue"], item["totalQuantity"], item["orderCount"]),
        "orderCount": lambda item: (item["orderCount"], item["totalQuantity"], item["salesValue"]),
    }
    items = sorted(items, key=sort_key_map[normalized_sort_by], reverse=True)

    totals = {
        "productCount": len(items),
        "quantity": sum(item["totalQuantity"] for item in items),
        "salesValue": sum(item["salesValue"] for item in items),
        "orderCount": sum(item["orderCount"] for item in items),
    }

    ranked_items = []
    for index, item in enumerate(items[:safe_limit], start=1):
        ranked_items.append({"rank": index, **item})

    return {
        "year": selected_year,
        "month": selected_month,
        "sortBy": normalized_sort_by,
        "limit": safe_limit,
        "items": ranked_items,
        "totals": totals,
        "filters": {
            "platformIds": platform_ids or [],
        },
    }


def get_order_status_breakdown(
    *,
    year: int | None = None,
    month: int | None = None,
    platform_ids: list[int] | None = None,
) -> dict:
    selected_year, selected_month, start_at, end_at = _year_month_range(year, month)
    status_expr = func.coalesce(
        func.nullif(func.ltrim(func.rtrim(PlatformOrder.OrderStatus)), literal_column("''")),
        literal_column("'Unknown'"),
    )

    quantity_by_order = (
        db.session.query(
            PlatformOrderItem.PlatformOrderId.label("PlatformOrderId"),
            func.coalesce(func.sum(PlatformOrderItem.Quantity), 0).label("Quantity"),
        )
        .filter(PlatformOrderItem.isDeleted == False)
        .group_by(PlatformOrderItem.PlatformOrderId)
        .subquery()
    )

    query = (
        db.session.query(
            status_expr.label("Status"),
            func.count(PlatformOrder.PlatformOrderId).label("OrderCount"),
            func.coalesce(func.sum(PlatformOrder.SalesValue), 0).label("SalesValue"),
            func.coalesce(func.sum(quantity_by_order.c.Quantity), 0).label("Quantity"),
        )
        .select_from(PlatformOrder)
        .outerjoin(quantity_by_order, quantity_by_order.c.PlatformOrderId == PlatformOrder.PlatformOrderId)
        .filter(PlatformOrder.isDeleted == False)
        .filter(PlatformOrder.OrderCreatedAt.isnot(None))
        .filter(PlatformOrder.OrderCreatedAt >= start_at)
        .filter(PlatformOrder.OrderCreatedAt < end_at)
    )
    if platform_ids:
        query = query.filter(PlatformOrder.PlatformId.in_(platform_ids))

    rows = (
        query
        .group_by(status_expr)
        .all()
    )

    total_order_count = sum(int(row.OrderCount or 0) for row in rows)
    total_sales_value = sum(_to_float(row.SalesValue) for row in rows)
    total_quantity = sum(int(row.Quantity or 0) for row in rows)

    items = []
    for row in rows:
        order_count = int(row.OrderCount or 0)
        sales_value = _to_float(row.SalesValue)
        quantity = int(row.Quantity or 0)
        items.append(
            {
                "status": row.Status or "Unknown",
                "orderCount": order_count,
                "salesValue": sales_value,
                "quantity": quantity,
                "orderShare": _rate(order_count, total_order_count),
                "salesShare": _rate(sales_value, total_sales_value),
                "quantityShare": _rate(quantity, total_quantity),
            }
        )

    items = sorted(items, key=lambda item: (item["orderCount"], item["salesValue"]), reverse=True)

    return {
        "year": selected_year,
        "month": selected_month,
        "items": items,
        "totals": {
            "statusCount": len(items),
            "orderCount": total_order_count,
            "salesValue": total_sales_value,
            "quantity": total_quantity,
        },
        "filters": {
            "platformIds": platform_ids or [],
        },
    }
