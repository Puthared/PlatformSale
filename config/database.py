from sqlalchemy import create_engine
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
import pyodbc as pyodbc


Url_DEV = sa.URL.create(
    drivername="mssql+pyodbc",
    host=r"localhost\SQLEXPRESS",
    database="PlatformSales",
    query={
        "driver":"ODBC DRIVER 17 for SQL Server",
        "nolock":"1"
    }
)

serverEngine = create_engine(Url_DEV,
    pool_size=20, max_overflow=5, pool_timeout=30,
    pool_recycle=3600, echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=serverEngine, expire_on_commit=False)
session = SessionLocal()
Base = declarative_base()

