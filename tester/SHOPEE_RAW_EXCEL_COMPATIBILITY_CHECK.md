# Shopee Raw Excel Compatibility Check

## Purpose

Use this document to check whether a new Shopee raw Excel export is compatible with the current database mapping for `ShopeeMaster`.

When given this `.md` file and a new Shopee Excel file, the AI should:

1. Read the header row from the Shopee order worksheet.
2. Compare the new headers against the expected headers in this document.
3. Report missing columns.
4. Report extra/new columns.
5. Report suspicious renamed columns.
6. Say whether the file can be imported into `ShopeeMaster` safely.
7. Recommend mapping/model changes if needed.

This document is intentionally simple. The project owner can update the mapping manually when Shopee changes the export format.

## Current Reference File

Reference file:

```text
C:\Education\PlatformSale\tester\Shopee_Orders_Raw.xlsx
```

Reference worksheet:

```text
Shopee คำสั่งซื้อ
```

Expected row structure:

```text
Row 1 = header
Row 2 onward = data rows
```

Current expected shape:

```text
1501 rows
74 columns
```

The row count can change in future files. The column compatibility check should focus on the header row.

## Database Target

Target SQLAlchemy model:

```text
models/ShopeeMaster.py
```

Target database table:

```text
ShopeeMaster
```

Raw Excel values are currently stored as text fields in `ShopeeMaster` using `Unicode(...)`.

## Compatibility Rules

### Pass

A file is compatible if:

- It has a worksheet named `Shopee คำสั่งซื้อ`, or the user clearly identifies the Shopee order sheet.
- All required headers are present.
- Known optional headers may be present or blank.
- Extra headers are allowed only if they are reported clearly.

### Warning

Return a warning if:

- Extra columns exist that are not in the mapping.
- A header looks like a renamed version of an expected header.
- Duplicate header names appear.
- Expected optional columns are missing.

### Fail

Return fail if any required header is missing:

- `หมายเลขคำสั่งซื้อ`
- `สถานะการสั่งซื้อ`
- `ชื่อสินค้า`
- `เลขอ้างอิง SKU (SKU Reference No.)`
- `ราคาตั้งต้น`
- `ราคาขาย`
- `จำนวน`

These required headers are needed to identify orders and items.

## Expected Headers And Database Mapping

| # | Excel Header | ShopeeMaster Column | Required |
|---:|---|---|---|
| 1 | หมายเลขคำสั่งซื้อ | OrderId | Yes |
| 2 | สถานะการสั่งซื้อ | OrderStatus | Yes |
| 3 | Hot Listing | HotListing | No |
| 4 | เหตุผลในการยกเลิกคำสั่งซื้อ | CancellationReason | No |
| 5 | สถานะการคืนเงินหรือคืนสินค้า | ReturnRefundStatus | No |
| 6 | ชื่อผู้ใช้ (ผู้ซื้อ) | BuyerUsername | No |
| 7 | วันที่ทำการสั่งซื้อ | OrderCreatedAt | No |
| 8 | เวลาการชำระสินค้า | PaidAt | No |
| 9 | ช่องทางการชำระเงิน | PaymentMethod | No |
| 10 | ช่องทางการชำระเงิน (รายละเอียด) | PaymentMethodDetail | No |
| 11 | แผนการผ่อนชำระ | InstallmentPlan | No |
| 12 | ค่าธรรมเนียม (%) | FeeRate | No |
| 13 | ตัวเลือกการจัดส่ง | ShippingOption | No |
| 14 | วิธีการจัดส่ง | ShippingMethod | No |
| 15 | *หมายเลขติดตามพัสดุ | TrackingNumber | No |
| 16 | วันที่คาดว่าจะทำการจัดส่งสินค้า | EstimatedShipBy | No |
| 17 | เวลาส่งสินค้า | ShippedAt | No |
| 18 | เลขอ้างอิง Parent SKU | ParentSku | No |
| 19 | ชื่อสินค้า | ProductName | Yes |
| 20 | เลขอ้างอิง SKU (SKU Reference No.) | SkuReference | Yes |
| 21 | ชื่อตัวเลือก | VariationName | No |
| 22 | ราคาตั้งต้น | OriginalPrice | Yes |
| 23 | ราคาขาย | SalePrice | Yes |
| 24 | จำนวน | Quantity | Yes |
| 25 | จำนวนที่ส่งคืน | ReturnedQuantity | No |
| 26 | ราคาขายสุทธิ | NetSalePrice | No |
| 27 | ส่วนลดจาก Shopee | ShopeeDiscount | No |
| 28 | โค้ดส่วนลดชำระโดยผู้ขาย | SellerVoucherDiscount | No |
| 29 | โค้ด Coins Cashback ชำระโดยผู้ขาย | SellerCoinsCashback | No |
| 30 | โค้ดส่วนลดชำระโดย Shopee (เช่น โค้ดจากโปรแกรม ร้านโค้ดคุ้ม, โค้ดส่วนลด Shopee, โค้ดส่วนลด Shopee Mall) | ShopeeVoucherDiscount | No |
| 31 | โค้ดส่วนลด | DiscountCodes | No |
| 32 | เข้าร่วมแคมเปญ bundle deal หรือไม่ | IsBundleDeal | No |
| 33 | ส่วนลด bundle deal ชำระโดยผู้ขาย | SellerBundleDiscount | No |
| 34 | ส่วนลด bundle deal ชำระโดย Shopee | ShopeeBundleDiscount | No |
| 35 | ส่วนลดจากการใช้เหรียญ | CoinDiscount | No |
| 36 | โปรโมชั่นช่องทางชำระเงินทั้งหมด | PaymentChannelPromotionDiscount | No |
| 37 | ส่วนลดเครื่องเก่าแลกใหม่ | TradeInDiscount | No |
| 38 | โบนัสส่วนลดเครื่องเก่าแลกใหม่ | TradeInBonusDiscount | No |
| 39 | ค่าคอมมิชชั่น | CommissionFee | No |
| 40 | Transaction Fee | TransactionFee | No |
| 41 | ราคาสินค้าที่ชำระโดยผู้ซื้อ (THB) | BuyerPaidProductAmountThb | No |
| 42 | ค่าจัดส่งที่ชำระโดยผู้ซื้อ | BuyerPaidShippingFee | No |
| 43 | ค่าจัดส่งที่ Shopee ออกให้โดยประมาณ | EstimatedShopeeShippingSubsidy | No |
| 44 | ค่าจัดส่งสินค้าคืน | ReturnShippingFee | No |
| 45 | ค่าบริการ | ServiceFee | No |
| 46 | จำนวนเงินทั้งหมด | TotalAmount | No |
| 47 | ค่าจัดส่งโดยประมาณ | EstimatedShippingFee | No |
| 48 | โบนัสส่วนลดเครื่องเก่าแลกใหม่จากผู้ขาย | SellerTradeInBonusDiscount | No |
| 49 | ชื่อผู้รับ | RecipientName | No |
| 50 | หมายเลขโทรศัพท์ | RecipientPhone | No |
| 51 | หมายเหตุจากผู้ซื้อ | BuyerNote | No |
| 52 | ที่อยู่ในการจัดส่ง | ShippingAddress | No |
| 53 | ประเทศ | ShippingCountry | No |
| 54 | จังหวัด | ShippingProvince | No |
| 55 | เขต/อำเภอ | ShippingDistrict | No |
| 56 | รหัสไปรษณีย์ | ShippingPostalCode | No |
| 57 | ประเภทคำสั่งซื้อ | OrderType | No |
| 58 | เวลาที่ทำการสั่งซื้อสำเร็จ | CompletedAt | No |
| 59 | บันทึก | SellerNote | No |
| 60 | ผู้ซื้อร้องขอใบกำกับภาษี | BuyerRequestedTaxInvoice | No |
| 61 | ประเภทใบกำกับภาษี | TaxInvoiceType | No |
| 62 | ชื่อ | TaxInvoiceName | No |
| 63 | ประเภทสาขา | TaxBranchType | No |
| 64 | ชื่อสาขา | TaxBranchName | No |
| 65 | รหัสประจำสาขา | TaxBranchCode | No |
| 66 | ที่อยู่สำหรับออกใบกำกับภาษีแบบเต็มรูป | TaxFullAddress | No |
| 67 | รายละเอียดที่อยู่ | TaxAddressDetail | No |
| 68 | แขวง/ตำบล | TaxSubdistrict | No |
| 69 | เขต/อำเภอ | TaxDistrict | No |
| 70 | จังหวัด | TaxProvince | No |
| 71 | รหัสไปรษณีย์ | TaxPostalCode | No |
| 72 | หมายเลขประจำตัวผู้เสียภาษี | TaxId | No |
| 73 | หมายเลขโทรศัพท์สำหรับออกใบกำกับภาษี | TaxPhone | No |
| 74 | อีเมลสำหรับรับใบกำกับภาษี | TaxEmail | No |

## Duplicate Header Note

The raw Excel file contains duplicate Thai header names:

- `เขต/อำเภอ`
- `จังหวัด`
- `รหัสไปรษณีย์`

These appear once for shipping information and once for tax invoice information.

The mapping depends on column position:

| Excel Position | Header | Meaning | Database Column |
|---:|---|---|---|
| 54 | จังหวัด | Shipping province | ShippingProvince |
| 55 | เขต/อำเภอ | Shipping district | ShippingDistrict |
| 56 | รหัสไปรษณีย์ | Shipping postal code | ShippingPostalCode |
| 69 | เขต/อำเภอ | Tax district | TaxDistrict |
| 70 | จังหวัด | Tax province | TaxProvince |
| 71 | รหัสไปรษณีย์ | Tax postal code | TaxPostalCode |

If future files reorder these duplicate columns, the AI must warn the user.

## AI Check Instructions

When checking a future Shopee Excel file:

1. Open the workbook.
2. Find worksheet `Shopee คำสั่งซื้อ`.
3. Read row 1 as headers.
4. Normalize header text by trimming leading/trailing whitespace only.
5. Compare headers against the mapping table above.
6. Check required headers.
7. Check duplicate headers by position.
8. Report all differences.

## Expected AI Output Format

Use this response format:

```text
Compatibility: PASS / WARNING / FAIL

Summary:
- Expected headers: 74
- Actual headers: <number>
- Required missing: <number>
- Extra headers: <number>
- Suspected renamed headers: <number>

Missing Required Headers:
- ...

Missing Optional Headers:
- ...

Extra Headers:
- ...

Suspected Renamed Headers:
- old -> new, reason

Duplicate Header Position Check:
- OK / Warning details

Recommended Changes:
- update mapping
- add column to ShopeeMaster
- no change needed
```

## Import Recommendation

If compatibility is `PASS`, the file can be imported using the current mapping.

If compatibility is `WARNING`, the file may be imported only if:

- required headers are present
- duplicate header positions still match
- extra columns are intentionally ignored or handled

If compatibility is `FAIL`, do not import until the mapping/model is updated.
