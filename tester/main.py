from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from build_shopee_commission_report import add_commission_fee_sheet
from build_shopee_service_fee_report import add_service_fee_sheet
from build_shopee_transaction_fee_report import add_transaction_fee_sheet
from shopee_order_reader import read_shopee_orders
from shopee_report_common import add_summary_sheet, group_active_orders


RAW_WORKBOOK_PATH = Path(r"C:\Education\PlatformSale\Commission_MML.xlsx")
OUTPUT_WORKBOOK_PATH = Path(r"C:\Education\PlatformSale\Shopee_Fee_Report.xlsx")


def build_fee_report(raw_workbook_path: Path, output_workbook_path: Path) -> Path:
    orders = read_shopee_orders(raw_workbook_path)
    grouped_orders = group_active_orders(orders)

    wb = Workbook()
    wb.remove(wb.active)

    commission_result = add_commission_fee_sheet(wb, grouped_orders)
    transaction_result = add_transaction_fee_sheet(wb, grouped_orders)
    service_result = add_service_fee_sheet(wb, grouped_orders)
    sheet_results = [commission_result, transaction_result, service_result]

    add_summary_sheet(
        wb,
        sheet_results,
        raw_row_count=len(orders),
        active_order_count=len(grouped_orders),
    )

    saved_path = output_workbook_path
    try:
        wb.save(saved_path)
    except PermissionError:
        saved_path = output_workbook_path.with_name(f"{output_workbook_path.stem}_new{output_workbook_path.suffix}")
        wb.save(saved_path)

    print(f"created {saved_path}")
    print(f"raw item rows={len(orders)}")
    print(f"active order count={len(grouped_orders)}")
    print()

    for result in sheet_results:
        summary = result.summary
        print(f"{result.sheet_name} percent summary")
        print(f"count={summary.order_count} orders")
        print(f"min={summary.min_percent:.2%}")
        print(f"mean={summary.mean_percent:.2%}")
        print(f"std={summary.std_percent:.2%}")
        print(f"max={summary.max_percent:.2%}")
        print("rounded buckets:")
        for bucket, count in summary.rounded_buckets.items():
            print(f"{bucket}% = {count} orders")
        print()

    return saved_path


if __name__ == "__main__":
    build_fee_report(RAW_WORKBOOK_PATH, OUTPUT_WORKBOOK_PATH)
