import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import { ThemeProvider } from "@/components/ThemeProvider";

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
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased overflow-hidden`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          <div className="flex h-screen w-full relative">
            {/* Subtle Background Glows dynamically react to globals.css */}
            <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-rose-500/10 blur-[120px] pointer-events-none transition-colors duration-700" />
            <div className="absolute bottom-[-10%] left-[20%] w-[30%] h-[30%] bg-sky-500/10 blur-[100px] pointer-events-none transition-colors duration-700" />

            {/* Sidebar Area */}
            <div className="w-80 hidden lg:block shrink-0 h-full relative z-20">
              <Sidebar />
            </div>

            {/* Main Content Area */}
            <main className="flex-1 overflow-x-hidden overflow-y-auto relative z-10 custom-scrollbar">
              <div className="w-full max-w-[1600px] mx-auto p-10 lg:p-14 min-h-screen">
                {children}
              </div>
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
