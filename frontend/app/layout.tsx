import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PlotLens × Type B Digital | Grounded movie intelligence",
  description: "A Type B Digital-inspired RAG experience for exploring movie plots with visible evidence.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
