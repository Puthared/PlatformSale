# Import Data Workflow

เอกสารนี้สรุปแนวทางทำหน้า `Import Data` สำหรับอัปโหลดไฟล์ Raw Excel ของแต่ละ Platform แล้วสั่ง Normalize ข้อมูลเข้า Table กลางของระบบ

## เป้าหมาย

สร้างหน้า Import Data แยกออกมาจาก Dashboard เพราะการ Import และ Normalize ใช้เวลานาน และควรมีหน้าที่ผู้ใช้เห็นสถานะงานได้ชัดเจน

Flow หลักคือ:

1. ผู้ใช้เลือก Platform เช่น Shopee, TikTok, Lazada
2. ผู้ใช้เลือกไฟล์ Excel Raw Data
3. ระบบตรวจสอบว่าไฟล์และ Header ตรงกับ Format ที่ระบบรองรับหรือไม่
4. ระบบ Import ข้อมูลเข้า Raw Table ของ Platform นั้น
5. ระบบแสดงข้อมูลที่ยังไม่ถูก Normalize
6. ผู้ใช้กด Normalize
7. ระบบ Normalize ข้อมูลทั้งหมดที่ยัง pending เข้า `PlatformOrder`, `PlatformOrderItem`, `PlatformOrderFee`

## ข้อตกลงสำคัญเรื่อง Normalize

Normalize จะไม่จำกัดจำนวนต่อรอบ เช่น ไม่ใช้แนวคิด `limit = 1000 orders`

เมื่อผู้ใช้กด Normalize ให้ระบบประมวลผลข้อมูลทั้งหมดที่ยัง pending ของ Platform นั้นไปเลย โดยใช้เงื่อนไขหลักประมาณนี้:

- `isDeleted = False`
- `IsNormalized = False`

เหตุผลคือผู้ใช้ต้องการกดครั้งเดียวแล้วให้ระบบจัดการให้ครบ ไม่ต้องแบ่งรอบเอง

ถ้าในอนาคตข้อมูลใหญ่จน API รอนานเกินไป ค่อยพัฒนาเป็น Background Job เพิ่มภายหลัง แต่ Logic ธุรกิจยังเหมือนเดิมคือ Normalize ทั้งหมดที่ pending

## ปัญหาหลัก

แต่ละ Platform มี Raw Data และวิธี Normalize ไม่เหมือนกัน

ตัวอย่าง:

- Shopee ใช้ `ShopeeMaster`
- TikTok ใช้ `TiktokMaster`
- Lazada จะมี `LazadaMaster` ในอนาคต

ดังนั้นไม่ควรเขียน Import และ Normalize ของทุก Platform ปนกันใน Function เดียว

ควรแยกเป็น Service เฉพาะของแต่ละ Platform แล้วให้ API กลางเลือกเรียกตาม Platform ที่ผู้ใช้เลือก

## Backend Plan

สร้าง Route กลางสำหรับหน้า Import Data เช่น:

- `routes/DataImport.py`

API ที่ควรมี:

### 1. Validate Raw File

`POST /DataImport/ValidateRawFile`

หน้าที่:

- รับ `platform`
- รับไฟล์ Excel
- ตรวจสอบชื่อ Sheet
- ตรวจสอบ Header ที่จำเป็น
- แจ้ง Field ที่ขาด
- แจ้ง Field ที่เพิ่มมา
- แจ้ง Field ที่ชื่อเปลี่ยนหรือไม่ตรง Format

### 2. Import Raw File

`POST /DataImport/ImportRawFile`

หน้าที่:

- รับ `platform`
- รับ `createdBy`
- รับไฟล์ Excel
- เรียก Import Service ของ Platform นั้น
- Insert หรือ Update Raw Table
- เก็บ `ImportFileName`
- ถ้า Record ใหม่หรือมีข้อมูลเปลี่ยน ให้ตั้ง `IsNormalized = False`

ตัวอย่าง Raw Table:

- Shopee -> `ShopeeMaster`
- TikTok -> `TiktokMaster`
- Lazada -> `LazadaMaster`

### 3. Get Pending Normalize

`GET /DataImport/GetPendingNormalize`

หน้าที่:

- รับ `platform`
- Query จำนวนข้อมูลที่ยังไม่ Normalize
- แสดงจำนวน Raw Rows
- แสดงจำนวน Orders
- แสดงจำนวน Error ถ้ามี `NormalizeError`
- แสดงชื่อไฟล์ Import ล่าสุดจาก `ImportFileName`

### 4. Normalize Raw Data

`POST /DataImport/NormalizeRawData`

หน้าที่:

- รับ `platform`
- รับ `createdBy`
- เรียก Normalizer ของ Platform นั้น
- Normalize ข้อมูลทั้งหมดที่ pending
- ไม่มี parameter `limit`

ตัวอย่าง Payload:

```json
{
  "platform": "shopee",
  "createdBy": "admin",
  "mode": "all_pending"
}
```

ผลลัพธ์ที่ควรส่งกลับ:

```json
{
  "status": "success",
  "message": "Normalize success.",
  "data": {
    "rawRowsPicked": 0,
    "ordersPicked": 0,
    "ordersCreated": 0,
    "ordersUpdated": 0,
    "ordersSkipped": 0,
    "itemsCreated": 0,
    "feesCreated": 0,
    "rawRowsMarkedNormalized": 0,
    "failedOrders": 0
  }
}
```

## Service Plan

ควรแยก Service ตาม Platform:

- `services/ShopeeImportService.py`
- `services/ShopeeNormalizer.py`
- `services/TiktokImportService.py`
- `services/TiktokNormalizer.py`
- `services/LazadaImportService.py`
- `services/LazadaNormalizer.py`

Route กลางไม่ควรรู้รายละเอียด Field ของแต่ละ Platform มากเกินไป

Route กลางควรทำหน้าที่:

1. รับ Request
2. ตรวจสอบว่า Platform ไหน
3. Dispatch ไปยัง Service ของ Platform นั้น
4. ส่งผลลัพธ์กลับ Frontend

## Frontend Plan

สร้างหน้าใหม่:

- `/import-data`

ไฟล์ที่คาดว่าจะเกี่ยวข้อง:

- `src/routes/import-data.tsx`
- `src/components/AppSidebar.tsx`
- `src/lib/api.ts`
- `src/styles.css`

UI หลัก:

1. Platform selector
   - Shopee
   - TikTok
   - Lazada

2. File upload
   - เลือกไฟล์ Excel
   - แสดงชื่อไฟล์ที่เลือก

3. Validate / Import button
   - ตรวจสอบไฟล์ก่อน
   - ถ้าผ่านค่อย Import

4. Import result panel
   - จำนวนแถวที่อ่านได้
   - จำนวนแถวที่สร้างใหม่
   - จำนวนแถวที่ Update
   - จำนวนแถวที่ Soft delete ถ้ามี
   - จำนวน Error

5. Pending normalize panel
   - จำนวน Raw Rows ที่ยังไม่ Normalize
   - จำนวน Orders ที่ยังไม่ Normalize
   - จำนวน Error
   - Import file ล่าสุด

6. Normalize button
   - กดแล้ว Normalize ทั้งหมดที่ pending
   - ไม่มีการเลือก limit ต่อรอบ

7. Normalize result panel
   - แสดงผลลัพธ์หลัง Normalize เสร็จ

## Frontend State

State ที่ควรมี:

- `selectedPlatform`
- `selectedFile`
- `isValidating`
- `isUploading`
- `isLoadingPending`
- `isNormalizing`
- `validationResult`
- `importResult`
- `pendingSummary`
- `normalizeResult`
- `errorMessage`

## Long Running Process

เวอร์ชันแรกสามารถทำแบบ Synchronous ได้ก่อน:

- กด Import แล้วรอ API Response
- กด Normalize แล้วรอ API Response

แต่ถ้างานใช้เวลานานมากจน Browser หรือ API Timeout ค่อยเพิ่มระบบ Job ภายหลัง เช่น:

- `ImportJob`
- `JobStatus`
- `StartedOn`
- `FinishedOn`
- `ErrorMessage`
- API สำหรับ Polling สถานะงาน

แนวคิดนี้ยังไม่ต้องทำทันที เพื่อไม่ให้ระบบซับซ้อนเกินความจำเป็นในตอนนี้

## Completion Criteria

งานส่วน Import Data จะถือว่าใช้งานได้เมื่อ:

1. ผู้ใช้เปิดหน้า Import Data ได้จาก Sidebar
2. เลือก Platform ได้
3. เลือกไฟล์ Excel ได้
4. Upload และ Import Raw Data ได้
5. เห็นจำนวนข้อมูลที่ยังไม่ Normalize
6. กด Normalize แล้วระบบประมวลผลทั้งหมดที่ pending ได้
7. เห็น Summary หลัง Normalize เสร็จ
8. แต่ละ Platform ใช้ Logic ของตัวเอง ไม่ปนกันใน Function เดียว

