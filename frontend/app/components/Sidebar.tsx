"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: "📊" },
    { name: "Upload", path: "/upload", icon: "📁" },
    { name: "Insights", path: "/insights", icon: "💡" },
    { name: "Simulation", path: "/simulation", icon: "⚙️" },
    { name: "Chat", path: "/chat", icon: "💬" },
  ];

  return (
    <div className="w-72 bg-[#0B0F1A]/80 border-r border-white/10 backdrop-blur-xl p-6 flex flex-col fixed h-full left-0 top-0">
      <div className="mb-10 mt-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-400 to-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.6)]"></div>
        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-indigo-400">
          DeciFlow AI
        </h1>
      </div>

      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.path || (pathname === "/" && item.path === "/dashboard");
          
          return (
            <Link
              key={item.path}
              href={item.path}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-2xl transition-all duration-300
                ${isActive 
                  ? "bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 text-cyan-300 border border-cyan-500/30 shadow-[0_0_15px_rgba(34,211,238,0.1)]" 
                  : "text-gray-400 hover:text-white hover:bg-white/5"}
              `}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto pt-6 border-t border-white/10">
        <div className="flex items-center gap-3 px-4 py-2">
          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold shadow-lg">
            R
          </div>
          <div>
            <p className="text-sm font-medium text-white">Richa</p>
            <p className="text-xs text-gray-400">Pro Plan</p>
          </div>
        </div>
      </div>
    </div>
  );
}
