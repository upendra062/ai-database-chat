import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Database Chat Agent",
  description: "LLM-powered agent for database queries",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
