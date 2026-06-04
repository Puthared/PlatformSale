# Platform Summary Dashboard AI Instructions

ไฟล์นี้ใช้เป็นคู่มือให้ AI สร้างหรือปรับปรุง Sheet `Platform_Summary` จาก Sheet `Clean_All`
สำหรับทำ Dashboard สรุปยอดขายของ Shopee, TikTok และ Lazada ใน Google Sheets หรือ Excel

## Source Sheet

ใช้ข้อมูลจาก Sheet:

```text
Clean_All
```

โดย `Clean_All` ต้องมีคอลัมน์หลักดังนี้:

```text
หมายเลขคำสั่งซื้อออนไลน์
วันที่สั่งซื้อ
แพลตฟอร์ม
SKU
Revenue
จังหวัด
Order_Status_Clean
Purchase_Hour
Day_of_Week
Month_Year
Product_Name
Basket Size
Is_Unique_Order
ตัวเลือกสินค้า
```

## Core Rule

Dashboard นี้ต้องคำนวณเฉพาะออเดอร์ที่สำเร็จแล้วเท่านั้น

```text
Order_Status_Clean = Completed
```

ห้ามนำออเดอร์สถานะอื่น เช่น Cancelled, Returned หรือ Pending มารวมใน metric หลัก

## Dashboard Sheet

ให้สร้างหรือปรับปรุง Sheet ชื่อ:

```text
Platform_Summary
```

ทุกอย่างควรอยู่ใน Sheet เดียวกัน ได้แก่:

- Summary KPI
- Platform comparison
- Top products
- Hourly sales trend
- Monthly sales
- Basket size analysis
- Helper tables สำหรับเลี้ยง chart

ถ้าจำเป็นต้องมี helper tables ให้วางไว้ด้านล่างหรือด้านขวาของ Sheet เดียวกัน

## Main Metrics

### Total Revenue

คำนวณจาก:

```text
SUM(Revenue)
```

โดยกรอง:

```text
Order_Status_Clean = Completed
```

### Total Orders

คำนวณจาก:

```text
SUM(Is_Unique_Order)
```

โดยกรอง:

```text
Order_Status_Clean = Completed
```

เหตุผล: ใน `Clean_All` ออเดอร์หนึ่งอาจมีหลาย item rows ดังนั้น row แรกของ order จะมี `Is_Unique_Order = 1` และ row ถัดไปของ order เดิมจะเป็น `0`

### Average Order Value

คำนวณจาก:

```text
Total Revenue / Total Orders
```

## Recommended Dashboard Sections

### 1. Overall Metrics

แสดงตารางสรุปแยกตามแพลตฟอร์ม:

```text
Platform
Total Revenue
Total Orders
Average Order Value
```

ตัวอย่าง Google Sheets formula:

```excel
=QUERY(Clean_All!A:N,"select C, sum(E), sum(M), sum(E)/sum(M) where C is not null and G='Completed' group by C label C 'Platform', sum(E) 'Total Revenue', sum(M) 'Total Orders', sum(E)/sum(M) 'Average Order Value'",1)
```

### 2. Platform Revenue Comparison

สร้างกราฟเปรียบเทียบ Revenue ของแต่ละแพลตฟอร์มจาก Overall Metrics

รูปแบบที่แนะนำ:

```text
Column chart หรือ Bar chart
```

### 3. Top 5 Products

แสดงสินค้าขายดี 5 อันดับแรกแยกตามแพลตฟอร์ม โดยเรียงจาก Revenue สูงสุด

ต้องกรอง:

```text
Order_Status_Clean = Completed
```

ตัวอย่าง Shopee:

```excel
=QUERY(Clean_All!A:N,"select K, sum(E), sum(M) where C='Shopee' and G='Completed' and K is not null group by K order by sum(E) desc limit 5 label K 'Product Name', sum(E) 'Revenue', sum(M) 'Orders'",1)
```

ตัวอย่าง TikTok:

```excel
=QUERY(Clean_All!A:N,"select K, sum(E), sum(M) where C='TikTok' and G='Completed' and K is not null group by K order by sum(E) desc limit 5 label K 'Product Name', sum(E) 'Revenue', sum(M) 'Orders'",1)
```

ตัวอย่าง Lazada:

```excel
=QUERY(Clean_All!A:N,"select K, sum(E), sum(M) where C='Lazada' and G='Completed' and K is not null group by K order by sum(E) desc limit 5 label K 'Product Name', sum(E) 'Revenue', sum(M) 'Orders'",1)
```

### 4. Hourly Sales Trends

วิเคราะห์ยอดขายตามชั่วโมงจาก:

```text
Purchase_Hour
```

แนะนำให้ทำ helper table ด้วยสูตร:

```excel
=QUERY(Clean_All!A:N,"select H, sum(E) where H is not null and G='Completed' group by H pivot C order by H",1)
```

รูปแบบกราฟที่แนะนำ:

```text
Line chart
```

### 5. Monthly Sales

วิเคราะห์ยอดขายรายเดือนจาก:

```text
Month_Year
```

แนะนำให้ทำ helper table ด้วยสูตร:

```excel
=QUERY(Clean_All!A:N,"select J, sum(E) where J is not null and G='Completed' group by J pivot C order by J",1)
```

รูปแบบกราฟที่แนะนำ:

```text
Line chart
```

### 6. Basket Size Analysis

วิเคราะห์ยอดขายตามช่วง Basket Size

แนะนำให้ทำ helper table ด้วยสูตร:

```excel
=QUERY(Clean_All!A:N,"select L, sum(E), sum(M) where L is not null and G='Completed' group by L order by L label L 'Basket Size', sum(E) 'Revenue', sum(M) 'Orders'",1)
```

รูปแบบกราฟที่แนะนำ:

```text
Column chart
```

## Layout Recommendation

จัด Sheet ให้อ่านง่ายในหน้าเดียว:

```text
Top:
  Dashboard title
  Short description

Upper:
  Overall Metrics
  Platform Revenue Comparison chart

Middle:
  Top 5 Products: Shopee / TikTok / Lazada

Lower:
  Hourly Sales Trends chart
  Monthly Sales chart
  Basket Size Analysis chart

Bottom or right side:
  Helper tables
```

## Styling Recommendation

- ใช้หัวข้อใหญ่ชัดเจน
- ใช้สีพื้นหลังอ่อนสำหรับ section header
- ใช้ตัวเลข format `#,##0.00` สำหรับ Revenue และ AOV
- ใช้ตัวเลข format `#,##0` สำหรับ Orders
- เปิด wrap text สำหรับ Product Name เพราะชื่อสินค้ายาว
- ใช้ chart เพื่อลดภาระการอ่านตาราง
- อย่าทำสีเยอะเกินไป เพราะ dashboard ต้องอ่านเร็ว

## Validation Checklist

หลังสร้างหรือแก้ Dashboard ให้ตรวจสอบ:

- Sheet ชื่อ `Platform_Summary`
- Overall Metrics กรองเฉพาะ `Order_Status_Clean = Completed`
- Total Orders ใช้ `SUM(Is_Unique_Order)` ไม่ใช่ count row
- Revenue ใช้ `SUM(Revenue)`
- Top Products ทุกแพลตฟอร์มกรอง `Completed`
- Hourly Sales Trends กรอง `Completed`
- Monthly Sales กรอง `Completed`
- Basket Size Analysis กรอง `Completed`
- Chart อ้างอิง helper table ที่ถูกต้อง

## Important Note

ถ้าในอนาคตมีการเพิ่มสถานะใหม่ใน `Order_Status_Clean` ต้องตรวจสอบก่อนว่าสถานะนั้นควรถูกนับเป็นยอดขายสำเร็จหรือไม่
สำหรับ Dashboard เวอร์ชันนี้ให้ถือว่าเฉพาะ `Completed` เท่านั้นที่นับเป็นยอดขายหลัก
