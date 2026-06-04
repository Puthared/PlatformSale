# TikTok Raw Data To Clean Data Instructions

เอกสารนี้ใช้เป็นคู่มือสำหรับ AI หรือผู้ช่วยอัตโนมัติในการแปลงข้อมูล Excel จาก TikTok raw data ให้เป็น clean data ที่พร้อมใช้ทำรายงานหรือ dashboard

จุดประสงค์คือให้ผู้ใช้สามารถแนบไฟล์ `.xlsx` ที่มี sheet `Raw_Tiktok` พร้อมเอกสารนี้ แล้วให้ AI สร้าง sheet หรือไฟล์ใหม่ชื่อ `Clean_Tiktok` ได้ทันที

## Input

อ่านข้อมูลจาก sheet:

```text
Raw_Tiktok
```

โครงสร้างสำคัญ:

- Row 1 คือ header
- Row 2 คือคำอธิบาย field จาก TikTok ไม่ใช่ข้อมูล order จริง
- Row 3 เป็นต้นไปคือ data จริง
- Raw data เป็น item-level หรือ SKU-line level
- 1 `Order ID` อาจมีหลายแถว ถ้า order นั้นมีหลายสินค้า
- ข้อมูลระดับ order เช่น วันที่สั่งซื้อ จังหวัด ยอดเงิน และสถานะ จะซ้ำกันในหลาย item row ของ order เดียวกัน

## Output

สร้าง sheet หรือไฟล์ใหม่ชื่อ:

```text
Clean_Tiktok
```

ให้มี header ตามลำดับนี้:

```text
หมายเลขคำสั่งซื้อออนไลน์
วันที่สั่งซื้อ
แพลตฟอร์ม
SKU
จำนวนเงินที่ควรได้รับ
จังหวัด
Order_Status_Clean
Purchase_Hour
Day_of_Week
Month_Year
Product_NAME
ตัวเลือก
Item_Line_Count
Total_Quantity
```

## Output Level

`Clean_Tiktok` ต้องเป็น order-level summary

กฎสำคัญ:

```text
1 row ต่อ 1 Order ID
```

ถ้า `Raw_Tiktok` มีหลายแถวสำหรับ order เดียวกัน ให้รวมให้เหลือ row เดียวใน `Clean_Tiktok`

## Field Mapping

### หมายเลขคำสั่งซื้อออนไลน์

ใช้จาก `Raw_Tiktok`

```text
Order ID
```

ต้องมี 1 row ต่อ 1 `Order ID`

### วันที่สั่งซื้อ

ใช้จาก `Raw_Tiktok`

```text
Created Time
```

แปลงเป็น date หรือ datetime ตามที่ Excel รองรับ

ถ้า order มีหลาย item row ให้ใช้ค่า `Created Time` จาก row แรกของ order

### แพลตฟอร์ม

ใส่ค่าคงที่:

```text
TikTok
```

### SKU

ใช้จาก `Raw_Tiktok`

```text
Seller SKU
```

ถ้า order มีหลาย item row ให้ใช้ `Seller SKU` จาก item row แรกของ order

เหตุผลคือ output นี้เป็น order-level summary ไม่ใช่ item-level detail

### จำนวนเงินที่ควรได้รับ

ใช้จาก `Raw_Tiktok`

```text
Order Amount
```

กฎสำคัญ:

- `Order Amount` เป็นยอดระดับ order
- ถ้า order มีหลาย item row ห้ามนำ `Order Amount` มาบวกซ้ำทุก row
- ให้ใช้ `Order Amount` เพียงครั้งเดียวต่อ 1 `Order ID`

ถ้าใน order เดียวกันมี `Order Amount` หลายค่า ให้ใช้ค่าจาก row แรกที่ไม่ว่าง

### จังหวัด

ใช้จาก `Raw_Tiktok`

```text
Province
```

ถ้า order มีหลาย item row ให้ใช้ค่าจาก row แรกของ order

### Order_Status_Clean

ใช้จาก `Raw_Tiktok`

```text
Order Status
Order Substatus
Cancelation/Return Type
```

ให้ map เป็นภาษาอังกฤษตามนี้:

| Raw TikTok Status | Raw TikTok Substatus | Cancelation/Return Type | Clean Status |
|---|---|---|---|
| ยกเลิกแล้ว | any | any | Cancelled |
| จัดส่งแล้ว | จัดส่งสำเร็จ | blank | Completed |
| เสร็จสมบูรณ์ | any | blank | Completed |
| any | any | Return/Refund | Returned |

ลำดับการตัดสิน:

1. ถ้า `Cancelation/Return Type` เท่ากับ `Return/Refund` ให้เป็น `Returned`
2. ถ้า `Order Status` เท่ากับ `ยกเลิกแล้ว` ให้เป็น `Cancelled`
3. ถ้า `Order Status` เท่ากับ `จัดส่งแล้ว` และ `Order Substatus` เท่ากับ `จัดส่งสำเร็จ` ให้เป็น `Completed`
4. ถ้า `Order Status` เท่ากับ `เสร็จสมบูรณ์` ให้เป็น `Completed`
5. ถ้าไม่เข้า rule ใด ให้ใช้ค่าเดิมจาก `Order Status`

### Purchase_Hour

คำนวณจาก:

```text
Created Time
```

ให้ดึงเฉพาะชั่วโมง เช่น:

```text
30/04/2026 23:28:00 -> 23
```

### Day_of_Week

คำนวณจาก:

```text
Created Time
```

ให้ใส่ชื่อวัน เช่น:

```text
Monday
Tuesday
Wednesday
Thursday
Friday
Saturday
Sunday
```

### Month_Year

คำนวณจาก:

```text
Created Time
```

ให้แปลงเป็นเดือนของปีนั้น โดยแนะนำให้ใช้วันที่วันแรกของเดือน เช่น:

```text
2026-04-01
```

### Product_NAME

ใช้จาก `Raw_Tiktok`

```text
Product Name
```

ถ้า order มีหลาย item row ให้ใช้ `Product Name` จาก item row แรกของ order

### ตัวเลือก

ใช้จาก `Raw_Tiktok`

```text
Variation
```

ถ้า order มีหลาย item row ให้ใช้ `Variation` จาก item row แรกของ order

### Item_Line_Count

คำนวณจากจำนวน raw rows ของแต่ละ order

```text
Item_Line_Count = COUNT(raw rows for this Order ID)
```

ตัวอย่าง:

- ถ้า order มี 1 item row ให้เป็น `1`
- ถ้า order มี 4 item rows ให้เป็น `4`

### Total_Quantity

คำนวณจาก:

```text
Quantity
```

ของทุก item row ใน order เดียวกัน

```text
Total_Quantity = SUM(Quantity for this Order ID)
```

ถ้า `Quantity` ว่างหรือแปลงเป็นตัวเลขไม่ได้ ให้ถือเป็น 0

## Important Rules

### 1. Skip Description Row

ต้องข้าม row 2 เสมอ

เหตุผล:

- Row 2 เป็นคำอธิบาย field จาก TikTok
- ไม่ใช่ข้อมูล order จริง

Data จริงเริ่มที่ row 3

### 2. Aggregate To One Row Per Order

ห้ามปล่อย order เดียวกันออกมาหลาย row ใน `Clean_Tiktok`

ต้อง group ด้วย:

```text
Order ID
```

### 3. Do Not Double Count Order Amount

`Order Amount` เป็นยอดระดับ order

ถ้า order มีหลาย item row:

- ห้าม SUM `Order Amount` ทุก item row
- ให้ใช้ `Order Amount` ครั้งเดียวต่อ order

### 4. Keep Original Order As Much As Possible

ให้เรียง output ตามลำดับที่ `Order ID` ปรากฏครั้งแรกใน raw data

ไม่จำเป็นต้อง sort ใหม่ เว้นแต่ user สั่ง

### 5. Keep Cancelled And Returned Orders Unless User Says Otherwise

โดย default ให้เก็บทุกสถานะไว้ รวมถึง:

- `Cancelled`
- `Returned`

ห้ามลบ order ที่ยกเลิกหรือคืนสินค้าเอง เว้นแต่ user สั่งชัดเจน

เหตุผล:

- Dashboard บางแบบต้องดู cancelled rate และ returned rate
- ถ้าลบออกโดยไม่บอก จะตรวจยอดรวมลำบาก

## Date Parsing

TikTok date อาจอยู่ในรูปแบบ:

```text
30/04/2026 23:28:00
30/04/2026 23:28
2026-04-30 23:28:00
2026-04-30
```

ให้พยายาม parse เป็น datetime ให้ได้

ถ้า parse ไม่ได้:

- ให้คงค่าเดิมไว้ใน `วันที่สั่งซื้อ`
- ให้เว้น `Purchase_Hour`, `Day_of_Week`, `Month_Year` เป็นค่าว่าง

## Suggested Workflow For AI

1. Open the Excel file
2. Read sheet `Raw_Tiktok`
3. Use row 1 as header
4. Skip row 2
5. Start data from row 3
6. Group rows by `Order ID`
7. For each `Order ID`:
   - Use the first raw row as the representative row for order-level fields
   - Count item lines
   - Sum quantity
   - Use `Order Amount` once
8. Create output sheet `Clean_Tiktok`
9. Write headers in the exact order listed in this document
10. Write one output row per order
11. Apply basic formatting:
    - freeze header row
    - auto filter
    - amount column as number with 2 decimals
    - date columns as date
    - set readable column widths

## Validation Checklist

หลังสร้าง `Clean_Tiktok` ให้ตรวจสอบ:

- จำนวน row ของ `Clean_Tiktok` ต้องเท่ากับจำนวน unique `Order ID` ใน `Raw_Tiktok`
- ต้องข้าม row 2 ของ `Raw_Tiktok`
- ห้ามมี `Order ID` ซ้ำใน `Clean_Tiktok`
- ผลรวม `จำนวนเงินที่ควรได้รับ` ต้องไม่ double count order ที่มีหลาย item
- `Item_Line_Count` ต้องตรงกับจำนวน raw rows ของแต่ละ order
- `Total_Quantity` ต้องตรงกับผลรวม `Quantity` ของแต่ละ order
- Sheet output ต้องชื่อ `Clean_Tiktok`
- Header ต้องเรียงตามที่กำหนด

## Example Prompt To Use With AI

ใช้ prompt นี้เมื่อแนบไฟล์ Excel และเอกสารนี้กับ AI:

```text
Please read the attached Excel file and follow the instructions in Tiktok_Raw_To_Clean_AI_Instructions.md.

Create a new Excel file with a sheet named Clean_Tiktok.

Read input data from sheet Raw_Tiktok.
Use row 1 as header.
Skip row 2 because it is a field description row.
Start actual data from row 3.

Group rows by Order ID and create exactly one output row per Order ID.
Do not double count Order Amount when an order has multiple item rows.

Return the generated Excel file.
```

