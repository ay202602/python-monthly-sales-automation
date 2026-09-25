import matplotlib.pyplot as plt
import pandas as pd
import pytest
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Wedge

import src.process.pie_plot as pie_plot
from src.common.columns import Columns


@pytest.fixture(autouse=True)
def close_all_figures():
    """テスト毎にmatplotlibbの図を閉じる"""
    yield
    plt.close("all")


@pytest.fixture
def sample_data() -> dict[str, pd.DataFrame]:
    return {
        "Sheet1": pd.DataFrame(
            {
                Columns.PRODUCT_NAME: ["商品A", "商品B"],
                Columns.TOTAL_SALE: [10000, 20000],
            }
        )
    }


def test_create_pie_plot_returns_figure_and_axes_per_sheet(monkeypatch, sample_data):
    """戻り値のキーとFigure・Axes型、必要列を持つDataFrameを渡せているか"""
    # pie_plot.pyがimportしているpie_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(pie_plot, "pie_plot_data_process", lambda: sample_data)

    result = pie_plot.create_pie_plot()

    # 戻り値のキーがシート名であること
    assert set(result.keys()) == {"Sheet1"}

    fig, ax = result["Sheet1"]

    # 戻り値の値がFigureであること
    assert isinstance(fig, Figure)

    # 戻り値の値がAxesであること
    assert isinstance(ax, Axes)


def test_create_pie_plot_wedge_count_matches_data(monkeypatch, sample_data):
    """データ行数とウェッジ（扇形）の数が一致しているか"""
    # pie_plot.pyがimportしているpie_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(pie_plot, "pie_plot_data_process", lambda: sample_data)

    result = pie_plot.create_pie_plot()

    _, ax = result["Sheet1"]

    assert len(ax.patches) == len(sample_data["Sheet1"])


def test_create_pie_plot_title(monkeypatch, sample_data):
    """タイトルが正しく設定されているか"""
    # pie_plot.pyがimportしているpie_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(pie_plot, "pie_plot_data_process", lambda: sample_data)

    result = pie_plot.create_pie_plot()
    _, ax = result["Sheet1"]

    assert ax.get_title() == "Sheet1分売上データ"


def test_create_pie_plot_labels_and_autopct(monkeypatch, sample_data):
    """商品名ラベルとパーセント表記が表示されているか"""
    # pie_plot.pyがimportしているpie_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(pie_plot, "pie_plot_data_process", lambda: sample_data)

    result = pie_plot.create_pie_plot()
    _, ax = result["Sheet1"]

    label_texts = [t.get_text() for t in ax.texts]

    # 商品名ラベルが表示されていること
    assert "商品A" in label_texts
    assert "商品B" in label_texts

    # autopct="%1.1f%"による割合表示がされていること（10000:20000 = 33.3% 66.7%）
    assert "33.3%" in label_texts
    assert "66.7%" in label_texts


def test_create_pie_plot_startangle_and_direction(monkeypatch, sample_data):
    """startangle=90・counterclock=Falseが適用されているか（最初のウェッジの開始角度で確認）"""
    # pie_plot.pyがimportしているpie_plot_data_processを差し替える（定義元のdata_process側ではない）
    monkeypatch.setattr(pie_plot, "pie_plot_data_process", lambda: sample_data)

    result = pie_plot.create_pie_plot()
    _, ax = result["Sheet1"]

    first_wedge = ax.patches[0]

    # Pylance対策: first_wedgeの戻り値がWedgeであることを実行時に保証し、型の絞り込みを行う
    assert isinstance(first_wedge, Wedge)

    # theta1（開始角度）がtheta2（終了角度）から扇形の角度分引いた値であること
    # 今回のケース: 1つ目の値データ（10000）割合分の角度（33.3% = 120度）
    assert first_wedge.theta1 == pytest.approx(-30.0, abs=1e-3)

    # theta2（終了角度）が90度であること
    assert first_wedge.theta2 == pytest.approx(90.0, abs=1e-3)
