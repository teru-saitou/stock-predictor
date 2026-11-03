"""予測に関するポート（抽象）。

どんな特徴量を作るか・どのライブラリで学習するかは「詳細」なので、
ここでは振る舞いだけを定義し、実装は infrastructure/ml に置く。
"""
from collections.abc import Callable
from typing import Protocol

import numpy as np
import pandas as pd

from app.domain.entities import PriceHistory


class FeatureBuilder(Protocol):
    # True のとき、ユースケースは市場指数（ベンチマーク）の株価も取得して渡す
    uses_benchmark: bool

    def build(self, history: PriceHistory, benchmark: PriceHistory | None = None) -> pd.DataFrame:
        """index=日付（history と同じ）、列=特徴量の DataFrame を返す。

        日付 t の行は「t の終値時点までに分かる情報」だけで作ること（未来の情報を使わない）。
        計算できない行は NaN のままでよい。benchmark が None でも動くこと。
        """
        ...


class Predictor(Protocol):
    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
        ...

    def predict_proba_up(self, features: pd.DataFrame) -> np.ndarray:
        """各行について「翌日に上がる確率」を返す。"""
        ...


# 学習のたびに新しいモデルを作るためのファクトリ
PredictorFactory = Callable[[], Predictor]
