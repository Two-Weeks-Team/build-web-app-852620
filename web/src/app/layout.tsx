import type { Metadata } from "next";
import { Lora, Manrope } from "next/font/google";
import "@/app/globals.css";

const display = Lora({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display"
});

const body = Manrope({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body"
});

export const metadata: Metadata = {
  title: "Field Journal Financial Planner",
  description: "Turn messy money details into a clear personal financial plan you can act on today."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${display.variable} ${body.variable} bg-background text-foreground`}>{children}</body>
    </html>
  );
}
