"use client";

import React, { Suspense } from "react";
import Sidebar from "@/components/Sidebar";
import MobileNav from "@/components/MobileNav";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex flex-col lg:flex-row min-h-screen w-full relative">
      {/* Global Animated Background */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-emerald/5 rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] left-[10%] w-[40%] h-[40%] bg-sapphire/5 rounded-full animate-pulse [animation-delay:2s]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] brightness-100 contrast-150" />
      </div>

      <Suspense fallback={null}>
        <MobileNav />
      </Suspense>

      {/* Sidebar Area - Desktop */}
      <div className="hidden lg:block w-80 shrink-0 h-screen sticky top-0 z-20">
        <Suspense fallback={null}>
          <Sidebar />
        </Suspense>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 relative z-10 min-h-screen">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ 
              duration: 0.4, 
              ease: [0.16, 1, 0.3, 1] 
            }}
            className="w-full max-w-[1600px] mx-auto p-4 md:p-8 lg:p-12"
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
