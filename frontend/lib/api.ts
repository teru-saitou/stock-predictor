// バックエンド API の呼び出しはすべてここに集める
import type { Period, PredictResponse } from "@/types/predict";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

export async function fetchPrediction(ticker: string, period: Period): Promise<PredictResponse> {
  const q = new URLSearchParams({ ticker, period });
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
