// 銘柄コードの調べ方の案内と、クリックで入力できる例
type Example = { label: string; ticker: string };

const EXAMPLES: Example[] = [
  { label: "トヨタ", ticker: "7203.T" },
  { label: "ソニーG", ticker: "6758.T" },
  { label: "任天堂", ticker: "7974.T" },
  { label: "日経平均", ticker: "^N225" },
  { label: "Apple", ticker: "AAPL" },
  { label: "NVIDIA", ticker: "NVDA" },
  { label: "デモ", ticker: "DEMO" },
];

export function TickerGuide({ onPick }: { onPick: (ticker: string) => void }) {
  return (
    <div className="guide">
      <div className="chips">
        {EXAMPLES.map((e) => (
          <button key={e.ticker} type="button" className="chip" onClick={() => onPick(e.ticker)}>
            {e.label} <span className="chip-code">{e.ticker}</span>
          </button>
        ))}
      </div>

      <details>
        <summary>銘柄コードの調べ方</summary>
        <p>
          銘柄コードは <strong>Yahoo Finance の表記</strong> で入力します。
          分からないときは、Yahoo Finance で会社名を検索してコードを確認してください。
        </p>
        <ul>
          <li>
            <strong>日本株</strong>：4桁の証券コード + <code>.T</code>（例：トヨタ → <code>7203.T</code>）。
            <a href="https://finance.yahoo.co.jp/" target="_blank" rel="noopener noreferrer">
              Yahoo!ファイナンス
            </a>
            で会社名を検索すると、名前の横にコードが表示されます。<code>285A</code> のような英字入りのコードも <code>285A.T</code> でOKです。
          </li>
          <li>
            <strong>米国株</strong>：ティッカーシンボルをそのまま（例：Apple → <code>AAPL</code>）。
            <a href="https://finance.yahoo.com/" target="_blank" rel="noopener noreferrer">
              Yahoo Finance（英語版）
            </a>
            で確認できます。
          </li>
          <li>
            <strong>指数</strong>：日経平均 <code>^N225</code>、S&amp;P 500 <code>^GSPC</code>、NASDAQ総合 <code>^IXIC</code>
          </li>
        </ul>
        <p className="note">
          株価は配当・株式分割を反映した「調整後」の値のため、過去の値は実際の株価と少しずれることがあります。
        </p>
      </details>
    </div>
  );
}
