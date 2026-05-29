# Data Import Workflow

## Purpose

สร้างหน้าใหม่สำหรับ Import Raw Data โดยเฉพาะ เพราะขั้นตอน Import และ Normalize ใช้เวลานาน และควรแยกออกจาก Dashboard/Report page

หน้าใหม่นี้จะใช้สำหรับ:

```text
เลือก platform
เลือกไฟล์ Excel
Upload raw data
ดูข้อมูล raw ที่ยังไม่ Normalize
กด Normalize
ดูผลลัพธ์หลัง Normalize
```

## Important Decision

Normalize จะไม่จำกัดรอบละ 1000 order

เมื่อ user กด Normalize ให้ process ข้อมูล pending ทั้งหมดของ platform นั้นไปเลย

```text
Normalize pending raw data ทั้งหมด
ไม่ใช้ limit ต่อรอบ
```

## Core Problem

แต่ละ platform มีรูปแบบ raw data และ normalize logic ไม่เหมือนกัน

ดังนั้นไม่ควรเขียน normalize logic รวมกันเป็นก้อนเดียว

แนวทางที่ควรใช้:

```text
Frontend หน้าเดียว
Backend มี route กลาง
Service/Normalizer แยกตาม platform
```

## Supported Platforms

ช่วงแรก:

```text
Shopee
TikTok
Lazada
```

แต่ Lazada อาจยังเป็น placeholder ถ้า normalizer ยังไม่พร้อม

## FrontEnd Page

สร้างหน้าใหม่:

```text
src/routes/import-data.tsx
```

เพิ่มเมนู Sidebar:

```text
Import Data
```

## FrontEnd Workflow

1. User เข้าเมนู `Import Data`
2. เลือก Platform
3. เลือกไฟล์ Excel
4. กด Upload
5. ระบบเรียก API import raw data ของ platform นั้น
6. แสดงผล import
7. โหลด raw data ที่ยังไม่ normalize มาแสดง
8. User กด Normalize
9. ระบบเรียก API normalize ของ platform นั้น
10. แสดงผล normalize
11. โหลด pending raw data ใหม่อีกครั้ง

## FrontEnd UI

ส่วนที่ควรมี:

```text
Platform selector
File picker
Upload button
Import result panel
Pending normalize table
Normalize button
Normalize result panel
Error panel
Loading state
```

## Platform Selector

ตัวเลือก:

```text
Shopee
TikTok
Lazada
```

ถ้า platform ไหนยังไม่พร้อม ให้ disabled หรือแสดง Coming soon

## Upload Section

Input:

```text
platform
excel file
createdBy
```

ปุ่ม:

```text
Upload Raw Data
```

หลัง upload สำเร็จ ควรแสดง:

```text
importedRows
createdRows
updatedRows
softDeletedRows
errorRows
fileName
```

## Pending Normalize Section

หลัง upload หรือเมื่อเลือก platform ให้แสดงข้อมูล raw ที่ยังไม่ normalize

แสดงเฉพาะ summary ก่อน ไม่จำเป็นต้องแสดงทุก record ถ้าข้อมูลเยอะ

ข้อมูลที่ควรแสดง:

```text
pendingRawRows
pendingOrders
latestImportFileName
oldestCreatedOn
newestCreatedOn
errorCount
```

ถ้าต้องแสดง table ให้ใช้ pagination

## Normalize Section

ปุ่ม:

```text
Normalize Pending Data
```

เมื่อกดแล้ว:

```text
Normalize pending raw data ทั้งหมดของ platform ที่เลือก
```

ไม่ต้องส่ง limit

ผลลัพธ์ที่ควรแสดง:

```text
ordersPicked
ordersCreated
ordersUpdated
ordersSoftDeleted
itemsCreated
itemsSoftDeleted
feesCreated
feesSoftDeleted
rawRowsMarkedNormalized
failedOrders
```

## Backend API Design

ทำ route กลางสำหรับหน้า Import Data

```text
/DataImport/UploadRaw
/DataImport/GetPendingNormalizeSummary
/DataImport/Normalize
```

หรือถ้าต้องการใช้ route เดิมของแต่ละ platform ก่อน ก็สามารถให้ FrontEnd dispatch ไปตาม platform ได้

แต่ระยะยาวแนะนำทำ route กลาง

## Upload API

ตัวอย่าง:

```text
POST /DataImport/UploadRaw
```

Request:

```text
multipart/form-data
platform = shopee | tiktok | lazada
file = Excel file
createdBy = string
```

Backend dispatch:

```python
if platform == "shopee":
    call Shopee raw import
elif platform == "tiktok":
    call TikTok raw import
elif platform == "lazada":
    call Lazada raw import
```

## Pending Summary API

ตัวอย่าง:

```text
POST /DataImport/GetPendingNormalizeSummary
```

Request:

```json
{
  "platform": "shopee"
}
```

Response:

```json
{
  "platform": "shopee",
  "pendingRawRows": 1200,
  "pendingOrders": 800,
  "errorRows": 0,
  "latestImportFileName": "Shopee_Orders.xlsx"
}
```

## Normalize API

ตัวอย่าง:

```text
POST /DataImport/Normalize
```

Request:

```json
{
  "platform": "shopee",
  "createdBy": "admin"
}
```

ไม่มี `limit`

Backend dispatch:

```python
if platform == "shopee":
    call normalize_shopee_master_all()
elif platform == "tiktok":
    call normalize_tiktok_master_all()
elif platform == "lazada":
    call normalize_lazada_master_all()
```

## Service Structure

ควรแยก service ตาม platform

```text
ShopeeImportService
ShopeeNormalizer

TikTokImportService
TiktokNormalizer

LazadaImportService
LazadaNormalizer
```

และมี service กลาง:

```text
DataImportService
```

หน้าที่ของ `DataImportService` คือ dispatch ไปหา service ที่ถูกต้อง

## Why Not One Normalizer

ไม่ควรรวม normalize logic ของทุก platform เป็น function เดียว เพราะ:

```text
ชื่อ field raw data ไม่เหมือนกัน
วิธีคำนวณยอดขายไม่เหมือนกัน
fee ไม่เหมือนกัน
status ไม่เหมือนกัน
SKU mapping ไม่เหมือนกัน
return/refund logic ไม่เหมือนกัน
```

## Long Running Request

รอบแรกสามารถทำให้หน้าเว็บรอ request จนจบได้ก่อน

แต่ต้องมี:

```text
loading state
disable button ระหว่างทำงาน
แสดงข้อความว่า process อาจใช้เวลานาน
แสดง result หลังจบ
```

ในอนาคตถ้านานเกินไป ค่อยเพิ่มระบบ job:

```text
ImportJob
NormalizeJob
JobStatus
Progress
```

แต่ตอนนี้ยังไม่จำเป็น

## Backend Files

ไฟล์ที่อาจเกี่ยวข้อง:

```text
routes/DataImport.py
services/DataImportService.py
routes/ShopeeMaster.py
routes/TikTokMaster.py
services/ShopeeNormalizer.py
services/TiktokNormalizer.py
```

## FrontEnd Files

ไฟล์ที่อาจเกี่ยวข้อง:

```text
src/routes/import-data.tsx
src/lib/api.ts
src/components/AppSidebar.tsx
src/styles.css
```

## Completion Criteria

ถือว่างานหน้า Import Data เสร็จเมื่อ:

1. มีหน้าใหม่ `Import Data`
2. เลือก platform ได้
3. เลือกไฟล์ Excel ได้
4. Upload raw data ได้
5. แสดง import result ได้
6. แสดง pending normalize summary ได้
7. กด Normalize ได้
8. Normalize pending data ทั้งหมด โดยไม่ใช้ limit
9. แสดง normalize result ได้
10. รองรับอย่างน้อย Shopee และ TikTok
11. Backend `py_compile` ผ่าน
12. FrontEnd `npm run build` ผ่าน
