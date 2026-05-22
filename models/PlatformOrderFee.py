from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, Unicode

from config import database as db


class PlatformOrderFee(db.Base):
    __tablename__ = "PlatformOrderFee"

    PlatformOrderFeeId = Column(Integer, primary_key=True, autoincrement=True)
    PlatformOrderId = Column(Integer, ForeignKey("PlatformOrder.PlatformOrderId"), nullable=False)

    FeeType = Column(Unicode(200), nullable=False)
    FeeAmount = Column(Numeric(18, 2), nullable=True)
    FeeRate = Column(Numeric(18, 6), nullable=True)
    FeeBaseAmount = Column(Numeric(18, 2), nullable=True)

    RawSourceTable = Column(Unicode(200), nullable=True)
    RawSourceId = Column(Integer, nullable=True)

    isDeleted = Column(Boolean, nullable=False, default=False)
    createdBy = Column(Unicode(200), nullable=False)
    createdOn = Column(DateTime, nullable=False)
    modifiedBy = Column(Unicode(200), nullable=True)
    modifiedOn = Column(DateTime, nullable=True)

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
