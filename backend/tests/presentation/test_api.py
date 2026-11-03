"""presentation 層（API）のテスト。リポジトリを差し替えて、ネット接続なしで検証する。"""
from fastapi.testclient import TestClient

from app.config import Settings
from app.container import build_predict_stock_use_case
from app.main import create_app
from tests.fakes import InMemoryPriceRepository, NotFoundPriceRepository, demo_history


def _client(repo=None) -> TestClient:
    settings = Settings()
    use_case = build_predict_stock_use_case(settings, repo=repo)
    return TestClient(create_app(settings, use_case))


def test_health():
    assert _client().get("/api/health").json() == {"status": "ok"}


def test_predict_demo():
    res = _client().get("/api/predict", params={"ticker": "demo"})
    assert res.status_code == 200
    body = res.json()
    assert body["ticker"] == "DEMO"
    assert body["name"] == "デモ銘柄（疑似データ）"
    assert 0 <= body["next_up_probability"] <= 1
    assert body["metrics"]["test_days"] == len(body["equity"])


def test_company_name_may_be_missing():
    res = _client(InMemoryPriceRepository(demo_history(400), name=None)).get(
        "/api/predict", params={"ticker": "7203.T"}
    )
    assert res.status_code == 200
    assert res.json()["name"] is None


def test_not_found_returns_404():
    res = _client(NotFoundPriceRepository()).get("/api/predict", params={"ticker": "XXXX"})
    assert res.status_code == 404
    assert "XXXX" in res.json()["detail"]


def test_insufficient_data_returns_400():
    res = _client(InMemoryPriceRepository(demo_history(100))).get(
        "/api/predict", params={"ticker": "ANY"}
    )
    assert res.status_code == 400


def test_invalid_period_returns_422():
    res = _client().get("/api/predict", params={"ticker": "DEMO", "period": "3y"})
    assert res.status_code == 422
