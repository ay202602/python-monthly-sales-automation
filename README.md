# python-monthly-sales-automation
## 概要
- Excelで記入した売上データを月ごとに集計し、PDFとして出力する自動化ツールです。
- 毎月の集計業務を想定し、VBAが使用できない環境下で自動化できるようPythonで開発しました。
- 当プロジェクト内で使用しているExcelデータは、Claudeにて作成したダミーデータです。


## 機能
Excelの売上データを読み込み、以下のファイルを自動出力します。

| 出力ファイル |形式 | 出力先 |
|:---|:---|:---|
| 月次売上データ（画像添付済み） | .xlsx | data/processed |
| 棒 / 円グラフ画像 | .png | outputs/plot |
| 月次売上データ（Excel内のデータをpdf化） | .pdf | outputs/pdf |

- **複数シート対応**：シートごとに上記ファイルを出力し、シート名がそのままファイル名となります
- **フォルダ自動生成**：出力フォルダの格納フォルダがない場合、実行時にフォルダが自動生成されます
- **進捗表示**：各処理の完了とエラー内容をターミナルにて表示します

## 出力例
### 1月分の売上データの場合（ダミーデータです）
| 1月売上データ | 1月売上グラフ |
|:---:|:--:|
|![売上データ](result/result_1.jpg)|![売上グラフ](result/result_2.jpg)|


## 実行方法
**前提として、以下の環境が必要です。**
- Windows / Microsoft Excel インストール済み / Python 3.12

### 入力Excelの形式
必須列：取引先 / 商品名 / 単価 / 数量 / 合計金額（列名は `Columns` クラスの定義）

### 手順
1. 下記のコマンドを実行し、ライブラリをインストール
   ```powershell
   pip install -r requirements.txt
   ```

2. data/raw内に加工前のExcelファイル（.xlsx）を配置

3. **プロジェクト直下**で実行
   ```powershell
   python main.py
   ```

> [!WARNING]
> プロジェクト直下以外で実行すると`RuntimeError`になります。

4. 出力を確認（data/processed・outputs/plot・outputs/pdf）

### テストの実行
```powershell
pytest
```


## 動作環境・使用技術
> **動作環境**：Windows + Excel インストール済み（PDF出力に win32com を使用）

| 区分 | ライブラリ | バージョン | 用途 |
|:---|:---|:---|:---|
| 言語 | python | 3.12.10 | ツール開発 |
| テスト用フレームワーク | pytest | 9.1.1 | テストコード実装 |
| データ処理 | pandas | 3.0.5 | Excelファイルの集計 |
| グラフ描画① | matplotlib | 3.11.1 | 円グラフ出力 |
| グラフ描画② | seaborn | 0.13.2 | 棒グラフ出力 |
| Excel処理 | openpyxl | 3.1.5 | 加工済みExcelファイルの装飾・グラフ画像添付 |
| windowsのCOM操作 | pywin32 | 312 | 加工済みExcelファイルのPDF出力 |
| 画像処理 | pillow | 12.3.0 | テスト用ダミー画像の生成（openpyxlの画像添付にも必要） |


## 設計意図
### エラーハンドリング
想定エラーは `raise` で原因が分かる形で通知し、プログラムを終了します。

| 処理 | 想定エラー |
|:---|:---|
| Excel読み込み | パスが不正 / ファイルが未配置 / 中身が空 |
| データ検証 | 必要な列が欠けている / 数値列に数値以外が含まれる |
| 円グラフ加工 | 合計金額が0 |
| PDF出力 | グラフ画像（円・棒）が見つからない |

### グラフ作成
Excel内蔵グラフではなく matplotlib / seaborn を採用。描画・設定の自由度が高いため。

### テスト
pytestで本処理の動作を保証。win32 など外部依存はフェイククラスではなく `MagicMock` で差し替え。

### モジュール構成
責務を分けるため2フォルダに分割しました。

| フォルダ | 役割 |
|:---:|:---:|
| src/common | 列名定義・パス処理などの共通処理 |
| src/process | 本処理（Excel出力・グラフ・PDF） 1ファイルにつき1つの責務 |


## ディレクトリ構成
```
python-monthly-sales-automation
├── data  # Excelデータ格納
│   ├── processed
│   └── raw
│
├── outputs # 出力ファイル格納
│   ├── pdf
│   └── plot
│        ├── bar_plot
│        └── pie_plot
│
├── result  # README.md用画像ファイル格納
│   ├── result_1.jpg
│   └── result_2.jpg
│
├── src # ソースコード格納
│   ├── common  # 共通処理用コード格納
│   │   ├── __init__.py
│   │   ├── columns.py
│   │   ├── data_process.py
│   │   ├── path_general.py
│   │   └── plot_general.py
│   │
│   ├── process # 本処理用コード格納
│   │   ├── __init__.py
│   │   ├── bar_plot.py
│   │   ├── export_excel.py
│   │   ├── export_pdf.py
│   │   └── pie_plot.py
│   │
│   └── __init__.py
│
├── test  # テスト用コード格納
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_bar_plot.py
│   ├── test_data_process.py
│   ├── test_export_excel.py
│   ├── test_export_pdf.py
│   └── test_pie_plot.py
│
├── .gitignore
├── CLAUDE.md
├── main.py # メインプログラム
├── README.md
└── requirements.txt
```