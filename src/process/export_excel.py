import sys
import unicodedata

import openpyxl as px
import pandas as pd  # 型ヒント記述用
from openpyxl.styles import Border, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows

from src.common.data_process import data_process
from src.common.path_general import FolderPath


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

    processed_path = FolderPath().get_process_data_path()

    for sheet_name, wb in workbooks.items():
        wb.save(processed_path / f"{sheet_name}売上データ.xlsx")
        print(
            f"xlsxファイルの出力が完了しました ファイル名: {sheet_name}売上データ.xlsx"
        )


def main() -> None:
    try:
        processed = data_process()
        workbooks = cell_decoration(processed)
        save_excel(workbooks)
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as e:
        print(f"処理を中断しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"想定外のエラーが発生しました: {e}")
        sys.exit(1)
    finally:
        print("処理を実行しました: export_excel.py")


if __name__ == "__main__":
    main()
