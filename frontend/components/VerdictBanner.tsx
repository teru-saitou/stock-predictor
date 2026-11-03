// 結果の先頭で「この予測をどこまで信じてよいか」を一言で伝える
import type { Metrics } from "@/types/predict";
import { verdict } from "@/lib/reading";

export function VerdictBanner({ metrics, prob }: { metrics: Metrics; prob: number }) {
  const v = verdict(metrics, prob);
  return (
    <div className={`verdict ${v.level}`} role="note">
      <strong>⚠ {v.title}</strong>
      <ul>
        {v.reasons.map((r) => (
          <li key={r}>{r}</li>
        ))}
      </ul>
      <p>この結果だけで売買を決めないでください。</p>
    </div>
  );
}
