import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes  # 型ヒント記述用
from matplotlib.figure import Figure  # 型ヒント記述用

from data_process import data_process


def get_base_path() -> Path:
    """画像フォルダパスの取得"""
    file_path = Path(__file__).resolve().parents[1] / "outputs"

    if not file_path.exists():
        raise FileNotFoundError("outputsフォルダが存在しません")

    return file_path


def create_pie_plot() -> None:
    """円グラフ作成"""
    processed = data_process()

    THRESHOLD = 0.06

    # 文字化け防止（メイリオに設定）
    plt.rcParams["font.family"] = "Meiryo"
    
    for sheet_name, df in processed.items():
        df_grouped = df.groupby("商品名", as_index=False)["合計金額"].sum()
        df_grouped = df_grouped.sort_values(by="合計金額", ascending=False) # type: ignore

        total = df_grouped["合計金額"].sum()
        ratio = df_grouped["合計金額"] / total

        large = df_grouped[ratio >= THRESHOLD]
        small = df_grouped[ratio < THRESHOLD]

        if not small.empty:
            other_row = pd.DataFrame({
                "商品名": ["その他"],
                "合計金額": [small["合計金額"].sum()]
            })
            df_grouped = pd.concat(
                [large, other_row], ignore_index=True
            )
        else:
            df_grouped = large

        fig, ax = plt.subplots()
        # labelsにDataFrameを渡すため、tolist()にてリスト化
        ax.pie(
            df_grouped["合計金額"], 
            labels=df_grouped["商品名"].tolist(), 
            autopct="%1.1f%%",startangle=90, 
            counterclock=False
        )
        ax.set_title(f"{sheet_name}分売上データ")