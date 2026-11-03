"use client";

import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { EquityPoint, Metrics, PricePoint } from "@/types/predict";
import { pct } from "@/lib/format";
import { hints } from "@/lib/reading";
import { Stat } from "./Stat";

type Props = { metrics: Metrics; equity: EquityPoint[]; prices: PricePoint[]; prob: number };

// 日付 t の資産額は「t の終値で持ち、翌営業日の終値まで保有した結果」なので、
// ツールチップには翌営業日の株価を日付付きで添える
type ChartPoint = EquityPoint & { priceDate?: string; close?: number };

function withPrices(equity: EquityPoint[], prices: PricePoint[]): ChartPoint[] {
  const index = new Map(prices.map((p, i) => [p.date, i]));
  return equity.map((e) => {
    const next = prices[(index.get(e.date) ?? -2) + 1];
    return next ? { ...e, priceDate: next.date, close: next.close } : e;
  });
}

type TooltipProps = { active?: boolean; payload?: { payload: ChartPoint }[] };

function EquityTooltip({ active, payload }: TooltipProps) {
  const p = payload?.[0]?.payload;
  if (!active || !p) return null;
  return (
    <div className="chart-tooltip">
      <div className="tt-date">{p.date}</div>
      <div className="tt-strategy">モデルどおり売買：{p.strategy.toFixed(3)}</div>
      <div className="tt-buyhold">株価の動き（買い持ち）：{p.buy_hold.toFixed(3)}</div>
      {p.close !== undefined && (
        <div className="tt-price">
          株価：{Math.round(p.close).toLocaleString()}円（{p.priceDate} 終値）
        </div>
      )}
    </div>
  );
}

export function BacktestResult({ metrics: m, equity, prices, prob }: Props) {
  const h = hints(m, prob);
  const data = withPrices(equity, prices);
  return (
    <div className="card">
      <h2>バックテスト（{m.test_period[0]} 〜 {m.test_period[1]}）</h2>
      <p className="lead">もし過去にこのモデルの予測どおり売買していたら、お金がどう増減したかを試算したものです。</p>
      <div className="grid">
        <Stat
          label="モデル戦略のリターン"
          value={pct(m.strategy_return)}
          tone={m.strategy_return >= 0 ? "up" : "down"}
          hint={h.strategyReturn}
        />
        <Stat
          label="買い持ちのリターン"
          value={pct(m.buy_hold_return)}
          tone={m.buy_hold_return >= 0 ? "up" : "down"}
          hint={h.buyHoldReturn}
        />
        <Stat
          label="最大下落（モデル / 買い持ち）"
          value={`${pct(m.strategy_max_drawdown)} / ${pct(m.buy_hold_max_drawdown)}`}
          hint={h.drawdown}
        />
        <Stat label="売買回数" value={`${m.trades}回`} hint={h.trades} />
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="date" minTickGap={60} tick={{ fontSize: 11 }} />
          <YAxis domain={["auto", "auto"]} tick={{ fontSize: 11 }} width={60} />
          <Tooltip content={<EquityTooltip />} />
          <Legend />
          <Line type="monotone" dataKey="strategy" name="青：モデルどおり売買" stroke="var(--accent)" dot={false} strokeWidth={1.5} />
          <Line type="monotone" dataKey="buy_hold" name="灰色：株価の動き（買い持ち）" stroke="var(--muted)" dot={false} strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
      <p className="note">過去の試算で、将来の成績を保証するものではありません。</p>
      <details className="more">
        <summary>詳しい見方と前提</summary>
        <h3>グラフの見方</h3>
        <ul>
          <li>縦軸は、最初の資金を 1 とした倍率です（1.2 なら +20%、0.8 なら -20%）。</li>
          <li>青線は、モデルが「上がる」と予測した日だけ株を持った場合です。</li>
          <li>灰色の線は、テスト期間初日の株価を 1 とした株価の動きです（最初に買って持ち続けた場合と同じ）。</li>
          <li>青線が平らな期間は、「下がる」と予測して株を持たず、待っていた期間です。</li>
          <li>線にマウスを置くと、その時点の実際の株価（円）も表示されます。</li>
        </ul>
        <h3>計算の前提</h3>
        <ul>
          <li>「上がる」と予測した日の終値で買い、翌日の終値まで保有する単純な戦略です。</li>
          <li>片道 {pct(m.cost_per_trade, 2)} の取引コストを差し引いています。</li>
          <li>
            {m.validation === "walk_forward"
              ? `最初の学習期間は ${m.train_period[0]} 〜 ${m.train_period[1]} です。以降は${m.retrain_every}営業日ごとに、その時点までの全データで学習し直しています。`
              : `学習期間は ${m.train_period[0]} 〜 ${m.train_period[1]} です。`}
          </li>
          <li>実際には利益に約20%（20.315%）の税金がかかりますが、この試算には含めていません。</li>
          <li>学習用のシミュレーションで、将来の成績を保証するものではありません。</li>
        </ul>
      </details>
    </div>
  );
}
