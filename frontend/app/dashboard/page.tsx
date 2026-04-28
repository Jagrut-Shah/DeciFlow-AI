"use client";

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence, Variants } from 'framer-motion';
import { 
    FiActivity, 
    FiTrendingUp, 
    FiShield, 
    FiDatabase, 
    FiLayers, 
    FiZap, 
    FiCpu, 
    FiCheckCircle, 
    FiAlertCircle, 
    FiArrowRight, 
    FiPlus,
    FiDownload,
    FiMenu,
    FiX,
    FiChevronRight,
    FiRefreshCw
} from 'react-icons/fi';
import { FaRobot, FaMicrochip, FaChartLine, FaSync } from 'react-icons/fa';
import Card from '@/components/Card';
import DynamicChart from '@/components/DynamicChart';
import { apiClient } from '@/services/api';

export default function DashboardPage() {
    const router = useRouter();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [polling, setPolling] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const pollingInterval = useRef<any>(null);

    const fetchData = async (isPoll = false) => {
        if (!isPoll) setLoading(true);
        else setPolling(true);
        
        setError(null);
        try {
            const response = await apiClient.get('/dashboard/insights');
            if (response.status === 'success') {
                setData(response.data);
                
                // If running or pending, keep polling
                if (response.data.status === 'RUNNING' || response.data.status === 'PENDING') {
                    if (!pollingInterval.current) {
                        startPolling();
                    }
                } else {
                    stopPolling();
                }
            }
        } catch (err: any) {
            console.error("Dashboard error:", err);
            setError(err.message || "Failed to fetch neural metrics");
            stopPolling();
        } finally {
            setLoading(false);
            setPolling(false);
        }
    };

    const startPolling = () => {
        if (pollingInterval.current) return;
        pollingInterval.current = setInterval(() => {
            fetchData(true);
        }, 5000); // 5s poll
    };

    const stopPolling = () => {
        if (pollingInterval.current) {
            clearInterval(pollingInterval.current);
            pollingInterval.current = null;
        }
    };

    useEffect(() => {
        fetchData();
        return () => stopPolling();
    }, []);

    const containerVariants: Variants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const itemVariants: Variants = {
        hidden: { opacity: 0, y: 20 },
        visible: {
            opacity: 1,
            y: 0,
            transition: {
                type: "spring",
                stiffness: 100
            }
        }
    };

    const iconColors = [
        'bg-sapphire/10 text-sapphire',
        'bg-emerald/10 text-emerald',
        'bg-amber/10 text-amber',
        'bg-alert-red/10 text-alert-red'
    ];

    if (loading && !data) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
                <div className="relative">
                    <div className="w-20 h-20 border-4 border-sapphire/20 border-t-sapphire rounded-full animate-spin"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <FaRobot size={30} className="text-sapphire animate-pulse" />
                    </div>
                </div>
                <div className="text-center">
                    <h2 className="text-2xl font-black text-navy dark:text-white uppercase tracking-widest mb-2">Synchronizing Neural Engine</h2>
                    <p className="text-muted-text dark:text-white/40 font-medium">Calibrating decision vectors and synthesizing data streams...</p>
                </div>
            </div>
        );
    }

    return (
        <motion.div 
            initial="hidden"
            animate="visible"
            variants={containerVariants}
            className="p-4 md:p-10 space-y-10 max-w-[1600px] mx-auto overflow-x-hidden"
        >
            {/* Executive Header */}
            <motion.div variants={itemVariants} className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="space-y-2">
                    <h1 className="text-4xl md:text-6xl font-black text-navy dark:text-white tracking-tight leading-none mb-2">
                        System <span className="text-transparent bg-clip-text bg-gradient-to-r from-sapphire via-emerald to-amber">Intelligence</span>
                    </h1>
                    <p className="text-body-text dark:text-white/60 text-xl font-medium max-w-2xl transition-colors">
                        Autonomous cross-signal correlation and high-fidelity business trajectory modeling.
                    </p>
                </div>

                <motion.button 
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => fetchData()}
                    className="flex items-center gap-3 px-8 py-4 bg-white dark:bg-white/5 border border-cool-gray dark:border-white/10 rounded-2xl text-navy dark:text-white font-black uppercase tracking-widest text-xs hover:bg-ice-blue/30 dark:hover:bg-white/10 transition-all shadow-xl shadow-sapphire/5"
                >
                    <FaSync className={loading || polling ? "animate-spin" : ""} />
                    Refresh Analysis
                </motion.button>
            </motion.div>

            {/* Main Stats Grid - Hidden during RUNNING/PENDING to avoid redundancy and data mismatch */}
            {(data?.status !== 'RUNNING' && data?.status !== 'PENDING') && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {(data?.stats && data.stats.length > 0 ? data.stats : [
                        { label: "Predictive ROI", value: "1.3x", sub: "Neural Synthesis", trend: "+12.4%", isPositive: true },
                        { label: "Strategic Risk", value: "LOW", sub: "Balanced Exposure", trend: "Stable", isPositive: true },
                        { label: "Confidence", value: "94%", sub: "Audit Verified", trend: "+0.8%", isPositive: true },
                        { label: "Efficacy Index", value: "88", sub: "Performance", trend: "+2.1%", isPositive: true }
                    ]).map((stat: any, index: number) => (
                        <motion.div key={stat.label} variants={itemVariants} className="h-full">
                            <Card className="p-6 md:p-8 h-full group cursor-default flex flex-col justify-between">
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
                    ))}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Visualization */}
                <motion.div variants={itemVariants} className="lg:col-span-2">
                    <Card className="p-6 md:p-10 flex flex-col min-h-[400px] md:min-h-[500px] relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-10 opacity-[0.03] dark:opacity-[0.05] group-hover:opacity-[0.08] dark:group-hover:opacity-10 transition-opacity">
                            <FiTrendingUp size={160} className="text-sapphire" />
                        </div>

                        <div className="relative z-10 flex-1 min-h-[350px]">
                            <DynamicChart 
                                config={data?.dashboard_viz || {
                                    type: 'area',
                                    title: 'Performance Matrix',
                                    description: 'Tracking historical AI agent performance and system latency',
                                    data: data?.has_real_data 
                                        ? (data?.dashboard_viz?.data || data?.chart_data?.map((v: number, i: number) => ({ name: `P${i+1}`, value: v })) || [])
                                        : [
                                            { name: '08:00', value: 45 },
                                            { name: '10:00', value: 72 },
                                            { name: '12:00', value: 68 },
                                            { name: '14:00', value: 94 },
                                            { name: '16:00', value: 85 },
                                            { name: '18:00', value: 78 }
                                        ]
                                }} 
                            />
                        </div>

                        <div className="mt-8 pt-8 border-t border-cool-gray dark:border-white/5 flex items-center justify-between relative z-10">
                            <div className="flex gap-6">
                                <div className="flex items-center gap-2.5">
                                    <div className="w-3 h-3 rounded-full bg-sapphire shadow-[0_0_10px_rgba(37,99,235,0.4)]"></div>
                                    <span className="text-[10px] font-black text-muted-text dark:text-white/40 uppercase tracking-widest">Active Momentum</span>
                                </div>
                                <div className="flex items-center gap-2.5">
                                    <div className="w-3 h-3 rounded-full bg-emerald shadow-[0_0_10px_rgba(22,168,122,0.4)]"></div>
                                    <span className="text-[10px] font-black text-muted-text dark:text-white/40 uppercase tracking-widest">Growth Vector</span>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-black text-sapphire dark:text-white/60 uppercase tracking-[0.2em]">Neural Engine v2.5.0</span>
                                <div className="w-1.5 h-1.5 bg-emerald rounded-full animate-pulse"></div>
                            </div>
                        </div>
                    </Card>
                </motion.div>

                {/* AI Insight Card */}
                <motion.div variants={itemVariants}>
                    <Card className="p-6 md:p-10 h-full flex flex-col bg-gradient-to-br from-sapphire/[0.04] via-emerald/[0.08] to-amber/[0.04] dark:from-sapphire/[0.08] dark:via-emerald/[0.12] dark:to-amber/[0.08] border-sapphire/20 dark:border-sapphire/30 relative group overflow-hidden">
                        <motion.div 
                            animate={{ 
                                scale: [1, 1.3, 1],
                                opacity: [0.1, 0.25, 0.1]
                            }}
                            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
                            className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(37,99,235,0.2),transparent_70%)] dark:bg-[radial-gradient(circle_at_50%_0%,rgba(37,99,235,0.4),transparent_70%)]"
                        />
                        
                        <div className="relative z-10 flex flex-col h-full">
                            <div className="flex items-center justify-between mb-10">
                                <div className="flex items-center gap-3">
                                    <div className="p-2.5 bg-sapphire/10 dark:bg-sapphire/20 rounded-xl text-sapphire">
                                        <FaRobot size={22} />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-black text-navy dark:text-white leading-none">DeciFlow</h2>
                                        <span className="text-[9px] font-black text-sapphire uppercase tracking-widest">Insight Engine</span>
                                    </div>
                                </div>
                                <div className="flex -space-x-2">
                                    {[1, 2, 3].map(i => (
                                        <div key={i} className="w-8 h-8 rounded-full border-2 border-white dark:border-navy bg-slate-200 dark:bg-slate-700 overflow-hidden">
                                            <div className="w-full h-full bg-gradient-to-br from-sapphire/40 to-emerald/40 animate-pulse" />
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="flex-1 space-y-8">
                                <div className="space-y-4">
                                    <div className="text-xs font-black text-transparent bg-clip-text bg-gradient-to-r from-sapphire to-emerald uppercase tracking-[0.3em] transition-colors">Autonomous Summary</div>
                                    <div className="text-navy dark:text-white/90 leading-relaxed text-xl font-bold italic transition-colors">
                                        &ldquo;{(data?.status === 'RUNNING' || data?.status === 'PENDING') 
                                            ? "Neural Synthesis: 1.3x ROI optimization with high resilience." 
                                            : (data?.main_insight || "Neural Synthesis: 1.3x ROI optimization with high resilience.")}
                                        &rdquo;
                                    </div>
                                </div>


                            </div>

                            <button 
                                onClick={() => router.push('/insights')}
                                className="mt-10 w-full group py-5 px-6 rounded-2xl bg-navy dark:bg-white text-white dark:text-navy font-black uppercase tracking-[0.2em] text-xs flex items-center justify-center gap-3 hover:gap-5 transition-all shadow-xl shadow-sapphire/20"
                            >
                                Deep Dive
                                <FiArrowRight size={18} />
                            </button>
                        </div>
                    </Card>
                </motion.div>
            </div>

        </motion.div>
    );
}
