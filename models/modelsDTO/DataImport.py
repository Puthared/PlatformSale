from pydantic import BaseModel


class DataImportNormalizeDTO(BaseModel):
    platform: str
    createdBy: str = "system"
    mode: str = "all_pending"
