"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";
import { FiGrid, FiUploadCloud, FiBarChart2, FiPlay, FiMessageSquare, FiSettings } from "react-icons/fi";
import { ThemeToggle } from "./ThemeToggle";
import { motion } from "framer-motion";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: <FiGrid size={20} /> },
    { name: "Upload", path: "/upload", icon: <FiUploadCloud size={20} /> },
    { name: "Insights", path: "/insights", icon: <FiBarChart2 size={20} /> },
    { name: "Simulation", path: "/simulation", icon: <FiPlay size={20} /> },
    { name: "Chat", path: "/chat", icon: <FiMessageSquare size={20} /> },
  ];

  return (
    <div className="w-80 bg-white/60 dark:bg-[#0b0f19]/80 border-r border-slate-200 dark:border-white/5 backdrop-blur-3xl p-8 flex flex-col fixed h-full left-0 top-0 z-50 transition-colors duration-500">
      <div className="mb-14 mt-2 flex items-center justify-between">
        <div className="flex items-center gap-4 group cursor-pointer">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-sky-400 via-rose-400 to-amber-400 shadow-[0_0_20px_rgba(244,63,94,0.3)] group-hover:scale-110 group-hover:rotate-6 transition-all duration-500"></div>
          <div>
            <h1 className="text-2xl font-black tracking-tighter text-slate-900 dark:text-white transition-colors duration-500 flex items-center gap-2">
              <span>Deci<span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 to-rose-500">Flow</span></span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-lg bg-rose-100 dark:bg-rose-500/20 border border-rose-200 dark:border-rose-500/30 text-rose-600 dark:text-rose-400 tracking-widest uppercase shadow-sm">AI</span>
            </h1>
          </div>
        </div>
        <ThemeToggle />
      </div>

      <nav className="flex-1 space-y-3">
        {navItems.map((item, index) => {
          const isActive = pathname === item.path || (pathname === "/" && item.path === "/dashboard");
          
          return (
            <motion.div
              key={item.path}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Link
                href={item.path}
                className={`
                  flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-500 relative group
                  ${isActive 
                    ? "bg-sky-50 dark:bg-white/[0.03] text-sky-700 dark:text-white border border-sky-100 dark:border-white/10 shadow-[0_4px_20px_rgba(14,165,233,0.1)] dark:shadow-[0_4px_20px_rgba(14,165,233,0.2)]" 
                    : "text-slate-500 hover:text-slate-900 dark:text-gray-400 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-white/[0.02] border border-transparent"}
                `}
              >
                {isActive && (
                   <motion.div layoutId="sidebar-active" className="absolute left-[-8px] w-2 h-8 bg-gradient-to-b from-sky-400 to-rose-400 rounded-full blur-[1px] shadow-[0_0_15px_rgba(244,63,94,0.8)]" />
                )}
                <span className={`${isActive ? "text-sky-600 dark:text-sky-400" : "group-hover:text-sky-500"} transition-colors`}>{item.icon}</span>
                <span className="font-bold tracking-tight text-[15px]">{item.name}</span>
              </Link>
            </motion.div>
          );
        })}
      </nav>

      <div className="mt-auto space-y-6">


        <div className="pt-6 border-t border-slate-200 dark:border-white/5 flex items-center justify-between transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sky-500 via-rose-500 to-amber-500 p-[1px]">
              <div className="w-full h-full rounded-2xl bg-white dark:bg-black/40 flex items-center justify-center text-slate-900 dark:text-white font-black text-lg transition-colors">
                R
              </div>
            </div>
            <div>
              <p className="text-sm font-black text-slate-900 dark:text-white transition-colors">Richa Shah</p>
              <p className="text-[10px] font-bold text-slate-500 dark:text-gray-400 uppercase tracking-wider">Strategic Admin</p>
            </div>
          </div>
          <button className="p-3 rounded-xl bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-all border border-slate-200 dark:border-white/5">
            <FiSettings size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
