from datetime import datetime
import math
from fastapi import APIRouter, FastAPI, Depends, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import Platform, PlatformOrder, SalesDashboard, ShopeeMaster, TikTokMaster
from config import database as db
from config.app_settings import APP_NAME, VERSION
from src.util.CustomException import CustomHTTPException
#from src.config.database import


app = FastAPI(
    title=APP_NAME,
    version=VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

def config_router():
    app.include_router(Platform.router)
    app.include_router(PlatformOrder.router)
    app.include_router(SalesDashboard.router)
    app.include_router(ShopeeMaster.router)
    app.include_router(TikTokMaster.router)
                               
config_router()

@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request:Request, exc:CustomHTTPException):
    HeaderReturn = exc.headers
    return JSONResponse(status_code=exc.status_code,
        content={"status":HeaderReturn["status"], "message":exc.detail, "data":""})
