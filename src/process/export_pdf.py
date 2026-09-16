from pathlib import Path

import openpyxl as px
import win32com.client.gencache as win32
from openpyxl.drawing.image import Image as XLImage
from openpyxl.worksheet.worksheet import Worksheet  # 型ヒント記述用

from src.common.plot_path import get_outputs_path


# TODO: リファクタリング時に削除（パス指定専用pyファイルにてまとめる）
def get_pdf_path() -> Path:
    outputs_path = Path(__file__).resolve().parents[2] / "outputs"

    if not outputs_path.exists():
        raise FileNotFoundError("outputsフォルダが存在しません")

    pdf_path = outputs_path / "pdf"

    if not pdf_path.exists():
        raise FileNotFoundError("pdfフォルダが存在しません")

    return pdf_path


# TODO: リファクタリング時に削除（パス指定専用pyファイルにてまとめる）
def get_excel_path() -> list[Path]:
    """加工済みExcelファイルのパス取得（複数対応可能）"""
    data_path = Path(__file__).resolve().parents[2] / "data"

    if not data_path.exists():
        raise FileNotFoundError("dataフォルダが存在しません")

    process_path = data_path / "processed"

    if not process_path.exists():
        raise FileNotFoundError("processedフォルダが存在しません")

    process_excel_path = list(process_path.glob("*.xlsx"))

    if not process_excel_path:
        raise FileNotFoundError("加工済みExcelファイルが見つかりません")

    return process_excel_path


def resize_image(img: XLImage, target_width: int) -> None:
    """画像の縦横比を保ったまま幅を基準にリサイズ"""
    ratio = target_width / img.width
    img.width = target_width
    img.height = int(img.height * ratio)


def set_print_setup(ws: Worksheet) -> None:
    """印刷設定（A4・縦向き・余白・1ページ納め）を統一"""
    # A4・縦向き・余白設定
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT
    ws.page_margins.top = 1.0
    ws.page_margins.bottom = 1.0
    ws.page_margins.right = 0.75
    ws.page_margins.left = 0.75

    assert ws.sheet_properties.pageSetUpPr is not None
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    # 横は1ページに納める、縦の場合は1ページを超える場合は次のページで表示
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0  # 0 = 高さ制限なし

    ws.print_options.horizontalCentered = True


def plot_png_paste():
    """加工済みExcelファイル内にグラフ結果pngファイルを添付"""
    excel_paths = get_excel_path()

    pie_plot_path = get_outputs_path() / "pie_plot"
    bar_plot_path = get_outputs_path() / "bar_plot"

    # A4印刷可能領域に合わせた画像幅（px、余白19mm・96dpi換算の目安）
    IMAGE_WIDTH = 650

    for excel_path in excel_paths:
        wb = px.load_workbook(excel_path)

        # 既存シート名を基準にpngファイル名を組み立て
        data_ws = wb.worksheets[0]
        sheet_name = data_ws.title
        set_print_setup(data_ws)

        pie_png_path = pie_plot_path / f"{sheet_name}売上円グラフ.png"
        bar_png_path = bar_plot_path / f"{sheet_name}売上棒グラフ.png"

        if not pie_png_path.exists():
            raise FileNotFoundError(f"円グラフpngが見つかりません：{pie_png_path}")
        if not bar_png_path.exists():
            raise FileNotFoundError(f"棒グラフpngが見つかりません：{bar_png_path}")

        # グラフ貼り付け用の新規ワークシート追加
        ws = wb.create_sheet("グラフ")
        set_print_setup(ws)
        
        pie_img = XLImage(str(pie_png_path))
        resize_image(pie_img, IMAGE_WIDTH)

        bar_img = XLImage(str(bar_png_path))
        resize_image(bar_img, IMAGE_WIDTH)

        ws.add_image(pie_img, "A1")
        ws.add_image(bar_img, "A30")

        wb.save(excel_path)
        print(f"pngファイルを添付しました：{excel_path.name}")


def create_pdf() -> None:
    """加工済ExcelファイルをPDFとして出力"""
    excel_paths = get_excel_path()
    pdf_dir = get_pdf_path()

    excel = win32.EnsureDispatch("Excel.Application")
    excel.Visible = False

    try:
        for excel_path in excel_paths:
            wb = excel.Workbooks.Open(str(excel_path))
            try:
                wb.Worksheets.Select()  # 全シート選択
                pdf_path = pdf_dir / f"{excel_path.stem}.pdf"
                wb.ActiveSheet.ExportAsFixedFormat(0, str(pdf_path))
                print(f"PDF出力しました：{pdf_path.name}")
            finally:
                wb.Close(SaveChanges=False)
    finally:
        excel.Quit()


def main() -> None:
    plot_png_paste()
    create_pdf()


if __name__ == "__main__":
    main()
