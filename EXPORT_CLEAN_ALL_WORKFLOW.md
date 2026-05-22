# Clean ALL Excel Export Workflow

เอกสารนี้สรุปแนวทางทำฟังก์ชัน Export Excel จากข้อมูลกลาง `PlatformOrder`, `PlatformOrderItem`, `PlatformOrderFee` ให้ออกมาใน format คล้าย sheet `Clean_ALL` ของไฟล์ Zortout เดิม

## เป้าหมาย

สร้างปุ่ม `Export Excel` บนหน้า Dashboard เพื่อให้ผู้ใช้เลือก platform และช่วงวันที่ที่ต้องการ export โดยไม่ export ข้อมูลทั้งหมดใน database ออกมาทีเดียว

รองรับแนวคิดสำหรับ 3 platform:

- Shopee
- Lazada
- Tiktok

ใน phase แรกให้ implement เฉพาะ Shopee ก่อน แต่โครงสร้างต้องไม่ผูกกับ Shopee จนเกินไป เพื่อให้เพิ่ม Lazada และ Tiktok ได้ในอนาคต

## Frontend Flow

บนหน้า Dashboard จะมีปุ่ม:

```text
Export Excel
```

เมื่อกดปุ่ม ให้เปิด Modal สำหรับตั้งค่า export

Modal จะมี section ของแต่ละ platform:

```text
[ ] Shopee
    date_from: ____
    date_to:   ____

[ ] Lazada
    date_from: ____
    date_to:   ____

[ ] Tiktok
    date_from: ____
    date_to:   ____
```

## UI Rules

- ผู้ใช้เลือก platform ได้มากกว่า 1 platform
- ปุ่ม `Export` จะกดไม่ได้จนกว่าจะมี platform อย่างน้อย 1 รายการถูกเลือก
- ถ้า platform ไหนไม่ได้ถูกติ๊กเลือก ช่อง `date_from` และ `date_to` ของ platform นั้นต้อง disabled
- เมื่อ platform ถูก untick ให้ clear ค่า `date_from` และ `date_to` ของ platform นั้นเป็นค่าว่างทันที
- ถ้า platform ถูกติ๊กเลือก ต้องมี `date_from` และ `date_to` ก่อน export
- ถ้า `date_from` มากกว่า `date_to` ต้องแจ้ง validation error
- ใน phase แรก Lazada และ Tiktok อาจแสดงไว้แต่ disabled หรือแสดงข้อความว่ายังไม่รองรับ หาก backend ยังรองรับเฉพาะ Shopee

## API Contract

แนะนำให้ใช้ `POST` เพราะเงื่อนไข export อาจเพิ่มในอนาคต

```text
POST /Export/CleanAll
```

ตัวอย่าง request:

```json
{
  "platforms": [
    {
      "platform": "Shopee",
      "date_from": "2026-04-01",
      "date_to": "2026-04-30"
    },
    {
      "platform": "Tiktok",
      "date_from": "2026-05-01",
      "date_to": "2026-05-31"
    }
  ]
}
```

Backend จะ export เฉพาะ platform ที่ถูกส่งมาใน `platforms`

## Clean ALL Output Columns

ใช้ header format นี้ โดยไม่เอา column แปลกที่เป็นวันที่ เช่น `2026-04-30 00:00:00`

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

## Shopee Mapping

Mapping เบื้องต้นสำหรับ Shopee:

```text
หมายเลขคำสั่งซื้อออนไลน์ -> PlatformOrder.PlatformOrderNo
วันที่สั่งซื้อ -> PlatformOrder.OrderCreatedAt
แพลตฟอร์ม -> Platform.PlatformName
SKU -> PlatformOrderItem.SellerSku หรือ PlatformOrderItem.PlatformSku
จำนวนเงินที่ควรได้รับ -> PlatformOrder.TotalAmount
จังหวัด -> ShopeeMaster.ShippingProvince
Order_Status_Clean -> PlatformOrder.OrderStatus
Purchase_Hour -> hour จาก PlatformOrder.OrderCreatedAt
Day_of_Week -> weekday จาก PlatformOrder.OrderCreatedAt
Month_Year -> month จาก PlatformOrder.OrderCreatedAt
Product_Name -> PlatformOrderItem.ProductName
Basket Size -> bucket จาก PlatformOrder.TotalAmount
Is_Unique_Order -> row แรกของ order = 1, row ถัดไปของ order เดิม = 0
```

## Order-Level Field Rule

ถ้า 1 order มีหลาย item row ให้แสดง field ระดับ order เฉพาะ row แรกของ order เท่านั้น

ตัวอย่าง:

```text
Order A, Item 1 -> จำนวนเงินที่ควรได้รับ = 2,690, Is_Unique_Order = 1
Order A, Item 2 -> จำนวนเงินที่ควรได้รับ = blank, Is_Unique_Order = 0
Order A, Item 3 -> จำนวนเงินที่ควรได้รับ = blank, Is_Unique_Order = 0
```

เหตุผลคือทำให้ Excel อ่านง่าย และช่วยให้ pivot/report นับจำนวน order จริงได้จาก `SUM(Is_Unique_Order)` โดยไม่โดน item row นับซ้ำ

## Basket Size Rule

`Basket Size` คือช่วงราคาที่ลูกค้าจ่ายเงินให้บริษัท โดย phase แรกให้คำนวณจาก `PlatformOrder.TotalAmount`

Rule เริ่มต้น:

```text
0 - 500
501 - 1,000
1,001 - 2,000
2,001 - 3,000
> 3,000
```

หากมี business rule ที่ชัดเจนจากไฟล์เดิมในอนาคต ค่อยปรับ bucket ให้ตรงกับ source เดิม

## Backend Flow

1. รับ request จาก frontend
2. validate ว่ามีอย่างน้อย 1 platform ถูกเลือก
3. validate date range ของแต่ละ platform
4. query เฉพาะ platform และช่วงวันที่ที่เลือก
5. join `PlatformOrder` กับ `PlatformOrderItem`
6. สำหรับ Shopee ให้ join หรือ lookup `ShopeeMaster` เพื่อดึง `ShippingProvince`
7. group row ตาม `PlatformOrderId` หรือ `PlatformOrderNo`
8. ใส่ order-level fields เฉพาะ item row แรก
9. generate Excel sheet `Clean_ALL`
10. return เป็นไฟล์ `.xlsx` ให้ frontend download

## Performance Guard

ไม่ควร export ทั้ง database ในครั้งเดียว

ควรมี guard เช่น:

```text
ถ้า result เกิน 50,000 rows ให้ reject และแจ้งให้ผู้ใช้ลดช่วงวันที่
```

เหตุผล:

- ลด memory usage ของ backend
- ลดเวลาสร้างไฟล์ Excel
- ลดโอกาส browser timeout
- ทำให้ผู้ใช้เปิด Excel ได้ง่ายขึ้น

## Future Extension

เพื่อรองรับ Lazada และ Tiktok ในอนาคต ควรแยก logic เฉพาะ platform ออกจาก export หลัก

แนวคิด:

```text
CleanAllExporter
ShopeeCleanAllAdapter
LazadaCleanAllAdapter
TiktokCleanAllAdapter
```

export format ยังคงเป็น `Clean_ALL` เดียวกัน แต่ field เฉพาะ platform เช่น จังหวัด หรือ raw lookup ให้ adapter ของแต่ละ platform จัดการเอง

