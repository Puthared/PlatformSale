from sqlalchemy import Column, ForeignKey, Unicode, DateTime, Integer, Boolean
from sqlalchemy.orm import mapped_column
from config import database as db

class Platform(db.Base):
    __tablename__ = "Platform"
    PlatformId = Column(Integer, primary_key=True, autoincrement=True)
    PlatformName = Column(Unicode(200), nullable=False)
    isDeleted = Column(Boolean, nullable=False, default=False)
    createdBy = Column(Unicode(200), nullable=False)
    createdOn = Column(DateTime, nullable=False)
    modifiedBy = Column(Unicode(200), nullable=True)
    modifiedOn = Column(DateTime, nullable=True)

    def as_dict(self):
        package = {
            "PlatformId": self.PlatformId,
            "PlatformName": self.PlatformName,
            "isDeleted": self.isDeleted,
            "createdBy": self.createdBy,
            "createdOn": str(self.createdOn),
            "modifiedBy": self.modifiedBy,
            "modifiedOn": str(self.modifiedOn) if self.modifiedOn else None
        }
        return package