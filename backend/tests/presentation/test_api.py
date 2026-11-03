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
    # 既定は「拡張特徴量 + ウォークフォワード」
    assert body["metrics"]["feature_set"] == "extended"
    assert body["metrics"]["validation"] == "walk_forward"
    assert body["metrics"]["benchmark"] == "DEMO_INDEX"


def test_predict_with_old_settings():
    res = _client().get(
        "/api/predict", params={"ticker": "DEMO", "feature_set": "basic", "validation": "holdout"}
    )
    assert res.status_code == 200
    m = res.json()["metrics"]
    assert (m["feature_set"], m["validation"], m["folds"], m["benchmark"]) == ("basic", "holdout", 1, None)


def test_invalid_options_return_422():
    c = _client()
    assert c.get("/api/predict", params={"ticker": "DEMO", "feature_set": "full"}).status_code == 422
    assert c.get("/api/predict", params={"ticker": "DEMO", "validation": "kfold"}).status_code == 422


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
