# Stock Predictor

FastAPI（Python）+ Next.js（React）で作る、株価の「翌営業日に上がるか」予測 & バックテストWebアプリの最小版です。

## 必要なもの
- Python 3.10 以上
- Node.js 20.9 以上（推奨: 最新 LTS）

## 起動方法

### 1. バックエンド（ターミナル①）
```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
動作確認: http://localhost:8000/api/predict?ticker=DEMO
API ドキュメント: http://localhost:8000/docs

### 2. フロントエンド（ターミナル②）
```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```
ブラウザで http://localhost:3000 を開き、銘柄コードを入れて「予測する」。

## 銘柄コードの例
| 入力 | 銘柄 |
|---|---|
| `DEMO` | オフライン動作確認用の疑似データ |
| `7203.T` | トヨタ自動車（日本株は末尾に `.T`） |
| `6758.T` | ソニーグループ |
| `AAPL` | Apple |
| `^N225` | 日経平均 |

データは yfinance（Yahoo Finance の非公式ライブラリ）で取得しています。個人の学習用途向けです。
本格的に日本株を扱うなら JPX 公式の J-Quants API への差し替えを検討してください（下の「データ源の差し替え」参照）。

## 構成（クリーンアーキテクチャ寄り）

```
backend/
  app/
    domain/                     ── 最内側：ビジネスルール（フレームワークに依存しない）
      entities.py                 PriceHistory（株価履歴の値オブジェクト）
      labels.py                   「翌日に上がるか」というラベルの定義
      timeseries.py               時系列順の学習/テスト分割
      evaluation.py               正解率・ベースライン
      backtest.py                 売買シミュレーション・最大ドローダウン
      errors.py                   ドメインの例外
    application/                ── ユースケース層
      ports/                      外部とのやり取りの抽象（内側が所有する）
        price_repository.py         株価の取得
        predictor.py                特徴量の作成・予測モデル
      use_cases/predict_stock.py  取得→特徴量→学習→評価→バックテストの流れ
      dto.py                      ユースケースの入出力
      errors.py                   ポートの契約としての例外
    infrastructure/             ── 外側：ポートの実装（詳細）
      repositories/               yfinance / デモデータ / 振り分け
      ml/features.py              テクニカル指標による特徴量
      ml/sklearn_predictor.py     scikit-learn による予測モデル
    presentation/api/           ── 外側：HTTP の入口
      routes/                     GET /api/predict, /api/health
      schemas.py                  レスポンス型（Pydantic）
      dependencies.py             ルーターへのユースケースの受け渡し
      errors.py                   例外 → HTTP ステータスの変換
    config.py                   設定値
    container.py                組み立て（どのポートにどの実装を差し込むか）
    main.py                     エントリポイント
  tests/                        層ごとのテスト（domain / application / infrastructure / presentation）
  .importlinter                 依存ルールの定義

frontend/
  app/page.tsx                  ページ（状態管理と部品の配置だけ）
  components/                   SearchForm, TickerGuide, PredictionSummary, PriceChart, BacktestResult, Stat
  lib/api.ts                    API クライアント
  lib/format.ts                 表示用フォーマット
  types/predict.ts              レスポンス型（backend の schemas.py と対応）
```

### 依存のルール

```
main → container → presentation ─┐
                   infrastructure ┴→ application → domain
```

- 依存は **外側から内側への一方向のみ**。domain は何も知らず、application は domain だけを知る。
- 抽象（ports）は application が持ち、infrastructure が実装する（依存性逆転）。
- presentation と infrastructure は互いを知らない。両者をつなぐのは `container.py` だけ。
- domain と application では FastAPI・Pydantic・scikit-learn・yfinance を使わない。
  pandas / numpy は時系列を扱う標準語として domain での利用を許容している。

これらのルールは `import-linter` で自動チェックしています。

## テスト・依存ルールのチェック
```bash
cd backend
pip install -r requirements-dev.txt
pytest          # テスト
lint-imports    # 依存ルールのチェック（違反があると BROKEN と表示）
```

## よくある拡張と触る場所
| やりたいこと | 触るファイル |
|---|---|
| データ源の差し替え（J-Quants など） | `infrastructure/repositories/` に `PriceRepository` を満たすクラスを追加 → `container.py` で差し替え |
| 特徴量を増やす | `infrastructure/ml/features.py`（または別の `FeatureBuilder` を作って差し替え） |
| モデルを変える（LightGBM など） | `infrastructure/ml/` に `Predictor` を満たすクラスを追加 → `container.py` で差し替え |
| 予測対象を変える（5日後など） | `domain/labels.py` |
| バックテストのルールを変える | `domain/backtest.py` |
| 新しい API を追加 | `application/use_cases/` にユースケース、`presentation/api/routes/` にルーター、`container.py` と `main.py` で登録 |

## 仕組み
1. 日付 t の特徴量（t の終値までに分かる情報のみ）から、t→t+1 の騰落を予測
2. データを **時系列順** に 70% 学習 / 30% テストに分ける（未来の情報が混ざらないように）
3. テスト期間を検証する（画面で切り替え可能）
   - **ウォークフォワード**（既定）：テスト期間を20営業日ずつに区切り、各区間の直前までの全データで学習し直して予測する。実運用で「定期的にモデルを作り直す」状況に近い
   - **ホールドアウト**：最初の学習データで1回だけ学習し、テスト期間全体を予測する
4. 正解率を「常に多い方を予測する」ベースラインと比較
5. 「上がると予測した日だけ保有」する戦略を、手数料（片道0.1%）込みで買い持ちと比較。t の終値を見てから t の終値では買えないので、**t+1 の始値で買い、t+2 の始値で売る**（続けて「上がる」なら持ち続ける）。買い持ちも同じ始値で買った場合と比べる
6. 最後に全データで学習し直し、最新日の翌営業日の上昇確率を出す

### 特徴量（画面で切り替え可能）
| セット | 内容 |
|---|---|
| 基本（11個） | 1/5/10/20日リターン、5/20/60日移動平均との乖離、20日ボラティリティ、RSI、出来高変化、当日の値幅 |
| 拡張（既定、最大24個） | 基本 + 60日リターン、MACD、ボリンジャー %B、ボラティリティ比、1年高値からの距離、寄り付きギャップ、出来高Zスコア、曜日、月 + **市場指数との関係**（指数の1/5日リターン、相対的な強さ、60日相関） |

市場指数は同じ取引所のものを使います（日本株 → `^N225`、それ以外 → `^GSPC`）。
取引時間が違う市場の指数を同じ日付で使うと、終値より後に決まる値を使うことになり、リークになるためです。
指数が取得できない場合は、指数の特徴量を除いて計算を続けます。

> 設定を変えると成績は変わりますが、ランダムな値動きの DEMO でも -10%〜+14% 程度ぶれます。
> 1銘柄・1期間の結果だけで「改善した」と判断せず、複数の銘柄・期間で比べてください。

## 次に試すと面白い改善
- **予測期間の変更**: 翌日ではなく5日後・20日後
- **確率のしきい値**: 0.5 ではなく 0.55 以上のときだけ買う
- **モデル比較**: LightGBM、ロジスティック回帰、LSTM など
- **特徴量の重要度**: どの指標が効いているかを可視化
- **複数銘柄での一括比較**: 設定ごとの成績を多数の銘柄で集計し、偶然でない改善かを確かめる

## 毎朝の予測（自動更新）
GitHub Actions（`.github/workflows/nightly.yml`）が火〜土の 7:00（日本時間）に、決めた銘柄の予測・バックテストを計算し直し、結果を `frontend/public/nightly.json` にコミットします。画面の「毎朝の予測」（`/nightly`）でまとめて見られます。API サーバーを使わないので、Render が止まっていてもすぐ表示されます。

- 対象の銘柄は `backend/nightly_tickers.txt` で増減する（1行に1つ）
- 今すぐ動かしたいときは、GitHub の Actions タブ →「nightly」→「Run workflow」
- 手元で試すとき（backend フォルダで）: `python -m app.nightly --tickers nightly_tickers.txt --out ../frontend/public/nightly.json`
- 一部の銘柄の取得に失敗しても、残りは更新されます。全部失敗したときは前回の結果を残し、Actions が失敗扱いになります（GitHub からメールが届きます）

## 注意
このアプリは学習・実験用です。予測やバックテストの結果は将来の成績を保証しません。
