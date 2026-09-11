from pathlib import Path


def get_outputs_path() -> Path:
    """画像フォルダパスの取得"""
    file_path = Path(__file__).resolve().parents[2] / "outputs"

    if not file_path.exists():
        raise FileNotFoundError("outputsフォルダが存在しません")

    full_path = file_path / "plot"

    if not full_path.exists():
        raise FileNotFoundError("plotフォルダが存在しません")

    return full_path
