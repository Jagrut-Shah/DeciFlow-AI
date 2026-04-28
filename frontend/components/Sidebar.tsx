"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import React from "react";
import { FiGrid, FiUploadCloud, FiBarChart2, FiPlay, FiMessageSquare, FiSettings, FiHome, FiTrendingUp } from "react-icons/fi";
import { ThemeToggle } from "./ThemeToggle";
import { motion } from "framer-motion";

export default function Sidebar() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session');

  const navItems = [
    { name: "Home", path: "/", icon: <FiHome size={20} /> },
    { name: "Dashboard", path: "/dashboard", icon: <FiGrid size={20} /> },
    { name: "Upload", path: "/upload", icon: <FiUploadCloud size={20} /> },
    { name: "Insights", path: "/insights", icon: <FiBarChart2 size={20} /> },
    { name: "Simulation", path: "/simulation", icon: <FiPlay size={20} /> },
    { name: "Chat", path: "/chat", icon: <FiMessageSquare size={20} /> },
  ];

  const [mounted, setMounted] = React.useState(false);
  const [dots, setDots] = React.useState<{ top: string; left: string }[]>([]);

  React.useEffect(() => {
    setMounted(true);
    setDots([...Array(6)].map(() => ({
      top: `${Math.random() * 100}%`,
      left: `${Math.random() * 100}%`
    })));
  }, []);

  return (
    <div className="w-80 bg-white dark:bg-[#0b0f19] border-r border-slate-200 dark:border-white/5 p-8 flex flex-col fixed h-full left-0 top-0 z-50 transition-all duration-700 ease-in-out">
      {/* Premium Texture Overlay */}
      <div className="absolute inset-0 pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.02] dark:opacity-[0.04] mix-blend-overlay"></div>
      
      {/* Subtle Background Glow */}
      <div className="absolute -top-20 -left-20 w-64 h-64 bg-sapphire/5 rounded-full pointer-events-none"></div>

      <div className="mb-14 mt-2 flex items-center justify-between relative z-10">
        <Link href="/" className="flex items-center gap-4 group cursor-pointer">
          <div className="relative">
            {/* Logo Pulse Rings */}
            <motion.div 
              animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0, 0.3] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="absolute inset-0 rounded-[20px] bg-sapphire/10 -z-10"
            />
            <div className="w-12 h-12 rounded-[20px] bg-gradient-to-br from-sapphire via-emerald to-amber shadow-[0_8px_30px_rgb(37,99,235,0.2)] group-hover:shadow-[0_15px_40px_rgb(37,99,235,0.4)] group-hover:scale-110 group-hover:rotate-3 transition-all duration-700 flex items-center justify-center overflow-hidden relative border border-white/20">
               {/* Neural Net Dot Background */}
               <div className="absolute inset-0 opacity-20">
                  {mounted && dots.map((dot, i) => (
                    <motion.div
                      key={i}
                      animate={{ 
                        opacity: [0.2, 0.5, 0.2],
                        scale: [1, 1.2, 1]
                      }}
                      transition={{ duration: 2 + i, repeat: Infinity }}
                      className="absolute w-1 h-1 bg-white rounded-full"
                      style={{ 
                        top: dot.top, 
                        left: dot.left 
                      }}
                    />
                  ))}
               </div>
               
               {/* Enhanced Growth Chart SVG */}
               <svg className="w-7 h-7 text-white drop-shadow-2xl relative z-10" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <motion.path 
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 1 }}
                    transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 2, ease: "easeInOut" }}
                    d="M4 18L9 13L13 17L20 7" 
                    stroke="currentColor" 
                    strokeWidth="3.5" 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                  />
                  <motion.path 
                    initial={{ scale: 0 }}
                    animate={{ scale: [0, 1.2, 1] }}
                    transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 3 }}
                    d="M20 7L16 7M20 7L20 11" 
                    stroke="currentColor" 
                    strokeWidth="3.5" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  />
                  {/* Subtle Secondary Line */}
                  <motion.path 
                    animate={{ opacity: [0.1, 0.3, 0.1] }}
                    transition={{ duration: 4, repeat: Infinity }}
                    d="M4 14L8 10L12 14L18 6" 
                    stroke="white" 
                    strokeWidth="1.5" 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    style={{ opacity: 0.2 }}
                  />
               </svg>
               <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
            </div>
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tighter text-navy dark:text-white transition-colors duration-500 flex flex-col leading-none">
              <span className="flex items-center gap-1.5">
                Deci<span className="text-transparent bg-clip-text bg-gradient-to-r from-sapphire to-emerald">Flow</span>
              </span>
              <span className="text-[9px] font-black mt-1 px-2 py-0.5 rounded-full bg-ice-blue dark:bg-sapphire/20 border border-cool-gray dark:border-sapphire/30 text-sapphire dark:text-sapphire-light tracking-[0.2em] uppercase shadow-sm w-fit">Intelligence</span>
            </h1>
          </div>
        </Link>
        <ThemeToggle />
      </div>

      <nav className="flex-1 space-y-3">
        {navItems.map((item, index) => {
          const isActive = pathname === item.path;
          
          return (
            <motion.div
              key={item.path}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Link
                href={sessionId && item.path !== "/" ? `${item.path}?session=${sessionId}` : item.path}
                className={`
                  flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-500 relative group
                  ${isActive 
                    ? "bg-gradient-to-r from-ice-blue to-transparent dark:from-white/[0.05] dark:to-transparent text-sapphire dark:text-white border border-cool-gray dark:border-white/10 shadow-[0_4px_20px_rgba(37,99,235,0.05)]" 
                    : "text-body-text hover:text-navy dark:text-gray-400 dark:hover:text-white hover:bg-ice-blue/50 dark:hover:bg-white/[0.02] border border-transparent"}
                `}
              >
                {isActive && (
                   <>
                     <motion.div layoutId="sidebar-active-indicator" className="absolute left-[-8px] w-2 h-8 bg-gradient-to-b from-sapphire to-emerald rounded-full" />
                     <motion.div layoutId="sidebar-active-glow" className="absolute inset-0 bg-sapphire/5 dark:bg-sapphire/10 rounded-2xl" />
                   </>
                )}
                <span className={`${isActive ? "text-sapphire" : "group-hover:text-sapphire group-hover:scale-110"} transition-all duration-300`}>{item.icon}</span>
                <span className={`font-bold tracking-tight text-[15px] ${isActive ? "translate-x-1" : "group-hover:translate-x-1"} transition-transform duration-300`}>{item.name}</span>
                
                {isActive && (
                  <motion.div 
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-sapphire shadow-[0_0_8px_rgba(37,99,235,0.8)]"
                  />
                )}
              </Link>
            </motion.div>
          );
        })}
      </nav>

      <div className="mt-auto space-y-6">
        <div className="pt-6 border-t border-cool-gray dark:border-white/5 flex items-center justify-between transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-sapphire via-emerald to-amber p-[1px] shadow-lg">
              <div className="w-full h-full rounded-2xl bg-white dark:bg-[#0b0f19] flex items-center justify-center text-navy dark:text-white font-black text-lg transition-colors">
                A
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <p className="text-sm font-black text-navy dark:text-white transition-colors">Aarav Gupta</p>
                <span className="text-[8px] font-black px-1.5 py-0.5 rounded-md bg-gradient-to-r from-amber to-orange-500 text-white shadow-sm shadow-amber/20">PRO</span>
              </div>
              <p className="text-[10px] font-bold text-muted-text dark:text-gray-400 uppercase tracking-wider">Strategic Admin</p>
            </div>
          </div>
          <motion.button 
            whileHover={{ rotate: 90, scale: 1.1 }}
            className="p-3 rounded-xl bg-ice-blue dark:bg-white/5 hover:bg-cool-gray dark:hover:bg-white/10 text-muted-text dark:text-gray-400 hover:text-navy dark:hover:text-white transition-all border border-cool-gray dark:border-white/5 shadow-sm"
          >
            <FiSettings size={18} />
          </motion.button>
        </div>
      </div>
    </div>
  );
}

