import type { PredictResponse } from "@/types/predict";
import { pct } from "@/lib/format";
import { baselineTone, hints, isCoinFlip } from "@/lib/reading";
import { ConditionBar } from "./ConditionBar";
import { Stat } from "./Stat";
import { VerdictBanner } from "./VerdictBanner";

export function PredictionSummary({ data }: { data: PredictResponse }) {
  const m = data.metrics;
  const prob = data.next_up_probability;
  const beatsBaseline = m.accuracy > m.baseline_accuracy;
  const h = hints(m, prob);
  // 五分五分に近いときは色を付けない（緑＝「買い」と受け取られないように）
  const probTone = isCoinFlip(prob) ? undefined : prob > 0.5 ? "up" : "down";

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
      <VerdictBanner metrics={m} prob={prob} />
      <div className="grid">
        <Stat label="翌営業日に上がる確率" value={pct(prob)} tone={probTone} hint={h.probability} />
        <Stat label="テスト期間の正解率" value={pct(m.accuracy)} hint={h.accuracy} />
        <Stat
          label="ベースライン正解率"
          value={pct(m.baseline_accuracy)}
          tone={baselineTone(m)}
          hint={h.baseline}
        />
      </div>
      <p className="note">
        正解率はベースラインと比べて読みます。モデルの正解率はベースラインを
        {beatsBaseline ? "上回って" : "下回って"}います。差が数ポイント程度なら偶然の範囲であることが多いです。
      </p>
    </div>
  );
}
