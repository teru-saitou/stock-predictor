// バックエンドの app/api/schemas.py の PredictResponse と対応する型

export type Period = "1y" | "2y" | "5y" | "10y" | "max";

export type PricePoint = { date: string; close: number };

export type EquityPoint = { date: string; strategy: number; buy_hold: number };

export type Metrics = {
  train_period: [string, string];
  test_period: [string, string];
  test_days: number;
  accuracy: number;
  baseline_accuracy: number;
  strategy_return: number;
  buy_hold_return: number;
  strategy_max_drawdown: number;
  buy_hold_max_drawdown: number;
  trades: number;
  cost_per_trade: number;
};

export type PredictResponse = {
  ticker: string;
  name: string | null;
  latest_date: string;
  latest_close: number;
  next_up_probability: number;
  metrics: Metrics;
  prices: PricePoint[];
  equity: EquityPoint[];
};
