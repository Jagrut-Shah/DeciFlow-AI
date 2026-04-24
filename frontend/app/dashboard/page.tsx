"use client";

import React, { useState, useEffect } from "react";
import Card from "@/components/Card";
import { FiActivity, FiCpu, FiTrendingUp, FiStar } from "react-icons/fi";
import { FaRobot } from "react-icons/fa";
import { motion } from "framer-motion";
import { apiClient } from "@/services/api";

export default function Dashboard() {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState('1M');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const result = await apiClient.get("/dashboard/insights");
                if (result.status === 'success') {
                    setData(result.data);
                }
            } catch (error) {
                console.error("Failed to fetch dashboard data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[70vh]">
                <div className="relative">
                    <div className="w-16 h-16 border-2 border-rose-500/20 rounded-full"></div>
                    <div className="w-16 h-16 border-t-2 border-rose-500 rounded-full animate-spin absolute top-0 left-0"></div>
                </div>
            </div>
        );
    }

    return (
        <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="space-y-10"
        >
            {/* Header Section */}
            <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="text-5xl font-black tracking-tight text-slate-900 dark:text-white mb-3 transition-colors">
                        System <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 via-rose-500 to-amber-500">Intelligence</span>
                    </h1>
                    <p className="text-slate-600 dark:text-gray-400 text-xl font-medium max-w-2xl transition-colors">
                        Agentic analysis complete. <span className="text-rose-600 dark:text-rose-400">3 new strategic signals</span> detected in your data stream.
                    </p>
                </div>
                <div className="flex items-center gap-3 bg-white/60 dark:bg-white/5 border border-slate-200 dark:border-white/10 px-4 py-2 rounded-2xl backdrop-blur-md transition-colors shadow-sm dark:shadow-none">
                    <div className="w-2 h-2 bg-rose-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.8)]" />
                    <span className="text-sm font-bold text-slate-700 dark:text-rose-400 tracking-wide uppercase transition-colors">Real-time Stream Active</span>
                </div>
            </motion.div>

            {/* Stats Grid */}
            <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {(data?.stats || []).map((stat: any, index: number) => {
                    const iconColors = [
                        'bg-sky-500/10 text-sky-600 dark:text-sky-400',
                        'bg-rose-500/10 text-rose-600 dark:text-rose-400',
                        'bg-amber-500/10 text-amber-600 dark:text-amber-400',
                        'bg-blue-500/10 text-blue-600 dark:text-blue-400'
                    ];
                    const bgHoverColors = [
                        'group-hover:text-sky-600 dark:group-hover:text-sky-400',
                        'group-hover:text-rose-600 dark:group-hover:text-rose-400',
                        'group-hover:text-amber-600 dark:group-hover:text-amber-400',
                        'group-hover:text-blue-600 dark:group-hover:text-blue-400'
                    ];

                    return (
                        <Card key={stat.label} className="p-6 group">
                            <div className="flex justify-between items-start mb-6">
                                <div className={`p-3 rounded-xl transition-colors ${iconColors[index % iconColors.length]}`}>
                                    {index === 0 ? <FiActivity size={20} /> : index === 1 ? <FiCpu size={20} /> : index === 2 ? <FaRobot size={20} /> : <FiTrendingUp size={20} />}
                                </div>
                                <span className={`text-xs font-bold px-2 py-1 rounded-lg transition-colors ${stat.isPositive ? 'bg-sky-50 dark:bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-100 dark:border-transparent' : 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 border border-red-100 dark:border-transparent'}`}>
                                    {stat.trend}
                                </span>
                            </div>
                            <h3 className="text-sm text-slate-500 dark:text-gray-400 font-bold uppercase tracking-wider mb-1 transition-colors">{stat.label}</h3>
                            <p className={`text-3xl font-black text-slate-900 dark:text-white transition-all ${bgHoverColors[index % bgHoverColors.length]}`}>{stat.value}</p>
                        </Card>
                    );
                })}
            </motion.div>

            <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Visualization */}
                <Card className="lg:col-span-2 p-8 flex flex-col min-h-[450px] relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-[0.03] dark:opacity-[0.05] group-hover:opacity-[0.08] dark:group-hover:opacity-10 transition-opacity">
                      <FiTrendingUp size={120} className="text-rose-500" />
                    </div>
                    
                    <div className="flex justify-between items-center mb-10 relative z-10">
                        <div>
                          <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-1 transition-colors">Performance Matrix</h3>
                          <p className="text-slate-500 dark:text-gray-400 text-sm font-medium transition-colors">Tracking historical AI agent performance and system latency</p>
                        </div>
                        <div className="flex p-1 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/5 transition-colors">
                            {['1D', '1W', '1M', '1Y'].map((t) => (
                                <button 
                                    key={t} 
                                    onClick={() => setTimeRange(t)}
                                    className={`px-4 py-2 text-xs font-bold rounded-lg transition-all ${timeRange === t ? 'bg-gradient-to-r from-sky-500 to-rose-500 text-white shadow-lg shadow-rose-500/20' : 'text-slate-500 hover:text-slate-900 dark:hover:text-white dark:text-gray-400'}`}>
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>
                    
                    <div className="flex-1 flex justify-center items-center relative min-h-[200px]">
                        <svg className="w-full h-full max-h-[300px]" viewBox="0 0 100 40" preserveAspectRatio="none">
                            <defs>
                                <linearGradient id="lineGrad" x1="0" y1="0" x2="100" y2="0">
                                    <stop offset="0%" stopColor="#0ea5e9" />
                                    <stop offset="50%" stopColor="#f43f5e" />
                                    <stop offset="100%" stopColor="#f59e0b" />
                                </linearGradient>
                                <linearGradient id="fillGradLight" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.15" />
                                    <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
                                </linearGradient>
                                <linearGradient id="fillGradDark" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.25" />
                                    <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
                                </linearGradient>
                            </defs>
                            <path d="M0,35 C10,32 15,38 25,28 C35,18 45,35 55,15 C65,-5 75,20 85,12 C95,4 100,8 100,8" 
                                  fill="none" stroke="url(#lineGrad)" strokeWidth="0.8" className="drop-shadow-[0_0_12px_rgba(244,63,94,0.5)]" />
                            <path d="M0,35 C10,32 15,38 25,28 C35,18 45,35 55,15 C65,-5 75,20 85,12 C95,4 100,8 100,8 L100,40 L0,40 Z" 
                                  fill="url(#fillGradLight)" className="dark:hidden" />
                            <path d="M0,35 C10,32 15,38 25,28 C35,18 45,35 55,15 C65,-5 75,20 85,12 C95,4 100,8 100,8 L100,40 L0,40 Z" 
                                  fill="url(#fillGradDark)" className="hidden dark:block" />
                        </svg>
                    </div>
                </Card>

                {/* AI Insight Card */}
                <Card className="p-8 flex flex-col bg-gradient-to-br from-sky-500/[0.02] via-rose-500/[0.05] to-amber-500/[0.02] dark:from-sky-500/[0.05] dark:via-rose-500/[0.1] dark:to-amber-500/[0.05] border-rose-500/10 dark:border-rose-500/20 relative group">
                    <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(244,63,94,0.05),transparent_70%)] dark:bg-[radial-gradient(circle_at_50%_0%,rgba(244,63,94,0.15),transparent_70%)] transition-colors" />
                    
                    <div className="relative z-10 flex-1">
                        <div className="flex items-center gap-4 mb-8">
                            <div className="w-12 h-12 rounded-2xl bg-rose-50 dark:bg-rose-500/20 flex items-center justify-center border border-rose-100 dark:border-rose-500/30 group-hover:rotate-12 transition-all duration-500 shadow-[0_0_20px_rgba(244,63,94,0.15)] dark:shadow-[0_0_15px_rgba(244,63,94,0.3)]">
                                <FaRobot size={24} className="text-rose-500 dark:text-rose-400 animate-pulse" />
                            </div>
                            <div>
                                <h3 className="text-xl font-black text-slate-900 dark:text-white leading-tight transition-colors">DeciFlow<br/>Insight Engine</h3>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="text-xs font-black text-transparent bg-clip-text bg-gradient-to-r from-sky-500 to-rose-500 uppercase tracking-widest transition-colors">Autonomous Summary</div>
                            <p className="text-slate-700 dark:text-gray-200 leading-relaxed text-lg font-medium italic transition-colors">
                                &ldquo;{data?.main_insight || "Awaiting multi-agent synthesis from the background pipeline..."}&rdquo;
                            </p>
                        </div>
                    </div>

                    <button className="relative z-10 mt-12 w-full py-5 rounded-2xl bg-gradient-to-r from-sky-500 via-rose-500 to-amber-500 hover:opacity-90 text-white font-black uppercase tracking-widest text-xs transition-all shadow-[0_0_20px_rgba(244,63,94,0.3)] hover:shadow-[0_0_30px_rgba(244,63,94,0.5)] active:scale-95 group-hover:translate-y-[-2px]">
                        Execute Deep Dive
                    </button>
                </Card>
            </motion.div>
        </motion.div>
    );
}
