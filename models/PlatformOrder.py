from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, Unicode

from config import database as db


class PlatformOrder(db.Base):
    __tablename__ = "PlatformOrder"

    PlatformOrderId = Column(Integer, primary_key=True, autoincrement=True)
    PlatformId = Column(Integer, ForeignKey("Platform.PlatformId"), nullable=False)

    PlatformOrderNo = Column(Unicode(200), nullable=False)
    OrderStatus = Column(Unicode(500), nullable=True)
    OrderCreatedAt = Column(DateTime, nullable=True)
    PaidAt = Column(DateTime, nullable=True)
    CompletedAt = Column(DateTime, nullable=True)
    BuyerUsername = Column(Unicode(300), nullable=True)

    BuyerPaidProductAmount = Column(Numeric(18, 2), nullable=True)
    BuyerPaidShippingFee = Column(Numeric(18, 2), nullable=True)
    TotalAmount = Column(Numeric(18, 2), nullable=True)

    IsCancelled = Column(Boolean, nullable=False, default=False)
    IsReturned = Column(Boolean, nullable=False, default=False)

    RawSourceTable = Column(Unicode(200), nullable=True)
    RawSourceId = Column(Integer, nullable=True)

    isDeleted = Column(Boolean, nullable=False, default=False)
    createdBy = Column(Unicode(200), nullable=False)
    createdOn = Column(DateTime, nullable=False)
    modifiedBy = Column(Unicode(200), nullable=True)
    modifiedOn = Column(DateTime, nullable=True)

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
