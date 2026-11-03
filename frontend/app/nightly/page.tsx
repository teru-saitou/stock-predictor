"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BacktestResult } from "@/components/BacktestResult";
import { PredictionSummary } from "@/components/PredictionSummary";
import { PriceChart } from "@/components/PriceChart";
import { fetchNightlyReport } from "@/lib/api";
import { pct } from "@/lib/format";
import { baselineTone, isCoinFlip } from "@/lib/reading";
import type { NightlyReport } from "@/types/nightly";
import type { PredictResponse } from "@/types/predict";

const jst = (iso: string) =>
  new Date(iso).toLocaleString("ja-JP", { timeZone: "Asia/Tokyo", dateStyle: "medium", timeStyle: "short" });

export default function Nightly() {
  const [report, setReport] = useState<NightlyReport | null | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<PredictResponse | null>(null);

  useEffect(() => {
    fetchNightlyReport()
      .then(setReport)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  return (
    <main>
      <h1>毎朝の予測</h1>
      <p className="sub">
        決まった銘柄を毎朝 7:00 ごろに計算し直しています（5年分・拡張特徴量・ウォークフォワード）。
        ほかの銘柄や条件は<Link href="/">トップ</Link>から調べられます。
      </p>

      <div className="card">
        {error && <p className="error">{error}</p>}
        {report === undefined && !error && <p className="note">読み込み中…</p>}
        {report === null && <p className="note">まだ一度も計算されていません。</p>}
        {report && (
          <>
            <h2>{jst(report.generated_at)} 更新</h2>
            <div className="table-wrap">
              <table className="nightly">
                <thead>
                  <tr>
                    <th>銘柄</th>
                    <th>翌営業日に上がる確率</th>
                    <th>正解率（ベースライン）</th>
                    <th>戦略（買い持ち）</th>
                  </tr>
                </thead>
                <tbody>
                  {report.results.map((r) =>
                    "error" in r ? (
                      <tr key={r.ticker}>
                        <td>{r.ticker}</td>
                        <td colSpan={3} className="error">計算できませんでした: {r.error}</td>
                      </tr>
                    ) : (
                      <Row
                        key={r.ticker}
                        data={r.data}
                        active={selected?.ticker === r.ticker}
                        onSelect={() => setSelected(r.data)}
                      />
                    ),
                  )}
                </tbody>
              </table>
            </div>
            <p className="note">行を押すと、くわしい結果を下に表示します。</p>
          </>
        )}
      </div>

      {selected && (
        <>
          <PredictionSummary data={selected} />
          <PriceChart prices={selected.prices} />
          <BacktestResult
            metrics={selected.metrics}
            equity={selected.equity}
            prices={selected.prices}
            prob={selected.next_up_probability}
          />
        </>
      )}
    </main>
  );
}

type RowProps = { data: PredictResponse; active: boolean; onSelect: () => void };

function Row({ data, active, onSelect }: RowProps) {
  const m = data.metrics;
  const prob = data.next_up_probability;
  // 色の付け方は PredictionSummary と揃える
  const probTone = isCoinFlip(prob) ? undefined : prob > 0.5 ? "up" : "down";
  return (
    <tr className={active ? "active" : undefined} onClick={onSelect}>
      <td>
        <span className="row-name">{data.name ?? data.ticker}</span>
        {data.name && <span className="ticker-badge">{data.ticker}</span>}
      </td>
      <td className={probTone}>{pct(prob)}</td>
      <td>
        <span className={baselineTone(m)}>{pct(m.accuracy)}</span>
        <span className="muted">（{pct(m.baseline_accuracy)}）</span>
      </td>
      <td>
        {pct(m.strategy_return)}
        <span className="muted">（{pct(m.buy_hold_return)}）</span>
      </td>
    </tr>
  );
}
