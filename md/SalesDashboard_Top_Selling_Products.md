# Sales Dashboard - Top Selling Products

## Purpose

Top Selling Products คือข้อ 5 ของ Sales Dashboard ToDoList

เป้าหมายคือดูว่าสินค้า SKU ไหนขายดีที่สุด โดยทำเป็นหน้าใหม่แยกจาก Dashboard หลัก

รายงานนี้ต้องช่วยตอบคำถามเช่น:

```text
SKU ไหนขายได้จำนวนชิ้นมากที่สุด
SKU ไหนทำยอดขายมากที่สุด
SKU ไหนมีจำนวน order มากที่สุด
```

## Important Decision

รายงานนี้จะจับสินค้าโดยใช้ SKU ตาม platform เพราะ Shopee และ TikTok เก็บ SKU ที่ใช้จริงไว้คนละ field หลัง normalize

```text
Shopee SKU key = PlatformOrderItem.PlatformSku
TikTok SKU key = PlatformOrderItem.SellerSku
```

หมายเหตุ: ในข้อมูล Shopee ปัจจุบัน `SkuReference` ถูก normalize มาอยู่ที่ `PlatformOrderItem.PlatformSku`

TikTok ใช้ `PlatformOrderItem.SellerSku`

ไม่ใช้ `ProductName` เป็น key

เหตุผลคือสินค้า SKU เดียวกันอาจมีหลายชื่อสินค้าได้ ถ้า group ด้วย `ProductName` จะทำให้สินค้าเดียวกันแตกเป็นหลายกลุ่ม

## Item SalesValue Rule

ยอดขายระดับ item ให้ใช้ field นี้:

```text
PlatformOrderItem.NetSalePrice
```

ถ้า `NetSalePrice` เป็น `NULL` ให้คิดเป็น `0`

ไม่ fallback ไปใช้ `SalePrice * Quantity`

สูตร:

```text
salesValue = SUM(COALESCE(PlatformOrderItem.NetSalePrice, 0))
```

## Backend API Plan

เพิ่ม endpoint ใหม่:

```text
POST /SalesDashboard/GetTopSellingProducts
```

Request ตัวอย่าง:

```json
{
  "year": 2026,
  "month": null,
  "platformIds": [],
  "sortBy": "quantity",
  "limit": 20
}
```

## Request Fields

```text
year
month
platformIds
sortBy
limit
```

`year`

ปีที่ต้องการดูข้อมูล

`month`

ถ้าเป็น `null` ให้ query ทั้งปี

ถ้ามีค่า 1-12 ให้ query เฉพาะเดือนนั้น

`platformIds`

ถ้าเป็น array ว่าง ให้รวมทุก platform

ถ้ามีค่า เช่น `[1]` ให้ดูเฉพาะ Shopee

`sortBy`

รองรับ:

```text
quantity
salesValue
orderCount
```

ค่า default:

```text
quantity
```

`limit`

จำนวนอันดับที่ต้องการแสดง

ค่า default:

```text
20
```

## Response Example

```json
{
  "year": 2026,
  "month": null,
  "sortBy": "quantity",
  "limit": 20,
  "items": [
    {
      "rank": 1,
      "sku": "123456789",
      "displayProductName": "Product name sample",
      "variationName": "Black / XL",
      "totalQuantity": 500,
      "salesValue": 250000,
      "orderCount": 180,
      "platformCount": 2,
      "productNameSamples": [
        "Product name sample",
        "Product name alternate"
      ]
    }
  ],
  "totals": {
    "productCount": 300,
    "quantity": 10000,
    "salesValue": 5000000,
    "orderCount": 8000
  }
}
```

## Backend Calculation

ใช้ table:

```text
PlatformOrder
PlatformOrderItem
```

Join:

```text
PlatformOrder.PlatformOrderId = PlatformOrderItem.PlatformOrderId
```

Filter หลัก:

```text
PlatformOrder.isDeleted = False
PlatformOrderItem.isDeleted = False
PlatformOrder.IsCancelled = False
PlatformOrder.IsReturned = False
PlatformOrder.OrderCreatedAt อยู่ในปี/เดือนที่เลือก
SKU key ตาม platform ไม่ว่าง
```

Group:

```text
GROUP BY SKU key ตาม platform

Logic:

```text
CASE
  WHEN PlatformOrder.PlatformId = 1 THEN PlatformOrderItem.PlatformSku
  ELSE PlatformOrderItem.SellerSku
END
```
```

Metrics:

```text
totalQuantity = SUM(COALESCE(PlatformOrderItem.Quantity, 0))
salesValue = SUM(COALESCE(PlatformOrderItem.NetSalePrice, 0))
orderCount = COUNT(DISTINCT PlatformOrder.PlatformOrderId)
platformCount = COUNT(DISTINCT PlatformOrder.PlatformId)
```

## ProductName Handling

ไม่ใช้ `ProductName` เป็น key

แต่ควรส่งชื่อสินค้าไว้เพื่อช่วยให้มนุษย์อ่านง่าย

แนวทางแรก:

```text
displayProductName = MIN(ProductName) หรือชื่อแรกที่ query เจอ
variationName = MIN(VariationName) หรือชื่อแรกที่ query เจอ
```

ภายหลังถ้าต้องการแม่นขึ้น สามารถทำ logic หา product name ที่เจอบ่อยที่สุดได้

ควรมี `productNameSamples` เพื่อช่วยตรวจสอบกรณี SKU เดียวมีหลายชื่อ

## Backend Files

ไฟล์ที่จะเกี่ยวข้อง:

```text
models/modelsDTO/SalesDashboard.py
services/SalesDashboardService.py
routes/SalesDashboard.py
```

เพิ่ม DTO:

```text
TopSellingProductsFilterDTO
```

เพิ่ม service function:

```text
get_top_selling_products()
```

เพิ่ม route:

```text
GetTopSellingProducts()
```

## FrontEnd Plan

ทำเป็นหน้าใหม่:

```text
src/routes/top-selling-products.tsx
```

เพิ่มเมนูใน Sidebar:

```text
Top Selling Products
```

## FrontEnd Filter

หน้า Top Selling Products จะมี filter ของตัวเอง:

```text
Year
Month
Platform
Sort By
Limit
Search
```

Default:

```text
Year = ปีปัจจุบัน
Month = All months
Platform = All platforms
Sort By = Quantity
Limit = 20
```

## FrontEnd Display

เริ่มจากตารางก่อน

Columns:

```text
Rank
SKU
ProductName
Variation
TotalQuantity
SalesValue
OrderCount
PlatformCount
```

Summary cards:

```text
Total Products
Total Quantity
Total SalesValue
Total Orders
```

## Future Improvement

สิ่งที่อาจเพิ่มภายหลัง:

```text
Top 10 bar chart
Switch between Top by Quantity and Top by SalesValue
Product detail modal
Show product name variations under same SKU
Filter by platform
Export Excel
```

## Completion Criteria

ถือว่าข้อ 5 เสร็จเมื่อ:

1. มี API `POST /SalesDashboard/GetTopSellingProducts`
2. API group ด้วย SKU key ตาม platform: Shopee ใช้ `PlatformSku`, TikTok ใช้ `SellerSku`
3. API ใช้ `NetSalePrice` และ `NULL = 0`
4. API exclude cancelled / returned orders
5. มีหน้าใหม่ `Top Selling Products`
6. หน้าใหม่มี filter ปี/เดือน/sort/limit
7. หน้าใหม่แสดง summary cards และ table
8. `py_compile` ผ่าน
9. `npm run build` ผ่าน
10. Mark ToDoList ข้อ 5 เป็น Done
