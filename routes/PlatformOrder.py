import math
import sys
from decimal import Decimal
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse
from models import Platform, PlatformOrder
from models.modelsDTO import PlatformOrder as tb
from services.PlatformOrderCleanAllExporter import PlatformExportFilter, export_clean_all_excel
from config import database as db


router = APIRouter(
    prefix="/PlatformOrder",
    tags=["PlatformOrder"],
    responses={
        404: {
            "message": "Not Found"
        }
    }
)

PlatformTable = Platform.Platform
PlatformOrderTable = PlatformOrder.PlatformOrder


def _to_float(value):
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return float(value)
    return value


def _to_string(value):
    if value is None:
        return None
    return str(value)


def _clean_text(value):
    if value is None:
        return None
    if not isinstance(value, str):
        return value

    try:
        has_latin1_mojibake = any(127 < ord(char) < 256 for char in value)
        has_thai_text = any(0x0E00 <= ord(char) <= 0x0E7F for char in value)
        if has_latin1_mojibake and not has_thai_text:
            return value.encode("latin1").decode("utf-8")
    except UnicodeError:
        return value

    return value


def _platform_order_to_dict(order, platform_name):
    return {
        "PlatformOrderId": order.PlatformOrderId,
        "PlatformId": order.PlatformId,
        "PlatformName": _clean_text(platform_name),
        "PlatformOrderNo": _clean_text(order.PlatformOrderNo),
        "OrderStatus": _clean_text(order.OrderStatus),
        "OrderCreatedAt": _to_string(order.OrderCreatedAt),
        "PaidAt": _to_string(order.PaidAt),
        "CompletedAt": _to_string(order.CompletedAt),
        "BuyerUsername": _clean_text(order.BuyerUsername),
        "BuyerPaidProductAmount": _to_float(order.BuyerPaidProductAmount),
        "BuyerPaidShippingFee": _to_float(order.BuyerPaidShippingFee),
        "TotalAmount": _to_float(order.TotalAmount),
        "IsCancelled": bool(order.IsCancelled),
        "IsReturned": bool(order.IsReturned),
        "RawSourceTable": _clean_text(order.RawSourceTable),
        "RawSourceId": order.RawSourceId,
        "isDeleted": bool(order.isDeleted),
        "createdBy": order.createdBy,
        "createdOn": _to_string(order.createdOn),
        "modifiedBy": order.modifiedBy,
        "modifiedOn": _to_string(order.modifiedOn),
    }


@router.get("/GetPlatformOrder")
async def GetPlatformOrder(req: Request, page: int, perpage: int = 1000):
    try:
        if page < 1:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Page must be greater than 0.", "data": ""},
            )
        if perpage < 1:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Perpage must be greater than 0.", "data": ""},
            )

        BaseQuery = (
            db.session
            .query(PlatformOrderTable, PlatformTable.PlatformName)
            .join(PlatformTable, PlatformOrderTable.PlatformId == PlatformTable.PlatformId)
            .filter(PlatformOrderTable.isDeleted == False)
            .filter(PlatformTable.isDeleted == False)
        )

        TotalRecord = BaseQuery.count()
        AmountPage = 1 if TotalRecord <= perpage else math.ceil(TotalRecord / perpage)

        if page > AmountPage:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Invaild page pagination.", "data": ""},
            )

        PlatformOrderItems = (
            BaseQuery
            .order_by(PlatformOrderTable.PlatformOrderId.desc())
            .limit(perpage)
            .offset((page - 1) * perpage)
            .all()
        )

        PaginatedRecord = [
            _platform_order_to_dict(order, platform_name)
            for order, platform_name in PlatformOrderItems
        ]

        PaginateReturn = {
            "totalRecords": TotalRecord,
            "pageCount": AmountPage,
            "pageNo": page,
            "pageSize": perpage,
        }
        return {
            "status": "success",
            "message": "",
            "data": {"data": PaginatedRecord, "pagination": PaginateReturn},
        }

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()


@router.get("/GetPlatformOrderById/{platformOrderId}")
async def GetPlatformOrderById(req: Request, platformOrderId: int):
    try:
        PlatformOrderItem = (
            db.session
            .query(PlatformOrderTable, PlatformTable.PlatformName)
            .join(PlatformTable, PlatformOrderTable.PlatformId == PlatformTable.PlatformId)
            .filter(PlatformOrderTable.PlatformOrderId == platformOrderId)
            .filter(PlatformOrderTable.isDeleted == False)
            .filter(PlatformTable.isDeleted == False)
            .first()
        )

        if PlatformOrderItem is None:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "PlatformOrder not found.", "data": ""},
            )

        order, platform_name = PlatformOrderItem
        return {
            "status": "success",
            "message": "",
            "data": _platform_order_to_dict(order, platform_name),
        }

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()


@router.post("/ExportCleanAllExcel")
async def ExportCleanAllExcel(req: Request, body: tb.CleanAllExportDTO):
    try:
        export_filters = [
            PlatformExportFilter(
                platform=item.platform,
                date_from=item.date_from,
                date_to=item.date_to,
            )
            for item in body.platforms
        ]

        result = export_clean_all_excel(export_filters)

        return FileResponse(
            path=str(result.file_path),
            filename=result.file_name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "X-Export-Row-Count": str(result.row_count),
            },
        )

    except ValueError as err:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(err), "data": ""})
    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()
