from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class KpiSummaryFilterDTO(BaseModel):
    dateFrom: Optional[date] = None
    dateTo: Optional[date] = None
    platformIds: Optional[List[int]] = None
    orderStatuses: Optional[List[str]] = None
    includeCancelled: bool = False
    includeReturned: bool = False


class SalesByPlatformFilterDTO(KpiSummaryFilterDTO):
    pass


class SalesTrendFilterDTO(KpiSummaryFilterDTO):
    groupBy: Literal["day", "month"] = "day"
    year: int = Field(default_factory=lambda: datetime.now().year)
    month: Optional[int] = Field(default=None, ge=1, le=12)


class TopSellingProductsFilterDTO(BaseModel):
    year: int = Field(default_factory=lambda: datetime.now().year)
    month: Optional[int] = Field(default=None, ge=1, le=12)
    platformIds: Optional[List[int]] = None
    sortBy: Literal["quantity", "salesValue", "orderCount"] = "quantity"
    limit: int = Field(default=20, ge=1, le=100)


class OrderStatusBreakdownFilterDTO(BaseModel):
    year: int = Field(default_factory=lambda: datetime.now().year)
    month: Optional[int] = Field(default=None, ge=1, le=12)
    platformIds: Optional[List[int]] = None
