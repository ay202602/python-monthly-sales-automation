import pandas as pd
import openpyxl as px
from openpyxl.styles import PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "data"


def data_process() -> dict[str, pd.DataFrame]:
    """データを取引先ごとにグルーピング、売り上げを計算"""
    RAW_PATH = "raw"
    RAW_DATA = "monthly_sales_dummy_data.xlsx"

    sheets_dict = pd.read_excel(FILE_PATH / RAW_PATH / RAW_DATA, sheet_name=None)

    # dict[シート名, DataFrame(行・列を含むデータ全体)]
    processed: dict[str, pd.DataFrame] = {}

    for sheet_name, df in sheets_dict.items():
        df["合計金額"] = df["単価"] * df["数量"]
        result = df.groupby(["取引先", "商品名"], as_index=False)["合計金額"].sum()
        processed[sheet_name] = result[["取引先", "商品名", "合計金額"]]  # type: ignore

    return processed


def cell_decoration(processed: dict[str, pd.DataFrame]) -> dict[str, px.Workbook]:
    """加工済みのデータをExcelに装飾"""
    header_fill = PatternFill(
        fill_type="solid", start_color="DDEBF7", end_color="DDEBF7"
    )
    thin = Side(style="thin", color="000000")
    grid_border = Border(left=thin, right=thin, top=thin, bottom=thin)

    workbooks: dict[str, px.Workbook] = {}

    for sheet_name, df in processed.items():
        wb = px.Workbook()
        ws = wb.active
        assert ws is not None
        ws.title = sheet_name

        for row in dataframe_to_rows(df, index=False, header=True):
            ws.append(row)

        for cell in ws[1]:
            cell.fill = header_fill

        for row in ws.iter_rows(
            min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column
        ):
            for cell in row:
                cell.border = grid_border

        workbooks[sheet_name] = wb

    return workbooks


def save_excel(workbooks: dict[str, px.Workbook]) -> None:
    """装飾したExcelファイルを出力"""
    PROCESSED_PATH = FILE_PATH / "processed"

    for sheet_name, wb in workbooks.items():
        wb.save(PROCESSED_PATH / f"{sheet_name}売上データ.xlsx")
        print(
            f"xlsxファイルの出力が完了しました。ファイル名：{sheet_name}売上データ.xlsx"
        )


def main() -> None:
    processed = data_process()
    workbooks = cell_decoration(processed)
    save_excel(workbooks)


if __name__ == "__main__":
    main()
