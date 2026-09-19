from pathlib import Path

# TODO: 処理完了後にprint文でログを残す設計を行う（どの関数が実行されたか分かるように設計）
class FolderPath:
    def __init__(self) -> None:
        self._folder_path = Path(__file__).resolve().parents[2]

    def get_data_path(self, data_folder: str = "data") -> Path:
        """データ関連フォルダパスの取得（存在しない場合場合は新規作成）"""
        data_path = self._folder_path / data_folder

        if not data_path.exists():
            data_path.mkdir(parents=False, exist_ok=True)

        return data_path

    def get_raw_data_path(self, raw_data_folder: str = "raw") -> Path:
        """加工前データフォルダパスを取得（存在しない場合ば新規作成）"""
        # dataフォルダの存在を保証してから取得
        raw_data_path = self.get_data_path() / raw_data_folder

        if not raw_data_path.exists():
            raw_data_path.mkdir(parents=False, exist_ok=True)

        return raw_data_path

    def get_process_data_path(self, processed_data_folder: str = "processed") -> Path:
        """加工済データパスの取得（存在しない場合は新規作成）"""
        # dataフォルダの存在を保証してから取得
        processed_data_path = self.get_data_path() / processed_data_folder

        if not processed_data_path.exists():
            processed_data_path.mkdir(parents=False, exist_ok=True)

        return processed_data_path

    def get_excel_path(self) -> list[Path]:
        """加工済みExcelファイルのパス取得（複数対応可能）"""
        process_excel_path = list(self.get_process_data_path().glob("*.xlsx"))

        if not process_excel_path:
            raise FileNotFoundError("加工済みExcelファイルが見つかりません")

        return process_excel_path

    def get_outputs_path(self, outputs_folder: str = "outputs") -> Path:
        """出力フォルダパスの取得（存在しない場合は新規作成）"""
        outputs_path = self._folder_path / outputs_folder

        if not outputs_path.exists():
            outputs_path.mkdir(parents=False, exist_ok=True)

        return outputs_path

    def get_plot_path(self, plot_type: str, plot_folder: str = "plot") -> Path:
        """グラフフォルダパスの取得（存在しない場合は新規作成）"""
        # outputsフォルダの存在を保証してから取得
        plot_path = self.get_outputs_path() / plot_folder

        if not plot_path.exists():
            plot_path.mkdir(parents=False, exist_ok=True)

        plot_type_path = plot_path / plot_type

        if not plot_type_path.exists():
            plot_type_path.mkdir(parents=False, exist_ok=True)

        return plot_type_path

    def get_pdf_path(self, pdf_folder: str = "pdf") -> Path:
        """pdfフォルダパスの取得（存在しない場合ば新規作成）"""
        pdf_path = self.get_outputs_path() / pdf_folder

        if not pdf_path.exists():
            pdf_path.mkdir(parents=False, exist_ok=True)

        return pdf_path
