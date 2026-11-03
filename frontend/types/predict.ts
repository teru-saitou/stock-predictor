// バックエンドの app/presentation/api/schemas.py の PredictResponse と対応する型

export type Period = "1y" | "2y" | "5y" | "10y" | "max";
export type FeatureSet = "basic" | "extended";
export type Validation = "walk_forward" | "holdout";

export type PredictOptions = {
  period: Period;
  featureSet: FeatureSet;
  validation: Validation;
};

// open は古い nightly.json には無いことがある
export type PricePoint = { date: string; close: number; open?: number };

// date は売買の結果が確定した日（その日の始値で評価）
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
  validation: Validation;
  retrain_every: number | null;
  folds: number;
  feature_set: FeatureSet;
  feature_count: number;
  benchmark: string | null;
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
