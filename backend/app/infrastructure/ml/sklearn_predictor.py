"""Predictor の scikit-learn 実装。

LightGBM や深層学習に変えたいときは、同じ fit / predict_proba_up を持つクラスを作り、
container.py で差し替える。
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier


class SklearnUpDownPredictor:
    def __init__(self) -> None:
        self._clf = HistGradientBoostingClassifier(
            max_depth=3, learning_rate=0.05, max_iter=200, random_state=0
        )

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
        self._clf.fit(features, labels)

    def predict_proba_up(self, features: pd.DataFrame) -> np.ndarray:
        return self._clf.predict_proba(features)[:, 1]
