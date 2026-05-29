# Sales Dashboard - Sales Trend

## Purpose

Sales Trend คือข้อ 4 ของ Sales Dashboard ToDoList

เป้าหมายคือดูแนวโน้มยอดขายตามเวลา เช่น รายวันหรือรายเดือน เพื่อให้เห็นว่าช่วงไหนขายดี ช่วงไหนยอดตก และเมื่อใช้ร่วมกับ filter จะช่วยเปรียบเทียบแนวโน้มของแต่ละ platform ได้ง่ายขึ้น

## Scope

Sales Trend จะทำทั้งฝั่ง API และ FrontEnd

API จะสร้างข้อมูล trend จาก table ที่ normalize แล้ว

FrontEnd จะนำข้อมูลไปแสดงเป็นกราฟด้วย Chart.js

## Backend API Plan

เพิ่ม endpoint ใหม่ใน `routes/SalesDashboard.py`

```text
POST /SalesDashboard/GetSalesTrend
```

ใช้ filter ชุดเดียวกับ Dashboard ปัจจุบัน และเพิ่ม `groupBy`

```json
{
  "dateFrom": "2026-05-01",
  "dateTo": "2026-05-31",
  "platformIds": [1, 3],
  "orderStatuses": ["Completed"],
  "includeCancelled": false,
  "includeReturned": false,
  "groupBy": "day"
}
```

## groupBy

รองรับ 2 ค่าในช่วงแรก

```text
day
month
```

`day` คือ group ข้อมูลตามวันที่ เช่น `2026-05-01`

`month` คือ group ข้อมูลตามเดือน เช่น `2026-05`

## API Response

ตัวอย่าง response

```json
{
  "groupBy": "day",
  "items": [
    {
      "period": "2026-05-01",
      "salesValue": 150000,
      "orderCount": 120,
      "quantity": 180
    }
  ],
  "totals": {
    "salesValue": 28807890.57,
    "orderCount": 18308,
    "quantity": 20226
  },
  "filters": {
    "dateFrom": "2026-05-01",
    "dateTo": "2026-05-31",
    "platformIds": [1, 3],
    "orderStatuses": ["Completed"],
    "includeCancelled": false,
    "includeReturned": false
  }
}
```

## Backend Calculation

ใช้ table หลัก:

```text
PlatformOrder
PlatformOrderItem
```

Field หลัก:

```text
PlatformOrder.OrderCreatedAt
PlatformOrder.SalesValue
PlatformOrder.PlatformOrderId
PlatformOrder.IsCancelled
PlatformOrder.IsReturned
PlatformOrder.OrderStatus
PlatformOrder.PlatformId
PlatformOrderItem.Quantity
```

หลักการคำนวณ:

```text
salesValue = SUM(PlatformOrder.SalesValue)
orderCount = COUNT(PlatformOrder.PlatformOrderId)
quantity = SUM(PlatformOrderItem.Quantity)
```

ต้องระวังเรื่อง order ที่มีหลาย item

ห้าม join `PlatformOrder` กับ `PlatformOrderItem` แล้ว sum `SalesValue` ตรง ๆ เพราะจะทำให้ `SalesValue` ถูกคูณซ้ำตามจำนวน item

วิธีที่ควรใช้:

1. ทำ subquery รวม `Quantity` ตาม `PlatformOrderId`
2. Join subquery กลับเข้า `PlatformOrder`
3. Group ตาม period
4. Sum `SalesValue` จาก `PlatformOrder`

## Backend Files

ไฟล์ที่จะเกี่ยวข้อง:

```text
models/modelsDTO/SalesDashboard.py
services/SalesDashboardService.py
routes/SalesDashboard.py
```

DTO ที่ควรเพิ่ม:

```text
SalesTrendFilterDTO
```

Service function ที่ควรเพิ่ม:

```text
get_sales_trend()
```

Route function ที่ควรเพิ่ม:

```text
GetSalesTrend()
```

## FrontEnd Plan

ใช้ Chart.js ผ่าน React wrapper

Package ที่ต้องติดตั้ง:

```bash
npm install chart.js react-chartjs-2
```

สร้าง component ใหม่:

```text
src/components/SalesTrendChart.tsx
```

เพิ่ม API client:

```text
src/lib/api.ts
```

เพิ่ม type:

```text
SalesTrend
SalesTrendItem
SalesTrendGroupBy
```

เพิ่ม function:

```text
getSalesTrend()
```

เชื่อมในหน้า Dashboard:

```text
src/routes/index.tsx
```

## Chart Design

เริ่มจากกราฟ line chart

Metric หลัก:

```text
SalesValue
```

Metric เสริม:

```text
OrderCount
Quantity
```

คำแนะนำเบื้องต้น:

ให้แสดง `SalesValue` เป็นเส้นหลักก่อน เพราะเป็นตัวเลขที่สำคัญที่สุดของ Dashboard

`OrderCount` และ `Quantity` ควรแสดงใน tooltip หรือ summary detail ก่อน เพราะ scale ตัวเลขต่างจาก SalesValue มาก ถ้าเอามาอยู่แกนเดียวกันจะอ่านยาก

ภายหลังถ้าต้องการ สามารถเพิ่ม dual-axis chart หรือ metric toggle ได้

## UI Behavior

Sales Trend จะใช้ filter เดียวกับ Dashboard ทั้งหน้า

Workflow:

1. User เลือก date range, platform, status, include cancelled, include returned
2. User กด Apply
3. FrontEnd ยิง API พร้อมกัน
   - `GetKpiSummary`
   - `GetSalesByPlatform`
   - `GetSalesTrend`
4. KPI cards เปลี่ยนตาม filter
5. Sales by Platform เปลี่ยนตาม filter
6. Sales Trend chart เปลี่ยนตาม filter

## Default Behavior

ค่า default ที่แนะนำ:

```text
groupBy = day
metric = SalesValue
```

มี toggle ให้เลือก:

```text
Daily
Monthly
```

เมื่อเลือก `Daily` ให้ส่ง `groupBy = day`

เมื่อเลือก `Monthly` ให้ส่ง `groupBy = month`

## Error And Loading State

FrontEnd ควรมี state ต่อไปนี้:

```text
Loading
Error
Empty data
Success
```

กรณีไม่มีข้อมูล:

```text
No sales trend found
Try changing the dashboard filters.
```

## Future Improvement

สิ่งที่สามารถเพิ่มในอนาคต:

```text
Compare platform trend in one chart
Add SalesValue / OrderCount / Quantity metric toggle
Add weekly groupBy
Add moving average
Add previous period comparison
Add export chart image
```

## Completion Criteria

ถือว่าข้อ 4 เสร็จเมื่อ:

1. มี API `POST /SalesDashboard/GetSalesTrend`
2. API ใช้ filter เดียวกับ Dashboard ได้ครบ
3. API group by day/month ได้
4. API คำนวณ SalesValue, OrderCount, Quantity ถูกต้อง
5. FrontEnd แสดง Chart.js ได้
6. Chart เปลี่ยนตาม filter และ groupBy
7. `npm run build` ผ่าน
8. Mark ToDoList ข้อ 4 เป็น Done
