import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes  # 型ヒント記述用
from matplotlib.figure import Figure  # 型ヒント記述用

from src.process.data_process import data_process
from src.common.plot_path import get_outputs_path


def plot_data_process() -> dict[str, pd.DataFrame]:
    processed = data_process()

    THRESHOLD = 0.06

    # dict[シート名, DataFrame]
    result: dict[str, pd.DataFrame] = {}

    for sheet_name, df in processed.items():
        df_grouped = df.groupby("商品名", as_index=False)["合計金額"].sum()
        df_grouped = df_grouped.sort_values(by="合計金額", ascending=False)  # type: ignore

        total = df_grouped["合計金額"].sum()
        ratio = df_grouped["合計金額"] / total

        # large = 閾値以上の割合の値
        large = df_grouped[ratio >= THRESHOLD]

        # small = 閾値未満の割合の値
        small = df_grouped[ratio < THRESHOLD]

        # small内のdfに1件、行がある場合「その他」のdfを作って結合
        if not small.empty:
            other_row = pd.DataFrame(
                {"商品名": ["その他"], "合計金額": [small["合計金額"].sum()]}
            )
            df_grouped = pd.concat([large, other_row], ignore_index=True)
        else:
            df_grouped = large

        result[sheet_name] = df_grouped

    return result


def create_pie_plot() -> dict[str, tuple[Figure, Axes]]:
    """円グラフ作成"""
    # data_process()側で空データをガード済みの前提で代入
    result = plot_data_process()

    plot_result: dict[str, tuple[Figure, Axes]] = {}

    # 文字化け防止（メイリオに設定）
    plt.rcParams["font.family"] = "Meiryo"

    for sheet_name, df in result.items():
        fig, ax = plt.subplots()
        ax.pie(
            df["合計金額"],
            labels=df["商品名"].tolist(),  # labelsにdataframeを渡すため、リスト化
            autopct="%1.1f%%",
            startangle=90,
            counterclock=False,
        )
        ax.set_title(f"{sheet_name}分売上データ")

        plot_result[sheet_name] = (fig, ax)

    return plot_result


def plot_save_fig(plot_result: dict[str, tuple[Figure, Axes]]) -> None:
    """グラフ結果をpngファイルとして保存"""
    result_path = get_outputs_path()

    full_path = result_path / "pie_plot"

    if not full_path.exists():
        raise FileNotFoundError("pie_plotフォルダが存在しません")

    for sheet_name, (fig, ax) in plot_result.items():
        fig.savefig(f"{full_path}/{sheet_name}売上グラフ（円）.png", dpi=300)


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
