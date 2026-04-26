"use client";

import React, { useState, useEffect } from "react";
import Card from "@/components/Card";
import { FiActivity, FiCpu, FiTrendingUp, FiStar } from "react-icons/fi";
import { FaRobot, FaSync } from "react-icons/fa";
import { motion, AnimatePresence, Variants } from "framer-motion";
import { apiClient } from "@/services/api";
import Link from "next/link";

export default function Dashboard() {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState('1M');

    const fetchData = async () => {
        setLoading(true);
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

    useEffect(() => {
        fetchData();
    }, []);

    const containerVariants: Variants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { 
                staggerChildren: 0.08,
                delayChildren: 0.2
            }
        }
    };

    const itemVariants: Variants = {
        hidden: { opacity: 0, y: 15 },
        show: { 
            opacity: 1, 
            y: 0, 
            transition: { 
                type: "spring", 
                stiffness: 260, 
                damping: 20 
            } 
        }
    };

    const generatePath = (points: number[]) => {
        if (!points || points.length < 2) return "M0,20 L100,20";
        const min = Math.min(...points);
        const max = Math.max(...points);
        const range = max - min || 1;
        const width = 100;
        const height = 40;
        const padding = 5;
        const scaledPoints = points.map((p, i) => ({
            x: (i / (points.length - 1)) * width,
            y: height - (padding + ((p - min) / range) * (height - 2 * padding))
        }));
        let path = `M${scaledPoints[0].x},${scaledPoints[0].y}`;
        for (let i = 0; i < scaledPoints.length - 1; i++) {
            const p0 = scaledPoints[i];
            const p1 = scaledPoints[i + 1];
            const cp1x = p0.x + (p1.x - p0.x) / 2;
            path += ` C${cp1x},${p0.y} ${cp1x},${p1.y} ${p1.x},${p1.y}`;
        }
        return path;
    };

    const chartPath = generatePath(data?.chart_data || []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[70vh]">
                <div className="relative">
                    <motion.div 
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                        className="w-16 h-16 border-2 border-sapphire/20 rounded-full"
                    ></motion.div>
                    <motion.div 
                        animate={{ rotate: -360 }}
                        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                        className="w-16 h-16 border-t-2 border-sapphire rounded-full absolute top-0 left-0"
                    ></motion.div>
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
                <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-end justify-between gap-6 w-full border-b border-cool-gray dark:border-white/5 pb-8">
                    <div>
                        <h1 className="text-5xl font-black tracking-tight text-navy dark:text-white mb-3 transition-colors">
                            System <span className="text-transparent bg-clip-text bg-gradient-to-r from-sapphire via-emerald to-amber">Intelligence</span>
                        </h1>
                        <p className="text-body-text dark:text-white/60 text-xl font-medium max-w-2xl transition-colors">
                            Agentic analysis complete. <span className="text-sapphire">Strategic signals</span> detected in your data stream.
                        </p>
                    </div>
                    <motion.button 
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={fetchData}
                        className="flex items-center gap-3 px-8 py-4 bg-white dark:bg-white/5 border border-cool-gray dark:border-white/10 rounded-2xl text-navy dark:text-white font-black uppercase tracking-widest text-xs hover:bg-ice-blue/30 dark:hover:bg-white/10 transition-all shadow-xl shadow-sapphire/5"
                    >
                        <FaSync className={loading ? "animate-spin" : ""} />
                        Refresh Analysis
                    </motion.button>
                </motion.div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {(data?.stats || []).map((stat: any, index: number) => {
                    const iconColors = [
                        'bg-sapphire/10 text-sapphire',
                        'bg-emerald/10 text-emerald',
                        'bg-amber/10 text-amber',
                        'bg-alert-red/10 text-alert-red'
                    ];

                    return (
                        <motion.div key={stat.label} variants={itemVariants} className="h-full">
                            <Card className="p-8 h-full group cursor-default flex flex-col justify-between">
                                <div>
                                    <div className="flex justify-between items-start mb-8">
                                        <div className={`p-4 rounded-2xl transition-all duration-500 group-hover:scale-110 group-hover:rotate-6 ${iconColors[index % iconColors.length]}`}>
                                            {index === 0 ? <FiActivity size={24} /> : index === 1 ? <FiCpu size={24} /> : index === 2 ? <FaRobot size={24} /> : <FiTrendingUp size={24} />}
                                        </div>
                                        <span className={`text-[10px] font-black px-3 py-1.5 rounded-full uppercase tracking-widest transition-colors ${stat.isPositive ? 'bg-emerald/10 text-emerald border border-emerald/20' : 'bg-alert-red/10 text-alert-red border border-alert-red/20'}`}>
                                            {stat.trend}
                                        </span>
                                    </div>
                                    <h3 className="text-xs text-muted-text dark:text-white/40 font-black uppercase tracking-[0.2em] mb-2 transition-colors">{stat.label}</h3>
                                    <p className="text-4xl font-black text-navy dark:text-white transition-all duration-500 group-hover:tracking-tight">{stat.value}</p>
                                </div>
                            </Card>
                        </motion.div>
                    );
                })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Visualization */}
                <motion.div variants={itemVariants} className="lg:col-span-2">
                    <Card className="p-10 flex flex-col min-h-[500px] relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-10 opacity-[0.03] dark:opacity-[0.05] group-hover:opacity-[0.08] dark:group-hover:opacity-10 transition-opacity">
                            <FiTrendingUp size={160} className="text-sapphire" />
                        </div>
                        
                        <div className="flex justify-between items-center mb-12 relative z-10">
                            <div>
                                <h3 className="text-3xl font-black text-navy dark:text-white mb-2 transition-colors">Performance Matrix</h3>
                                <p className="text-muted-text dark:text-white/40 text-base font-medium transition-colors">Tracking historical AI agent performance and system latency</p>
                            </div>
                            <div className="flex p-1.5 bg-ice-blue dark:bg-white/5 rounded-2xl border border-cool-gray dark:border-white/5 transition-colors">
                                {['1D', '1W', '1M', '1Y'].map((t) => (
                                    <button 
                                        key={t} 
                                        onClick={() => setTimeRange(t)}
                                        className={`px-6 py-2.5 text-xs font-black rounded-xl transition-all ${timeRange === t ? 'bg-gradient-to-r from-sapphire to-emerald text-white shadow-xl shadow-sapphire/30' : 'text-body-text hover:text-navy dark:hover:text-white dark:text-white/40'}`}>
                                        {t}
                                    </button>
                                ))}
                            </div>
                        </div>
                        
                        <div className="flex-1 flex justify-center items-center relative min-h-[250px] mt-6 px-4">
                            <div className="absolute left-0 h-full flex flex-col justify-between text-[11px] font-black text-muted-text/40 dark:text-white/20 pb-8">
                                <span>High</span>
                                <span>Low</span>
                            </div>
                            <svg className="w-full h-full max-h-[350px] pl-10 pb-6" viewBox="0 0 100 40" preserveAspectRatio="none">
                                <defs>
                                    <linearGradient id="lineGrad" x1="0" y1="0" x2="100" y2="0">
                                        <stop offset="0%" stopColor="#2563EB" />
                                        <stop offset="50%" stopColor="#16A87A" />
                                        <stop offset="100%" stopColor="#F59E0B" />
                                    </linearGradient>
                                    <linearGradient id="fillGradLight" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#2563EB" stopOpacity="0.1" />
                                        <stop offset="100%" stopColor="#2563EB" stopOpacity="0" />
                                    </linearGradient>
                                    <linearGradient id="fillGradDark" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#2563EB" stopOpacity="0.25" />
                                        <stop offset="100%" stopColor="#2563EB" stopOpacity="0" />
                                    </linearGradient>
                                </defs>
                                <motion.path 
                                    initial={{ pathLength: 0, opacity: 0 }}
                                    animate={{ pathLength: 1, opacity: 1 }}
                                    transition={{ duration: 2, ease: "circOut" }}
                                    d={chartPath} 
                                    fill="none" stroke="url(#lineGrad)" strokeWidth="1.2" strokeLinecap="round" className="drop-shadow-[0_0_15px_rgba(37,99,235,0.6)]" 
                                />
                                <motion.path 
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ duration: 2.5, delay: 0.8 }}
                                    d={`${chartPath} L100,40 L0,40 Z`} 
                                    fill="url(#fillGradLight)" className="dark:hidden" 
                                />
                                <motion.path 
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ duration: 2.5, delay: 0.8 }}
                                    d={`${chartPath} L100,40 L0,40 Z`} 
                                    fill="url(#fillGradDark)" className="hidden dark:block" 
                                />
                            </svg>
                            <div className="absolute bottom-0 w-full flex justify-between text-[11px] font-black text-muted-text/40 dark:text-white/20 pl-10">
                                <span>Analysis Start</span>
                                <span>Real-time Peak</span>
                            </div>
                        </div>
                    </Card>
                </motion.div>

                {/* AI Insight Card */}
                <motion.div variants={itemVariants}>
                    <Card className="p-10 h-full flex flex-col bg-gradient-to-br from-sapphire/[0.04] via-emerald/[0.08] to-amber/[0.04] dark:from-sapphire/[0.08] dark:via-emerald/[0.12] dark:to-amber/[0.08] border-sapphire/20 dark:border-sapphire/30 relative group overflow-hidden">
                        <motion.div 
                            animate={{ 
                                scale: [1, 1.3, 1],
                                opacity: [0.1, 0.25, 0.1]
                            }}
                            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
                            className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(37,99,235,0.2),transparent_70%)] dark:bg-[radial-gradient(circle_at_50%_0%,rgba(37,99,235,0.4),transparent_70%)]" 
                        />
                        
                        <div className="relative z-10 flex-1">
                            <div className="flex items-center gap-5 mb-10">
                                <motion.div 
                                    whileHover={{ rotate: 15, scale: 1.1 }}
                                    className="w-16 h-16 rounded-3xl bg-white dark:bg-sapphire/30 flex items-center justify-center border border-cool-gray dark:border-sapphire/40 transition-all duration-500 shadow-2xl shadow-sapphire/20">
                                    <FaRobot size={32} className="text-sapphire dark:text-white animate-pulse" />
                                </motion.div>
                                <div>
                                    <h3 className="text-2xl font-black text-navy dark:text-white leading-tight transition-colors italic tracking-tighter">DeciFlow<br/>Insight Engine</h3>
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div className="text-xs font-black text-transparent bg-clip-text bg-gradient-to-r from-sapphire to-emerald uppercase tracking-[0.3em] transition-colors">Autonomous Summary</div>
                                <p className="text-navy dark:text-white/90 leading-relaxed text-xl font-bold italic transition-colors">
                                    &ldquo;{data?.main_insight || "Awaiting multi-agent synthesis from the background pipeline..."}&rdquo;
                                </p>
                            </div>
                        </div>

                        <div className="relative z-10 mt-16">
                            <Link href="/insights" className="w-full block">
                                <motion.button 
                                    whileHover={{ y: -4, scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    className="w-full py-6 rounded-2xl bg-gradient-to-r from-sapphire via-indigo-600 to-emerald hover:opacity-95 text-white font-black uppercase tracking-[0.2em] text-xs transition-all shadow-2xl shadow-sapphire/40 active:scale-95">
                                    Execute Deep Dive
                                </motion.button>
                            </Link>
                        </div>
                    </Card>
                </motion.div>
            </div>
        </motion.div>
    );
}

