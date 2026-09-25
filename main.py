import os

import src.process.bar_plot as bar_plot
import src.process.export_excel as export_excel
import src.process.export_pdf as export_pdf
import src.process.pie_plot as pie_plot


def check_working_directory() -> None:
    project_root = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
    current_dir = os.path.normcase(os.getcwd())
    if current_dir != project_root:
        raise RuntimeError(
            f"main.py はプロジェクトのルートディレクトリ({project_root}) で実行してください"
            f" 現在の実行場所: ({os.getcwd()})"
        )


def main() -> None:
    check_working_directory()
    export_excel.main()
    bar_plot.main()
    pie_plot.main()
    export_pdf.main()


if __name__ == "__main__":
    main()
