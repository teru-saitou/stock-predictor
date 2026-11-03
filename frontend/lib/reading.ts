// 初心者向けの「読み方」を数字から組み立てる。
// どんなに成績がよくても「参考程度」までしか言わない方針。
import type { Metrics } from "@/types/predict";
import { pct } from "./format";

// 正解率がベースラインをこれ未満しか上回らないなら「参考にならない」とみなす（ポイント）
export const MIN_EDGE_POINTS = 3;
// 上がる確率がこの範囲なら「ほぼ五分五分」とみなす
export const COIN_FLIP_RANGE: [number, number] = [0.45, 0.55];

export type Verdict = {
  level: "unreliable" | "reference";
  title: string;
  reasons: string[];
};

const points = (v: number) => (v * 100).toFixed(1);
const man = (ratio: number) => Math.round(100 * ratio).toLocaleString();

export function isCoinFlip(prob: number): boolean {
  return prob >= COIN_FLIP_RANGE[0] && prob <= COIN_FLIP_RANGE[1];
}

export function verdict(m: Metrics, prob: number): Verdict {
  const edge = m.accuracy - m.baseline_accuracy;
  const unreliable = edge * 100 < MIN_EDGE_POINTS;
  const reasons: string[] = [];

  if (edge < 0) {
    reasons.push(
      `過去の正解率 ${pct(m.accuracy)} は、学習期間に多かった方を毎日答えるだけの場合（${pct(m.baseline_accuracy)}）を下回っています。`,
    );
  } else if (unreliable) {
    reasons.push(
      `過去の正解率 ${pct(m.accuracy)} は、学習期間に多かった方を毎日答えるだけの場合（${pct(m.baseline_accuracy)}）と ${points(edge)} ポイントしか違いません。偶然の範囲です。`,
    );
  } else {
    reasons.push(
      `過去の正解率 ${pct(m.accuracy)} は基準（${pct(m.baseline_accuracy)}）を ${points(edge)} ポイント上回っていますが、1つの銘柄・1つの期間での結果で、この先も続くとは限りません。`,
    );
  }

  if (isCoinFlip(prob)) {
    reasons.push(`明日上がる確率 ${pct(prob)} はほぼ五分五分で、上がるとも下がるとも言えません。`);
  } else {
    const other = prob > 0.5 ? `下がる可能性も ${pct(1 - prob)}` : `上がる可能性も ${pct(prob)}`;
    reasons.push(`明日上がる確率は ${pct(prob)} ですが、${other} あります。`);
  }

  return {
    level: unreliable ? "unreliable" : "reference",
    title: unreliable ? "この予測は参考にならない水準です" : "この予測は参考程度にとどめてください",
    reasons,
  };
}

// 各数字の下に添える「→ どういう意味か」
export function hints(m: Metrics, prob: number) {
  return {
    probability: isCoinFlip(prob)
      ? "ほぼ五分五分。上がるとも下がるとも言えない"
      : prob > 0.5
        ? `やや上がりやすいという予測。ただし ${pct(1 - prob)} は下がる可能性`
        : `やや下がりやすいという予測。ただし ${pct(prob)} は上がる可能性`,
    accuracy: `テスト期間（${m.test_days}営業日）で、翌日に上がるか下がるかを当てた割合`,
    baseline: "学習期間に多かった方（上昇か下落）を毎日答えた場合の正解率。モデルを比べる基準",
    strategyReturn: `100万円が約${man(1 + m.strategy_return)}万円になった計算（過去の試算）`,
    buyHoldReturn: `最初に買って持ち続けた場合。100万円が約${man(1 + m.buy_hold_return)}万円`,
    drawdown: `途中でいちばん資金が減ったときの幅。買い持ちでは一時、100万円が約${man(1 + m.buy_hold_max_drawdown)}万円まで減った`,
    trades: `売買のたびに手数料がかかる（片道 ${pct(m.cost_per_trade, 2)} を差し引き済み）`,
  };
}
