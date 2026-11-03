"use client";

import { useState, type FormEvent } from "react";
import type { Period } from "@/types/predict";
import { TickerGuide } from "./TickerGuide";

type Props = {
  loading: boolean;
  onSubmit: (ticker: string, period: Period) => void;
};

export function SearchForm({ loading, onSubmit }: Props) {
  const [ticker, setTicker] = useState("DEMO");
  const [period, setPeriod] = useState<Period>("5y");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSubmit(ticker.trim(), period);
  }

  function handlePick(code: string) {
    setTicker(code);
    if (!loading) onSubmit(code, period);
  }

  return (
    <>
      <form onSubmit={handleSubmit}>
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="銘柄コード（例: 7203.T, AAPL, ^N225）"
          aria-label="銘柄コード"
        />
        <select value={period} onChange={(e) => setPeriod(e.target.value as Period)} aria-label="期間">
          <option value="2y">2年</option>
          <option value="5y">5年</option>
          <option value="10y">10年</option>
          <option value="max">全期間</option>
        </select>
        <button type="submit" disabled={loading || !ticker.trim()}>
          {loading ? "計算中…" : "予測する"}
        </button>
      </form>
      <TickerGuide onPick={handlePick} />
    </>
  );
}
