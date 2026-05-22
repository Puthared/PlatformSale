from sqlalchemy import Boolean, Column, DateTime, Integer, Unicode, text

from config import database as db


class ShopeeMaster(db.Base):
    __tablename__ = "ShopeeMaster"

    ShopeeMasterId = Column(Integer, primary_key=True, autoincrement=True)

    # หมายเลขคำสั่งซื้อ
    OrderId = Column(Unicode(200), nullable=True)
    # สถานะการสั่งซื้อ
    OrderStatus = Column(Unicode(500), nullable=True)
    # Hot Listing
    HotListing = Column(Unicode(50), nullable=True)
    # เหตุผลในการยกเลิกคำสั่งซื้อ
    CancellationReason = Column(Unicode(1000), nullable=True)
    # สถานะการคืนเงินหรือคืนสินค้า
    ReturnRefundStatus = Column(Unicode(500), nullable=True)
    # ชื่อผู้ใช้ (ผู้ซื้อ)
    BuyerUsername = Column(Unicode(300), nullable=True)
    # วันที่ทำการสั่งซื้อ
    OrderCreatedAt = Column(Unicode(100), nullable=True)
    # เวลาการชำระสินค้า
    PaidAt = Column(Unicode(100), nullable=True)
    # ช่องทางการชำระเงิน
    PaymentMethod = Column(Unicode(300), nullable=True)
    # ช่องทางการชำระเงิน (รายละเอียด)
    PaymentMethodDetail = Column(Unicode(300), nullable=True)
    # แผนการผ่อนชำระ
    InstallmentPlan = Column(Unicode(300), nullable=True)
    # ค่าธรรมเนียม (%)
    FeeRate = Column(Unicode(100), nullable=True)
    # ตัวเลือกการจัดส่ง
    ShippingOption = Column(Unicode(500), nullable=True)
    # วิธีการจัดส่ง
    ShippingMethod = Column(Unicode(200), nullable=True)
    # *หมายเลขติดตามพัสดุ
    TrackingNumber = Column(Unicode(300), nullable=True)
    # วันที่คาดว่าจะทำการจัดส่งสินค้า
    EstimatedShipBy = Column(Unicode(100), nullable=True)
    # เวลาส่งสินค้า
    ShippedAt = Column(Unicode(100), nullable=True)
    # เลขอ้างอิง Parent SKU
    ParentSku = Column(Unicode(300), nullable=True)
    # ชื่อสินค้า
    ProductName = Column(Unicode(1000), nullable=True)
    # เลขอ้างอิง SKU (SKU Reference No.)
    SkuReference = Column(Unicode(300), nullable=True)
    # ชื่อตัวเลือก
    VariationName = Column(Unicode(500), nullable=True)
    # ราคาตั้งต้น
    OriginalPrice = Column(Unicode(100), nullable=True)
    # ราคาขาย
    SalePrice = Column(Unicode(100), nullable=True)
    # จำนวน
    Quantity = Column(Unicode(100), nullable=True)
    # จำนวนที่ส่งคืน
    ReturnedQuantity = Column(Unicode(100), nullable=True)
    # ราคาขายสุทธิ
    NetSalePrice = Column(Unicode(100), nullable=True)
    # ส่วนลดจาก Shopee
    ShopeeDiscount = Column(Unicode(100), nullable=True)
    # โค้ดส่วนลดชำระโดยผู้ขาย
    SellerVoucherDiscount = Column(Unicode(100), nullable=True)
    # โค้ด Coins Cashback ชำระโดยผู้ขาย
    SellerCoinsCashback = Column(Unicode(100), nullable=True)
    # โค้ดส่วนลดชำระโดย Shopee
    ShopeeVoucherDiscount = Column(Unicode(100), nullable=True)
    # โค้ดส่วนลด
    DiscountCodes = Column(Unicode(1000), nullable=True)
    # เข้าร่วมแคมเปญ bundle deal หรือไม่
    IsBundleDeal = Column(Unicode(50), nullable=True)
    # ส่วนลด bundle deal ชำระโดยผู้ขาย
    SellerBundleDiscount = Column(Unicode(100), nullable=True)
    # ส่วนลด bundle deal ชำระโดย Shopee
    ShopeeBundleDiscount = Column(Unicode(100), nullable=True)
    # ส่วนลดจากการใช้เหรียญ
    CoinDiscount = Column(Unicode(100), nullable=True)
    # โปรโมชั่นช่องทางชำระเงินทั้งหมด
    PaymentChannelPromotionDiscount = Column(Unicode(100), nullable=True)
    # ส่วนลดเครื่องเก่าแลกใหม่
    TradeInDiscount = Column(Unicode(100), nullable=True)
    # โบนัสส่วนลดเครื่องเก่าแลกใหม่
    TradeInBonusDiscount = Column(Unicode(100), nullable=True)
    # ค่าคอมมิชชั่น
    CommissionFee = Column(Unicode(100), nullable=True)
    # Transaction Fee
    TransactionFee = Column(Unicode(100), nullable=True)
    # ราคาสินค้าที่ชำระโดยผู้ซื้อ (THB)
    BuyerPaidProductAmountThb = Column(Unicode(100), nullable=True)
    # ค่าจัดส่งที่ชำระโดยผู้ซื้อ
    BuyerPaidShippingFee = Column(Unicode(100), nullable=True)
    # ค่าจัดส่งที่ Shopee ออกให้โดยประมาณ
    EstimatedShopeeShippingSubsidy = Column(Unicode(100), nullable=True)
    # ค่าจัดส่งสินค้าคืน
    ReturnShippingFee = Column(Unicode(100), nullable=True)
    # ค่าบริการ
    ServiceFee = Column(Unicode(100), nullable=True)
    # จำนวนเงินทั้งหมด
    TotalAmount = Column(Unicode(100), nullable=True)
    # ค่าจัดส่งโดยประมาณ
    EstimatedShippingFee = Column(Unicode(100), nullable=True)
    # โบนัสส่วนลดเครื่องเก่าแลกใหม่จากผู้ขาย
    SellerTradeInBonusDiscount = Column(Unicode(100), nullable=True)
    # ชื่อผู้รับ
    RecipientName = Column(Unicode(300), nullable=True)
    # หมายเลขโทรศัพท์
    RecipientPhone = Column(Unicode(200), nullable=True)
    # หมายเหตุจากผู้ซื้อ
    BuyerNote = Column(Unicode(2000), nullable=True)
    # ที่อยู่ในการจัดส่ง
    ShippingAddress = Column(Unicode(2000), nullable=True)
    # ประเทศ
    ShippingCountry = Column(Unicode(100), nullable=True)
    # จังหวัด
    ShippingProvince = Column(Unicode(300), nullable=True)
    # เขต/อำเภอ
    ShippingDistrict = Column(Unicode(300), nullable=True)
    # รหัสไปรษณีย์
    ShippingPostalCode = Column(Unicode(100), nullable=True)
    # ประเภทคำสั่งซื้อ
    OrderType = Column(Unicode(300), nullable=True)
    # เวลาที่ทำการสั่งซื้อสำเร็จ
    CompletedAt = Column(Unicode(100), nullable=True)
    # บันทึก
    SellerNote = Column(Unicode(2000), nullable=True)
    # ผู้ซื้อร้องขอใบกำกับภาษี
    BuyerRequestedTaxInvoice = Column(Unicode(100), nullable=True)
    # ประเภทใบกำกับภาษี
    TaxInvoiceType = Column(Unicode(200), nullable=True)
    # ชื่อ
    TaxInvoiceName = Column(Unicode(500), nullable=True)
    # ประเภทสาขา
    TaxBranchType = Column(Unicode(200), nullable=True)
    # ชื่อสาขา
    TaxBranchName = Column(Unicode(500), nullable=True)
    # รหัสประจำสาขา
    TaxBranchCode = Column(Unicode(200), nullable=True)
    # ที่อยู่สำหรับออกใบกำกับภาษีแบบเต็มรูป
    TaxFullAddress = Column(Unicode(2000), nullable=True)
    # รายละเอียดที่อยู่
    TaxAddressDetail = Column(Unicode(2000), nullable=True)
    # แขวง/ตำบล
    TaxSubdistrict = Column(Unicode(300), nullable=True)
    # เขต/อำเภอ
    TaxDistrict = Column(Unicode(300), nullable=True)
    # จังหวัด
    TaxProvince = Column(Unicode(300), nullable=True)
    # รหัสไปรษณีย์
    TaxPostalCode = Column(Unicode(100), nullable=True)
    # หมายเลขประจำตัวผู้เสียภาษี
    TaxId = Column(Unicode(200), nullable=True)
    # หมายเลขโทรศัพท์สำหรับออกใบกำกับภาษี
    TaxPhone = Column(Unicode(200), nullable=True)
    # อีเมลสำหรับรับใบกำกับภาษี
    TaxEmail = Column(Unicode(300), nullable=True)

    ImportFileName = Column(Unicode(500), nullable=True)
    IsNormalized = Column(Boolean, nullable=False, default=False, server_default=text("0"))
    NormalizedOn = Column(DateTime, nullable=True)
    NormalizeError = Column(Unicode(2000), nullable=True)

    isDeleted = Column(Boolean, nullable=False, default=False)
    createdBy = Column(Unicode(200), nullable=False)
    createdOn = Column(DateTime, nullable=False)
    modifiedBy = Column(Unicode(200), nullable=True)
    modifiedOn = Column(DateTime, nullable=True)

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
