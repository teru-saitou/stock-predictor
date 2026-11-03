"""時系列データの扱いに関するルール。

シャッフルすると未来のデータで過去を当てることになる（リーク）ため、
学習データは必ずテストデータより過去に限る。
"""
from dataclasses import dataclass


def chronological_split_point(n_rows: int, test_ratio: float) -> int:
    """時系列順に学習/テストへ分ける位置。先頭〜split-1 が学習、split〜末尾がテスト。"""
    if not 0 < test_ratio < 1:
        raise ValueError("test_ratio は 0 より大きく 1 未満にしてください")
    return int(n_rows * (1 - test_ratio))


@dataclass(frozen=True)
class Fold:
    """1回分の学習・予測の範囲（行番号、終端は含まない）。

    学習は [0, train_end)、予測は [test_start, test_end)。
    """

    train_end: int
    test_start: int
    test_end: int


def walk_forward_folds(n_rows: int, test_ratio: float, retrain_every: int) -> list[Fold]:
    """ウォークフォワード検証の区切り（拡大ウィンドウ方式）。

    テスト期間を retrain_every 行ずつに区切り、各区間の直前までの全データで学習し直す。
    実運用で「定期的にモデルを作り直しながら使う」状況を再現する。
    """
    if retrain_every < 1:
        raise ValueError("retrain_every は 1 以上にしてください")
    start = chronological_split_point(n_rows, test_ratio)
    return [
        Fold(train_end=s, test_start=s, test_end=min(s + retrain_every, n_rows))
        for s in range(start, n_rows, retrain_every)
    ]


def holdout_folds(n_rows: int, test_ratio: float) -> list[Fold]:
    """ホールドアウト検証：1回だけ学習し、テスト期間全体を予測する。"""
    return walk_forward_folds(n_rows, test_ratio, retrain_every=n_rows)
