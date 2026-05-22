import math
import sys
from datetime import datetime
from os import path

sys.path.append(path.join(path.dirname(__file__), ".."))

from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from models import Platform
from models.modelsDTO import Platform as tb
from config import database as db


router = APIRouter(
    prefix="/Platform",
    tags=["Platform"],
    responses={
        404: {
            "message": "Not Found"
        }
    }
)

PlatformTable = Platform.Platform


def _payload_to_dict(payload) -> dict:
    if hasattr(payload, "model_dump"):
        return payload.model_dump(exclude_unset=True)
    if hasattr(payload, "dict"):
        return payload.dict(exclude_unset=True)
    return dict(payload)


@router.get("/GetPlatform")
async def GetPlatform(req: Request, page: int, perpage: int = 1000):
    try:
        PlatformItem = (
            db.session
            .query(PlatformTable)
            .filter(PlatformTable.isDeleted == False)
            .order_by(PlatformTable.PlatformId)
            .all()
        )

        PaginatedRecord = []
        Page = page
        Perpage = perpage
        TotalRecord = PlatformItem.__len__()
        AmountPage = 1 if TotalRecord <= Perpage else math.ceil(TotalRecord / Perpage)

        if Page > AmountPage:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Invaild page pagination.", "data": ""},
            )

        TargetIndex = (Page - 1) * Perpage
        FinishElement = TargetIndex + Perpage
        if Page < AmountPage:
            PaginatedRecord = PlatformItem[TargetIndex:FinishElement]
        else:
            PaginatedRecord = PlatformItem[TargetIndex:]
        PaginatedRecord = [item.as_dict() for item in PaginatedRecord]

        PaginateReturn = {
            "totalRecords": TotalRecord,
            "pageCount": AmountPage,
            "pageNo": Page,
            "pageSize": Perpage,
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


@router.get("/GetPlatformById/{platformId}")
async def GetPlatformById(req: Request, platformId: int):
    try:
        PlatformItem = (
            db.session
            .query(PlatformTable)
            .filter(PlatformTable.PlatformId == platformId)
            .filter(PlatformTable.isDeleted == False)
            .first()
        )

        if PlatformItem is None:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Platform not found.", "data": ""},
            )

        return {"status": "success", "message": "", "data": PlatformItem.as_dict()}

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()


@router.post("/CreatePlatform")
async def CreatePlatform(req: Request, body: tb.PlatformCreateDTO):
    try:
        payload = _payload_to_dict(body)
        PlatformItem = PlatformTable(
            PlatformName=payload.get("PlatformName"),
            isDeleted=False,
            createdBy=payload.get("createdBy") or "system",
            createdOn=datetime.now(),
        )

        db.session.add(PlatformItem)
        db.session.commit()
        db.session.refresh(PlatformItem)

        return {"status": "success", "message": "Create Platform success.", "data": PlatformItem.as_dict()}

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()


@router.put("/UpdatePlatform/{platformId}")
async def UpdatePlatform(req: Request, platformId: int, body: tb.PlatformUpdateDTO):
    try:
        PlatformItem = (
            db.session
            .query(PlatformTable)
            .filter(PlatformTable.PlatformId == platformId)
            .filter(PlatformTable.isDeleted == False)
            .first()
        )

        if PlatformItem is None:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Platform not found.", "data": ""},
            )

        payload = _payload_to_dict(body)
        if "PlatformName" in payload:
            PlatformItem.PlatformName = payload.get("PlatformName")
        PlatformItem.modifiedBy = payload.get("modifiedBy") or "system"
        PlatformItem.modifiedOn = datetime.now()

        db.session.commit()
        db.session.refresh(PlatformItem)

        return {"status": "success", "message": "Update Platform success.", "data": PlatformItem.as_dict()}

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()


@router.delete("/DeletePlatform/{platformId}")
async def DeletePlatform(req: Request, platformId: int, payload: dict = Body(default={})):
    try:
        PlatformItem = (
            db.session
            .query(PlatformTable)
            .filter(PlatformTable.PlatformId == platformId)
            .filter(PlatformTable.isDeleted == False)
            .first()
        )

        if PlatformItem is None:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Platform not found.", "data": ""},
            )

        PlatformItem.isDeleted = True
        PlatformItem.modifiedBy = payload.get("modifiedBy") or payload.get("createdBy") or "system"
        PlatformItem.modifiedOn = datetime.now()

        db.session.commit()
        db.session.refresh(PlatformItem)

        return {"status": "success", "message": "Delete Platform success.", "data": PlatformItem.as_dict()}

    except Exception as err:
        error = str(err)
        db.session.rollback()
        return JSONResponse(status_code=500, content={"status": "error", "message": error, "data": ""})
    finally:
        db.session.close()
