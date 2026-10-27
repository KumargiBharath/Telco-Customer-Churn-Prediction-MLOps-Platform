// app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppProvider } from "./context/AppContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Churn Prediction App",
  description: "Predict customer churn with AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    // suppressHydrationWarning is needed for dark mode to work with Next.js
    <html lang="en" suppressHydrationWarning>
      {/* bg-gray-50 (light mode) and dark:bg-gray-900 (dark mode) */}
      <body
        className={`${inter.className} bg-gray-50 dark:bg-gray-900 transition-colors`}
      >
        <AppProvider>{children}</AppProvider>
      </body>
    </html>
  );
}
