import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Offer Center",
  description: "A job search operating system focused on decision quality."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

