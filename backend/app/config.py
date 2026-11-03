"""実行環境ごとの設定値。"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])
    test_ratio: float = 0.3
    min_rows: int = 200
    chart_days: int = 500


settings = Settings()
