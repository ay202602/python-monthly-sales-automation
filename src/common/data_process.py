import pandas as pd

from src.common.columns import Columns
from src.common.path_general import FolderPath
def _load_excel(raw_data: str) -> dict[str, pd.DataFrame]:
    """xlsxファイルの取得、パスが不正の場合は異常終了"""
    raw_data_path = FolderPath().get_raw_data_path() / raw_data

    try:
        df_dict = pd.read_excel(raw_data_path, sheet_name=None)
    except Exception as e:
        raise RuntimeError(
            f"Excelファイルの読み込みに失敗しました。{raw_data_path}"
        ) from e
    else:
        print("Excelファイルの読み込みが完了しました")
        return df_dict


def data_process() -> dict[str, pd.DataFrame]:
    """データを取引先ごとにグルーピング、売り上げを計算"""

    sheets_dict = _load_excel(raw_data="monthly_sales_dummy_data.xlsx")

    # dict[シート名, DataFrame(行・列を含むデータ全体)]
    processed: dict[str, pd.DataFrame] = {}

    required_columns = [
        Columns.CUSTOMER,
        Columns.PRODUCT_NAME,
        Columns.UNIT_PRICE,
        Columns.QUANTITY,
    ]

    for sheet_name, df in sheets_dict.items():
        if df.empty:
            raise ValueError(f"シート{sheet_name}にデータが存在しません")

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(
                f"シート{sheet_name}に必要な列がありません: {missing_columns}"
            )

        df[Columns.TOTAL_SALE] = df[Columns.UNIT_PRICE] * df[Columns.QUANTITY]
        result = df.groupby([Columns.CUSTOMER, Columns.PRODUCT_NAME], as_index=False)[
            Columns.TOTAL_SALE
        ].sum()
        result = result.sort_values(by=[Columns.CUSTOMER, Columns.PRODUCT_NAME], ascending=True)  # type: ignore
        processed[sheet_name] = result[[Columns.CUSTOMER, Columns.PRODUCT_NAME, Columns.TOTAL_SALE]]  # type: ignore

    return processed
