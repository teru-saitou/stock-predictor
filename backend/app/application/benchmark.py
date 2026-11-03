"""銘柄ごとに比較対象とする市場指数（ベンチマーク）を決めるルール。

同じ取引所の指数を使う。取引時間が違う市場の指数（例：日本株に S&P 500）を
同じ日付で使うと、日本の終値より後に決まる値を使うことになり、リークになるため。
"""


def benchmark_ticker_for(ticker: str) -> str | None:
    t = ticker.upper()
    if t.startswith("^"):
        return None  # 指数そのものには比較対象を付けない
    if t.startswith("DEMO"):
        return "DEMO_INDEX" if t != "DEMO_INDEX" else None
    if t.endswith(".T"):
        return "^N225"  # 東証 → 日経平均
    return "^GSPC"  # それ以外（米国株を想定）→ S&P 500
