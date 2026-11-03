"use client";

import { useState, type FormEvent } from "react";
import type { FeatureSet, Period, PredictOptions, Validation } from "@/types/predict";
import { TickerGuide } from "./TickerGuide";

type Props = {
  loading: boolean;
  onSubmit: (ticker: string, opts: PredictOptions) => void;
};

export function SearchForm({ loading, onSubmit }: Props) {
  const [ticker, setTicker] = useState("DEMO");
  const [period, setPeriod] = useState<Period>("5y");
  const [featureSet, setFeatureSet] = useState<FeatureSet>("extended");
  const [validation, setValidation] = useState<Validation>("walk_forward");

  const opts: PredictOptions = { period, featureSet, validation };

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSubmit(ticker.trim(), opts);
  }

  function handlePick(code: string) {
    setTicker(code);
    if (!loading) onSubmit(code, opts);
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

      <div className="options">
        <label>
          特徴量
          <select value={featureSet} onChange={(e) => setFeatureSet(e.target.value as FeatureSet)}>
            <option value="extended">拡張（市場指数・カレンダー等を追加）</option>
            <option value="basic">基本（テクニカル11種）</option>
          </select>
        </label>
        <label>
          検証方法
          <select value={validation} onChange={(e) => setValidation(e.target.value as Validation)}>
            <option value="walk_forward">ウォークフォワード（定期的に再学習）</option>
            <option value="holdout">ホールドアウト（1回だけ学習）</option>
          </select>
        </label>
      </div>

      <TickerGuide onPick={handlePick} />
    </>
  );
}
