import sys
import unicodedata
from pathlib import Path

import openpyxl as px
import pandas as pd
from openpyxl.styles import Border, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows

from src.common.columns import CUSTOMER, PRODUCT_NAME, QUANTITY, TOTAL_SALE, UNIT_PRICE


def get_file_path() -> Path:
    """データファイル格納パスを取得"""
    file_path = Path(__file__).resolve().parents[2] / "data"

    if not file_path.exists():
        raise FileNotFoundError("dataフォルダが存在しません。")

    return file_path


def load_excel(raw_path: str, raw_data: str) -> dict[str, pd.DataFrame]:
    """xlsxファイルの取得、パスが不正の場合は異常終了"""
    base_path = get_file_path() / raw_path
    if not base_path.exists():
        raise FileNotFoundError(
            f"指定されたフォルダが存在しません: raw_path= {raw_path}"
        )

    full_path = base_path / raw_data
    if not full_path.exists():
        raise FileNotFoundError(
            f"指定されたファイルが存在しません: raw_data= {raw_data}"
        )

    try:
        df_dict = pd.read_excel(full_path, sheet_name=None)
    except Exception as e:
        raise RuntimeError(f"Excelファイルの読み込みに失敗しました。{full_path}") from e
    else:
        print("Excelファイルの読み込みが完了しました")
        return df_dict


def display_width(text: str) -> int:
    """全角文字は2、半角文字は1としてカウントした表示幅を返す"""
    width = 0
    # east_asian_width()は1文字しか判定できないため、for文で対応
    for ch in text:
        # F(fullwidth), W(Wide)は全角扱い、それ以外は半角扱い
        if unicodedata.east_asian_width(ch) in ("F", "W"):
            width += 2
        else:
            width += 1
    return width


def data_process() -> dict[str, pd.DataFrame]:
    """データを取引先ごとにグルーピング、売り上げを計算"""

    sheets_dict = load_excel(raw_path="raw", raw_data="monthly_sales_dummy_data.xlsx")

    # dict[シート名, DataFrame(行・列を含むデータ全体)]
    processed: dict[str, pd.DataFrame] = {}

    required_columns = [CUSTOMER, PRODUCT_NAME, UNIT_PRICE, QUANTITY]

    for sheet_name, df in sheets_dict.items():
        if df.empty:
            raise ValueError(f"シート{sheet_name}にデータが存在しません")

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(
                f"シート{sheet_name}に必要な列がありません: {missing_columns}"
            )

        df[TOTAL_SALE] = df[UNIT_PRICE] * df[QUANTITY]
        result = df.groupby([CUSTOMER, PRODUCT_NAME], as_index=False)[TOTAL_SALE].sum()
        result = result.sort_values(by=[CUSTOMER, PRODUCT_NAME], ascending=True)  # type: ignore
        processed[sheet_name] = result[[CUSTOMER, PRODUCT_NAME, TOTAL_SALE]]  # type: ignore

    return processed


def cell_decoration(processed: dict[str, pd.DataFrame]) -> dict[str, px.Workbook]:
    """加工済みのデータをExcelに装飾"""
    # DDEBF7 = 薄い青色
    header_fill = PatternFill(
        fill_type="solid", start_color="DDEBF7", end_color="DDEBF7"
    )

    # 格子罫線（黒）
    thin = Side(style="thin", color="000000")
    grid_border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # dict[シート名、ワークブック]
    workbooks: dict[str, px.Workbook] = {}

    # DataFrameをExcelワークシートに転記できるよう変換
    for sheet_name, df in processed.items():
        wb = px.Workbook()
        ws = wb.active
        
        assert ws is not None
        ws.title = sheet_name

        assert ws.oddHeader is not None
        ws.oddHeader.center.text = f"{sheet_name}分売上データ"

        for row in dataframe_to_rows(df, index=False, header=True):
            ws.append(row)

        # ws[1] = セル1行目全体（ヘッダー部分）
        for cell in ws[1]:
            cell.fill = header_fill

        for row in ws.iter_rows(
            min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column
        ):
            for cell in row:
                cell.border = grid_border

        # 数値部分の書式設定を会計に設定（書式設定はExcelから引用）
        accouting_format = '_ ¥* #,##0_ ;_ ¥* -#,##0_ ;_ ¥* "-"_ ;_ @_ '
        for row in ws.iter_rows(
            min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column
        ):
            for cell in row:
                if isinstance(cell.value, (int, float)):
                    cell.number_format = accouting_format

        # セルを1行ずつ走査し、一番長い文字列を基準にセルの幅を調整（余白を2追加）
        for col_idx, col_cells in enumerate(
            ws.iter_cols(min_row=1, max_row=ws.max_row), start=1
        ):
            max_length = 0
            for cell in col_cells:
                # セルの値がない場合はそのままスキップ（次のセルに進む）
                if cell.value is None:
                    continue
                if isinstance(cell.value, (int, float)):
                    display_text = f"{cell.value:,.0f}"
                else:
                    display_text = str(cell.value)
                # 前の文字列の幅と取得した文字列の幅を比較して最大値を取得
                max_length = max(max_length, display_width(display_text))
            # get_column_letterで列名に変換（列幅調整のため）
            ws.column_dimensions[get_column_letter(col_idx)].width = max_length + 2

        workbooks[sheet_name] = wb

    return workbooks


def save_excel(workbooks: dict[str, px.Workbook]) -> None:
    """装飾したExcelファイルを出力"""

    processed_path = get_file_path() / "processed"

    if not processed_path.exists():
        raise FileNotFoundError("processedフォルダが存在しません。")

    for sheet_name, wb in workbooks.items():
        wb.save(processed_path / f"{sheet_name}売上データ.xlsx")
        print(
            f"xlsxファイルの出力が完了しました。ファイル名：{sheet_name}売上データ.xlsx"
        )


def main() -> None:
    try:
        processed = data_process()
        workbooks = cell_decoration(processed)
        save_excel(workbooks)
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as e:
        print(f"処理を中断しました。: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"想定外のエラーが発生しました。: {e}")
        sys.exit(1)
    finally:
        print("処理を実行しました")


if __name__ == "__main__":
    main()
