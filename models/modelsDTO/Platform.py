from typing import Optional

from pydantic import BaseModel


class PlatformCreateDTO(BaseModel):
    PlatformName: str
    createdBy: str


class PlatformUpdateDTO(BaseModel):
    PlatformName: Optional[str] = None
    modifiedBy: str
