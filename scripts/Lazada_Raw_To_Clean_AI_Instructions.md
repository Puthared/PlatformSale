# Lazada Raw Data To Clean Data Instructions

เอกสารนี้ใช้เป็นคู่มือสำหรับ AI หรือผู้ช่วยอัตโนมัติในการแปลงข้อมูล Excel จาก Lazada raw data ให้เป็น clean data ที่พร้อมใช้ทำรายงานหรือ dashboard

จุดประสงค์คือให้ผู้ใช้สามารถแนบไฟล์ `.xlsx` ที่มี sheet `Raw_Lazada` พร้อมเอกสารนี้ แล้วให้ AI สร้าง sheet หรือไฟล์ใหม่ชื่อ `Clean_Lazada` ได้ทันที

## Input

อ่านข้อมูลจาก sheet:

```text
Raw_Lazada
```

โครงสร้างสำคัญ:

- Row 1 คือ header
- Row 2 เป็นต้นไปคือ data จริง
- Raw data อาจเป็น item-level หรือ order item line-level
- 1 `orderNumber` อาจมีหลายแถว ถ้า order นั้นมีหลาย item line
- ข้อมูลระดับ order เช่น วันที่สั่งซื้อ ยอดเงิน และสถานะ อาจซ้ำกันในหลาย item row ของ order เดียวกัน

## Output

สร้าง sheet หรือไฟล์ใหม่ชื่อ:

```text
Clean_Lazada
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
```

## Output Level

`Clean_Lazada` ต้องเป็น order-level summary

กฎสำคัญ:

```text
1 row ต่อ 1 orderNumber
```

ถ้า `Raw_Lazada` มีหลายแถวสำหรับ order เดียวกัน ให้รวมให้เหลือ row เดียวใน `Clean_Lazada`

## Field Mapping

### หมายเลขคำสั่งซื้อออนไลน์

ใช้จาก `Raw_Lazada`

```text
orderNumber
```

ต้องมี 1 row ต่อ 1 `orderNumber`

### วันที่สั่งซื้อ

ใช้จาก `Raw_Lazada`

```text
createTime
```

แปลงเป็น date หรือ datetime ตามที่ Excel รองรับ

ถ้า order มีหลาย item row ให้ใช้ค่า `createTime` จาก row แรกของ order

### แพลตฟอร์ม

ใส่ค่าคงที่:

```text
Lazada
```

### SKU

ใช้จาก `Raw_Lazada`

```text
sellerSku
```

ถ้า order มีหลาย item row ให้ใช้ `sellerSku` จาก item row แรกของ order

เหตุผลคือ output นี้เป็น order-level summary ไม่ใช่ item-level detail

### จำนวนเงินที่ควรได้รับ

ใช้จาก `Raw_Lazada`

```text
paidPrice
```

กฎสำคัญ:

- `paidPrice` เป็นยอดระดับ item line ได้ใน raw data
- แต่ `Clean_Lazada` ต้องเป็นระดับ order
- ถ้า order มีหลาย item row ให้รวมยอด `paidPrice` ของทุก row ใน order เดียวกัน

สูตร:

```text
จำนวนเงินที่ควรได้รับ = SUM(paidPrice for this orderNumber)
```

ถ้า `paidPrice` ว่างหรือแปลงเป็นตัวเลขไม่ได้ ให้ถือเป็น 0

### จังหวัด

ใน format เดิมของ `Clean_Lazada` มี column นี้ แต่ข้อมูล raw ที่ได้รับอาจไม่มีจังหวัดแบบชัดเจน

ให้พยายามใช้จาก field ต่อไปนี้ตามลำดับ:

```text
shippingRegion
shippingCity
billingCity
```

ถ้าไม่มีข้อมูลหรือเป็นค่าว่าง ให้เว้นว่าง

### Order_Status_Clean

ใช้จาก `Raw_Lazada`

```text
status
```

ให้ map เป็นภาษาอังกฤษตามนี้:

| Raw Lazada Status | Clean Status |
|---|---|
| delivered | Completed |
| shipped | Completed |
| ready_to_ship | Processing |
| pending | Processing |
| canceled | Cancelled |
| cancelled | Cancelled |
| returned | Returned |
| failed | Failed |

ถ้าเจอ status อื่นที่ไม่อยู่ในตาราง ให้ใช้ค่าเดิมจาก raw data

ถ้า order มีหลาย item row ให้ใช้ status จาก row แรกของ order หรือ status แรกที่ไม่ว่าง

### Purchase_Hour

คำนวณจาก:

```text
createTime
```

ให้ดึงเฉพาะชั่วโมง เช่น:

```text
31 May 2026 16:48 -> 16
```

### Day_of_Week

คำนวณจาก:

```text
createTime
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
createTime
```

ให้แปลงเป็นเดือนของปีนั้น โดยแนะนำให้ใช้วันที่วันแรกของเดือน เช่น:

```text
2026-05-01
```

### Product_NAME

ใช้จาก `Raw_Lazada`

```text
itemName
```

ถ้า order มีหลาย item row ให้ใช้ `itemName` จาก item row แรกของ order

## Important Rules

### 1. Aggregate To One Row Per Order

ห้ามปล่อย order เดียวกันออกมาหลาย row ใน `Clean_Lazada`

ต้อง group ด้วย:

```text
orderNumber
```

### 2. Sum paidPrice For Multi-Line Orders

Lazada raw data อาจมีหลาย item line ต่อ order

ถ้า order มีหลาย row:

- ให้ SUM `paidPrice`
- ห้ามใช้ `paidPrice` จาก row แรกอย่างเดียว
- ห้ามปล่อย order ซ้ำใน output

### 3. Keep Original Order As Much As Possible

ให้เรียง output ตามลำดับที่ `orderNumber` ปรากฏครั้งแรกใน raw data

ไม่จำเป็นต้อง sort ใหม่ เว้นแต่ user สั่ง

### 4. Keep Cancelled And Returned Orders Unless User Says Otherwise

โดย default ให้เก็บทุกสถานะไว้ รวมถึง:

- `Cancelled`
- `Returned`
- `Failed`

ห้ามลบ order เหล่านี้เอง เว้นแต่ user สั่งชัดเจน

เหตุผล:

- Dashboard บางแบบต้องดู cancelled rate และ returned rate
- ถ้าลบออกโดยไม่บอก จะตรวจยอดรวมลำบาก

## Date Parsing

Lazada date อาจอยู่ในรูปแบบ:

```text
31 May 2026 16:48
03 Jun 2026 14:06
2026-05-31 16:48:00
31/05/2026 16:48
```

ให้พยายาม parse เป็น datetime ให้ได้

ถ้า parse ไม่ได้:

- ให้คงค่าเดิมไว้ใน `วันที่สั่งซื้อ`
- ให้เว้น `Purchase_Hour`, `Day_of_Week`, `Month_Year` เป็นค่าว่าง

## Suggested Workflow For AI

1. Open the Excel file
2. Read sheet `Raw_Lazada`
3. Use row 1 as header
4. Start data from row 2
5. Group rows by `orderNumber`
6. For each `orderNumber`:
   - Use the first raw row as representative row for order-level text fields
   - Sum `paidPrice` from every row in the order
   - Map `status` to `Order_Status_Clean`
   - Calculate date helper fields from `createTime`
7. Create output sheet `Clean_Lazada`
8. Write headers in the exact order listed in this document
9. Write one output row per order
10. Apply basic formatting:
    - freeze header row
    - auto filter
    - amount column as number with 2 decimals
    - date columns as date
    - set readable column widths

## Validation Checklist

หลังสร้าง `Clean_Lazada` ให้ตรวจสอบ:

- จำนวน row ของ `Clean_Lazada` ต้องเท่ากับจำนวน unique `orderNumber` ใน `Raw_Lazada`
- ห้ามมี `orderNumber` ซ้ำใน `Clean_Lazada`
- ผลรวม `จำนวนเงินที่ควรได้รับ` ต้องเท่ากับผลรวม `paidPrice` ของ raw data หลังแปลงเป็นตัวเลข
- ถ้า order มีหลาย row ต้องรวมยอด `paidPrice` ให้ครบ
- Sheet output ต้องชื่อ `Clean_Lazada`
- Header ต้องเรียงตามที่กำหนด

## Example Prompt To Use With AI

ใช้ prompt นี้เมื่อแนบไฟล์ Excel และเอกสารนี้กับ AI:

```text
Please read the attached Excel file and follow the instructions in Lazada_Raw_To_Clean_AI_Instructions.md.

Create a new Excel file with a sheet named Clean_Lazada.

Read input data from sheet Raw_Lazada.
Use row 1 as header.
Start actual data from row 2.

Group rows by orderNumber and create exactly one output row per orderNumber.
If an order has multiple item rows, sum paidPrice for that order.

Return the generated Excel file.
```

