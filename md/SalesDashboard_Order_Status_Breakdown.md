# Sales Dashboard - Order Status Breakdown

## Purpose

Order Status Breakdown คือข้อ 6 ของ Sales Dashboard ToDoList

เป้าหมายคือดูว่า order ในระบบกระจายอยู่ในสถานะอะไรบ้าง และแต่ละสถานะมีผลต่อจำนวน order, ยอดขาย และจำนวนสินค้าอย่างไร

หน้านี้ควรช่วยตอบคำถามเช่น:

```text
มี order Completed กี่รายการ
มี order Cancelled กี่รายการ
ยอดขายของแต่ละ status เป็นเท่าไร
สัดส่วน order แต่ละ status คิดเป็นกี่ %
Shopee กับ TikTok มี status กระจายต่างกันไหม
```

## Important Decision

หน้านี้ไม่ควร exclude cancelled หรือ returned orders

เหตุผลคือจุดประสงค์ของหน้านี้คือการดูสถานะทั้งหมด ถ้าตัด cancelled/returned ออก จะทำให้รายงานสถานะไม่ครบ

ดังนั้น API ของหน้านี้จะไม่ใช้ logic:

```text
includeCancelled
includeReturned
```

แต่จะนับทุก order ที่ไม่ถูก soft delete

## Backend API Plan

เพิ่ม endpoint ใหม่:

```text
POST /SalesDashboard/GetOrderStatusBreakdown
```

Request ตัวอย่าง:

```json
{
  "year": 2026,
  "month": null,
  "platformIds": []
}
```

## Request Fields

```text
year
month
platformIds
```

`year`

ปีที่ต้องการดูข้อมูล

`month`

ถ้าเป็น `null` ให้ query ทั้งปี

ถ้ามีค่า 1-12 ให้ query เฉพาะเดือนนั้น

`platformIds`

ถ้าเป็น array ว่าง ให้รวมทุก platform

ถ้ามีค่า เช่น `[1]` ให้ดูเฉพาะ Shopee

ถ้ามีค่า `[3]` ให้ดูเฉพาะ TikTok

## Backend Calculation

ใช้ table:

```text
PlatformOrder
PlatformOrderItem
```

Group หลัก:

```text
PlatformOrder.OrderStatus
```

ถ้า `OrderStatus` เป็น `NULL` หรือค่าว่าง ให้แสดงเป็น:

```text
Unknown
```

Metrics:

```text
orderCount = COUNT(PlatformOrder.PlatformOrderId)
salesValue = SUM(COALESCE(PlatformOrder.SalesValue, 0))
quantity = SUM(quantity จาก PlatformOrderItem)
orderShare = orderCount / totalOrderCount
salesShare = salesValue / totalSalesValue
quantityShare = quantity / totalQuantity
```

## Important Calculation Detail

ต้องระวังเรื่อง join กับ item

ห้าม join `PlatformOrder` กับ `PlatformOrderItem` แล้ว sum `PlatformOrder.SalesValue` ตรง ๆ เพราะ order หนึ่งอาจมีหลาย item และจะทำให้ `SalesValue` ถูกคูณซ้ำ

วิธีที่ควรใช้:

1. ทำ subquery รวม `PlatformOrderItem.Quantity` ตาม `PlatformOrderId`
2. Join subquery กลับเข้า `PlatformOrder`
3. Group ตาม `OrderStatus`
4. Sum `PlatformOrder.SalesValue` จาก order header

## Response Example

```json
{
  "year": 2026,
  "month": null,
  "items": [
    {
      "status": "Completed",
      "orderCount": 10000,
      "salesValue": 15000000,
      "quantity": 12000,
      "orderShare": 0.7,
      "salesShare": 0.8,
      "quantityShare": 0.75
    },
    {
      "status": "Cancelled",
      "orderCount": 500,
      "salesValue": 0,
      "quantity": 0,
      "orderShare": 0.03,
      "salesShare": 0,
      "quantityShare": 0
    }
  ],
  "totals": {
    "statusCount": 2,
    "orderCount": 10500,
    "salesValue": 15000000,
    "quantity": 12000
  },
  "filters": {
    "platformIds": []
  }
}
```

## Backend Files

ไฟล์ที่จะเกี่ยวข้อง:

```text
models/modelsDTO/SalesDashboard.py
services/SalesDashboardService.py
routes/SalesDashboard.py
```

เพิ่ม DTO:

```text
OrderStatusBreakdownFilterDTO
```

เพิ่ม service function:

```text
get_order_status_breakdown()
```

เพิ่ม route:

```text
GetOrderStatusBreakdown()
```

## FrontEnd Plan

ทำเป็นหน้าใหม่:

```text
src/routes/order-status-breakdown.tsx
```

เพิ่มเมนูใน Sidebar:

```text
Order Status Breakdown
```

## FrontEnd Filters

หน้า Order Status Breakdown จะมี filter ของตัวเอง:

```text
Year
Month
Platform
Search
```

Default:

```text
Year = ปีปัจจุบัน
Month = All months
Platform = All platforms
```

Platform checkbox:

```text
Shopee
TikTok
```

ถ้าไม่เลือก platform ใดเลย ให้ถือว่าเป็นทุก platform

## FrontEnd Display

มี 3 ส่วนหลัก

### 1. Summary Cards

```text
Total Orders
Total SalesValue
Total Quantity
Status Count
```

### 2. Chart

ใช้ Chart.js

ชนิดกราฟที่แนะนำ:

```text
Horizontal Bar Chart
```

เหตุผล:

```text
OrderStatus อาจเป็นข้อความยาว เช่น DeliveredPendingReturn
Bar chart อ่านง่ายกว่า donut เมื่อ status มีหลายประเภท
เปรียบเทียบ OrderCount ได้ตรงไปตรงมา
```

Metric รอบแรก:

```text
OrderCount
```

ภายหลังอาจเพิ่ม toggle:

```text
OrderCount
SalesValue
Quantity
```

### 3. Table

Columns:

```text
Status
OrderCount
SalesValue
Quantity
Order Share
Sales Share
Quantity Share
```

## FrontEnd Files

ไฟล์ที่จะเกี่ยวข้อง:

```text
src/lib/api.ts
src/components/AppSidebar.tsx
src/routes/order-status-breakdown.tsx
src/styles.css
```

## Behavior

เปิดหน้าแรก:

```text
โหลดปีปัจจุบัน
Month = All months
Platform = All platforms
```

เลือกเดือน:

```text
query เฉพาะเดือนนั้น
```

เลือก Shopee:

```text
query เฉพาะ PlatformId = 1
```

เลือก TikTok:

```text
query เฉพาะ PlatformId = 3
```

ไม่เลือก platform:

```text
query ทุก platform
```

## Edge Cases

`OrderStatus` เป็น NULL:

```text
แสดงเป็น Unknown
```

`OrderStatus` เป็น string ว่าง:

```text
แสดงเป็น Unknown
```

Cancelled / Returned:

```text
ต้องถูกนับใน report นี้
```

## Future Improvement

สิ่งที่อาจเพิ่มในอนาคต:

```text
Metric toggle: OrderCount / SalesValue / Quantity
Platform split per status
Status color mapping
Export Excel
Click status to view orders
```

## Completion Criteria

ถือว่าข้อ 6 เสร็จเมื่อ:

1. มี API `POST /SalesDashboard/GetOrderStatusBreakdown`
2. API group ด้วย `OrderStatus`
3. API ไม่ exclude cancelled / returned
4. API รวม quantity ด้วย subquery ตาม order เพื่อกัน SalesValue ซ้ำ
5. มีหน้าใหม่ `Order Status Breakdown`
6. หน้าใหม่มี filter ปี/เดือน/platform
7. หน้าใหม่มี summary cards
8. หน้าใหม่มี Chart.js horizontal bar chart
9. หน้าใหม่มี table metrics ครบ
10. `py_compile` ผ่าน
11. `npm run build` ผ่าน
12. Mark ToDoList ข้อ 6 เป็น Done
