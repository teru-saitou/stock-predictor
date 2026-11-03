// バックエンドの app/presentation/batch/nightly.py が書き出す nightly.json と対応する型
import type { PredictResponse } from "./predict";

export type NightlyResult =
  | { ticker: string; data: PredictResponse }
  | { ticker: string; error: string };

export type NightlyReport = {
  generated_at: string; // UTC の ISO 形式
  results: NightlyResult[];
};
