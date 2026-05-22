from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, Unicode

from config import database as db


class PlatformOrderItem(db.Base):
    __tablename__ = "PlatformOrderItem"

    PlatformOrderItemId = Column(Integer, primary_key=True, autoincrement=True)
    PlatformOrderId = Column(Integer, ForeignKey("PlatformOrder.PlatformOrderId"), nullable=False)
    
    PlatformSku = Column(Unicode(300), nullable=True)
    SellerSku = Column(Unicode(300), nullable=True)
    ProductName = Column(Unicode(1000), nullable=True)
    VariationName = Column(Unicode(500), nullable=True)

    OriginalPrice = Column(Numeric(18, 2), nullable=True)
    SalePrice = Column(Numeric(18, 2), nullable=True)
    Quantity = Column(Integer, nullable=True)
    ReturnedQuantity = Column(Integer, nullable=True)
    NetSalePrice = Column(Numeric(18, 2), nullable=True)

    RawSourceTable = Column(Unicode(200), nullable=True)
    RawSourceId = Column(Integer, nullable=True)

    isDeleted = Column(Boolean, nullable=False, default=False)
    createdBy = Column(Unicode(200), nullable=False)
    createdOn = Column(DateTime, nullable=False)
    modifiedBy = Column(Unicode(200), nullable=True)
    modifiedOn = Column(DateTime, nullable=True)

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
