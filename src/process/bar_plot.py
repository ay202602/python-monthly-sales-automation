import sys

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.axes import Axes  # 型ヒント記述用
from matplotlib.container import BarContainer
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from src.common.columns import Columns
from src.common.data_process import bar_plot_data_process
from src.common.path_general import FolderPath
from src.common.plot_general import add_figure_border


# TODO: エラーハンドリング実装
def create_bar_plot():
    """棒グラフ作成"""
    # data_process.py側で空データをガード済みの前提で代入
    data_result = bar_plot_data_process()

    plot_result: dict[str, Axes] = {}

    # font="Meiryo"は文字化け防止
    sns.set_theme(style="darkgrid", context="notebook", font="Meiryo")

    for sheet_name, plot_df in data_result.items():
        plt.figure(figsize=(10, 6))  # 幅・高さ

        ax = sns.barplot(
            data=plot_df,
            x=Columns.TOTAL_SALE,
            y=Columns.CUSTOMER,
        )

        ax.set_title(f"{sheet_name}分売上データ")
        ax.set_xlabel("合計金額（千円）")
        ax.set_ylabel("取引先".join("\n"))

        # バー先端がプロット領域からはみ出さないよう余白を確保
        ax.margins(x=0.2)

        # 各バーに数値ラベルを表示（外側・千円単位・カンマ区切り）
        for contaier in ax.containers:
            if isinstance(contaier, BarContainer):
                ax.bar_label(
                    contaier,
                    fmt=lambda x: f"{x/1000:,.0f}千円",
                    label_type="edge",
                    padding=3,
                )

        # x軸ラベルも千円単位・カンマ区切りに統一
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x/1000):,}千円"))
        ax.locator_params(axis="x", nbins=5)

        plt.tight_layout()
        
        fig = ax.get_figure()
        assert isinstance(fig, Figure)
        add_figure_border(fig)
        
        plot_result[sheet_name] = ax

    return plot_result

# TODO: エラーハンドリング実装
def plot_save_fig(plot_result: dict[str, Axes]):
    """グラフ結果をpngとして保存"""
    result_path = FolderPath().get_plot_path("bar_plot")
    
    for sheet_name, ax in plot_result.items():
        fig = ax.get_figure()
        assert isinstance(fig, Figure)
        fig.savefig(f"{result_path}/{sheet_name}売上棒グラフ.png", dpi=300)
        print(f"作成しました：{sheet_name}売上棒グラフ.png")


def main() -> None:
    try:
        plot_result = create_bar_plot()
        plot_save_fig(plot_result)
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as e:
        print(f"処理を中断しました。：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"想定外のエラーが発生しました。：{e}")
        sys.exit(1)
    finally:
        print("処理を実行しました")


if __name__ == "__main__":
    main()
