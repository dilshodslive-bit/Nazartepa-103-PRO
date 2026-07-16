import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";

export const metadata: Metadata = {
  title: "Nazartepa 103",
  description: "AI asosidagi tez tibbiy yordam dispetcherligi",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uz">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
