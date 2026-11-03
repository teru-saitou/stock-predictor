// バックエンド API の呼び出しはすべてここに集める
import type { NightlyReport } from "@/types/nightly";
import type { PredictOptions, PredictResponse } from "@/types/predict";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

export async function fetchPrediction(ticker: string, opts: PredictOptions): Promise<PredictResponse> {
  const q = new URLSearchParams({
    ticker,
    period: opts.period,
    feature_set: opts.featureSet,
    validation: opts.validation,
  });
  let res: Response;
  try {
    res = await fetch(`${API_URL}/api/predict?${q}`);
  } catch {
    throw new ApiError("バックエンドに接続できません。起動しているか確認してください。", 0);
  }
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = typeof body.detail === "string" ? body.detail : "入力内容を確認してください";
    throw new ApiError(detail, res.status);
  }
  return body as PredictResponse;
}

// 毎朝 GitHub Actions が計算して置いておく結果（API サーバーは使わない）
export async function fetchNightlyReport(): Promise<NightlyReport | null> {
  const res = await fetch("/nightly.json", { cache: "no-store" }).catch(() => null);
  if (!res || res.status === 404) return null;
  if (!res.ok) throw new ApiError("毎朝の予測を読み込めませんでした", res.status);
  return (await res.json()) as NightlyReport;
}
