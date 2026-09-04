import pandas as pd
import openpyxl as px
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "data"


def data_process() -> dict[str, pd.DataFrame]:
    """データを取引先ごとにグルーピング、売り上げを計算"""
    RAW_PATH = "raw"
    RAW_DATA = "monthly_sales_dummy_data.xlsx"


def data_process() -> None:
    """データを取引先ごとにグルーピング、売り上げを計算"""
    sheets_dict = pd.read_excel(FILE_PATH / RAW_PATH / RAW_DATA, sheet_name=None)

    # dict[シート名, DataFrame(行・列を含むデータ全体)]
    processed: dict[str, pd.DataFrame] = {}

    for sheet_name, df in sheets_dict.items():
        df["合計金額"] = df["単価"] * df["数量"]
        result = df.groupby(["取引先", "商品名"], as_index=False)["合計金額"].sum()
        processed[sheet_name] = result[["取引先", "商品名", "合計金額"]]  # type: ignore

    return processed


def cell_decoration() -> None:
    """加工済みのデータをExcelに保存（装飾）"""
    pass


def main() -> None:
    data_process()
    cell_decoration()


if __name__ == "__main__":
    main()
