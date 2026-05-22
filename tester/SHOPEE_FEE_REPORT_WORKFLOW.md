# Shopee Fee Report Workflow

## บริบทของโปรเจกต์

งานนี้เริ่มจากการทำความเข้าใจ raw data ของ Shopee ที่ export มาในไฟล์ Excel ซึ่งอ่านยาก เพราะข้อมูล 1 คำสั่งซื้ออาจถูกแยกเป็นหลายแถวตามจำนวนสินค้าใน order นั้น

เป้าหมายระยะยาวคือทำให้ workflow นี้กลายเป็นโปรแกรมที่รันซ้ำได้ เวลาได้ raw data รอบใหม่ จะสามารถสร้างไฟล์ cleaned report แบบเดิมได้โดยไม่ต้องจัดมือใน Excel ใหม่ทุกครั้ง

ตอนนี้เราแบ่งงานเป็น 2 ชั้นหลัก:

1. Reformat raw data ให้กลายเป็นข้อมูลระดับ order ที่อ่านง่าย
2. เพิ่มโมดูลวิเคราะห์ fee แต่ละประเภท เช่น Commission Fee, Transaction Fee และ fee อื่นในอนาคต

## เป้าหมาย

แปลง raw data จากไฟล์ `Commission_MML.xlsx` ชีต `Shopee คำสั่งซื้อ` ให้เป็นรายงาน Excel ระดับคำสั่งซื้อที่อ่านง่าย และสรุปสถิติของ fee แต่ละประเภท

Output หลักตอนนี้คือ:

```text
Shopee_Fee_Report.xlsx
```

แนวคิดสำคัญคือ output workbook หนึ่งไฟล์จะมีหลาย sheet:

- `Summary` สำหรับสรุปภาพรวมทุก fee
- `Commission Fee` สำหรับวิเคราะห์ค่าคอมมิชชั่น
- `Transaction Fee` สำหรับวิเคราะห์ Transaction Fee
- sheet อื่น ๆ ที่อาจเพิ่มในอนาคต เช่น Service Fee

## โครงสร้างโมดูล

- `main.py`
  - เป็น entry point
  - กำหนด path ของ raw workbook และ output workbook
  - อ่าน raw data ครั้งเดียว
  - group/clean order ครั้งเดียว
  - เรียกโมดูล fee แต่ละตัวให้สร้าง sheet ลง workbook เดียวกัน

- `shopee_order.py`
  - เก็บ `ShopeeOrder` dataclass
  - map field ภาษาอังกฤษกลับไปยัง header ภาษาไทยเดิม

- `shopee_order_reader.py`
  - อ่านชีต `Shopee คำสั่งซื้อ`
  - แปลงแต่ละ raw row เป็น `ShopeeOrder`

- `shopee_report_common.py`
  - utility กลางสำหรับ report
  - แปลงตัวเลข
  - กรอง order
  - group ด้วย `order_id`
  - คำนวณ summary `count/min/mean/std/max`
  - สร้าง summary sheet
  - จัด style ตาราง Excel

- `build_shopee_commission_report.py`
  - โมดูลสำหรับสร้าง sheet `Commission Fee`
  - คำนวณ `% commission`

- `build_shopee_transaction_fee_report.py`
  - โมดูลสำหรับสร้าง sheet `Transaction Fee`
  - คำนวณ `% transaction fee`

- `build_shopee_service_fee_report.py`
  - โมดูลสำหรับสร้าง sheet `Service Fee`
  - คำนวณ `% service fee`

หลักการออกแบบตอนนี้คือ `main.py` เป็น orchestrator และโมดูล fee แต่ละไฟล์มีหน้าที่เฉพาะของตัวเอง ไม่ให้โมดูลย่อยไปกำหนด path ไฟล์เอง

## Path อยู่ที่ไหน

ไม่ hardcode path ของไฟล์ raw MML ในโมดูล fee แล้ว

ให้กำหนดใน `main.py`:

```python
RAW_WORKBOOK_PATH = Path(r"C:\Education\PlatformSale\Commission_MML.xlsx")
OUTPUT_WORKBOOK_PATH = Path(r"C:\Education\PlatformSale\Shopee_Fee_Report.xlsx")
```

ถ้าจะเปลี่ยนไฟล์ต้นทางหรือไฟล์ output ให้เปลี่ยนที่ `main.py` จุดเดียว

## Data Flow ปัจจุบัน

```text
Commission_MML.xlsx
  -> shopee_order_reader.py
  -> list[ShopeeOrder]
  -> shopee_report_common.group_active_orders()
  -> grouped_orders: order_id -> list[ShopeeOrder]
  -> build_shopee_commission_report.add_commission_fee_sheet()
  -> build_shopee_transaction_fee_report.add_transaction_fee_sheet()
  -> build_shopee_service_fee_report.add_service_fee_sheet()
  -> shopee_report_common.add_summary_sheet()
  -> Shopee_Fee_Report.xlsx
```

## หลักการ Clean Data

Raw data ของ Shopee มี 1 คำสั่งซื้อที่อาจแตกออกเป็นหลาย item rows ได้ เช่น 1 order มีสินค้า 3 รายการ

ดังนั้นค่าต่อไปนี้ต้องมองเป็นระดับ order ไม่ใช่ระดับสินค้า:

- `commission_fee`
- `transaction_fee`
- `service_fee`
- `buyer_paid_product_amount_thb`
- `buyer_paid_shipping_fee`
- `return_shipping_fee`
- `total_amount`

Workflow จึงต้อง group ด้วย:

```text
order_id
```

หลัง clean แล้ว:

```text
1 row = 1 order_id
```

## เงื่อนไขการกรอง

ไม่นำคำสั่งซื้อต่อไปนี้มาคิด:

```python
order_status == "ยกเลิกแล้ว"
returned_quantity > 0
```

เหตุผลของ `returned_quantity > 0` คือเราเจอเคส order ที่สถานะสำเร็จแล้ว แต่มีการคืนสินค้า เช่น order `260505HU455M10` ซึ่งมี `returned_quantity = 1` และ `total_amount = 0.00` ดังนั้นไม่ควรนำมาวิเคราะห์ fee ของยอดขายจริง

## สูตรคำนวณ

### Commission Fee

ใช้ราคาตั้งต้นรวมของสินค้าใน order เป็นฐาน:

```python
commission_percent = commission_fee / sum(original_price * quantity)
```

เหตุผล:

- `commission_fee` เป็นค่าระดับ order
- `original_price` เป็นค่าระดับ item
- 1 order อาจมีหลายสินค้า จึงต้องรวมราคาตั้งต้นทุก item ก่อน

### Transaction Fee

ใช้ยอดสินค้าที่ผู้ซื้อชำระจริงเป็นฐาน:

```python
transaction_percent = transaction_fee / buyer_paid_product_amount_thb
```

เหตุผล:

- `transaction_fee` เป็นค่าระดับ order
- `buyer_paid_product_amount_thb` เป็นยอดสินค้า net ที่ผู้ซื้อจ่ายจริงใน order นั้น
- ถ้าภายหลังต้องเปลี่ยนฐานคำนวณ ให้แก้ที่ `build_shopee_transaction_fee_report.py`

### Service Fee

ใช้ราคาตั้งต้นรวมของสินค้าใน order เป็นฐาน:

```python
service_percent = service_fee / sum(original_price * quantity)
```

เหตุผล:

- `service_fee` เป็นค่าระดับ order
- ใช้ฐานเดียวกับ Commission Fee เพื่อไม่ให้ order ที่ถูกส่วนลดหนักทำให้เปอร์เซ็นต์ service fee สูงผิดธรรมชาติ
- `original_price` เป็นค่าระดับ item จึงต้องรวมทุก item ใน order ก่อน
- ถ้าภายหลังต้องเปลี่ยนฐานคำนวณ ให้แก้ที่ `build_shopee_service_fee_report.py`

## โครงสร้างไฟล์ Excel Output

ไฟล์ `Shopee_Fee_Report.xlsx` มี 4 sheets:

### Summary

รวมสถิติของทุก fee sheet:

- count
- min
- mean
- std
- max
- bucket แบบปัดเป็นเปอร์เซ็นต์เต็ม เช่น `9%`, `10%`, `11%`

### Commission Fee

ข้อมูลระดับคำสั่งซื้อสำหรับค่าคอมมิชชั่น

### Transaction Fee

ข้อมูลระดับคำสั่งซื้อสำหรับ Transaction Fee

### Service Fee

ข้อมูลระดับคำสั่งซื้อสำหรับ Service Fee

## หลักการของ Summary Sheet

`Summary` จะรวมผลสถิติจากทุก fee module ที่ถูกเรียกใน `main.py`

แต่ละ fee จะมี:

- `count`: จำนวน order ที่ใช้คำนวณ
- `min`: ค่าเปอร์เซ็นต์ต่ำสุด
- `mean`: ค่าเฉลี่ย
- `std`: standard deviation
- `max`: ค่าเปอร์เซ็นต์สูงสุด
- rounded bucket: จำนวน order ตามเปอร์เซ็นต์ที่ปัดเป็นเลขเต็ม

ทุกค่าใน summary ควรมาจากข้อมูลหลัง clean แล้วเท่านั้น ไม่ใช้ raw item rows ตรง ๆ

## วิธีรัน

จากโฟลเดอร์โปรเจกต์:

```powershell
python main.py
```

ถ้าเครื่องไม่มี `python` ใน PATH ให้ใช้ Python จาก environment ที่มีอยู่แทน

สิ่งที่ `main.py` ทำ:

1. อ่าน raw data จาก `RAW_WORKBOOK_PATH`
2. clean และ group เป็น order-level
3. สร้าง workbook ใหม่
4. เรียกโมดูล `Commission Fee`
5. เรียกโมดูล `Transaction Fee`
6. เรียกโมดูล `Service Fee`
7. สร้าง sheet `Summary`
8. save เป็น `OUTPUT_WORKBOOK_PATH`
9. print summary ใน terminal

ถ้าไฟล์ output เปิดอยู่ใน Excel แล้ว save ทับไม่ได้ `main.py` จะ fallback ไปบันทึกเป็น:

```text
Shopee_Fee_Report_new.xlsx
```

## วิธีคิดเวลาเพิ่มโมดูลใหม่

โมดูลใหม่ควรรับ `wb` และ `grouped_orders` เหมือนโมดูลเดิม:

```python
add_some_fee_sheet(wb, grouped_orders)
```

โมดูลควรคืนค่า `FeeSheetResult` เพื่อให้ `main.py` ส่งต่อให้ `add_summary_sheet()` ได้:

```python
FeeSheetResult(sheet_name, row_count, summary)
```

สิ่งที่โมดูล fee ใหม่ต้องกำหนดเอง:

- ชื่อ sheet
- columns ที่ต้องการแสดง
- สูตรคำนวณ percent
- ฐานที่ใช้หาร
- field เงินที่ต้อง format เป็นตัวเลข

สิ่งที่ควรใช้จาก `shopee_report_common.py`:

- `to_float()`
- `calculate_fee_summary()`
- `style_report_sheet()`

## ผลลัพธ์ล่าสุด

หลังกรอง order ยกเลิกและ order คืนสินค้า:

```text
raw item rows = 1500
active order count = 1094
```

Commission Fee:

```text
count = 1094 orders
min = 4.78%
mean = 9.45%
std = 1.11%
max = 11.27%
```

Transaction Fee:

```text
count = 1094 orders
min = 3.19%
mean = 5.22%
std = 1.64%
max = 13.25%
```

Service Fee:

```text
count = 1094 orders
min = 3.62%
mean = 9.89%
std = 2.30%
max = 14.98%
```

## การเพิ่มโมดูล fee ใหม่ในอนาคต

สร้างไฟล์ใหม่ เช่น:

```text
build_shopee_new_fee_report.py
```

ให้โมดูลนั้นมี function ลักษณะเดียวกัน:

```python
add_new_fee_sheet(wb, grouped_orders)
```

แล้วเพิ่มใน `main.py`:

```python
new_fee_result = add_new_fee_sheet(wb, grouped_orders)
sheet_results = [commission_result, transaction_result, service_result, new_fee_result]
```

## หมายเหตุสำคัญสำหรับการกลับมาทำต่อ

ถ้ารอบหน้าเริ่มสับสน ให้กลับมาเช็กตามลำดับนี้:

1. raw data มีจำนวนกี่แถว
2. หลัง group ด้วย `order_id` เหลือกี่ order
3. หลังกรอง `ยกเลิกแล้ว` และ `returned_quantity > 0` เหลือกี่ order
4. fee ที่กำลังวิเคราะห์เป็นระดับ order หรือ item
5. ฐานที่ใช้หารควรเป็น field ไหน
6. summary ควรคำนวณจาก order-level rows เท่านั้น

สำหรับ workflow ปัจจุบัน จำนวน order หลัง clean ควรอยู่ที่:

```text
active order count = 1094
```
