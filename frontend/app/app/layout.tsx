import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DeciFlow AI",
  description: "Next Generation AI Dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#0B0F1A] text-gray-100 antialiased overflow-hidden`}>
        <div className="flex h-screen w-full">
          {/* Sidebar Area */}
          <div className="w-72 hidden md:block">
            <Sidebar />
          </div>

          {/* Main Content Area */}
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-900/20 via-[#0B0F1A] to-[#0B0F1A]">
            <div className="w-full max-w-7xl mx-auto p-6 md:p-10">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}