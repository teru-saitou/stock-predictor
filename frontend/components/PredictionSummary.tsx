import type { PredictResponse } from "@/types/predict";
import { pct } from "@/lib/format";
import { ConditionBar } from "./ConditionBar";
import { Stat } from "./Stat";

export function PredictionSummary({ data }: { data: PredictResponse }) {
  const m = data.metrics;
  const prob = data.next_up_probability;
  const beatsBaseline = m.accuracy > m.baseline_accuracy;

  return (
    <div className="card">
      <div className="company">
        <span className="company-name">{data.name ?? data.ticker}</span>
        {data.name && <span className="ticker-badge">{data.ticker}</span>}
      </div>
      <h2>
        予測（{data.latest_date} 終値 {data.latest_close.toLocaleString()} 時点）
      </h2>
      <ConditionBar metrics={m} />
      <div className="grid">
        <Stat label="翌営業日に上がる確率" value={pct(prob)} tone={prob >= 0.5 ? "up" : "down"} />
        <Stat label="テスト期間の正解率" value={pct(m.accuracy)} />
        <Stat
          label="ベースライン正解率"
          value={pct(m.baseline_accuracy)}
          tone={beatsBaseline ? "up" : "down"}
        />
      </div>
      <p className="note">
        ベースライン＝学習期間に多かった方（上昇 or 下落）を毎日予測した場合。
        モデルの正解率がこれを{beatsBaseline ? "上回って" : "下回って"}います。
        差が数%程度なら偶然の範囲であることが多いです。
      </p>
    </div>
  );
}
