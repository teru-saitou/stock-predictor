"""予測精度の評価。"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class AccuracyReport:
    accuracy: float
    baseline_accuracy: float


def evaluate_accuracy(pred: np.ndarray, actual: pd.Series, train_target: pd.Series) -> AccuracyReport:
    """モデルの正解率と、ベースライン（学習期間に多かった方を毎日予測）の正解率。"""
    accuracy = float((pred == actual.to_numpy()).mean())
    majority = int(train_target.mean() >= 0.5)
    baseline = float((actual == majority).mean())
    return AccuracyReport(accuracy=accuracy, baseline_accuracy=baseline)
