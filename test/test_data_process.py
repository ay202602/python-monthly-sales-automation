import pandas as pd
import pytest

import src.common.data_process as data_process
from src.common.columns import Columns


def test_data_process_normal():
    """正常系: 実データを読み込み、想定通りの構造で結果が返る"""
    result = data_process.data_process()

    assert isinstance(result, dict)

    # 各シートの結果検証
    for sheet_name, df in result.items():
        # DataFrameであること
        assert isinstance(df, pd.DataFrame)

        # 列構成が想定通りであること
        assert list(df.columns) == [
            Columns.CUSTOMER,
            Columns.PRODUCT_NAME,
            Columns.TOTAL_SALE,
        ]

        assert not df.empty

        # 合計金額がマイナスになっていないこと（単価・数量が正の前提）
        assert (df[Columns.TOTAL_SALE] >= 0).all()


def test_data_process_total_sale_is_numeric():
    """合計金額列が数値型になっているか"""
    result = data_process.data_process()

    for sheet_name, df in result.items():
        # 計算対象のカラムに数字が入っていること
        assert pd.api.types.is_numeric_dtype(df[Columns.TOTAL_SALE])


def test_data_process_no_duplicate_customer_product():
    """取引先・商品名の組み合わせに重複がないこと（groupbyの集計漏れ確認）"""
    result = data_process.data_process()

    for sheet_name, df in result.items():
        duplicated = df.duplicated(subset=[Columns.CUSTOMER, Columns.PRODUCT_NAME])
        # 取引先・商品名が重複していないこと
        assert not duplicated.any()


def test_data_process_with_mock(monkeypatch):
    """モックを使った正常系テスト"""
    # 偽のExcelデータ（1シート分）を用意
    fake_df = pd.DataFrame(
        {
            Columns.CUSTOMER: ["A社", "B社"],
            Columns.PRODUCT_NAME: ["商品1", "商品2"],
            Columns.UNIT_PRICE: [100, 200],
            Columns.QUANTITY: [2, 3],
        }
    )

    # _load_excelを偽関数に差し替え、fake_dfを返すようにする
    monkeypatch.setattr(
        data_process, "_load_excel", lambda raw_data: {"Sheet1": fake_df}
    )

    # モック化した状態でdata_process()を実行
    result = data_process.data_process()

    # 結果の検証
    out = result["Sheet1"]

    expected = pd.DataFrame(
        {
            Columns.CUSTOMER: ["A社", "B社"],
            Columns.PRODUCT_NAME: ["商品1", "商品2"],
            Columns.TOTAL_SALE: [200, 600],
        }
    )

    pd.testing.assert_frame_equal(
        out.reset_index(drop=True), expected.reset_index(drop=True)
    )


def test_data_process_raises_runtime_error(monkeypatch):
    """異常系: Excel読み込み失敗時にRuntimeErrorが発生する"""

    def fake_load_excel(raw_data):
        raise RuntimeError("読み込み失敗")

    monkeypatch.setattr(data_process, "_load_excel", fake_load_excel)

    with pytest.raises(RuntimeError):
        data_process.data_process()


def test_data_process_raises_value_error_when_empty(monkeypatch):
    """異常系: シートが空の場合ValueErrorが発生する"""
    monkeypatch.setattr(
        data_process, "_load_excel", lambda raw_data: {"Sheet1": pd.DataFrame()}
    )

    with pytest.raises(ValueError, match="データが存在しません"):
        data_process.data_process()


def test_data_process_raises_key_error_when_column_missing(monkeypatch):
    """異常系: 必要な列が欠けている場合KeyErrorが発生する"""
    df_missing_column = pd.DataFrame(
        {
            Columns.CUSTOMER: ["A社"],
            Columns.PRODUCT_NAME: ["商品1"],
            Columns.QUANTITY: [1],
            # UNIT_PRICE列がない
        }
    )

    monkeypatch.setattr(
        data_process, "_load_excel", lambda raw_data: {"Sheet1": df_missing_column}
    )

    with pytest.raises(KeyError, match="必要な列がありません"):
        data_process.data_process()


def test_data_process_raises_value_error_when_non_numeric(monkeypatch):
    """異常系: 単価・数量列に数値以外が含まれる場合ValueErrorが発生する"""
    df_non_numeric = pd.DataFrame(
        {
            Columns.CUSTOMER: ["A社"],
            Columns.PRODUCT_NAME: ["商品1"],
            Columns.UNIT_PRICE: ["abc"],  # 数値以外
            Columns.QUANTITY: [1],
        }
    )

    monkeypatch.setattr(
        data_process, "_load_excel", lambda raw_data: {"Sheet1": df_non_numeric}
    )

    with pytest.raises(ValueError, match="数字以外の値が含まれています"):
        data_process.data_process()
