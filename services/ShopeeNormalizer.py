from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from config import database as db
from models.Platform import Platform
from models.PlatformOrder import PlatformOrder
from models.PlatformOrderFee import PlatformOrderFee
from models.PlatformOrderItem import PlatformOrderItem
from models.ShopeeMaster import ShopeeMaster


RAW_SOURCE_TABLE = "ShopeeMaster"
SHOPEE_PLATFORM_NAME = "Shopee"
CANCELLED_STATUS = "ยกเลิกแล้ว"
COMPLETED_STATUS = "สำเร็จแล้ว"
DELIVERED_STATUS = "จัดส่งสำเร็จแล้ว"
DELIVERED_PENDING_RETURN_PREFIX = "ผู้ซื้อได้รับสินค้าแล้ว"
NORMALIZED_CANCELLED_STATUS = "Cancelled"
NORMALIZED_COMPLETED_STATUS = "Completed"
NORMALIZED_DELIVERED_STATUS = "Delivered"
NORMALIZED_DELIVERED_PENDING_RETURN_STATUS = "DeliveredPendingReturn"


def _to_decimal(value: Any) -> Decimal | None:
    if value in (None, "", "-"):
        return None
    try:
        return Decimal(str(value).replace(",", "").replace("%", "").strip())
    except (InvalidOperation, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    decimal_value = _to_decimal(value)
    if decimal_value is None:
        return None
    return int(decimal_value)


def _to_datetime(value: Any) -> datetime | None:
    if value in (None, "", "-"):
        return None
    text = str(value).strip()
    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    )
    for date_format in formats:
        try:
            return datetime.strptime(text, date_format)
        except ValueError:
            continue
    return None


def _decimal_or_zero(value: Any) -> Decimal:
    return _to_decimal(value) or Decimal("0")


def _rate(amount: Decimal | None, base_amount: Decimal | None) -> Decimal | None:
    if amount is None or base_amount in (None, Decimal("0")):
        return None
    return amount / base_amount


def _normalize_order_status(raw_status: Any) -> str | None:
    if raw_status in (None, ""):
        return None

    status = str(raw_status).strip()
    if status == COMPLETED_STATUS:
        return NORMALIZED_COMPLETED_STATUS
    if status == CANCELLED_STATUS:
        return NORMALIZED_CANCELLED_STATUS
    if status == DELIVERED_STATUS:
        return NORMALIZED_DELIVERED_STATUS
    if status.startswith(DELIVERED_PENDING_RETURN_PREFIX):
        return NORMALIZED_DELIVERED_PENDING_RETURN_STATUS

    return status


def _get_shopee_platform_id() -> int:
    platform = (
        db.session.query(Platform)
        .filter(Platform.PlatformName == SHOPEE_PLATFORM_NAME)
        .filter(Platform.isDeleted == False)
        .first()
    )
    if platform is None:
        raise ValueError("Platform 'Shopee' not found. Please create Platform record first.")
    return platform.PlatformId


def _group_by_order_id(raw_rows: list[ShopeeMaster]) -> OrderedDict[str, list[ShopeeMaster]]:
    grouped: OrderedDict[str, list[ShopeeMaster]] = OrderedDict()
    for raw_row in raw_rows:
        order_id = str(raw_row.OrderId or "").strip()
        if not order_id:
            raw_row.NormalizeError = "Missing OrderId"
            continue
        grouped.setdefault(order_id, []).append(raw_row)
    return grouped


def _chunks(values: list[str], chunk_size: int = 1000):
    for index in range(0, len(values), chunk_size):
        yield values[index:index + chunk_size]


def _sum_original_price(order_rows: list[ShopeeMaster]) -> Decimal:
    total = Decimal("0")
    for row in order_rows:
        original_price = _decimal_or_zero(row.OriginalPrice)
        quantity = _decimal_or_zero(row.Quantity)
        total += original_price * quantity
    return total


def _sum_returned_quantity(order_rows: list[ShopeeMaster]) -> int:
    total = 0
    for row in order_rows:
        total += _to_int(row.ReturnedQuantity) or 0
    return total


def _calculate_sales_value(row: ShopeeMaster) -> Decimal:
    return (
        _decimal_or_zero(row.BuyerPaidProductAmountThb)
        + _decimal_or_zero(row.BuyerPaidShippingFee)
        + _decimal_or_zero(row.ShopeeVoucherDiscount)
        + _decimal_or_zero(row.ShopeeDiscount)
        + _decimal_or_zero(row.PaymentChannelPromotionDiscount)
        + (_decimal_or_zero(row.CoinDiscount) / Decimal("100"))
    )


def _apply_platform_order_values(
    platform_order: PlatformOrder,
    *,
    platform_id: int,
    order_id: str,
    first_row: ShopeeMaster,
    now: datetime,
    user: str,
    is_create: bool,
) -> PlatformOrder:
    normalized_order_status = _normalize_order_status(first_row.OrderStatus)
    platform_order.PlatformId = platform_id
    platform_order.PlatformOrderNo = order_id
    platform_order.OrderStatus = normalized_order_status
    platform_order.OrderCreatedAt = _to_datetime(first_row.OrderCreatedAt)
    platform_order.PaidAt = _to_datetime(first_row.PaidAt)
    platform_order.CompletedAt = _to_datetime(first_row.CompletedAt)
    platform_order.BuyerUsername = first_row.BuyerUsername
    platform_order.BuyerPaidProductAmount = _to_decimal(first_row.BuyerPaidProductAmountThb)
    platform_order.BuyerPaidShippingFee = _to_decimal(first_row.BuyerPaidShippingFee)
    platform_order.TotalAmount = _to_decimal(first_row.TotalAmount)
    platform_order.SalesValue = _calculate_sales_value(first_row)
    platform_order.IsCancelled = normalized_order_status == NORMALIZED_CANCELLED_STATUS
    platform_order.RawSourceTable = RAW_SOURCE_TABLE
    platform_order.RawSourceId = first_row.ShopeeMasterId
    platform_order.isDeleted = False

    if is_create:
        platform_order.createdBy = user
        platform_order.createdOn = now
    else:
        platform_order.modifiedBy = user
        platform_order.modifiedOn = now

    return platform_order


def _create_platform_order(
    *,
    platform_id: int,
    order_id: str,
    first_row: ShopeeMaster,
    now: datetime,
    created_by: str,
) -> PlatformOrder:
    platform_order = PlatformOrder(IsReturned=False)
    return _apply_platform_order_values(
        platform_order,
        platform_id=platform_id,
        order_id=order_id,
        first_row=first_row,
        now=now,
        user=created_by,
        is_create=True,
    )


def _create_platform_order_item(
    *,
    platform_order_id: int,
    raw_row: ShopeeMaster,
    now: datetime,
    created_by: str,
) -> PlatformOrderItem:
    return PlatformOrderItem(
        PlatformOrderId=platform_order_id,
        PlatformSku=raw_row.SkuReference,
        SellerSku=raw_row.ParentSku,
        ProductName=raw_row.ProductName,
        VariationName=raw_row.VariationName,
        OriginalPrice=_to_decimal(raw_row.OriginalPrice),
        SalePrice=_to_decimal(raw_row.SalePrice),
        Quantity=_to_int(raw_row.Quantity),
        ReturnedQuantity=_to_int(raw_row.ReturnedQuantity),
        NetSalePrice=_to_decimal(raw_row.NetSalePrice),
        RawSourceTable=RAW_SOURCE_TABLE,
        RawSourceId=raw_row.ShopeeMasterId,
        isDeleted=False,
        createdBy=created_by,
        createdOn=now,
    )


def _create_fee(
    *,
    platform_order_id: int,
    fee_type: str,
    amount: Decimal | None,
    base_amount: Decimal | None,
    raw_source_id: int,
    now: datetime,
    created_by: str,
) -> PlatformOrderFee:
    return PlatformOrderFee(
        PlatformOrderId=platform_order_id,
        FeeType=fee_type,
        FeeAmount=amount,
        FeeBaseAmount=base_amount,
        FeeRate=_rate(amount, base_amount),
        RawSourceTable=RAW_SOURCE_TABLE,
        RawSourceId=raw_source_id,
        isDeleted=False,
        createdBy=created_by,
        createdOn=now,
    )


def _mark_raw_rows_normalized(raw_rows: list[ShopeeMaster], now: datetime) -> int:
    marked_count = 0
    for raw_row in raw_rows:
        raw_row.IsNormalized = True
        raw_row.NormalizedOn = now
        raw_row.NormalizeError = None
        marked_count += 1
    return marked_count


def _soft_delete_platform_order_items(platform_order_id: int, now: datetime, modified_by: str) -> int:
    existing_items = (
        db.session.query(PlatformOrderItem)
        .filter(PlatformOrderItem.PlatformOrderId == platform_order_id)
        .all()
    )

    soft_deleted_count = 0
    for item in existing_items:
        if item.isDeleted is not True:
            soft_deleted_count += 1
        item.isDeleted = True
        item.modifiedBy = modified_by
        item.modifiedOn = now

    return soft_deleted_count


def _soft_delete_platform_order_fees(platform_order_id: int, now: datetime, modified_by: str) -> int:
    existing_fees = (
        db.session.query(PlatformOrderFee)
        .filter(PlatformOrderFee.PlatformOrderId == platform_order_id)
        .all()
    )

    soft_deleted_count = 0
    for fee in existing_fees:
        if fee.isDeleted is not True:
            soft_deleted_count += 1
        fee.isDeleted = True
        fee.modifiedBy = modified_by
        fee.modifiedOn = now

    return soft_deleted_count


def _soft_delete_platform_order_tree(platform_order: PlatformOrder, now: datetime, modified_by: str) -> tuple[int, int, int]:
    items_soft_deleted = _soft_delete_platform_order_items(platform_order.PlatformOrderId, now, modified_by)
    fees_soft_deleted = _soft_delete_platform_order_fees(platform_order.PlatformOrderId, now, modified_by)
    orders_soft_deleted = 0

    if platform_order.isDeleted is not True:
        orders_soft_deleted = 1
    platform_order.isDeleted = True
    platform_order.modifiedBy = modified_by
    platform_order.modifiedOn = now

    return orders_soft_deleted, items_soft_deleted, fees_soft_deleted


def normalize_shopee_master(limit: int = 1000, created_by: str = "system", mode: str = "skip_existing") -> dict:
    if mode != "skip_existing":
        raise ValueError("Only mode='skip_existing' is supported right now.")

    now = datetime.now()
    platform_id = _get_shopee_platform_id()

    trigger_rows = (
        db.session.query(ShopeeMaster)
        .filter(ShopeeMaster.IsNormalized == False)
        .order_by(ShopeeMaster.ShopeeMasterId)
        .limit(limit)
        .all()
    )
    trigger_orders = _group_by_order_id(trigger_rows)
    trigger_order_ids = list(trigger_orders.keys())

    raw_rows = []
    for order_id_chunk in _chunks(trigger_order_ids):
        raw_rows.extend(
            db.session.query(ShopeeMaster)
            .filter(ShopeeMaster.OrderId.in_(order_id_chunk))
            .order_by(ShopeeMaster.ShopeeMasterId)
            .all()
        )

    grouped_orders = _group_by_order_id(raw_rows)
    orders_created = 0
    orders_updated = 0
    orders_soft_deleted = 0
    orders_skipped = 0
    items_created = 0
    items_soft_deleted = 0
    fees_created = 0
    fees_soft_deleted = 0
    raw_rows_marked = 0
    failed_orders = 0

    for order_id, order_rows in grouped_orders.items():
        try:
            existing_order = (
                db.session.query(PlatformOrder)
                .filter(PlatformOrder.PlatformId == platform_id)
                .filter(PlatformOrder.PlatformOrderNo == order_id)
                .order_by(PlatformOrder.PlatformOrderId)
                .first()
            )

            active_order_rows = [
                raw_row for raw_row in order_rows
                if raw_row.isDeleted is not True
            ]

            if not active_order_rows:
                if existing_order is not None:
                    order_deleted_count, item_deleted_count, fee_deleted_count = _soft_delete_platform_order_tree(
                        existing_order,
                        now,
                        created_by,
                    )
                    orders_soft_deleted += order_deleted_count
                    items_soft_deleted += item_deleted_count
                    fees_soft_deleted += fee_deleted_count

                raw_rows_marked += _mark_raw_rows_normalized(order_rows, now)
                continue

            first_row = active_order_rows[0]
            original_price_sum = _sum_original_price(active_order_rows)
            returned_quantity_sum = _sum_returned_quantity(active_order_rows)

            if existing_order is None:
                platform_order = _create_platform_order(
                    platform_id=platform_id,
                    order_id=order_id,
                    first_row=first_row,
                    now=now,
                    created_by=created_by,
                )
                db.session.add(platform_order)
                db.session.flush()
                orders_created += 1
            else:
                platform_order = _apply_platform_order_values(
                    existing_order,
                    platform_id=platform_id,
                    order_id=order_id,
                    first_row=first_row,
                    now=now,
                    user=created_by,
                    is_create=False,
                )
                orders_updated += 1

            platform_order.IsReturned = returned_quantity_sum > 0
            items_soft_deleted += _soft_delete_platform_order_items(
                platform_order.PlatformOrderId,
                now,
                created_by,
            )
            fees_soft_deleted += _soft_delete_platform_order_fees(
                platform_order.PlatformOrderId,
                now,
                created_by,
            )

            for raw_row in active_order_rows:
                db.session.add(
                    _create_platform_order_item(
                        platform_order_id=platform_order.PlatformOrderId,
                        raw_row=raw_row,
                        now=now,
                        created_by=created_by,
                    )
                )
                items_created += 1

            buyer_paid_product_amount = _to_decimal(first_row.BuyerPaidProductAmountThb)
            fee_specs = (
                ("Commission", _to_decimal(first_row.CommissionFee), original_price_sum),
                ("Transaction", _to_decimal(first_row.TransactionFee), buyer_paid_product_amount),
                ("Service", _to_decimal(first_row.ServiceFee), original_price_sum),
                ("Shipping", _to_decimal(first_row.EstimatedShippingFee), buyer_paid_product_amount),
                ("ReturnShipping", _to_decimal(first_row.ReturnShippingFee), buyer_paid_product_amount),
            )

            for fee_type, fee_amount, fee_base_amount in fee_specs:
                db.session.add(
                    _create_fee(
                        platform_order_id=platform_order.PlatformOrderId,
                        fee_type=fee_type,
                        amount=fee_amount,
                        base_amount=fee_base_amount,
                        raw_source_id=first_row.ShopeeMasterId,
                        now=now,
                        created_by=created_by,
                    )
                )
                fees_created += 1

            raw_rows_marked += _mark_raw_rows_normalized(order_rows, now)

        except Exception as err:
            failed_orders += 1
            error = str(err)
            for raw_row in order_rows:
                raw_row.NormalizeError = error

    db.session.commit()

    return {
        "rawRowsPicked": len(trigger_rows),
        "ordersPicked": len(grouped_orders),
        "ordersCreated": orders_created,
        "ordersUpdated": orders_updated,
        "ordersSoftDeleted": orders_soft_deleted,
        "ordersSkipped": orders_skipped,
        "itemsCreated": items_created,
        "itemsSoftDeleted": items_soft_deleted,
        "feesCreated": fees_created,
        "feesSoftDeleted": fees_soft_deleted,
        "rawRowsMarkedNormalized": raw_rows_marked,
        "failedOrders": failed_orders,
    }
