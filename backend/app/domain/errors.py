"""ドメインのルール違反を表す例外。"""


class DomainError(Exception):
    """ドメイン層の例外の基底クラス。"""


class InvalidPriceDataError(DomainError):
    """株価データが形式を満たしていない。"""


class InsufficientDataError(DomainError):
    """学習・検証に必要なデータ量が足りない。"""
