from enum import StrEnum


class Columns(StrEnum):
    CUSTOMER = "取引先"
    PRODUCT_NAME = "商品名"
    TOTAL_SALE = "合計金額"
    UNIT_PRICE = "単価"
    QUANTITY = "数量"
    OTHERS = "その他"
