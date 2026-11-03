"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { PricePoint } from "@/types/predict";

export function PriceChart({ prices }: { prices: PricePoint[] }) {
  return (
    <div className="card">
      <h2>株価（直近）</h2>
      <ul className="chart-hints">
        <li>横軸：日付（左が過去、右が最新）</li>
        <li>縦軸：株価（円）</li>
        <li>線にマウスを置くと、その日の終値が出ます</li>
        <li>実際の値動きだけを表示していて、予測は含みません</li>
      </ul>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={prices}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="date" minTickGap={60} tick={{ fontSize: 11 }} />
          <YAxis domain={["auto", "auto"]} tick={{ fontSize: 11 }} width={60} />
          <Tooltip />
          <Line type="monotone" dataKey="close" name="終値" stroke="var(--accent)" dot={false} strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
