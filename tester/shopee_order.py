from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass(slots=True)
class ShopeeOrder:
    """Row model for the `Shopee คำสั่งซื้อ` worksheet."""

    # หมายเลขคำสั่งซื้อ
    order_id: str | None = field(default=None, metadata={"source": "หมายเลขคำสั่งซื้อ"})

    # สถานะการสั่งซื้อ
    order_status: str | None = field(default=None, metadata={"source": "สถานะการสั่งซื้อ"})

    # Hot Listing
    hot_listing: str | None = field(default=None, metadata={"source": "Hot Listing"})

    # เหตุผลในการยกเลิกคำสั่งซื้อ
    cancellation_reason: str | None = field(default=None, metadata={"source": "เหตุผลในการยกเลิกคำสั่งซื้อ"})

    # สถานะการคืนเงินหรือคืนสินค้า
    return_refund_status: str | None = field(default=None, metadata={"source": "สถานะการคืนเงินหรือคืนสินค้า"})

    # ชื่อผู้ใช้ (ผู้ซื้อ)
    buyer_username: str | None = field(default=None, metadata={"source": "ชื่อผู้ใช้ (ผู้ซื้อ)"})

    # วันที่ทำการสั่งซื้อ
    order_created_at: str | None = field(default=None, metadata={"source": "วันที่ทำการสั่งซื้อ"})

    # เวลาการชำระสินค้า
    paid_at: str | None = field(default=None, metadata={"source": "เวลาการชำระสินค้า"})

    # ช่องทางการชำระเงิน
    payment_method: str | None = field(default=None, metadata={"source": "ช่องทางการชำระเงิน"})

    # ช่องทางการชำระเงิน (รายละเอียด)
    payment_method_detail: str | None = field(default=None, metadata={"source": "ช่องทางการชำระเงิน (รายละเอียด)"})

    # แผนการผ่อนชำระ
    installment_plan: str | None = field(default=None, metadata={"source": "แผนการผ่อนชำระ"})

    # ค่าธรรมเนียม (%)
    fee_rate: str | None = field(default=None, metadata={"source": "ค่าธรรมเนียม (%)"})

    # ตัวเลือกการจัดส่ง
    shipping_option: str | None = field(default=None, metadata={"source": "ตัวเลือกการจัดส่ง"})

    # วิธีการจัดส่ง
    shipping_method: str | None = field(default=None, metadata={"source": "วิธีการจัดส่ง"})

    # *หมายเลขติดตามพัสดุ
    tracking_number: str | None = field(default=None, metadata={"source": "*หมายเลขติดตามพัสดุ"})

    # วันที่คาดว่าจะทำการจัดส่งสินค้า
    estimated_ship_by: str | None = field(default=None, metadata={"source": "วันที่คาดว่าจะทำการจัดส่งสินค้า"})

    # เวลาส่งสินค้า
    shipped_at: str | None = field(default=None, metadata={"source": "เวลาส่งสินค้า"})

    # เลขอ้างอิง Parent SKU
    parent_sku: str | None = field(default=None, metadata={"source": "เลขอ้างอิง Parent SKU"})

    # ชื่อสินค้า
    product_name: str | None = field(default=None, metadata={"source": "ชื่อสินค้า"})

    # เลขอ้างอิง SKU (SKU Reference No.)
    sku_reference: str | None = field(default=None, metadata={"source": "เลขอ้างอิง SKU (SKU Reference No.)"})

    # ชื่อตัวเลือก
    variation_name: str | None = field(default=None, metadata={"source": "ชื่อตัวเลือก"})

    # ราคาตั้งต้น
    original_price: str | None = field(default=None, metadata={"source": "ราคาตั้งต้น"})

    # ราคาขาย
    sale_price: str | None = field(default=None, metadata={"source": "ราคาขาย"})

    # จำนวน
    quantity: str | None = field(default=None, metadata={"source": "จำนวน"})

    # จำนวนที่ส่งคืน
    returned_quantity: str | None = field(default=None, metadata={"source": "จำนวนที่ส่งคืน"})

    # ราคาขายสุทธิ
    net_sale_price: str | None = field(default=None, metadata={"source": "ราคาขายสุทธิ"})

    # ส่วนลดจาก Shopee
    shopee_discount: str | None = field(default=None, metadata={"source": "ส่วนลดจาก Shopee"})

    # โค้ดส่วนลดชำระโดยผู้ขาย
    seller_voucher_discount: str | None = field(default=None, metadata={"source": "โค้ดส่วนลดชำระโดยผู้ขาย"})

    # โค้ด Coins Cashback ชำระโดยผู้ขาย
    seller_coins_cashback: str | None = field(default=None, metadata={"source": "โค้ด Coins Cashback ชำระโดยผู้ขาย"})

    # โค้ดส่วนลดชำระโดย Shopee (เช่น โค้ดจากโปรแกรม ร้านโค้ดคุ้ม, โค้ดส่วนลด Shopee, โค้ดส่วนลด Shopee Mall)
    shopee_voucher_discount: str | None = field(
        default=None,
        metadata={
            "source": "โค้ดส่วนลดชำระโดย Shopee (เช่น โค้ดจากโปรแกรม ร้านโค้ดคุ้ม, โค้ดส่วนลด Shopee, โค้ดส่วนลด Shopee Mall)"
        },
    )

    # โค้ดส่วนลด
    discount_codes: str | None = field(default=None, metadata={"source": "โค้ดส่วนลด"})

    # เข้าร่วมแคมเปญ bundle deal หรือไม่
    is_bundle_deal: str | None = field(default=None, metadata={"source": "เข้าร่วมแคมเปญ bundle deal หรือไม่"})

    # ส่วนลด bundle deal ชำระโดยผู้ขาย
    seller_bundle_discount: str | None = field(default=None, metadata={"source": "ส่วนลด bundle deal ชำระโดยผู้ขาย"})

    # ส่วนลด bundle deal ชำระโดย Shopee
    shopee_bundle_discount: str | None = field(default=None, metadata={"source": "ส่วนลด bundle deal ชำระโดย Shopee"})

    # ส่วนลดจากการใช้เหรียญ
    coin_discount: str | None = field(default=None, metadata={"source": "ส่วนลดจากการใช้เหรียญ"})

    # โปรโมชั่นช่องทางชำระเงินทั้งหมด
    payment_channel_promotion_discount: str | None = field(default=None, metadata={"source": "โปรโมชั่นช่องทางชำระเงินทั้งหมด"})

    # ส่วนลดเครื่องเก่าแลกใหม่
    trade_in_discount: str | None = field(default=None, metadata={"source": "ส่วนลดเครื่องเก่าแลกใหม่"})

    # โบนัสส่วนลดเครื่องเก่าแลกใหม่
    trade_in_bonus_discount: str | None = field(default=None, metadata={"source": "โบนัสส่วนลดเครื่องเก่าแลกใหม่"})

    # ค่าคอมมิชชั่น
    commission_fee: str | None = field(default=None, metadata={"source": "ค่าคอมมิชชั่น"})

    # Transaction Fee
    transaction_fee: str | None = field(default=None, metadata={"source": "Transaction Fee"})

    # ราคาสินค้าที่ชำระโดยผู้ซื้อ (THB)
    buyer_paid_product_amount_thb: str | None = field(default=None, metadata={"source": "ราคาสินค้าที่ชำระโดยผู้ซื้อ (THB)"})

    # ค่าจัดส่งที่ชำระโดยผู้ซื้อ
    buyer_paid_shipping_fee: str | None = field(default=None, metadata={"source": "ค่าจัดส่งที่ชำระโดยผู้ซื้อ"})

    # ค่าจัดส่งที่ Shopee ออกให้โดยประมาณ
    estimated_shopee_shipping_subsidy: str | None = field(default=None, metadata={"source": "ค่าจัดส่งที่ Shopee ออกให้โดยประมาณ"})

    # ค่าจัดส่งสินค้าคืน
    return_shipping_fee: str | None = field(default=None, metadata={"source": "ค่าจัดส่งสินค้าคืน"})

    # ค่าบริการ
    service_fee: str | None = field(default=None, metadata={"source": "ค่าบริการ"})

    # จำนวนเงินทั้งหมด
    total_amount: str | None = field(default=None, metadata={"source": "จำนวนเงินทั้งหมด"})

    # ค่าจัดส่งโดยประมาณ
    estimated_shipping_fee: str | None = field(default=None, metadata={"source": "ค่าจัดส่งโดยประมาณ"})

    # โบนัสส่วนลดเครื่องเก่าแลกใหม่จากผู้ขาย
    seller_trade_in_bonus_discount: str | None = field(default=None, metadata={"source": "โบนัสส่วนลดเครื่องเก่าแลกใหม่จากผู้ขาย"})

    # ชื่อผู้รับ
    recipient_name: str | None = field(default=None, metadata={"source": "ชื่อผู้รับ"})

    # หมายเลขโทรศัพท์
    recipient_phone: str | None = field(default=None, metadata={"source": "หมายเลขโทรศัพท์"})

    # หมายเหตุจากผู้ซื้อ
    buyer_note: str | None = field(default=None, metadata={"source": "หมายเหตุจากผู้ซื้อ"})

    # ที่อยู่ในการจัดส่ง
    shipping_address: str | None = field(default=None, metadata={"source": "ที่อยู่ในการจัดส่ง"})

    # ประเทศ
    shipping_country: str | None = field(default=None, metadata={"source": "ประเทศ"})

    # จังหวัด
    shipping_province: str | None = field(default=None, metadata={"source": "จังหวัด", "source_index": 54})

    # เขต/อำเภอ
    shipping_district: str | None = field(default=None, metadata={"source": "เขต/อำเภอ", "source_index": 55})

    # รหัสไปรษณีย์
    shipping_postal_code: str | None = field(default=None, metadata={"source": "รหัสไปรษณีย์", "source_index": 56})

    # ประเภทคำสั่งซื้อ
    order_type: str | None = field(default=None, metadata={"source": "ประเภทคำสั่งซื้อ"})

    # เวลาที่ทำการสั่งซื้อสำเร็จ
    completed_at: str | None = field(default=None, metadata={"source": "เวลาที่ทำการสั่งซื้อสำเร็จ"})

    # บันทึก
    seller_note: str | None = field(default=None, metadata={"source": "บันทึก"})

    # ผู้ซื้อร้องขอใบกำกับภาษี
    buyer_requested_tax_invoice: str | None = field(default=None, metadata={"source": "ผู้ซื้อร้องขอใบกำกับภาษี"})

    # ประเภทใบกำกับภาษี
    tax_invoice_type: str | None = field(default=None, metadata={"source": "ประเภทใบกำกับภาษี"})

    # ชื่อ
    tax_invoice_name: str | None = field(default=None, metadata={"source": "ชื่อ"})

    # ประเภทสาขา
    tax_branch_type: str | None = field(default=None, metadata={"source": "ประเภทสาขา"})

    # ชื่อสาขา
    tax_branch_name: str | None = field(default=None, metadata={"source": "ชื่อสาขา"})

    # รหัสประจำสาขา
    tax_branch_code: str | None = field(default=None, metadata={"source": "รหัสประจำสาขา"})

    # ที่อยู่สำหรับออกใบกำกับภาษีแบบเต็มรูป
    tax_full_address: str | None = field(default=None, metadata={"source": "ที่อยู่สำหรับออกใบกำกับภาษีแบบเต็มรูป"})

    # รายละเอียดที่อยู่
    tax_address_detail: str | None = field(default=None, metadata={"source": "รายละเอียดที่อยู่"})

    # แขวง/ตำบล
    tax_subdistrict: str | None = field(default=None, metadata={"source": "แขวง/ตำบล"})

    # เขต/อำเภอ
    tax_district: str | None = field(default=None, metadata={"source": "เขต/อำเภอ", "source_index": 69})

    # จังหวัด
    tax_province: str | None = field(default=None, metadata={"source": "จังหวัด", "source_index": 70})

    # รหัสไปรษณีย์
    tax_postal_code: str | None = field(default=None, metadata={"source": "รหัสไปรษณีย์", "source_index": 71})

    # หมายเลขประจำตัวผู้เสียภาษี
    tax_id: str | None = field(default=None, metadata={"source": "หมายเลขประจำตัวผู้เสียภาษี"})

    # หมายเลขโทรศัพท์สำหรับออกใบกำกับภาษี
    tax_phone: str | None = field(default=None, metadata={"source": "หมายเลขโทรศัพท์สำหรับออกใบกำกับภาษี"})

    # อีเมลสำหรับรับใบกำกับภาษี
    tax_email: str | None = field(default=None, metadata={"source": "อีเมลสำหรับรับใบกำกับภาษี"})

    SOURCE_COLUMNS: ClassVar[tuple[str, ...]] = (
        "หมายเลขคำสั่งซื้อ",
        "สถานะการสั่งซื้อ",
        "Hot Listing",
        "เหตุผลในการยกเลิกคำสั่งซื้อ",
        "สถานะการคืนเงินหรือคืนสินค้า",
        "ชื่อผู้ใช้ (ผู้ซื้อ)",
        "วันที่ทำการสั่งซื้อ",
        "เวลาการชำระสินค้า",
        "ช่องทางการชำระเงิน",
        "ช่องทางการชำระเงิน (รายละเอียด)",
        "แผนการผ่อนชำระ",
        "ค่าธรรมเนียม (%)",
        "ตัวเลือกการจัดส่ง",
        "วิธีการจัดส่ง",
        "*หมายเลขติดตามพัสดุ",
        "วันที่คาดว่าจะทำการจัดส่งสินค้า",
        "เวลาส่งสินค้า",
        "เลขอ้างอิง Parent SKU",
        "ชื่อสินค้า",
        "เลขอ้างอิง SKU (SKU Reference No.)",
        "ชื่อตัวเลือก",
        "ราคาตั้งต้น",
        "ราคาขาย",
        "จำนวน",
        "จำนวนที่ส่งคืน",
        "ราคาขายสุทธิ",
        "ส่วนลดจาก Shopee",
        "โค้ดส่วนลดชำระโดยผู้ขาย",
        "โค้ด Coins Cashback ชำระโดยผู้ขาย",
        "โค้ดส่วนลดชำระโดย Shopee (เช่น โค้ดจากโปรแกรม ร้านโค้ดคุ้ม, โค้ดส่วนลด Shopee, โค้ดส่วนลด Shopee Mall)",
        "โค้ดส่วนลด",
        "เข้าร่วมแคมเปญ bundle deal หรือไม่",
        "ส่วนลด bundle deal ชำระโดยผู้ขาย",
        "ส่วนลด bundle deal ชำระโดย Shopee",
        "ส่วนลดจากการใช้เหรียญ",
        "โปรโมชั่นช่องทางชำระเงินทั้งหมด",
        "ส่วนลดเครื่องเก่าแลกใหม่",
        "โบนัสส่วนลดเครื่องเก่าแลกใหม่",
        "ค่าคอมมิชชั่น",
        "Transaction Fee",
        "ราคาสินค้าที่ชำระโดยผู้ซื้อ (THB)",
        "ค่าจัดส่งที่ชำระโดยผู้ซื้อ",
        "ค่าจัดส่งที่ Shopee ออกให้โดยประมาณ",
        "ค่าจัดส่งสินค้าคืน",
        "ค่าบริการ",
        "จำนวนเงินทั้งหมด",
        "ค่าจัดส่งโดยประมาณ",
        "โบนัสส่วนลดเครื่องเก่าแลกใหม่จากผู้ขาย",
        "ชื่อผู้รับ",
        "หมายเลขโทรศัพท์",
        "หมายเหตุจากผู้ซื้อ",
        "ที่อยู่ในการจัดส่ง",
        "ประเทศ",
        "จังหวัด",
        "เขต/อำเภอ",
        "รหัสไปรษณีย์",
        "ประเภทคำสั่งซื้อ",
        "เวลาที่ทำการสั่งซื้อสำเร็จ",
        "บันทึก",
        "ผู้ซื้อร้องขอใบกำกับภาษี",
        "ประเภทใบกำกับภาษี",
        "ชื่อ",
        "ประเภทสาขา",
        "ชื่อสาขา",
        "รหัสประจำสาขา",
        "ที่อยู่สำหรับออกใบกำกับภาษีแบบเต็มรูป",
        "รายละเอียดที่อยู่",
        "แขวง/ตำบล",
        "เขต/อำเภอ",
        "จังหวัด",
        "รหัสไปรษณีย์",
        "หมายเลขประจำตัวผู้เสียภาษี",
        "หมายเลขโทรศัพท์สำหรับออกใบกำกับภาษี",
        "อีเมลสำหรับรับใบกำกับภาษี",
    )

    @classmethod
    def from_excel_row(cls, row: list[Any] | tuple[Any, ...]) -> "ShopeeOrder":
        """Create an order from a row that follows SOURCE_COLUMNS order."""
        values = list(row) + [None] * (len(cls.SOURCE_COLUMNS) - len(row))
        return cls(
            order_id=values[0],
            order_status=values[1],
            hot_listing=values[2],
            cancellation_reason=values[3],
            return_refund_status=values[4],
            buyer_username=values[5],
            order_created_at=values[6],
            paid_at=values[7],
            payment_method=values[8],
            payment_method_detail=values[9],
            installment_plan=values[10],
            fee_rate=values[11],
            shipping_option=values[12],
            shipping_method=values[13],
            tracking_number=values[14],
            estimated_ship_by=values[15],
            shipped_at=values[16],
            parent_sku=values[17],
            product_name=values[18],
            sku_reference=values[19],
            variation_name=values[20],
            original_price=values[21],
            sale_price=values[22],
            quantity=values[23],
            returned_quantity=values[24],
            net_sale_price=values[25],
            shopee_discount=values[26],
            seller_voucher_discount=values[27],
            seller_coins_cashback=values[28],
            shopee_voucher_discount=values[29],
            discount_codes=values[30],
            is_bundle_deal=values[31],
            seller_bundle_discount=values[32],
            shopee_bundle_discount=values[33],
            coin_discount=values[34],
            payment_channel_promotion_discount=values[35],
            trade_in_discount=values[36],
            trade_in_bonus_discount=values[37],
            commission_fee=values[38],
            transaction_fee=values[39],
            buyer_paid_product_amount_thb=values[40],
            buyer_paid_shipping_fee=values[41],
            estimated_shopee_shipping_subsidy=values[42],
            return_shipping_fee=values[43],
            service_fee=values[44],
            total_amount=values[45],
            estimated_shipping_fee=values[46],
            seller_trade_in_bonus_discount=values[47],
            recipient_name=values[48],
            recipient_phone=values[49],
            buyer_note=values[50],
            shipping_address=values[51],
            shipping_country=values[52],
            shipping_province=values[53],
            shipping_district=values[54],
            shipping_postal_code=values[55],
            order_type=values[56],
            completed_at=values[57],
            seller_note=values[58],
            buyer_requested_tax_invoice=values[59],
            tax_invoice_type=values[60],
            tax_invoice_name=values[61],
            tax_branch_type=values[62],
            tax_branch_name=values[63],
            tax_branch_code=values[64],
            tax_full_address=values[65],
            tax_address_detail=values[66],
            tax_subdistrict=values[67],
            tax_district=values[68],
            tax_province=values[69],
            tax_postal_code=values[70],
            tax_id=values[71],
            tax_phone=values[72],
            tax_email=values[73],
        )
