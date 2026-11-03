"""ポート（外部とのやり取り）の契約として定義する例外。

infrastructure のアダプタはこれらを投げ、presentation が HTTP ステータスに変換する。
"""


class ApplicationError(Exception):
    """アプリケーション層の例外の基底クラス。"""


class DataNotFoundError(ApplicationError):
    """銘柄のデータが見つからなかった。"""


class DataSourceError(ApplicationError):
    """外部データソースとの通信に失敗した。"""
