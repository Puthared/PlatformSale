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
DELIVERED_PENDING_RETURN_PREFIX = "ผู้ซื้อได้รับสินค้าแล้ว"
NORMALIZED_CANCELLED_STATUS = "Cancelled"
NORMALIZED_COMPLETED_STATUS = "Completed"
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


def _create_platform_order(
    *,
    platform_id: int,
    order_id: str,
    first_row: ShopeeMaster,
    now: datetime,
    created_by: str,
) -> PlatformOrder:
    normalized_order_status = _normalize_order_status(first_row.OrderStatus)
    return PlatformOrder(
        PlatformId=platform_id,
        PlatformOrderNo=order_id,
        OrderStatus=normalized_order_status,
        OrderCreatedAt=_to_datetime(first_row.OrderCreatedAt),
        PaidAt=_to_datetime(first_row.PaidAt),
        CompletedAt=_to_datetime(first_row.CompletedAt),
        BuyerUsername=first_row.BuyerUsername,
        BuyerPaidProductAmount=_to_decimal(first_row.BuyerPaidProductAmountThb),
        BuyerPaidShippingFee=_to_decimal(first_row.BuyerPaidShippingFee),
        TotalAmount=_to_decimal(first_row.TotalAmount),
        IsCancelled=normalized_order_status == NORMALIZED_CANCELLED_STATUS,
        IsReturned=False,
        RawSourceTable=RAW_SOURCE_TABLE,
        RawSourceId=first_row.ShopeeMasterId,
        isDeleted=False,
        createdBy=created_by,
        createdOn=now,
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


def normalize_shopee_master(limit: int = 1000, created_by: str = "system", mode: str = "skip_existing") -> dict:
    if mode != "skip_existing":
        raise ValueError("Only mode='skip_existing' is supported right now.")

    now = datetime.now()
    platform_id = _get_shopee_platform_id()

    raw_rows = (
        db.session.query(ShopeeMaster)
        .filter(ShopeeMaster.isDeleted == False)
        .filter(ShopeeMaster.IsNormalized == False)
        .order_by(ShopeeMaster.ShopeeMasterId)
        .limit(limit)
        .all()
    )

    grouped_orders = _group_by_order_id(raw_rows)
    orders_created = 0
    orders_skipped = 0
    items_created = 0
    fees_created = 0
    raw_rows_marked = 0
    failed_orders = 0

    for order_id, order_rows in grouped_orders.items():
        try:
            existing_order = (
                db.session.query(PlatformOrder)
                .filter(PlatformOrder.PlatformId == platform_id)
                .filter(PlatformOrder.PlatformOrderNo == order_id)
                .filter(PlatformOrder.isDeleted == False)
                .first()
            )

            if existing_order is not None:
                orders_skipped += 1
                for raw_row in order_rows:
                    raw_row.IsNormalized = True
                    raw_row.NormalizedOn = now
                    raw_row.NormalizeError = None
                    raw_rows_marked += 1
                continue

            first_row = order_rows[0]
            original_price_sum = _sum_original_price(order_rows)
            returned_quantity_sum = _sum_returned_quantity(order_rows)

            platform_order = _create_platform_order(
                platform_id=platform_id,
                order_id=order_id,
                first_row=first_row,
                now=now,
                created_by=created_by,
            )
            platform_order.IsReturned = returned_quantity_sum > 0
            db.session.add(platform_order)
            db.session.flush()
            orders_created += 1

            for raw_row in order_rows:
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

            for raw_row in order_rows:
                raw_row.IsNormalized = True
                raw_row.NormalizedOn = now
                raw_row.NormalizeError = None
                raw_rows_marked += 1

        except Exception as err:
            failed_orders += 1
            error = str(err)
            for raw_row in order_rows:
                raw_row.NormalizeError = error

    db.session.commit()

    return {
        "rawRowsPicked": len(raw_rows),
        "ordersPicked": len(grouped_orders),
        "ordersCreated": orders_created,
        "ordersSkipped": orders_skipped,
        "itemsCreated": items_created,
        "feesCreated": fees_created,
        "rawRowsMarkedNormalized": raw_rows_marked,
        "failedOrders": failed_orders,
    }
