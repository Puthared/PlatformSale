from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TiktokMasterCreateDTO(BaseModel):
    OrderId: Optional[str] = None
    OrderStatus: Optional[str] = None
    OrderSubstatus: Optional[str] = None
    CancelationReturnType: Optional[str] = None
    NormalOrPreOrder: Optional[str] = None
    SkuId: Optional[str] = None
    SellerSku: Optional[str] = None
    ProductName: Optional[str] = None
    Variation: Optional[str] = None
    Quantity: Optional[str] = None
    SkuQuantityOfReturn: Optional[str] = None
    SkuUnitOriginalPrice: Optional[str] = None
    SkuSubtotalBeforeDiscount: Optional[str] = None
    SkuPlatformDiscount: Optional[str] = None
    SkuSellerDiscount: Optional[str] = None
    SkuSubtotalAfterDiscount: Optional[str] = None
    ShippingFeeAfterDiscount: Optional[str] = None
    OriginalShippingFee: Optional[str] = None
    ShippingFeeSellerDiscount: Optional[str] = None
    ShippingFeePlatformDiscount: Optional[str] = None
    PaymentPlatformDiscount: Optional[str] = None
    Taxes: Optional[str] = None
    OrderAmount: Optional[str] = None
    OrderRefundAmount: Optional[str] = None
    CreatedTime: Optional[str] = None
    PaidTime: Optional[str] = None
    RtsTime: Optional[str] = None
    ShippedTime: Optional[str] = None
    DeliveredTime: Optional[str] = None
    CancelledTime: Optional[str] = None
    CancelBy: Optional[str] = None
    CancelReason: Optional[str] = None
    FulfillmentType: Optional[str] = None
    WarehouseName: Optional[str] = None
    TrackingId: Optional[str] = None
    DeliveryOption: Optional[str] = None
    ShippingProviderName: Optional[str] = None
    BuyerMessage: Optional[str] = None
    BuyerUsername: Optional[str] = None
    Recipient: Optional[str] = None
    Phone: Optional[str] = None
    Zipcode: Optional[str] = None
    Country: Optional[str] = None
    Province: Optional[str] = None
    District: Optional[str] = None
    Districts: Optional[str] = None
    DetailAddress: Optional[str] = None
    AdditionalAddressInformation: Optional[str] = None
    PaymentMethod: Optional[str] = None
    WeightKg: Optional[str] = None
    ProductCategory: Optional[str] = None
    PackageId: Optional[str] = None
    SellerNote: Optional[str] = None
    CheckedStatus: Optional[str] = None
    CheckedMarkedBy: Optional[str] = None
    RequestTaxInvoice: Optional[str] = None
    TaxInfoBuyerTaxId: Optional[str] = None
    TaxInfoType: Optional[str] = None
    TaxInfoFullNameOfBuyer: Optional[str] = None
    TaxInfoEmail: Optional[str] = None
    TaxInfoPhoneNumber: Optional[str] = None
    TaxInfoRegisteredAddress: Optional[str] = None
    TaxInfoAddressType: Optional[str] = None
    ImportFileName: Optional[str] = None
    IsNormalized: Optional[bool] = None
    NormalizedOn: Optional[datetime] = None
    NormalizeError: Optional[str] = None

    createdBy: str


class TiktokMasterUpdateDTO(TiktokMasterCreateDTO):
    createdBy: Optional[str] = None
    modifiedBy: str


class TiktokMasterNormalizeDTO(BaseModel):
    limit: int = 1000
    createdBy: str
    mode: str = "skip_existing"
