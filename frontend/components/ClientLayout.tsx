"use client";

import React from "react";
import Sidebar from "@/components/Sidebar";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-full relative">
      {/* Global Animated Background */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-emerald/5 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] left-[10%] w-[40%] h-[40%] bg-sapphire/5 blur-[100px] rounded-full animate-pulse [animation-delay:2s]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] brightness-100 contrast-150" />
      </div>

      {/* Sidebar Area */}
      <div className="w-80 hidden lg:block shrink-0 h-full relative z-20">
        <Sidebar />
      </div>

      {/* Main Content Area */}
      <main className="flex-1 relative z-10 overflow-hidden h-full">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={pathname}
            initial={{ opacity: 0, x: 20, filter: "blur(10px)" }}
            animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
            exit={{ opacity: 0, x: -20, filter: "blur(10px)" }}
            transition={{ 
              duration: 0.5, 
              ease: [0.16, 1, 0.3, 1] 
            }}
            className="h-full overflow-y-auto custom-scrollbar"
          >
            <div className="w-full max-w-[1600px] mx-auto p-8 lg:p-12 min-h-full">
              {children}
            </div>
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
