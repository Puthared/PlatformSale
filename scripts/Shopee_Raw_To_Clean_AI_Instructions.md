# Shopee Raw Data To Clean Data Instructions

เอกสารนี้ใช้เป็นคู่มือสำหรับ AI หรือผู้ช่วยอัตโนมัติในการแปลงข้อมูล Excel จาก Shopee raw data ให้เป็น clean data ที่พร้อมใช้ทำรายงานหรือ dashboard

จุดประสงค์คือให้ผู้ใช้สามารถแนบไฟล์ `.xlsx` ที่มี sheet `Raw_Shopee` พร้อมเอกสารนี้ แล้วให้ AI สร้าง sheet หรือไฟล์ใหม่ชื่อ `Clean_Shopee` ได้ทันที แม้ระบบเว็บหรือ API ยังไม่เสร็จสมบูรณ์

## Input

อ่านข้อมูลจาก sheet:

```text
Raw_Shopee
```

ข้อมูลใน sheet นี้มาจาก Shopee Export โดยตรง

โครงสร้างสำคัญ:

- Row 1 คือ header
- Row 2 เป็นต้นไปคือ data
- 1 order อาจมีหลายแถว เพราะ 1 order อาจมีหลายสินค้า
- แต่ละแถวคือระดับ item หรือ product line
- ข้อมูลระดับ order เช่น วันที่สั่งซื้อ ยอดรวม จังหวัด สถานะ อาจซ้ำกันในหลาย item row ของ order เดียวกัน

## Output

สร้าง sheet หรือไฟล์ใหม่ชื่อ:

```text
Clean_Shopee
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
Product_Name
Basket Size
Is_Unique_Order
```

## Field Mapping

### หมายเลขคำสั่งซื้อออนไลน์

ใช้จาก `Raw_Shopee`

```text
หมายเลขคำสั่งซื้อ
```

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่หมายเลขคำสั่งซื้อ
- row ถัดไปของ order เดียวกันให้เว้นว่าง

### วันที่สั่งซื้อ

ใช้จาก `Raw_Shopee`

```text
วันที่ทำการสั่งซื้อ
```

แปลงเป็น date หรือ datetime ตามที่ Excel รองรับ

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่วันที่
- row ถัดไปของ order เดียวกันให้เว้นว่าง

### แพลตฟอร์ม

ใส่ค่าคงที่:

```text
Shopee
```

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่ `Shopee`
- row ถัดไปของ order เดียวกันให้เว้นว่าง

### SKU

ใช้จาก `Raw_Shopee`

```text
เลขอ้างอิง Parent SKU
```

ถ้าไม่มีค่า ให้ใช้ fallback จาก:

```text
เลขอ้างอิง SKU (SKU Reference No.)
```

SKU เป็นข้อมูลระดับ item ดังนั้นให้ใส่ทุก row

### จำนวนเงินที่ควรได้รับ

ใช้จาก `Raw_Shopee`

```text
จำนวนเงินทั้งหมด
```

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่จำนวนเงิน
- row ถัดไปของ order เดียวกันให้เว้นว่าง

เหตุผลคือยอดนี้เป็นยอดระดับ order ไม่ใช่ระดับ item

### จังหวัด

ใช้จาก `Raw_Shopee`

```text
จังหวัด
```

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่จังหวัด
- row ถัดไปของ order เดียวกันให้เว้นว่าง

### Order_Status_Clean

ใช้จาก `Raw_Shopee`

```text
สถานะการสั่งซื้อ
```

ให้ map เป็นภาษาอังกฤษตามนี้:

| Raw Shopee Status | Clean Status |
|---|---|
| สำเร็จแล้ว | Completed |
| ยกเลิกแล้ว | Cancelled |
| จัดส่งสำเร็จแล้ว | Delivered |
| ผู้ซื้อได้รับสินค้าแล้ว โปรดทราบว่า... | DeliveredPendingReturn |

ถ้าเจอ status อื่นที่ไม่อยู่ในตาราง ให้ใช้ค่าเดิมจาก raw data

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่ status
- row ถัดไปของ order เดียวกันให้เว้นว่าง

### Purchase_Hour

คำนวณจาก:

```text
วันที่ทำการสั่งซื้อ
```

ให้ดึงเฉพาะชั่วโมง เช่น:

```text
2026-05-01 14:35 -> 14
```

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่ชั่วโมง
- row ถัดไปของ order เดียวกันให้เว้นว่าง

### Day_of_Week

คำนวณจาก:

```text
วันที่ทำการสั่งซื้อ
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

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่วัน
- row ถัดไปของ order เดียวกันให้เว้นว่าง

### Month_Year

คำนวณจาก:

```text
วันที่ทำการสั่งซื้อ
```

ให้แปลงเป็นเดือนของปีนั้น โดยแนะนำให้ใช้วันที่วันแรกของเดือน เช่น:

```text
2026-05-01
```

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่ Month_Year
- row ถัดไปของ order เดียวกันให้เว้นว่าง

### Product_Name

ใช้จาก `Raw_Shopee`

```text
ชื่อสินค้า
```

Product name เป็นข้อมูลระดับ item ดังนั้นให้ใส่ทุก row

### Basket Size

คำนวณจาก:

```text
จำนวนเงินทั้งหมด
```

ให้ใช้ bucket ตามนี้:

| Amount | Basket Size |
|---:|---|
| 0 - 500 | 0 - 500 |
| 501 - 1,000 | 501 - 1,000 |
| 1,001 - 2,000 | 1,001 - 2,000 |
| 2,001 - 3,000 | 2,001 - 3,000 |
| มากกว่า 3,000 | > 3,000 |

ถ้า order เดียวกันมีหลาย item row:

- row แรกของ order ให้ใส่ Basket Size
- row ถัดไปของ order เดียวกันให้เว้นว่าง

### Is_Unique_Order

ใช้เพื่อบอกว่า row นี้เป็น row แรกของ order หรือไม่

กฎ:

```text
row แรกของ order = 1
row ถัดไปของ order เดิม = 0
```

Field นี้ต้องใส่ทุก row

## Important Rules

### 1. Preserve Item Rows

ห้ามรวม item หลายแถวให้เหลือ order เดียว

เหตุผล:

- รายงานต้องรู้ว่า order นี้มีสินค้าอะไรบ้าง
- `Product_Name` และ `SKU` เป็นข้อมูลระดับ item
- แต่ยอดเงินรวมเป็นระดับ order

ดังนั้น output ต้องยังมีหลาย row ได้ ถ้า order มีหลาย item

### 2. Put Order-Level Values Only On First Row

สำหรับข้อมูลระดับ order ให้ใส่เฉพาะ row แรกของ order และเว้นว่างใน row ถัดไปของ order เดียวกัน

Field ที่เป็น order-level:

```text
หมายเลขคำสั่งซื้อออนไลน์
วันที่สั่งซื้อ
แพลตฟอร์ม
จำนวนเงินที่ควรได้รับ
จังหวัด
Order_Status_Clean
Purchase_Hour
Day_of_Week
Month_Year
Basket Size
```

Field ที่เป็น item-level:

```text
SKU
Product_Name
Is_Unique_Order
```

### 3. Keep Cancelled Orders Unless User Says Otherwise

โดย default ให้เก็บ order ทุกสถานะไว้ รวมถึง `Cancelled`

ห้ามลบ order ที่ยกเลิกเอง เว้นแต่ user สั่งชัดเจนว่าไม่ต้องเอา cancelled orders

เหตุผล:

- Dashboard บางแบบต้องดู cancelled rate
- ถ้าลบ cancelled orders โดยไม่บอก จะทำให้ยอดรวมและจำนวน order ตรวจสอบยาก

### 4. Returned Orders

ถ้า `จำนวนที่ส่งคืน` มากกว่า 0 ให้ถือว่า item หรือ order นั้นมีการคืนสินค้า

ใน clean format ปัจจุบันยังไม่มี field `Is_Returned`

ถ้า user ต้องการเพิ่ม field ในอนาคต ให้เพิ่มได้ เช่น:

```text
Is_Returned
Returned_Quantity
```

แต่สำหรับ format นี้ยังไม่ต้องเพิ่มเอง

### 5. Date Parsing

Shopee date อาจอยู่ในรูปแบบ:

```text
2026-05-01 14:35
2026-05-01 14:35:00
01/05/2026 14:35
01/05/2026
```

ให้พยายาม parse เป็น datetime ให้ได้

ถ้า parse ไม่ได้ ให้คงค่าเดิมไว้ใน `วันที่สั่งซื้อ` และเว้น `Purchase_Hour`, `Day_of_Week`, `Month_Year` เป็นค่าว่าง

## Suggested Workflow For AI

1. Open the Excel file
2. Read sheet `Raw_Shopee`
3. Use row 1 as header
4. For each data row, read:
   - หมายเลขคำสั่งซื้อ
   - วันที่ทำการสั่งซื้อ
   - เลขอ้างอิง Parent SKU
   - เลขอ้างอิง SKU (SKU Reference No.)
   - ชื่อสินค้า
   - จำนวนเงินทั้งหมด
   - จังหวัด
   - สถานะการสั่งซื้อ
   - จำนวนที่ส่งคืน
5. Group or track rows by `หมายเลขคำสั่งซื้อ`
6. Keep original row order as much as possible
7. For each row:
   - If this is the first row of the order, fill order-level fields
   - If this is not the first row of the order, leave order-level fields blank
   - Always fill item-level fields
8. Create output sheet `Clean_Shopee`
9. Write headers in the exact order listed in this document
10. Write all clean rows
11. Apply basic formatting:
    - freeze header row
    - auto filter
    - amount column as number with 2 decimals
    - date columns as date
    - set readable column widths

## Validation Checklist

หลังสร้าง `Clean_Shopee` ให้ตรวจสอบ:

- จำนวน row ของ `Clean_Shopee` ควรเท่ากับจำนวน data row ของ `Raw_Shopee`
- จำนวน `Is_Unique_Order = 1` ควรเท่ากับจำนวน order ที่ไม่ซ้ำ
- ผลรวม `จำนวนเงินที่ควรได้รับ` ใน `Clean_Shopee` ควรเป็นยอดรวมระดับ order เพราะใส่เฉพาะ row แรกของ order
- ห้ามมีการ double count ยอดเงินจาก order ที่มีหลาย item
- Sheet output ต้องชื่อ `Clean_Shopee`
- Header ต้องเรียงตามที่กำหนด

## Example Prompt To Use With AI

ใช้ prompt นี้เมื่อแนบไฟล์ Excel และเอกสารนี้กับ AI:

```text
Please read the attached Excel file and follow the instructions in Shopee_Raw_To_Clean_AI_Instructions.md.

Create a new Excel file with a sheet named Clean_Shopee.

Read input data from sheet Raw_Shopee.

Do not merge item rows.
For repeated order rows, put order-level values only on the first row and leave them blank on subsequent rows.
Keep SKU and Product_Name on every item row.

Return the generated Excel file.
```

