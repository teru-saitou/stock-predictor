"""夜間の一括更新のエントリポイント（GitHub Actions から毎晩呼ばれる）。

使い方（backend フォルダで）:
    python -m app.nightly --tickers nightly_tickers.txt --out ../frontend/public/nightly.json
"""
import argparse
import json
import sys
from pathlib import Path

from app.config import settings
from app.container import build_predict_stock_use_case
from app.presentation.batch.nightly import read_tickers, run_nightly, succeeded_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="決めた銘柄の予測・バックテストをまとめて更新する")
    parser.add_argument("--tickers", type=Path, required=True, help="銘柄コードを1行に1つ書いたファイル")
    parser.add_argument("--out", type=Path, required=True, help="結果の JSON を書き出す場所")
    args = parser.parse_args(argv)

    tickers = read_tickers(args.tickers.read_text(encoding="utf-8").splitlines())
    report = run_nightly(build_predict_stock_use_case(settings), tickers)
    for r in report["results"]:
        print(f"{r['ticker']}: {'OK' if 'data' in r else 'NG ' + r['error']}")

    # 全滅なら前回の結果を残す（画面が空になるより、1日古い結果の方がまし）
    if succeeded_count(report) == 0:
        print("すべての銘柄で失敗したため、結果を書き出しませんでした", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
