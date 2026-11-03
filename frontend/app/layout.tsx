import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Stock Predictor",
  description: "株価の騰落予測とバックテスト",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
