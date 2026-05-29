# Sales Dashboard KPI Summary

## Purpose

KPI Summary คือส่วนบนสุดของ Sales Dashboard ที่ใช้ตอบคำถามเร็ว ๆ ว่า "ตอนนี้ธุรกิจขายเป็นยังไง"

เป้าหมายคือให้ดูตัวเลขสำคัญได้ทันที โดยยังไม่ต้องเข้าไปดูตารางละเอียด เช่น:

- ขายได้กี่บาท
- มีกี่ order
- ขายได้กี่ชิ้น
- เฉลี่ย order ละเท่าไร
- เสียไปกับ cancel/return แค่ไหน
- Shopee กับ TikTok ใครทำเงินมากกว่า

## Main Data Source

Dashboard ควรใช้ข้อมูล normalized table เป็นหลัก:

- `PlatformOrder` = ข้อมูลระดับ order header
- `PlatformOrderItem` = ข้อมูลสินค้า/variation ใน order
- `PlatformOrderFee` = fee, discount, refund, tax

ไม่ควรใช้ raw table เช่น `ShopeeMaster` หรือ `TiktokMaster` เป็นแหล่งหลักของ dashboard เพราะ raw data มี format ต่างกันตาม platform

## KPI Cards

### 1. Total SalesValue

ยอดขายสุทธิที่ใช้เป็นตัวเลขหลักของ Dashboard

Formula:

```text
SUM(PlatformOrder.SalesValue)
```

Filter ที่ควรใช้:

```text
PlatformOrder.isDeleted = 0
PlatformOrder.IsCancelled = 0
PlatformOrder.IsReturned = 0
```

ความหมาย:

```text
ยอดขายที่นับเป็นรายได้หลังปรับตามสูตรของแต่ละ platform
```

ตัวนี้ควรเป็น KPI card ตัวใหญ่สุดในหน้า Dashboard

### 2. Total Orders

จำนวนคำสั่งซื้อทั้งหมดที่นับเป็นยอดขาย

Formula:

```text
COUNT(PlatformOrder.PlatformOrderId)
```

Filter ที่ควรใช้:

```text
PlatformOrder.isDeleted = 0
PlatformOrder.IsCancelled = 0
PlatformOrder.IsReturned = 0
```

ความหมาย:

```text
จำนวน order ที่ขายสำเร็จและนับเป็นยอดขายได้
```

### 3. Total Quantity Sold

จำนวนชิ้นสินค้าที่ขายได้รวม

Formula:

```text
SUM(PlatformOrderItem.Quantity)
```

Join:

```text
PlatformOrder.PlatformOrderId = PlatformOrderItem.PlatformOrderId
```

Filter ที่ควรใช้:

```text
PlatformOrder.isDeleted = 0
PlatformOrder.IsCancelled = 0
PlatformOrder.IsReturned = 0
PlatformOrderItem.isDeleted = 0
```

ความหมาย:

```text
ขายสินค้าออกไปทั้งหมดกี่ชิ้น
```

### 4. Average Order Value (AOV)

ยอดขายเฉลี่ยต่อ order

Formula:

```text
SUM(PlatformOrder.SalesValue) / COUNT(PlatformOrder.PlatformOrderId)
```

หรือ:

```text
AVG(PlatformOrder.SalesValue)
```

เมื่อ 1 row ใน `PlatformOrder` เท่ากับ 1 order

ความหมาย:

```text
โดยเฉลี่ย 1 order ลูกค้าจ่ายให้เราประมาณเท่าไร
```

ตัวอย่าง:

```text
Total SalesValue = 1,000,000
Total Orders = 500
AOV = 2,000 บาท/order
```

### 5. Cancelled Orders

จำนวน order ที่ถูกยกเลิก

Formula:

```text
COUNT(PlatformOrder.PlatformOrderId)
WHERE PlatformOrder.IsCancelled = 1
```

ควรแสดง 2 ค่า:

```text
Cancelled Orders
Cancelled Rate
```

Cancelled Rate:

```text
Cancelled Orders / Gross Orders
```

ความหมาย:

```text
มี order ที่เสียไปเพราะยกเลิกกี่รายการ
```

### 6. Returned Orders

จำนวน order ที่มีการคืนสินค้า/คืนเงิน

Formula:

```text
COUNT(PlatformOrder.PlatformOrderId)
WHERE PlatformOrder.IsReturned = 1
```

ควรแสดง 2 ค่า:

```text
Returned Orders
Returned Rate
```

Returned Rate:

```text
Returned Orders / Gross Orders
```

ความหมาย:

```text
มี order ที่มีปัญหาหลังซื้อกี่รายการ
```

### 7. Gross Orders / Valid Orders

ควรมีตัวเลขนี้เพื่อช่วยอธิบาย KPI ให้ไม่สับสน

```text
Gross Orders = order ทั้งหมดที่ไม่ถูก delete
Valid Orders = order ที่ไม่ Cancelled และไม่ Returned
```

ตัวอย่าง:

```text
Gross Orders = 20,000
Cancelled Orders = 2,000
Returned Orders = 100
Valid Orders = 17,900
```

### 8. Platform Split

KPI Summary ควรมี mini breakdown เพื่อดูว่า platform ไหนนำอยู่

ตัวอย่าง:

```text
Shopee SalesValue
TikTok SalesValue
Shopee Orders
TikTok Orders
```

อาจแสดงเป็น small chart หรือ mini table

## Recommended Layout

แถวแรก:

```text
Total SalesValue | Total Orders | Total Quantity | AOV
```

แถวสอง:

```text
Cancelled Orders | Cancelled Rate | Returned Orders | Returned Rate
```

ด้านล่างหรือด้านข้าง:

```text
Shopee vs TikTok Sales Share
```

## SQL Concepts

### KPI From PlatformOrder

```sql
SELECT
    SUM([SalesValue]) AS [TotalSalesValue],
    COUNT(1) AS [TotalOrders],
    AVG([SalesValue]) AS [AverageOrderValue]
FROM [PlatformSales].[dbo].[PlatformOrder]
WHERE [isDeleted] = 0
  AND [IsCancelled] = 0
  AND [IsReturned] = 0;
```

### Total Quantity Sold

```sql
SELECT
    SUM(ISNULL(poi.[Quantity], 0)) AS [TotalQuantitySold]
FROM [PlatformSales].[dbo].[PlatformOrder] po
INNER JOIN [PlatformSales].[dbo].[PlatformOrderItem] poi
    ON poi.[PlatformOrderId] = po.[PlatformOrderId]
WHERE po.[isDeleted] = 0
  AND po.[IsCancelled] = 0
  AND po.[IsReturned] = 0
  AND poi.[isDeleted] = 0;
```

### Cancel / Return Summary

```sql
SELECT
    COUNT(1) AS [GrossOrders],
    SUM(CASE WHEN [IsCancelled] = 1 THEN 1 ELSE 0 END) AS [CancelledOrders],
    SUM(CASE WHEN [IsReturned] = 1 THEN 1 ELSE 0 END) AS [ReturnedOrders],
    SUM(CASE WHEN [IsCancelled] = 0 AND [IsReturned] = 0 THEN 1 ELSE 0 END) AS [ValidOrders]
FROM [PlatformSales].[dbo].[PlatformOrder]
WHERE [isDeleted] = 0;
```

### Platform Split

```sql
SELECT
    p.[PlatformName],
    COUNT(1) AS [OrderCount],
    SUM(po.[SalesValue]) AS [SalesValue]
FROM [PlatformSales].[dbo].[PlatformOrder] po
INNER JOIN [PlatformSales].[dbo].[Platform] p
    ON p.[PlatformId] = po.[PlatformId]
WHERE po.[isDeleted] = 0
  AND po.[IsCancelled] = 0
  AND po.[IsReturned] = 0
GROUP BY
    p.[PlatformName]
ORDER BY
    [SalesValue] DESC;
```

## Important Warning

อย่า join `PlatformOrderItem` แล้วนับ order ตรง ๆ เพราะ order ที่มีหลาย item จะถูกคูณแถว

ผิด:

```sql
COUNT(po.[PlatformOrderId])
```

เมื่อ join กับ `PlatformOrderItem`

ถูก:

```sql
COUNT(DISTINCT po.[PlatformOrderId])
```

หรือแยก query order-level และ item-level ออกจากกัน

## Metric Standard

มาตรฐานของ Dashboard:

```text
ยอดขาย = PlatformOrder.SalesValue
จำนวน order = COUNT(PlatformOrder.PlatformOrderId)
จำนวนชิ้น = SUM(PlatformOrderItem.Quantity)
สินค้าขายดี = SUM(PlatformOrderItem.Quantity)
AOV = SUM(SalesValue) / COUNT(Order)
```

## V1 Recommendation

KPI Summary V1 ควรมี:

- Total SalesValue
- Total Orders
- Total Quantity Sold
- Average Order Value
- Cancelled Orders
- Cancelled Rate
- Returned Orders
- Returned Rate
- Platform Split แบบย่อ

