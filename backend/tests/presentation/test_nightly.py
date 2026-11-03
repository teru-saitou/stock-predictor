"""夜間の一括更新のテスト。リポジトリを差し替えて、ネット接続なしで検証する。"""
import json

from app.config import Settings
from app.container import build_predict_stock_use_case
from app.infrastructure.repositories.demo_repository import DemoPriceRepository
from app.infrastructure.repositories.routing_repository import RoutingPriceRepository
from app.nightly import main
from app.presentation.batch.nightly import read_tickers, run_nightly, succeeded_count
from tests.fakes import NotFoundPriceRepository


def test_read_tickers_skips_blank_lines_and_comments():
    lines = ["# 見出し", "", "7203.T   # トヨタ", "  AAPL  ", "^N225"]
    assert read_tickers(lines) == ["7203.T", "AAPL", "^N225"]


def test_run_nightly_keeps_going_after_a_failure():
    repo = RoutingPriceRepository(default=NotFoundPriceRepository(), demo=DemoPriceRepository())
    use_case = build_predict_stock_use_case(Settings(), repo=repo)
    report = run_nightly(use_case, ["demo", "NOPE.T"])
    ok, ng = report["results"]
    # 中身は API の /api/predict と同じ形
    assert ok["ticker"] == "DEMO"
    assert ok["data"]["metrics"]["test_days"] == len(ok["data"]["equity"])
    assert ng["ticker"] == "NOPE.T" and "error" in ng
    assert succeeded_count(report) == 1


def test_main_writes_json(tmp_path):
    tickers = tmp_path / "tickers.txt"
    tickers.write_text("DEMO\n", encoding="utf-8")
    out = tmp_path / "out" / "nightly.json"
    assert main(["--tickers", str(tickers), "--out", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert [r["ticker"] for r in report["results"]] == ["DEMO"]
    assert report["generated_at"].endswith("+00:00")


def test_main_keeps_previous_file_when_everything_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.nightly.build_predict_stock_use_case",
        lambda s: build_predict_stock_use_case(s, repo=NotFoundPriceRepository()),
    )
    tickers = tmp_path / "tickers.txt"
    tickers.write_text("7203.T\n", encoding="utf-8")
    out = tmp_path / "nightly.json"
    out.write_text("前回の結果", encoding="utf-8")
    assert main(["--tickers", str(tickers), "--out", str(out)]) == 1
    assert out.read_text(encoding="utf-8") == "前回の結果"
