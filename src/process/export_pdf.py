from pathlib import Path
from openpyxl.drawing.image import Image as XLImage
def get_outputs_path() -> Path:
    outputs_path = Path(__file__).resolve().parents[2] / "outputs"

    if not outputs_path.exists():
        raise FileNotFoundError("outputsフォルダが存在しません")

    pdf_path = outputs_path / "pdf"

    if not pdf_path.exists():
        raise FileNotFoundError("pdfフォルダが存在しません")

    return pdf_path
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


