# python-monthly-sales-automation

Excelの売上データを月ごとに集計し、加工済みExcel・グラフ画像・PDFを出力する。
概要・使用ライブラリ・ディレクトリ構成は README.md を参照（ここでは重複させない）。

## 設計方針
- `src/common`: 複数モジュールで共有する処理（列名定義 `columns.py`、パス管理 `path_general.py` など）
- `src/process`: 本処理（Excel出力・グラフ作成・PDF出力）。1ファイル1責務
- 列名は `Columns` クラス、フォルダパスは `path_general.py` 経由で参照し、文字列を直書きしない
- 想定エラーは `raise` でユーザーに分かる内容を通知し、プログラムを終了する設計（README「設計意図」参照）
- グラフはExcel内蔵ではなく matplotlib / seaborn で作成する

## 環境の制約
- PDF出力は `win32com`（Excel.Application）を使うため、Windows + Excel インストール済みが前提
- `main.py` はプロジェクト直下から実行する（相対パス前提）

## コーディング方針
- Pylance(Standard)の静的解析に沿ったコーディングを行う。

## テスト
- pytest を使用。実行は `pytest`（プロジェクト直下）
- テストは `test/test_<モジュール名>.py` に置く
- win32 など外部依存は `unittest.mock.MagicMock` で差し替える（自作FakeClassは使わない）
- matplotlib は `test/conftest.py` で設定済み（GUI不要）

## git
- 運用は GitHub Flow: `main` は常に動く状態を保ち、作業は `main` から切ったブラン　　チで行い、PR → 　確認 → `main` へマージする。`main` へ直接コミットしない
- ブランチ名: `<type>/<短い説明>`（例: `feat/add-monthly-summary`, `fix/pdf-export-error`）
- コミットメッセージは Conventional Commits: `<type>(<scope>): <説明>`
  - type: `feat` / `fix` / `docs` / `refactor` / `test` / `chore` など（type・scope は英語、説明は日本語）
  - scope は任意（例: `export_pdf`, `data_process`）
  - 例: `refactor(test): test_export_pdf.py のwin32テストをMagicMockに変更`
- 1コミット1目的にする
- 過去のコミットは旧形式（add/update/edit/refactor）。履歴は書き換えない
