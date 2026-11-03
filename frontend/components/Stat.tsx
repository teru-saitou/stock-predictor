type Props = { label: string; value: string; tone?: "up" | "down"; hint?: string };

export function Stat({ label, value, tone, hint }: Props) {
  return (
    <div className="stat">
      <div className="label">{label}</div>
      <div className={`value ${tone ?? ""}`}>{value}</div>
      {hint && <div className="hint">→ {hint}</div>}
    </div>
  );
}
