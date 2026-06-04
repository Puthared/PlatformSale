# Clean Platform Sheets To Clean_ALL Instructions

เอกสารนี้ใช้เป็นคู่มือสำหรับ AI หรือผู้ช่วยอัตโนมัติในการรวม clean data ของ 3 platform ให้กลายเป็น sheet กลางชื่อ `Clean_ALL`

จุดประสงค์คือให้ผู้ใช้สามารถแนบไฟล์ Excel ที่มี clean sheets ของ Shopee, TikTok, Lazada พร้อมเอกสารนี้ แล้วให้ AI สร้าง sheet `Clean_ALL` ที่มี column กลางชุดเดียวกันสำหรับทำ dashboard ได้ทันที

## Input

อ่านข้อมูลจากไฟล์ Excel ที่มี sheet ต่อไปนี้:

```text
Clean_Shopee
Clean_Tiktok
Clean_Lazada
```

ถ้า sheet ใดไม่มี ให้แจ้ง user ว่า missing sheet และหยุดทำงาน

## Output

สร้าง sheet ใหม่ชื่อ:

```text
Clean_ALL
```

ถ้ามี sheet `Clean_ALL` อยู่แล้ว ให้ลบ sheet เดิมและสร้างใหม่

## Output Columns

`Clean_ALL` ต้องมี header ตามลำดับนี้เท่านั้น:

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

## Source Sheet Order

ให้รวมข้อมูลเรียงตามลำดับนี้:

1. `Clean_Shopee`
2. `Clean_Tiktok`
3. `Clean_Lazada`

ให้คงลำดับ row ภายในแต่ละ sheet ตามไฟล์ต้นทาง

## General Rules

### 1. Do Not Recalculate Raw Data

งานนี้ไม่ได้อ่าน raw sheets

ให้ใช้เฉพาะ clean sheets:

```text
Clean_Shopee
Clean_Tiktok
Clean_Lazada
```

ห้ามกลับไปอ่าน `Raw_Shopee`, `Raw_Tiktok`, `Raw_Lazada` เว้นแต่ user สั่งชัดเจน

### 2. Preserve Clean Rows

ให้เอา row จาก clean sheet มาต่อกันใน `Clean_ALL`

ไม่ต้อง group ใหม่

ไม่ต้อง merge order ใหม่

เหตุผลคือ clean sheet แต่ละ platform ถูกเตรียม logic เฉพาะ platform มาแล้ว

### 3. Normalize Column Names Only

สิ่งที่ต้องทำหลัก ๆ คือ map column จากแต่ละ clean sheet ให้เข้ากับ schema กลางของ `Clean_ALL`

## Mapping From Clean_Shopee

อ่านจาก sheet:

```text
Clean_Shopee
```

Mapping:

| Clean_ALL Column | Clean_Shopee Column | Rule |
|---|---|---|
| หมายเลขคำสั่งซื้อออนไลน์ | หมายเลขคำสั่งซื้อออนไลน์ | ใช้ตรง ๆ |
| วันที่สั่งซื้อ | วันที่สั่งซื้อ | ใช้ตรง ๆ |
| แพลตฟอร์ม | แพลตฟอร์ม | ถ้าว่างให้ใส่ `Shopee` เฉพาะ row ที่มี order id |
| SKU | SKU | ใช้ตรง ๆ |
| Revenue | จำนวนเงินที่ควรได้รับ | ใช้ตรง ๆ ถ้าว่างให้เป็น 0 |
| จังหวัด | จังหวัด | ใช้ตรง ๆ |
| Order_Status_Clean | Order_Status_Clean | ใช้ตรง ๆ |
| Purchase_Hour | Purchase_Hour | ใช้ตรง ๆ หรือคำนวณจากวันที่ถ้าว่าง |
| Day_of_Week | Day_of_Week | ใช้ตรง ๆ หรือคำนวณจากวันที่ถ้าว่าง |
| Month_Year | Month_Year | ใช้ตรง ๆ หรือคำนวณจากวันที่ถ้าว่าง |
| Product_Name | Product_Name | ใช้ตรง ๆ |
| Basket Size | Basket Size | ใช้ตรง ๆ หรือคำนวณจาก Revenue ถ้าว่าง |
| Is_Unique_Order | Is_Unique_Order | ใช้ตรง ๆ ถ้าว่างให้เป็น 0 |
| ตัวเลือกสินค้า | ตัวเลือกสินค้า หรือ ตัวเลือก หรือ ชื่อตัวเลือก | ถ้าไม่มี column ให้เว้นว่าง |

หมายเหตุ:

- `Clean_Shopee` อาจเป็น item-level โดย order เดียวมีหลาย row
- ห้ามแก้ logic `Is_Unique_Order`
- ถ้า Revenue ว่างใน item row ถัดไป ให้ใส่ 0 ใน `Clean_ALL`

## Mapping From Clean_Tiktok

อ่านจาก sheet:

```text
Clean_Tiktok
```

Mapping:

| Clean_ALL Column | Clean_Tiktok Column | Rule |
|---|---|---|
| หมายเลขคำสั่งซื้อออนไลน์ | หมายเลขคำสั่งซื้อออนไลน์ | ใช้ตรง ๆ |
| วันที่สั่งซื้อ | วันที่สั่งซื้อ | ใช้ตรง ๆ |
| แพลตฟอร์ม | แพลตฟอร์ม | ถ้าว่างให้ใส่ `TikTok` |
| SKU | SKU | ใช้ตรง ๆ |
| Revenue | จำนวนเงินที่ควรได้รับ | ใช้ตรง ๆ ถ้าว่างให้เป็น 0 |
| จังหวัด | จังหวัด | ใช้ตรง ๆ |
| Order_Status_Clean | Order_Status_Clean | ใช้ตรง ๆ |
| Purchase_Hour | Purchase_Hour | ใช้ตรง ๆ หรือคำนวณจากวันที่ถ้าว่าง |
| Day_of_Week | Day_of_Week | ใช้ตรง ๆ หรือคำนวณจากวันที่ถ้าว่าง |
| Month_Year | Month_Year | ใช้ตรง ๆ หรือคำนวณจากวันที่ถ้าว่าง |
| Product_Name | Product_NAME | ใช้ตรง ๆ |
| Basket Size | ไม่มี | คำนวณจาก Revenue |
| Is_Unique_Order | ไม่มี | ใส่ 1 ทุก row เพราะ `Clean_Tiktok` เป็น order-level |
| ตัวเลือกสินค้า | ตัวเลือก | ใช้ตรง ๆ |

หมายเหตุ:

- `Clean_Tiktok` เป็น order-level summary
- 1 row ต่อ 1 order
- ดังนั้น `Is_Unique_Order` ต้องเป็น 1 ทุก row

## Mapping From Clean_Lazada

อ่านจาก sheet:

```text
Clean_Lazada
```

Mapping:

| Clean_ALL Column | Clean_Lazada Column | Rule |
|---|---|---|
| หมายเลขคำสั่งซื้อออนไลน์ | หมายเลขคำสั่งซื้อออนไลน์ | ใช้ตรง ๆ |
| วันที่สั่งซื้อ | วันที่สั่งซื้อ | ใช้ตรง ๆ |
| แพลตฟอร์ม | แพลตฟอร์ม | ถ้าว่างให้ใส่ `Lazada` |
| SKU | SKU | ใช้ตรง ๆ |
| Revenue | จำนวนเงินที่ควรได้รับ | ใช้ตรง ๆ ถ้าว่างให้เป็น 0 |
| จังหวัด | จังหวัด | ใช้ตรง ๆ |
| Order_Status_Clean | Order_Status_Clean | ใช้ตรง ๆ |
| Purchase_Hour | Purchase_Hour | ใช้ตรง ๆ หรือคำนวณจากวันที่ถ้าว่าง |
| Day_of_Week | Day_of_Week | ใช้ตรง ๆ หรือคำนวณจากวันที่ถ้าว่าง |
| Month_Year | Month_Year | ใช้ตรง ๆ หรือคำนวณจากวันที่ถ้าว่าง |
| Product_Name | Product_NAME | ใช้ตรง ๆ |
| Basket Size | ไม่มี | คำนวณจาก Revenue |
| Is_Unique_Order | ไม่มี | ใส่ 1 ทุก row เพราะ `Clean_Lazada` เป็น order-level |
| ตัวเลือกสินค้า | ไม่มี | เว้นว่าง |

หมายเหตุ:

- `Clean_Lazada` เป็น order-level summary
- 1 row ต่อ 1 order
- ดังนั้น `Is_Unique_Order` ต้องเป็น 1 ทุก row

## Basket Size Rule

ถ้า source sheet ไม่มี `Basket Size` หรือค่า `Basket Size` ว่าง ให้คำนวณจาก `Revenue`

ใช้ bucket ตามนี้:

| Revenue | Basket Size |
|---:|---|
| 0 - 800 | <= 800 |
| 801 - 1,500 | 801 - 1,500 |
| 1,501 - 2,000 | 1,501 - 2,000 |
| 2,001 - 3,000 | 2,001 - 3,000 |
| มากกว่า 3,000 | > 3,000 |

หมายเหตุ:

- ถ้า Revenue ว่างหรือแปลงเป็นตัวเลขไม่ได้ ให้ใส่ค่าว่างใน `Basket Size`

## Date Helper Fields

ถ้า `Purchase_Hour`, `Day_of_Week`, หรือ `Month_Year` ว่าง ให้พยายามคำนวณจาก `วันที่สั่งซื้อ`

### Purchase_Hour

ดึงชั่วโมงจากวันที่สั่งซื้อ:

```text
2026-05-31 16:48 -> 16
```

### Day_of_Week

ใส่ชื่อวันภาษาอังกฤษ:

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

ให้ใช้วันที่วันแรกของเดือน:

```text
2026-05-01
```

## Revenue Rule

ใน `Clean_ALL` column `Revenue` ต้องเป็นตัวเลขเสมอถ้าเป็นไปได้

ถ้า source value ว่าง:

```text
Revenue = 0
```

เหตุผล:

- ใช้ลดปัญหา double count ใน order ที่มีหลาย item
- สำหรับ Shopee item row ที่ไม่ใช่ row แรกของ order ค่า revenue อาจว่างหรือ 0 ได้

## Is_Unique_Order Rule

ใช้เพื่อระบุว่า row นี้ควรถูกนับเป็น order หลักหรือไม่

กฎ:

- Shopee: ใช้ค่าจาก `Clean_Shopee.Is_Unique_Order`
- TikTok: ใส่ `1` ทุก row
- Lazada: ใส่ `1` ทุก row

ถ้าค่า source ของ Shopee ว่าง ให้ใส่ `0`

## Suggested Workflow For AI

1. Open the Excel file
2. Confirm sheets exist:
   - `Clean_Shopee`
   - `Clean_Tiktok`
   - `Clean_Lazada`
3. If `Clean_ALL` exists, delete it
4. Create new sheet `Clean_ALL`
5. Write headers exactly as specified
6. Append rows from `Clean_Shopee` using Shopee mapping
7. Append rows from `Clean_Tiktok` using TikTok mapping
8. Append rows from `Clean_Lazada` using Lazada mapping
9. Apply basic formatting:
   - freeze header row
   - auto filter
   - Revenue as number with 2 decimals
   - date columns as date
   - readable column widths

## Validation Checklist

หลังสร้าง `Clean_ALL` ให้ตรวจสอบ:

- มี sheet `Clean_ALL`
- Header ตรงและเรียงตามที่กำหนด
- จำนวน row ของ `Clean_ALL` ต้องเท่ากับผลรวม data rows ของ:
  - `Clean_Shopee`
  - `Clean_Tiktok`
  - `Clean_Lazada`
- ต้องมี platform ครบ:
  - `Shopee`
  - `TikTok`
  - `Lazada`
- ผลรวม `Revenue` ใน `Clean_ALL` ต้องเท่ากับผลรวมรายได้ของ 3 clean sheets หลัง mapping
- `Is_Unique_Order` ของ TikTok และ Lazada ต้องเป็น 1 ทุก row
- ห้ามมีการกลับไปอ่าน raw sheets หรือ group ใหม่

## Example Prompt To Use With AI

ใช้ prompt นี้เมื่อแนบไฟล์ Excel และเอกสารนี้กับ AI:

```text
Please read the attached Excel file and follow the instructions in Clean_Platforms_To_Clean_ALL_AI_Instructions.md.

Use sheets Clean_Shopee, Clean_Tiktok, and Clean_Lazada.

Create a new sheet named Clean_ALL.

Use the exact output columns specified in the instruction file.
Do not read raw sheets.
Do not regroup the data.
Append rows in this order: Clean_Shopee, Clean_Tiktok, Clean_Lazada.

Return the updated Excel file.
```

