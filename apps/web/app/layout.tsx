import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentDesk",
  description: "Open-source AI Support Agent Platform"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

