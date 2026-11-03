"use client";

import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import type { EquityPoint, Metrics } from "@/types/predict";
import { pct } from "@/lib/format";
import { hints } from "@/lib/reading";
import { Stat } from "./Stat";

type Props = { metrics: Metrics; equity: EquityPoint[]; prob: number };

export function BacktestResult({ metrics: m, equity, prob }: Props) {
  const h = hints(m, prob);
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
      <ul className="chart-hints">
        <li>縦軸：最初の資金を 1 とした倍率（1.2 なら +20%、0.8 なら -20%）</li>
        <li>青線：モデルが「上がる」と予測した日だけ株を持った場合</li>
        <li>灰色の線：最初に買って持ち続けた場合（比べる基準）</li>
        <li>青線が平ら：「下がる」と予測して株を持たず、待っていた期間</li>
      </ul>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={equity} margin={{ top: 16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="date" minTickGap={60} tick={{ fontSize: 11 }} />
          <YAxis domain={["auto", "auto"]} tick={{ fontSize: 11 }} width={60} />
          <Tooltip formatter={(v) => (typeof v === "number" ? v.toFixed(3) : String(v ?? ""))} />
          <Legend />
          <Line type="monotone" dataKey="strategy" name="モデル戦略" stroke="var(--accent)" dot={false} strokeWidth={1.5} />
          <Line type="monotone" dataKey="buy_hold" name="買い持ち" stroke="var(--muted)" dot={false} strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
      <p className="note">
        「上がる」と予測した日の終値で買い、翌日終値まで保有する単純な戦略です。
        片道 {pct(m.cost_per_trade, 2)} の取引コストを差し引いています。
        {m.validation === "walk_forward"
          ? `最初の学習期間: ${m.train_period[0]} 〜 ${m.train_period[1]}。以降は${m.retrain_every}営業日ごとに、その時点までの全データで学習し直しています。`
          : `学習期間: ${m.train_period[0]} 〜 ${m.train_period[1]}。`}
        これは学習用のシミュレーションで、将来の成績を保証するものではありません。
      </p>
    </div>
  );
}
