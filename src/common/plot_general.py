from matplotlib.figure import Figure
from matplotlib.patches import Rectangle


def add_figure_border(fig: Figure, line_width: float = 5, color: str = "black") -> None:
    """グラフ全体を囲む枠線を追加する"""
    fig.add_artist(
        Rectangle(
            (0, 0),  # Rectangle（四角形）グラフの左下の起点座標
            1,  # グラフの幅・高さ共にFigure（グラフ）全体に対する位置の割合を1（100%）に指定
            1,
            transform=fig.transFigure,
            fill=False,
            edgecolor=color,
            linewidth=line_width,
        )
    )
