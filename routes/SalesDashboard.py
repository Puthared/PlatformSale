import sys
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from models.modelsDTO import SalesDashboard as tb
from config import database as db
from services.SalesDashboardService import (
    get_kpi_summary,
    get_order_status_breakdown,
    get_sales_by_platform,
    get_sales_trend,
    get_top_selling_products,
)


router = APIRouter(
    prefix="/SalesDashboard",
    tags=["SalesDashboard"],
    responses={
        404: {
            "message": "Not Found"
        }
    }
)


@router.post("/GetKpiSummary")
async def GetKpiSummary(req: Request, body: tb.KpiSummaryFilterDTO):
    try:
        result = get_kpi_summary(
            date_from=body.dateFrom,
            date_to=body.dateTo,
            platform_ids=body.platformIds,
            order_statuses=body.orderStatuses,
            include_cancelled=body.includeCancelled,
            include_returned=body.includeReturned,
        )
        return {"status": "success", "message": "", "data": result}

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()


@router.post("/GetSalesByPlatform")
async def GetSalesByPlatform(req: Request, body: tb.SalesByPlatformFilterDTO):
    try:
        result = get_sales_by_platform(
            date_from=body.dateFrom,
            date_to=body.dateTo,
            platform_ids=body.platformIds,
            order_statuses=body.orderStatuses,
            include_cancelled=body.includeCancelled,
            include_returned=body.includeReturned,
        )
        return {"status": "success", "message": "", "data": result}

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()


@router.post("/GetSalesTrend")
async def GetSalesTrend(req: Request, body: tb.SalesTrendFilterDTO):
    try:
        result = get_sales_trend(
            platform_ids=body.platformIds,
            order_statuses=body.orderStatuses,
            include_cancelled=body.includeCancelled,
            include_returned=body.includeReturned,
            year=body.year,
            month=body.month,
        )
        return {"status": "success", "message": "", "data": result}

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()


@router.post("/GetTopSellingProducts")
async def GetTopSellingProducts(req: Request, body: tb.TopSellingProductsFilterDTO):
    try:
        result = get_top_selling_products(
            year=body.year,
            month=body.month,
            platform_ids=body.platformIds,
            sort_by=body.sortBy,
            limit=body.limit,
        )
        return {"status": "success", "message": "", "data": result}

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()


@router.post("/GetOrderStatusBreakdown")
async def GetOrderStatusBreakdown(req: Request, body: tb.OrderStatusBreakdownFilterDTO):
    try:
        result = get_order_status_breakdown(
            year=body.year,
            month=body.month,
            platform_ids=body.platformIds,
        )
        return {"status": "success", "message": "", "data": result}

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()
