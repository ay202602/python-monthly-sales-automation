import math
import sys

import openpyxl as px
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter

from src.common.path_general import FolderPath

# 貼り付け時の画像幅（px）。棒グラフは取引先名・数値ラベルが読みやすいよう大きめにする
PIE_IMAGE_WIDTH = 600
BAR_IMAGE_WIDTH = 900

COLUMN_GAP = 2  # 集計データと画像の間にあける列数
ROW_GAP = 4  # 画像同士の間にあける行数

# Excel標準の行の高さ（15pt = 20px)。画像が占める行数の算出に使用
ROW_HEIGHT_PX = 20


def _resize_image(img: XLImage, target_width: int) -> None:
    """画像の縦横比を保ったまま幅を基準にリサイズ"""
    ratio = target_width / img.width
    img.width = target_width
    img.height = int(img.height * ratio)


def plot_png_paste():
    """加工済みExcelファイル内にグラフ結果pngファイルを添付"""
    folder_path = FolderPath()

    excel_paths = folder_path.get_excel_path()

    pie_plot_path = folder_path.get_plot_path("pie_plot")
    bar_plot_path = folder_path.get_plot_path("bar_plot")

    for excel_path in excel_paths:
        wb = px.load_workbook(excel_path)
        ws = wb.worksheets[0]

        # 既存シート名を基準にpngファイル名を組み立て
        sheet_name = ws.title

        pie_png_path = pie_plot_path / f"{sheet_name}売上円グラフ.png"
        bar_png_path = bar_plot_path / f"{sheet_name}売上棒グラフ.png"

        if not pie_png_path.exists():
            raise FileNotFoundError(f"円グラフpngが見つかりません: {pie_png_path}")
        if not bar_png_path.exists():
            raise FileNotFoundError(f"棒グラフpngが見つかりません: {bar_png_path}")

        pie_img = XLImage(str(pie_png_path))
        _resize_image(img=pie_img, target_width=PIE_IMAGE_WIDTH)

        bar_img = XLImage(str(bar_png_path))
        _resize_image(img=bar_img, target_width=BAR_IMAGE_WIDTH)

        # 集計データの最終列の右隣（空きCOLUMN_GAP）を貼り付け開始列にする
        anchor_col = get_column_letter(ws.max_column + COLUMN_GAP)

        # 円グラフが占める行数を求め、その下に棒グラフを配置（小数切り上げ）
        pie_rows = math.ceil(pie_img.height / ROW_HEIGHT_PX)
        bar_row = 1 + pie_rows + ROW_GAP

        # 再実行時に画像が重複しないよう既存画像をクリア
        ws._images.clear()  # type: ignore[attr-defined]

        ws.add_image(pie_img, f"{anchor_col}1")
        ws.add_image(bar_img, f"{anchor_col}{bar_row}")

        wb.save(excel_path)
        print(f"pngファイルを添付しました: {excel_path.name}")


def main() -> None:
    try:
        plot_png_paste()
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as e:
        print(f"処理を中断しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"想定外のエラーが発生しました: {e}")
        sys.exit(1)
    finally:
        print("処理を実行しました: paste_plot.py")


if __name__ == "__main__":
    main()
