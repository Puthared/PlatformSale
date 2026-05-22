from __future__ import annotations

from collections import OrderedDict
from typing import Any

from openpyxl import Workbook

from shopee_order import ShopeeOrder
from shopee_report_common import FeeSheetResult, calculate_fee_summary, style_report_sheet, to_float


SHEET_NAME = "Commission Fee"

REPORT_COLUMNS = [
    ("หมายเลขคำสั่งซื้อ (order_id)", "order_id"),
    ("จำนวนรายการสินค้า (item_count)", "item_count"),
    ("ยอดราคาขายรวมของสินค้า (item_sale_amount_sum)", "item_sale_amount_sum"),
    ("เปอร์เซ็นต์ค่าคอมมิชชั่น (commission_percent)", "commission_percent"),
    ("สถานะคำสั่งซื้อ (order_status)", "order_status"),
    ("อัตราค่าธรรมเนียม (fee_rate)", "fee_rate"),
    ("โค้ดส่วนลดชำระโดยผู้ขาย (seller_voucher_discount)", "seller_voucher_discount"),
    ("โค้ดส่วนลดชำระโดย Shopee (shopee_voucher_discount)", "shopee_voucher_discount"),
    ("โค้ด Coins Cashback ชำระโดยผู้ขาย (seller_coins_cashback)", "seller_coins_cashback"),
    ("ส่วนลดจาก Shopee (shopee_discount)", "shopee_discount"),
    ("ค่าคอมมิชชั่น (commission_fee)", "commission_fee"),
    ("Transaction Fee (transaction_fee)", "transaction_fee"),
    ("ค่าบริการ (service_fee)", "service_fee"),
    ("ราคาสินค้าที่ชำระโดยผู้ซื้อ (buyer_paid_product_amount_thb)", "buyer_paid_product_amount_thb"),
    ("ค่าจัดส่งที่ชำระโดยผู้ซื้อ (buyer_paid_shipping_fee)", "buyer_paid_shipping_fee"),
    ("ค่าจัดส่งที่ Shopee ออกให้โดยประมาณ (estimated_shopee_shipping_subsidy)", "estimated_shopee_shipping_subsidy"),
    ("ค่าจัดส่งสินค้าคืน (return_shipping_fee)", "return_shipping_fee"),
    ("จำนวนเงินทั้งหมด (total_amount)", "total_amount"),
    ("ค่าจัดส่งโดยประมาณ (estimated_shipping_fee)", "estimated_shipping_fee"),
]

MONEY_FIELDS = {
    "item_sale_amount_sum",
    "seller_voucher_discount",
    "shopee_voucher_discount",
    "seller_coins_cashback",
    "shopee_discount",
    "commission_fee",
    "transaction_fee",
    "service_fee",
    "buyer_paid_product_amount_thb",
    "buyer_paid_shipping_fee",
    "estimated_shopee_shipping_subsidy",
    "return_shipping_fee",
    "total_amount",
    "estimated_shipping_fee",
}


def build_report_rows(grouped_orders: OrderedDict[str, list[ShopeeOrder]]) -> list[list[Any]]:
    rows: list[list[Any]] = []

    for order_id, order_rows in grouped_orders.items():
        first = order_rows[0]
        item_sale_amount_sum = sum(to_float(row.sale_price) * to_float(row.quantity) for row in order_rows)
        original_price_sum = sum(to_float(row.original_price) * to_float(row.quantity) for row in order_rows)
        commission_fee = to_float(first.commission_fee)
        commission_percent = commission_fee / original_price_sum if original_price_sum else 0.0

        rows.append(
            [
                order_id,
                len(order_rows),
                item_sale_amount_sum,
                commission_percent,
                first.order_status,
                first.fee_rate,
                to_float(first.seller_voucher_discount),
                to_float(first.shopee_voucher_discount),
                to_float(first.seller_coins_cashback),
                to_float(first.shopee_discount),
                commission_fee,
                to_float(first.transaction_fee),
                to_float(first.service_fee),
                to_float(first.buyer_paid_product_amount_thb),
                to_float(first.buyer_paid_shipping_fee),
                to_float(first.estimated_shopee_shipping_subsidy),
                to_float(first.return_shipping_fee),
                to_float(first.total_amount),
                to_float(first.estimated_shipping_fee),
            ]
        )

    return rows


def add_commission_fee_sheet(wb: Workbook, grouped_orders: OrderedDict[str, list[ShopeeOrder]]) -> FeeSheetResult:
    rows = build_report_rows(grouped_orders)
    ws = wb.create_sheet(SHEET_NAME)

    headers = [header for header, _ in REPORT_COLUMNS]
    field_names = [field_name for _, field_name in REPORT_COLUMNS]
    for row_index, row_values in enumerate(rows, start=5):
        for col_index, value in enumerate(row_values, start=1):
            ws.cell(row=row_index, column=col_index, value=value)

    style_report_sheet(
        ws,
        title="Shopee Commission Fee",
        subtitle=(
            "Filtered: order_status != 'ยกเลิกแล้ว' and returned_quantity == 0. "
            "commission_percent = commission_fee / sum(original_price * quantity)."
        ),
        headers=headers,
        row_count=len(rows),
        percent_field="commission_percent",
        money_fields=MONEY_FIELDS,
        field_names=field_names,
        table_name="ShopeeCommissionFeeTable",
    )

    percent_values = [float(row[3]) for row in rows]
    return FeeSheetResult(SHEET_NAME, len(rows), calculate_fee_summary(percent_values))
