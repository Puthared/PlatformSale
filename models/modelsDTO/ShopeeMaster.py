from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ShopeeMasterCreateDTO(BaseModel):
    OrderId: Optional[str] = None
    OrderStatus: Optional[str] = None
    HotListing: Optional[str] = None
    CancellationReason: Optional[str] = None
    ReturnRefundStatus: Optional[str] = None
    BuyerUsername: Optional[str] = None
    OrderCreatedAt: Optional[str] = None
    PaidAt: Optional[str] = None
    PaymentMethod: Optional[str] = None
    PaymentMethodDetail: Optional[str] = None
    InstallmentPlan: Optional[str] = None
    FeeRate: Optional[str] = None
    ShippingOption: Optional[str] = None
    ShippingMethod: Optional[str] = None
    TrackingNumber: Optional[str] = None
    EstimatedShipBy: Optional[str] = None
    ShippedAt: Optional[str] = None
    ParentSku: Optional[str] = None
    ProductName: Optional[str] = None
    SkuReference: Optional[str] = None
    VariationName: Optional[str] = None
    OriginalPrice: Optional[str] = None
    SalePrice: Optional[str] = None
    Quantity: Optional[str] = None
    ReturnedQuantity: Optional[str] = None
    NetSalePrice: Optional[str] = None
    ShopeeDiscount: Optional[str] = None
    SellerVoucherDiscount: Optional[str] = None
    SellerCoinsCashback: Optional[str] = None
    ShopeeVoucherDiscount: Optional[str] = None
    DiscountCodes: Optional[str] = None
    IsBundleDeal: Optional[str] = None
    SellerBundleDiscount: Optional[str] = None
    ShopeeBundleDiscount: Optional[str] = None
    CoinDiscount: Optional[str] = None
    PaymentChannelPromotionDiscount: Optional[str] = None
    TradeInDiscount: Optional[str] = None
    TradeInBonusDiscount: Optional[str] = None
    CommissionFee: Optional[str] = None
    TransactionFee: Optional[str] = None
    BuyerPaidProductAmountThb: Optional[str] = None
    BuyerPaidShippingFee: Optional[str] = None
    EstimatedShopeeShippingSubsidy: Optional[str] = None
    ReturnShippingFee: Optional[str] = None
    ServiceFee: Optional[str] = None
    TotalAmount: Optional[str] = None
    EstimatedShippingFee: Optional[str] = None
    SellerTradeInBonusDiscount: Optional[str] = None
    RecipientName: Optional[str] = None
    RecipientPhone: Optional[str] = None
    BuyerNote: Optional[str] = None
    ShippingAddress: Optional[str] = None
    ShippingCountry: Optional[str] = None
    ShippingProvince: Optional[str] = None
    ShippingDistrict: Optional[str] = None
    ShippingPostalCode: Optional[str] = None
    OrderType: Optional[str] = None
    CompletedAt: Optional[str] = None
    SellerNote: Optional[str] = None
    BuyerRequestedTaxInvoice: Optional[str] = None
    TaxInvoiceType: Optional[str] = None
    TaxInvoiceName: Optional[str] = None
    TaxBranchType: Optional[str] = None
    TaxBranchName: Optional[str] = None
    TaxBranchCode: Optional[str] = None
    TaxFullAddress: Optional[str] = None
    TaxAddressDetail: Optional[str] = None
    TaxSubdistrict: Optional[str] = None
    TaxDistrict: Optional[str] = None
    TaxProvince: Optional[str] = None
    TaxPostalCode: Optional[str] = None
    TaxId: Optional[str] = None
    TaxPhone: Optional[str] = None
    TaxEmail: Optional[str] = None
    ImportFileName: Optional[str] = None
    IsNormalized: Optional[bool] = None
    NormalizedOn: Optional[datetime] = None
    NormalizeError: Optional[str] = None

    createdBy: str


class ShopeeMasterUpdateDTO(ShopeeMasterCreateDTO):
    createdBy: Optional[str] = None
    modifiedBy: str


class ShopeeMasterNormalizeDTO(BaseModel):
    limit: int = 1000
    createdBy: str
    mode: str = "skip_existing"
