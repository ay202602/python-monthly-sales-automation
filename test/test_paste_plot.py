import openpyxl as px
import pytest
from openpyxl.drawing.image import Image as XLImage
from openpyxl.worksheet.worksheet import Worksheet
from PIL import Image as PILImage

import src.process.paste_plot as paste_plot


def _make_png(path, width=1000, height=500):
    """テスト用のダミーpng画像を生成"""
    PILImage.new("RGB", (width, height), color="white").save(path)


# ----- _resize_image -----


def test_resize_image_keeps_aspect_ratio_and_sets_target_width(tmp_path):
    """縦横比を保ったまま幅がtarget_widthにリサイズされること"""
    png_path = tmp_path / "sample.png"
    _make_png(png_path, width=1000, height=500)  # 縦横比 1:0.5

    img = XLImage(str(png_path))
    original_ratio = img.height / img.width

    paste_plot._resize_image(img, target_width=650)

    # A4印刷可能領域に合わせた画像幅であること
    assert img.width == 650

    # 画像の高さがリサイズ前の縦横比×新しい幅(650)と一致していること
    assert img.height == pytest.approx(650 * original_ratio, abs=1)


# ----- plot_png_paste -----


class FakeFolderPath:
    """FolderPahtの代替として、テスト用の一時フォルダを返す"""

    def __init__(self, excel_paths, pie_dir: str, bar_dir: str):
        self._excel_paths = excel_paths
        self._pie_dir = pie_dir
        self._bar_dir = bar_dir

    def get_excel_path(self):
        return self._excel_paths

    def get_plot_path(self, plot_type):
        return self._pie_dir if plot_type == "pie_plot" else self._bar_dir


@pytest.fixture
def excel_path_with_plots(tmp_path, monkeypatch):
    """加工済みExcelファイルとダミーpng画像を用意し、FolderPathを差し替える"""
    # tmp_path = pytest用の仮ディレクトリ
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()

    pie_dir = tmp_path / "pie_plot"
    pie_dir.mkdir()

    bar_dir = tmp_path / "bar_plot"
    bar_dir.mkdir()

    excel_path = processed_dir / "Sheet1.xlsx"

    wb = px.Workbook()
    ws = wb.active

    # Pylance対策: None出ないことを保証する
    assert ws is not None

    ws.title = "Sheet1"
    ws.append(["取引先", "商品名", "合計金額"])  # 3列 → 画像はE列から貼られる想定
    wb.save(excel_path)

    _make_png(pie_dir / "Sheet1売上円グラフ.png")
    _make_png(bar_dir / "Sheet1売上棒グラフ.png")

    # paste_plot.py内のFolderPathクラスを差し替え（元のpath_general.pyではない）
    monkeypatch.setattr(
        paste_plot,
        "FolderPath",
        lambda: FakeFolderPath(
            # 複数Excelファイルを扱う処理にしているため、excel_pathsをリストとして渡す
            excel_paths=[excel_path],
            pie_dir=pie_dir,
            bar_dir=bar_dir,
        ),
    )

    return excel_path


def test_plot_png_paste_attaches_images_to_data_sheet(excel_path_with_plots):
    """円グラフ・棒グラフpngが集計シートに添付されていること"""
    paste_plot.plot_png_paste()

    wb = px.load_workbook(excel_path_with_plots)

    # グラフ専用シートは作成されず、集計シートのみであること
    assert wb.sheetnames == ["Sheet1"]
    ws = wb["Sheet1"]

    # Pylance対策: wsのインスタンスがWorksheetであることを保証する
    assert isinstance(ws, Worksheet)

    # 画像が2枚（円グラフ・棒グラフ）が添付されていること
    assert len(ws._images) == 2  # type: ignore[attr-defined]


def test_plot_png_paste_images_placed_beside_data_columns(excel_path_with_plots):
    """画像が集計データ（A〜C列）の右隣 = E列から、重ならず縦に並んで配置されていること"""
    paste_plot.plot_png_paste()

    wb = px.load_workbook(excel_path_with_plots)
    ws = wb["Sheet1"]

    # Pylance対策: wsのインスタンスがWorksheetであることを保証する
    assert isinstance(ws, Worksheet)

    # アンカー行番号は0始まりのため、E列 = 4, 1行目 = 0
    anchors = sorted((img.anchor._from.row, img.anchor._from.col) for img in ws._images)  # type: ignore[attr-defined]

    # 全画像が集計データの右隣（E列）から配置されていること
    assert all(col == 4 for _, col in anchors)

    # 円グラフが1行目、棒グラフがその下に配置されていること
    # 1つ目の[0] = 何番目の画像か   2つ目の[0] = タプルのどの値か
    assert anchors[0][0] == 0  # 円グラフ: 1行目から配置
    assert anchors[1][0] > 0  # 棒グラフ:　円グラフより下の行に配置


def test_plot_png_paste_does_not_duplicate_images_on_rerun(excel_path_with_plots):
    """2回実行しても画像が重複して増えないこと"""
    paste_plot.plot_png_paste()
    paste_plot.plot_png_paste()

    wb = px.load_workbook(excel_path_with_plots)
    ws = wb["Sheet1"]

    # Pylance対策: wsのインスタンスがWorksheetであることを保証する
    assert isinstance(ws, Worksheet)

    assert len(ws._images) == 2  # type: ignore[attr-defined]


def test_plot_png_paste_raises_when_pie_png_missing(tmp_path, monkeypatch):
    """円グラフpngが存在しない場合にFileNotFoundErrorが送出されること"""
    # tmp_path = pytest用の仮ディレクトリ
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()

    pie_dir = tmp_path / "pie_plot"
    pie_dir.mkdir()

    bar_dir = tmp_path / "bar_plot"
    bar_dir.mkdir()

    excel_path = processed_dir / "Sheet1.xlsx"

    wb = px.Workbook()
    ws = wb.active

    # Pylance対策: Noneではないことを保証する
    assert ws is not None

    ws.title = "Sheet1"
    wb.save(excel_path)

    # 棒グラフpngのみ用意し、円グラフpngは用意しない
    _make_png(bar_dir / "Sheet1売上棒グラフ.png")

    # paste_plot.py内のFolderPathクラスを差し替え（元のpath_general.pyではない）
    monkeypatch.setattr(
        paste_plot,
        "FolderPath",
        lambda: FakeFolderPath(
            # 複数Excelファイルを扱う処理にしているため、excel_pathsをリストとして渡す
            excel_paths=[excel_path],
            pie_dir=pie_dir,
            bar_dir=bar_dir,
        ),
    )

    with pytest.raises(FileNotFoundError, match="円グラフpng"):
        paste_plot.plot_png_paste()


def test_plot_png_paste_raises_when_bar_png_missing(tmp_path, monkeypatch):
    """棒グラフpngが存在しない場合にFileNotFoundErrorが送出されること"""
    # tmp_path = pytest用の仮ディレクトリ
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()

    pie_dir = tmp_path / "pie_plot"
    pie_dir.mkdir()

    bar_dir = tmp_path / "bar_plot"
    bar_dir.mkdir()

    excel_path = processed_dir / "Sheet1.xlsx"

    wb = px.Workbook()
    ws = wb.active

    # Pylance対策: Noneではないことを保証する
    assert ws is not None

    ws.title = "Sheet1"
    wb.save(excel_path)

    # 円グラフpngのみ用意し、棒グラフpngは用意しない
    _make_png(pie_dir / "Sheet1売上円グラフ.png")

    # paste_plot.py内のFolderPathクラスを差し替え（元のpath_general.pyではない）
    monkeypatch.setattr(
        paste_plot,
        "FolderPath",
        lambda: FakeFolderPath(
            # 複数Excelファイルを扱う処理にしているため、excel_pathsをリストとして渡す
            excel_paths=[excel_path],
            pie_dir=pie_dir,
            bar_dir=bar_dir,
        ),
    )

    with pytest.raises(FileNotFoundError, match="棒グラフpng"):
        paste_plot.plot_png_paste()
