"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { FiMenu, FiX, FiGrid, FiUploadCloud, FiBarChart2, FiPlay, FiMessageSquare, FiSettings } from "react-icons/fi";
import { motion, AnimatePresence } from "framer-motion";
import { ThemeToggle } from "./ThemeToggle";

export default function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: <FiGrid size={20} /> },
    { name: "Upload", path: "/upload", icon: <FiUploadCloud size={20} /> },
    { name: "Insights", path: "/insights", icon: <FiBarChart2 size={20} /> },
    { name: "Simulation", path: "/simulation", icon: <FiPlay size={20} /> },
    { name: "Chat", path: "/chat", icon: <FiMessageSquare size={20} /> },
  ];

  const toggleMenu = () => setIsOpen(!isOpen);

  return (
    <div className="lg:hidden">
      {/* Mobile Header Bar */}
      <div className="h-20 px-6 flex items-center justify-between bg-white/60 dark:bg-[#0b0f19]/80 backdrop-blur-xl border-b border-cool-gray dark:border-white/5 sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-sapphire via-emerald to-amber shadow-lg"></div>
          <h1 className="text-xl font-black tracking-tighter text-navy dark:text-white">
            Deci<span className="text-transparent bg-clip-text bg-gradient-to-r from-sapphire to-emerald">Flow</span>
          </h1>
        </div>
        
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <button 
            onClick={toggleMenu}
            className="p-2 rounded-xl bg-ice-blue dark:bg-white/5 text-navy dark:text-white"
          >
            {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
          </button>
        </div>
      </div>

      {/* Slide-over Menu */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={toggleMenu}
              className="fixed inset-0 bg-navy/20 dark:bg-black/60 backdrop-blur-sm z-[60]"
            />
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed right-0 top-0 bottom-0 w-[80%] max-w-xs bg-white dark:bg-[#0b0f19] z-[70] p-8 flex flex-col shadow-2xl"
            >
              <div className="flex justify-between items-center mb-10">
                <span className="text-xs font-black text-muted-text dark:text-white/30 uppercase tracking-[0.3em]">Navigation</span>
                <button onClick={toggleMenu} className="p-2 text-navy dark:text-white">
                  <FiX size={24} />
                </button>
              </div>

              <nav className="flex-1 space-y-2">
                {navItems.map((item) => {
                  const isActive = pathname === item.path || (pathname === "/" && item.path === "/dashboard");
                  return (
                    <Link
                      key={item.path}
                      href={item.path}
                      onClick={() => setIsOpen(false)}
                      className={`
                        flex items-center gap-4 px-5 py-4 rounded-2xl transition-all
                        ${isActive 
                          ? "bg-ice-blue dark:bg-sapphire/10 text-sapphire dark:text-white border border-cool-gray dark:border-white/10" 
                          : "text-body-text dark:text-gray-400"}
                      `}
                    >
                      {item.icon}
                      <span className="font-bold">{item.name}</span>
                    </Link>
                  );
                })}
              </nav>

              <div className="mt-auto pt-8 border-t border-cool-gray dark:border-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sapphire via-emerald to-amber p-[1px]">
                    <div className="w-full h-full rounded-xl bg-white dark:bg-black/40 flex items-center justify-center text-navy dark:text-white font-bold">
                      A
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-black text-navy dark:text-white">Aarav Gupta</p>
                    <p className="text-[10px] font-bold text-muted-text uppercase tracking-wider">Strategic Admin</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
