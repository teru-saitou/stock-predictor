// どの条件で計算した結果かを表示する（設定を変えて比べるときの目印）
import type { Metrics } from "@/types/predict";

export function ConditionBar({ metrics: m }: { metrics: Metrics }) {
  const validation =
    m.validation === "walk_forward"
      ? `ウォークフォワード（${m.retrain_every}営業日ごとに再学習・計${m.folds}回）`
      : "ホールドアウト（1回だけ学習）";
  const features = `${m.feature_set === "extended" ? "拡張" : "基本"} ${m.feature_count}個`;

  return (
    <div className="conditions">
      <span className="cond">
        <span className="cond-label">検証</span>
        {validation}
      </span>
      <span className="cond">
        <span className="cond-label">特徴量</span>
        {features}
      </span>
      {m.feature_set === "extended" && (
        <span className="cond">
          <span className="cond-label">市場指数</span>
          {m.benchmark ?? "なし（取得できなかったか、指数そのもの）"}
        </span>
      )}
    </div>
  );
}
