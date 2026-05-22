from datetime import date
from typing import List

from pydantic import BaseModel


class CleanAllPlatformExportDTO(BaseModel):
    platform: str
    date_from: date
    date_to: date


class CleanAllExportDTO(BaseModel):
    platforms: List[CleanAllPlatformExportDTO]
