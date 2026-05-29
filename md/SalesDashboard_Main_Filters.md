# Sales Dashboard Main Filters

## Purpose

Main Filters คือระบบกรองกลางของ Sales Dashboard

จุดประสงค์คือเมื่อ user เลือกเงื่อนไข เช่น วันที่, platform, status, SKU หรือจังหวัด ตัวเลขและกราฟทุกส่วนใน Dashboard ควรเปลี่ยนตาม filter เดียวกัน

ใน Dashboard ของเรา filter กลางควรใช้กับข้อมูล normalized table เป็นหลัก:

- `PlatformOrder`
- `PlatformOrderItem`
- `Platform`

ไม่ควรอิง raw table เป็นหลัก เพราะ raw table ของแต่ละ platform มี field และรูปแบบไม่เหมือนกัน

## Current State

ตอนนี้ KPI Summary API รองรับ filter แล้วบางส่วน:

```text
dateFrom
dateTo
platformIds
```

API ปัจจุบัน:

```text
POST /SalesDashboard/GetKpiSummary
```

ตัวอย่าง body:

```json
{
  "dateFrom": "2025-12-01",
  "dateTo": "2025-12-31",
  "platformIds": [1, 3]
}
```

## Filters That Dashboard Should Have

### 1. date_from / date_to

ใช้กรองช่วงวันที่ของ order

ควรอิงจาก:

```text
PlatformOrder.OrderCreatedAt
```

ตัวอย่าง:

```text
2025-12-01 ถึง 2025-12-31
```

SQL concept:

```sql
po.[OrderCreatedAt] >= @date_from
AND po.[OrderCreatedAt] < DATEADD(day, 1, @date_to)
```

เหตุผลที่ใช้ `< date_to + 1 day` เพราะข้อมูล datetime มีเวลา เช่น:

```text
2025-12-31 23:59:59
```

ถ้าใช้ `<= date_to` แบบ date ตรง ๆ อาจหลุดข้อมูลในวันสุดท้าย

### 2. Platform

ใช้เลือก platform ที่ต้องการดู

ค่าปัจจุบัน:

```text
Shopee
TikTok
```

อิงจาก:

```text
PlatformOrder.PlatformId
```

ตัวอย่าง:

```json
{
  "platformIds": [1, 3]
}
```

ถ้าไม่เลือก platform ใดเลย ควรตีความว่า:

```text
ดูทุก platform
```

### 3. OrderStatus

ใช้กรองสถานะ order

ค่าที่ normalized แล้ว เช่น:

```text
Completed
Delivered
Cancelled
DeliveredInReturnWindow
```

อิงจาก:

```text
PlatformOrder.OrderStatus
PlatformOrder.IsCancelled
PlatformOrder.IsReturned
```

ตัวอย่าง filter:

```text
Completed only
Delivered only
Exclude Cancelled
Include Returned
```

UX ที่แนะนำ:

```text
Completed
Delivered
Cancelled
Returned
```

ทำเป็น checkbox หรือ segmented controls

### 4. Include / Exclude Cancelled

ใช้ควบคุมว่าจะนับ order ที่ถูกยกเลิกหรือไม่

อิงจาก:

```text
PlatformOrder.IsCancelled
```

ค่า default ที่แนะนำ:

```text
includeCancelled = false
```

เหตุผล:

```text
Dashboard ยอดขายหลักไม่ควรนับ order ที่ยกเลิกแล้ว
```

แต่ user ควรเปิดดูได้เพื่อวิเคราะห์ cancellation rate

### 5. Include / Exclude Returned

ใช้ควบคุมว่าจะนับ order ที่คืนสินค้า/คืนเงินหรือไม่

อิงจาก:

```text
PlatformOrder.IsReturned
```

ค่า default ที่แนะนำ:

```text
includeReturned = false
```

เหตุผล:

```text
Dashboard ยอดขายหลักไม่ควรนับ order ที่คืนสินค้าแล้ว
```

แต่ user ควรเปิดดูได้เพื่อวิเคราะห์ returned rate

### 6. SKU / SellerSku / Product / Variation Search

ใช้กรองสินค้า

Shopee และ TikTok มี field ต้นทางไม่เหมือนกัน แต่ใน normalized table เรามี:

```text
PlatformOrderItem.PlatformSku
PlatformOrderItem.SellerSku
PlatformOrderItem.ProductName
PlatformOrderItem.VariationName
```

UX ที่แนะนำ:

```text
Search box: SKU / Product / Variation
```

ตัวอย่าง keyword:

```text
IMURASET1
P0041
โลชั่น
1 กล่อง
```

จุดที่ต้องระวัง:

```text
SalesValue เป็นยอดระดับ order
แต่ SKU/Product filter เป็นระดับ item
```

ดังนั้นถ้ากรอง SKU แล้ว KPI order-level เช่น Total SalesValue ต้องตัดสินใจว่าจะนับแบบไหน:

```text
1. นับยอดทั้ง order ที่มี SKU นี้
2. นับเฉพาะยอดของ item นั้น
```

สำหรับ V1 แนะนำ:

```text
SKU/Product filter ใช้กับ Top Product หรือ item-level charts ก่อน
ยังไม่เอาไปกระทบ Total SalesValue ทั้งหน้า
```

### 7. Province

ใช้กรองจังหวัดของลูกค้า

ตอนนี้ `PlatformOrder` ยังไม่มี field จังหวัดโดยตรง

ข้อมูลจังหวัดอยู่ใน raw table:

```text
ShopeeMaster.ShippingProvince
TiktokMaster.Province
```

ถ้าจะทำ Province filter ให้ดี ควรเพิ่ม field กลาง:

```text
PlatformOrder.ShippingProvince
```

จากนั้นแก้ normalizer ให้เติมข้อมูล:

```text
ShopeeMaster.ShippingProvince -> PlatformOrder.ShippingProvince
TiktokMaster.Province -> PlatformOrder.ShippingProvince
```

ข้อควรระวัง:

```text
ชื่อจังหวัดอาจไม่ตรงกัน เช่น กรุงเทพฯ และ กรุงเทพมหานคร
```

ควรมีขั้นตอน normalize province name ในอนาคต

## Recommended Filter DTO

ในอนาคต `KpiSummaryFilterDTO` ควรขยายเป็นประมาณนี้:

```json
{
  "dateFrom": "2025-12-01",
  "dateTo": "2025-12-31",
  "platformIds": [1, 3],
  "orderStatuses": ["Completed", "Delivered"],
  "includeCancelled": false,
  "includeReturned": false,
  "keyword": "IMURASET1",
  "province": "กรุงเทพมหานคร"
}
```

แต่ไม่ควรใส่ทุกอย่างพร้อมกันทันทีถ้ายังไม่ได้นิยาม logic ชัด โดยเฉพาะ `keyword` และ `province`

## Implementation Phases

### Phase 1: Safe Order-Level Filters

ทำก่อน เพราะใช้ข้อมูลจาก `PlatformOrder` โดยตรง

ควรทำ:

```text
date_from / date_to
Platform
OrderStatus
Include Cancelled
Include Returned
```

ข้อดี:

- ไม่ต้อง join raw table
- ไม่ต้อง join item table
- ไม่ทำให้ order count เพี้ยน
- ใช้ต่อกับ KPI Summary ได้ทันที

### Phase 2: Product Filter

เพิ่ม filter:

```text
SKU / Product / Variation keyword
```

ใช้กับ:

```text
Top Products
Product charts
Product detail tables
```

ยังไม่ควรเอาไปเปลี่ยน `Total SalesValue` จนกว่าจะตกลงนิยามว่า:

```text
นับยอดทั้ง order หรือเฉพาะ item
```

### Phase 3: Province Filter

ทำหลังจากเพิ่ม field:

```text
PlatformOrder.ShippingProvince
```

และแก้ normalizer ของแต่ละ platform แล้ว

ควรมี province normalization ด้วย เช่น:

```text
กรุงเทพฯ -> กรุงเทพมหานคร
กทม. -> กรุงเทพมหานคร
```

## Backend Work

### Current Backend

ไฟล์ที่เกี่ยวข้อง:

```text
models/modelsDTO/SalesDashboard.py
services/SalesDashboardService.py
routes/SalesDashboard.py
```

API:

```text
POST /SalesDashboard/GetKpiSummary
```

### Next Backend Changes

เพิ่ม field ใน DTO:

```text
orderStatuses
includeCancelled
includeReturned
```

แก้ service:

```text
_apply_order_filters(...)
```

ให้รองรับ:

```text
OrderStatus IN (...)
IsCancelled filter
IsReturned filter
```

## Frontend Work

หน้า Dashboard ควรมี filter bar ด้านบนของ content:

```text
date_from
date_to
Platform
OrderStatus
Include Cancelled
Include Returned
```

UX ที่แนะนำ:

- Date ใช้ date picker
- Platform ใช้ toggle/segmented button
- OrderStatus ใช้ checkbox หรือ multi-select
- Include Cancelled ใช้ toggle
- Include Returned ใช้ toggle
- Reset button สำหรับล้าง filter

## V1 Recommendation

สำหรับรอบถัดไป แนะนำทำ:

```text
OrderStatus filter
Include Cancelled toggle
Include Returned toggle
```

เพราะต่อยอดจาก KPI Summary ได้ทันที และใช้ข้อมูลจาก `PlatformOrder` โดยตรง

## Important Warning

อย่า join `PlatformOrderItem` เข้ามาใน KPI Summary โดยไม่ระวัง เพราะ 1 order มีหลาย item ทำให้ order count ถูกคูณ

ถ้าต้องนับ order หลัง join item ต้องใช้:

```sql
COUNT(DISTINCT po.[PlatformOrderId])
```

หรือแยก query order-level และ item-level ออกจากกัน

