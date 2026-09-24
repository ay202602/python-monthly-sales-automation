import pandas as pd
import pytest

from src.common.columns import Columns
from src.process.export_excel import cell_decoration, display_width

# ----- display_width -----


def test_display_width_half_width_only():
    """半角文字のみの場合、文字数と幅が一致すること"""
    assert display_width("abc123") == 6


def test_display_width_full_width_only():
    """全角文字のみの場合、文字数と幅が一致すること"""
    assert display_width("売上高") == 6


def test_display_width_mixed():
    """半角・全角混在の場合、正しく合算されること"""
    assert display_width("A社1") == 1 + 2 + 1  # "A" = 1, "社" = 2, "1" = 1


def test_display_width_empty_string():
    """空文字列の場合は0になること"""
    assert display_width("") == 0


# ----- cell_decoration -----


@pytest.fixture
def sample_processed() -> dict[str, pd.DataFrame]:
    df = pd.DataFrame(
        {
            Columns.CUSTOMER: ["A社", "B社"],
            Columns.PRODUCT_NAME: ["商品1", "商品2"],
            Columns.TOTAL_SALE: [1000, 2000],
        }
    )

    return {"Sheet1": df}


def test_cell_decoration_returns_workbook_per_sheet(sample_processed):
    """シート名ごとにWorkbookが生成され、戻り値のキーと一致すること"""
    wb = cell_decoration(sample_processed)
    ws = wb["Sheet1"].active

    # Pylance対策: Noneではないことを保証する
    assert ws is not None

    header_values = [cell.value for cell in ws[1]]
    assert header_values == [Columns.CUSTOMER, Columns.PRODUCT_NAME, Columns.TOTAL_SALE]

    for cell in ws[1]:
        # セルの色がDDEBF7（薄い青色）であること
        assert cell.fill.start_color.rgb == "00DDEBF7"


def test_cell_decoration_data_rows_written(sample_processed):
    """データ部分が正しく転記されていること"""
    wb = cell_decoration(sample_processed)
    ws = wb["Sheet1"].active

    # Pylance対策: Noneではないことを保証する
    assert ws is not None

    # 2行目以降のセルの値がリスト内の値と同じであること
    assert [cell.value for cell in ws[2]] == ["A社", "商品1", 1000]
    assert [cell.value for cell in ws[3]] == ["B社", "商品2", 2000]


def test_cell_decoration_all_cells_have_border(sample_processed):
    """全セルに格子罫線が設定されていること"""
    wb = cell_decoration(sample_processed)
    ws = wb["Sheet1"].active

    # Pylance対策: Noneではないことを保証する
    assert ws is not None

    for row in ws.iter_rows():
        for cell in row:
            assert cell.border.left.style == "thin"  # 左側のセルが格子罫線であること
            assert cell.border.right.style == "thin"  # 右側のセルが格子罫線であること
            assert cell.border.top.style == "thin"  # 上側のセルが格子罫線であること
            assert cell.border.bottom.style == "thin"  # 下側のセルが格子罫線であること


def test_cell_decoration_numeric_cells_have_accouting_format(sample_processed):
    """数値セルに会計書式が設定され、文字列セルには適用されないこと"""
    wb = cell_decoration(sample_processed)
    ws = wb["Sheet1"].active

    # Pylance対策: Noneではないことを保証する
    assert ws is not None

    accounting_format = '_ ¥* #,##0_ ;_ ¥* -#,##0_ ;_ ¥* "-"_ ;_ @_ '

    # TOTAL_SALE列（3列目）は数値なので会計書式
    for row in ws.iter_rows(min_row=2):
        customer_cell, product_cell, total_sale_cell = row
        # TOTAL_SALE列（3列目）が会計書式であること
        assert total_sale_cell.number_format == accounting_format

        # CUSTOMER, PRODUCT_NAME列は文字列なのでデフォルト書式のまま
        assert customer_cell.number_format == "General" # 取引先列（1列目）がデフォルトであること
        assert product_cell.number_format == "General" # 商品名列（2列目）がデフォルトであること


def test_cell_decoration_sheet_header_text_set(sample_processed):
    """印刷用ヘッダーにシート名が反映されていること"""
    wb = cell_decoration(sample_processed)
    ws = wb["Sheet1"].active

    assert ws is not None  # Pylance対策: Noneではないことを保証する
    assert ws.oddHeader is not None  # Pylance対策: Noneではないことを保証する

    assert ws.oddHeader.center.text == "Sheet1分売上データ"


def test_cell_decoration_multiple_sheets(sample_processed):
    """複数シートを渡した場合、それぞれ独立したWorkbookが作られること"""
    processed = dict(sample_processed)
    processed["Sheet2"] = pd.DataFrame(
        {
            Columns.CUSTOMER: ["C社"],
            Columns.PRODUCT_NAME: ["商品3"],
            Columns.TOTAL_SALE: [500],
        }
    )

    wb = cell_decoration(processed)

    # 2シート分のキーがそろっていること
    assert set(wb.keys()) == {"Sheet1", "Sheet2"}

    # それぞれ独立したworkbookであること
    assert wb["Sheet1"].active is not wb["Sheet2"].active
