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
            f"Excelファイルの読み込みに失敗しました: {raw_data_path}"
        ) from e
    else:
        print("Excelファイルの読み込みが完了しました")
        return df_dict


def data_process() -> dict[str, pd.DataFrame]:
    """データを取引先ごとにグルーピング、売り上げを計算"""
    raw_data = "monthly_sales_dummy_data.xlsx"

    try:
        sheets_dict = _load_excel(raw_data=raw_data)
    except RuntimeError:
        print(f"{raw_data}が存在しません")
        raise

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


def bar_plot_data_process() -> dict[str, pd.DataFrame]:
    """棒グラフ用データ整形：取引先ごとに売り上げを集計"""
    processed = data_process()
    bar_result: dict[str, pd.DataFrame] = {}

    # 取引先のみグルーピング、並び替え（data_process側の仕様とは異なる）
    for sheet_name, df in processed.items():
        plot_df = df.groupby(Columns.CUSTOMER, as_index=False)[
            [Columns.TOTAL_SALE]
        ].sum()
        plot_df = plot_df.sort_values(by=Columns.CUSTOMER, ascending=False)
        bar_result[sheet_name] = plot_df
    
    return bar_result


def pie_plot_data_process() -> dict[str, pd.DataFrame]:
    """円グラフ用データ整形：データが一定の数字以下の場合はその他のデータとしてまとめる"""
    processed = data_process()

    THRESHOLD = 0.06

    # dict[シート名, DataFrame]
    result: dict[str, pd.DataFrame] = {}

    for sheet_name, df in processed.items():
        df_grouped = df.groupby(Columns.PRODUCT_NAME, as_index=False)[
            Columns.TOTAL_SALE
        ].sum()
        df_grouped = df_grouped.sort_values(by=Columns.TOTAL_SALE, ascending=False)  # type: ignore

        total = df_grouped[Columns.TOTAL_SALE].sum()

        if total == 0:
            raise ValueError(f"{sheet_name}の合計金額が0のため、比率を計算できません")

        ratio = df_grouped[Columns.TOTAL_SALE] / total

        # large = 閾値（しきいち）以上の割合の値
        large = df_grouped[ratio >= THRESHOLD]

        # small = 閾値（しきいち）未満の割合の値
        small = df_grouped[ratio < THRESHOLD]

        # small内のdfに1件、行がある場合「その他」のdfを作って結合
        if not small.empty:
            other_row = pd.DataFrame(
                {
                    Columns.PRODUCT_NAME: [Columns.OTHERS],
                    Columns.TOTAL_SALE: [small[Columns.TOTAL_SALE].sum()],
                }
            )
            df_grouped = pd.concat([large, other_row], ignore_index=True)
        else:
            df_grouped = large

        result[sheet_name] = df_grouped

    return result
