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
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-sapphire via-emerald to-amber shadow-[0_0_20px_rgba(37,99,235,0.3)] group-hover:scale-110 group-hover:rotate-6 transition-all duration-500"></div>
          <div>
            <h1 className="text-2xl font-black tracking-tighter text-navy dark:text-white transition-colors duration-500 flex items-center gap-2">
              <span>Deci<span className="text-transparent bg-clip-text bg-gradient-to-r from-sapphire to-emerald">Flow</span></span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-lg bg-ice-blue dark:bg-sapphire/20 border border-cool-gray dark:border-sapphire/30 text-sapphire dark:text-sapphire tracking-widest uppercase shadow-sm">AI</span>
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
                    ? "bg-ice-blue dark:bg-white/[0.03] text-sapphire dark:text-white border border-cool-gray dark:border-white/10 shadow-[0_4px_20px_rgba(37,99,235,0.1)] dark:shadow-[0_4px_20px_rgba(37,99,235,0.2)]" 
                    : "text-body-text hover:text-navy dark:text-gray-400 dark:hover:text-white hover:bg-ice-blue/50 dark:hover:bg-white/[0.02] border border-transparent"}
                `}
              >
                {isActive && (
                   <motion.div layoutId="sidebar-active" className="absolute left-[-8px] w-2 h-8 bg-gradient-to-b from-sapphire to-emerald rounded-full blur-[1px] shadow-[0_0_15px_rgba(37,99,235,0.8)]" />
                )}
                <span className={`${isActive ? "text-sapphire" : "group-hover:text-sapphire"} transition-colors`}>{item.icon}</span>
                <span className="font-bold tracking-tight text-[15px]">{item.name}</span>
              </Link>
            </motion.div>
          );
        })}
      </nav>

      <div className="mt-auto space-y-6">


        <div className="pt-6 border-t border-cool-gray dark:border-white/5 flex items-center justify-between transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sapphire via-emerald to-amber p-[1px]">
              <div className="w-full h-full rounded-2xl bg-white dark:bg-black/40 flex items-center justify-center text-navy dark:text-white font-black text-lg transition-colors">
                A
              </div>
            </div>
            <div>
              <p className="text-sm font-black text-navy dark:text-white transition-colors">Aarav Gupta</p>
              <p className="text-[10px] font-bold text-muted-text dark:text-gray-400 uppercase tracking-wider">Strategic Admin</p>
            </div>
          </div>
          <button className="p-3 rounded-xl bg-ice-blue dark:bg-white/5 hover:bg-cool-gray dark:hover:bg-white/10 text-muted-text dark:text-gray-400 hover:text-navy dark:hover:text-white transition-all border border-cool-gray dark:border-white/5">
            <FiSettings size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
