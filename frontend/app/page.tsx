"use client";

import { useState } from "react";
import { BacktestResult } from "@/components/BacktestResult";
import { PredictionSummary } from "@/components/PredictionSummary";
import { PriceChart } from "@/components/PriceChart";
import { SearchForm } from "@/components/SearchForm";
import { fetchPrediction } from "@/lib/api";
import type { PredictOptions, PredictResponse } from "@/types/predict";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<PredictResponse | null>(null);

  async function handleSearch(ticker: string, opts: PredictOptions) {
    setLoading(true);
    setError(null);
    try {
      setData(await fetchPrediction(ticker, opts));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Stock Predictor</h1>
      <p className="sub">翌営業日の騰落を予測し、過去データで検証します</p>

      <div className="card">
        <SearchForm loading={loading} onSubmit={handleSearch} />
        {error && <p className="error">{error}</p>}
      </div>

      {data && (
        <>
          <PredictionSummary data={data} />
          <PriceChart prices={data.prices} />
          <BacktestResult metrics={data.metrics} equity={data.equity} prob={data.next_up_probability} />
        </>
      )}
    </main>
  );
}
