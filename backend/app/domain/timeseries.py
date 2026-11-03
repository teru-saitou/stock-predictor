"""時系列データの扱いに関するルール。"""


def chronological_split_point(n_rows: int, test_ratio: float) -> int:
    """時系列順に学習/テストへ分ける位置。先頭〜split-1 が学習、split〜末尾がテスト。

    シャッフルすると未来のデータで過去を当てることになる（リーク）ため、必ず時系列順に分ける。
    """
    if not 0 < test_ratio < 1:
        raise ValueError("test_ratio は 0 より大きく 1 未満にしてください")
    return int(n_rows * (1 - test_ratio))
