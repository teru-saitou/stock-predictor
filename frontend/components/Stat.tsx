type Props = { label: string; value: string; tone?: "up" | "down" };

export function Stat({ label, value, tone }: Props) {
  return (
    <div className="stat">
      <div className="label">{label}</div>
      <div className={`value ${tone ?? ""}`}>{value}</div>
    </div>
  );
}
