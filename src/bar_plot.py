import sys

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.axes import Axes  # 型ヒント記述用
from matplotlib.container import BarContainer
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from data_process import data_process
from plot_path import get_outputs_path


def create_bar_plot():
    """棒グラフ作成"""
    # data_process()側で空データをガード済みの前提で代入
    result = data_process()

    plot_result: dict[str, Axes] = {}

    sns.set_theme(style="darkgrid")

    # 文字化け防止（メイリオに設定）
    plt.rcParams["font.family"] = "Meiryo"

    for sheet_name, df in result.items():
        plot_df = df.groupby("取引先", as_index=False)[["合計金額"]].sum()
        plot_df = plot_df.sort_values(by="取引先", ascending=False)

        plt.figure(figsize=(10, 6))  # 幅・高さ

        ax = sns.barplot(
            data=plot_df,
            x="合計金額",
            y="取引先",
        )

        ax.set_title(f"{sheet_name}分売上データ")
        ax.set_xlabel("合計金額（千円）")
        ax.set_ylabel("取引先".join("\n"))

        # バー先端がプロット領域からはみ出さないよう余白を確保
        ax.margins(x=0.15)

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

        plt.tight_layout()
        plot_result[sheet_name] = ax
    plt.show()

    return plot_result


def plot_save_fig(plot_result: dict[str, Axes]):
    """グラフ結果をpngとして保存"""
    result_path = get_outputs_path()

    full_path = result_path / "bar_plot"

    if not full_path.exists():
        raise FileNotFoundError("bar_plotフォルダが存在しません")

    for sheet_name, ax in plot_result.items():
        fig = ax.get_figure()
        assert isinstance(fig, Figure)
        fig.savefig(f"{full_path}/{sheet_name}売上棒グラフ.png", dpi=300)
        print(f"作成しました：{sheet_name}売上棒グラフ.png")


def main() -> None:
    plot_result = create_bar_plot()
    plot_save_fig(plot_result)


if __name__ == "__main__":
    main()
