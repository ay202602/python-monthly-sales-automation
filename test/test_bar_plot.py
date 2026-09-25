import matplotlib.pyplot as plt
import pandas as pd
import pytest
from matplotlib.axes import Axes

import src.process.bar_plot as bar_plot
from src.common.columns import Columns


@pytest.fixture(autouse=True)
def close_all_figures():
    """テスト毎にmatplotlibの図を閉じる"""
    yield
    plt.close("all")


@pytest.fixture
def sample_data() -> dict[str, pd.DataFrame]:
    return {
        "Sheet1": pd.DataFrame(
            {
                Columns.CUSTOMER: ["A社", "B社"],
                Columns.TOTAL_SALE: [10000, 20000],
            }
        )
    }


def test_create_bar_plot_returns_axes_per_sheet(monkeypatch, sample_data):
    """戻り値のキーとAxes型、必要列を持つDataFrameを渡せているか"""
    # bar_plot.pyがimportしているbar_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(bar_plot, "bar_plot_data_process", lambda: sample_data)

    result = bar_plot.create_bar_plot()

    # 戻り値のキーがシート名であること
    assert set(result.keys()) == {"Sheet1"}

    # 戻り値がAxes型であること
    assert isinstance(result["Sheet1"], Axes)


def test_create_bar_plot_bar_count_matches_data(monkeypatch, sample_data):
    """データ行数とバー本数が一致しているか"""
    # bar_plot.pyがimportしているbar_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(bar_plot, "bar_plot_data_process", lambda: sample_data)

    result = bar_plot.create_bar_plot()
    ax = result["Sheet1"]

    assert len(ax.patches) == len(sample_data["Sheet1"])


def test_create_bar_plot_title_and_xlabel(monkeypatch, sample_data):
    """タイトル、x軸ラベルが正しく設定されているか"""
    # bar_plot.pyがimportしているbar_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(bar_plot, "bar_plot_data_process", lambda: sample_data)

    result = bar_plot.create_bar_plot()
    ax = result["Sheet1"]

    assert ax.get_title() == "Sheet1分売上データ"
    assert ax.get_xlabel() == "合計金額（千円）"


def test_create_bar_plot_ylabel_vertical_text(monkeypatch, sample_data):
    """ylabelが縦書き（1文字ずつ改行・正立）になっているか"""
    # bar_plot.pyがimportしているbar_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(bar_plot, "bar_plot_data_process", lambda: sample_data)

    result = bar_plot.create_bar_plot()
    ax = result["Sheet1"]

    assert ax.get_ylabel() == "取\n引\n先"
    assert ax.yaxis.get_label().get_rotation() == 0


def test_create_bar_plot_bar_labels_formatted(monkeypatch, sample_data):
    """バーラベルが千円単位・カンマ区切りで表示されているか"""
    # bar_plot.pyがimportしているbar_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(bar_plot, "bar_plot_data_process", lambda: sample_data)

    result = bar_plot.create_bar_plot()
    ax = result["Sheet1"]

    label_texts = [t.get_text() for t in ax.texts]
    assert "10千円" in label_texts
    assert "20千円" in label_texts
