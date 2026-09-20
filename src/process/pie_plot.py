import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes  # 型ヒント記述用
from matplotlib.figure import Figure  # 型ヒント記述用

from src.common.columns import Columns
from src.common.data_process import pie_plot_data_process
from src.common.path_general import FolderPath
from src.common.plot_general import add_figure_border


# TODO: エラーハンドリング実装
def create_pie_plot() -> dict[str, tuple[Figure, Axes]]:
    """円グラフ作成"""
    # data_process()側で空データをガード済みの前提で代入
    pie_result = pie_plot_data_process()

    plot_result: dict[str, tuple[Figure, Axes]] = {}

    # 文字化け防止（メイリオに設定）
    plt.rcParams["font.family"] = "Meiryo"
    plt.rcParams["font.size"] = 12

    for sheet_name, df in pie_result.items():
        fig, ax = plt.subplots()
        ax.pie(
            df[Columns.TOTAL_SALE],
            labels=df[
                Columns.PRODUCT_NAME
            ].tolist(),  # labelsにdataframeを渡すため、リスト化
            autopct="%1.1f%%",
            startangle=90,
            counterclock=False,
        )
        ax.set_title(f"{sheet_name}分売上データ")

        add_figure_border(fig)
        plot_result[sheet_name] = (fig, ax)

    return plot_result

# TODO: エラーハンドリング実装
def plot_save_fig(plot_result: dict[str, tuple[Figure, Axes]]) -> None:
    """グラフ結果をpngファイルとして保存"""
    result_path = FolderPath().get_plot_path("pie_plot")
    
    for sheet_name, (fig, ax) in plot_result.items():
        fig.savefig(f"{result_path}/{sheet_name}売上円グラフ.png", dpi=300)
        print(f"作成しました：{sheet_name}売上円グラフ.png")


def main() -> None:
    try:
        plot_result = create_pie_plot()
        plot_save_fig(plot_result)
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"処理を中断しました: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"想定外のエラーが発生しました：{e}")
    finally:
        print("処理を実行しました")


if __name__ == "__main__":
    main()
