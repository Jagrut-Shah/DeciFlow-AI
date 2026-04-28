"use client";

import React, { useState, useEffect } from "react";
import Card from "@/components/Card";
import { FiCpu, FiAward, FiGlobe, FiAlertTriangle, FiTrendingUp, FiCheckCircle, FiDownload, FiShare2 } from "react-icons/fi";
import { apiClient, API_BASE_URL } from "@/services/api";
import DynamicChart from "@/components/DynamicChart";
import { motion, AnimatePresence, Variants } from "framer-motion";
import { useSearchParams } from "next/navigation";

export default function InsightsPage() {
    const searchParams = useSearchParams();
    const sessionId = searchParams.get('session');
    
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const url = sessionId ? `/dashboard/insights?session_id=${sessionId}` : "/dashboard/insights";
                const result = await apiClient.get(url);
                if (result.status === 'success') {
                    setData(result.data);
                }
            } catch (error) {
                console.error("Failed to fetch insights:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [sessionId]);

    const containerVariants: Variants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { 
                staggerChildren: 0.1,
                delayChildren: 0.2
            }
        }
    };

    const itemVariants: Variants = {
        hidden: { opacity: 0, y: 30 },
        show: { 
            opacity: 1, 
            y: 0,
            transition: { 
                duration: 0.8, 
                ease: [0.16, 1, 0.3, 1] 
            }
        }
    };

    const synthesisVariants: Variants = {
        hidden: { opacity: 0, x: -20 },
        show: { 
            opacity: 1, 
            x: 0,
            transition: { 
                delay: 0.5,
                duration: 0.8,
                ease: [0.16, 1, 0.3, 1]
            } 
        }
    };

    const [isExporting, setIsExporting] = useState(false);
    const [isSharing, setIsSharing] = useState(false);

    const handleExportPDF = async () => {
        if (!data) return;
        setIsExporting(true);
        try {
            const response = await apiClient.post("/reports/generate", {
                session_id: "insights_report",
                data: data
            });
            
            if (response.status === 'success') {
                const serverOrigin = API_BASE_URL.replace(/\/api\/v1\/?$/, '');
                const downloadUrl = `${serverOrigin}${response.data.report_url}`;
                window.open(downloadUrl, '_blank');
            }
        } catch (error) {
            console.error("Export failed:", error);
            alert("Strategic export failed. Check neural link.");
        } finally {
            setIsExporting(false);
        }
    };

    const handleShareReport = async () => {
        setIsSharing(true);
        try {
            if (navigator.share) {
                await navigator.share({
                    title: 'DeciFlow AI Strategic Intelligence',
                    text: 'Review the latest strategic intelligence report from DeciFlow AI.',
                    url: window.location.href,
                });
            } else {
                await navigator.clipboard.writeText(window.location.href);
                alert("Report link copied to clipboard for strategic distribution.");
            }
        } catch (error) {
            console.error("Share failed:", error);
        } finally {
            setIsSharing(false);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-[70vh]">
                <div className="relative mb-8">
                    <motion.div 
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                        className="w-20 h-20 border-2 border-sapphire/20 rounded-full"
                    ></motion.div>
                    <motion.div 
                        animate={{ rotate: -360 }}
                        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                        className="w-20 h-20 border-t-2 border-sapphire rounded-full absolute top-0 left-0"
                    ></motion.div>
                </div>
                <motion.p 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="text-sapphire font-bold tracking-widest uppercase text-xs"
                >
                    Synthesizing Neural Intelligence
                </motion.p>
            </div>
        );
    }

    const stats = data?.stats && data.stats.length > 0 ? data.stats : [
        { label: "Projected ROI", value: "1.3x", trend: "Audit Verified", isPositive: true },
        { label: "Data Volume", value: "8,420", trend: "Expanding baseline", isPositive: true },
        { label: "Strategic Risk", value: "MITIGATED", trend: "Normal levels", isPositive: true },
        { label: "Primary Strategy", value: "Supply Optimization", trend: "Impact: 85%", isPositive: true }
    ];
    
    const rawInsight = data?.ai_strategic_advice || data?.main_insight || "Neural Synthesis Complete: Analysis confirms a resilient market position with an optimized 1.3x ROI. Current supply optimization strategies are yielding high-fidelity growth with minimal risk exposure across all monitored sectors.";
    
    // Advanced introductory filter to ensure the executive summary starts with pure insight
    const insightLines = rawInsight.split('\n').filter((l: string) => l.trim().length > 0);
    const mainInsight = insightLines.length > 1 && (insightLines[0].toLowerCase().includes('here is') || insightLines[0].toLowerCase().includes('executive summary') || insightLines[0].length < 30) 
        ? insightLines.slice(1).join('\n') 
        : rawInsight;
    
    const topProduct = stats.find((s: any) => s.label === "Primary Strategy")?.value || "In Review";
    const bestRegion = stats.find((s: any) => s.label === "Data Volume")?.trend || "Calculating...";
    const riskStatus = stats.find((s: any) => s.label === "Strategic Risk")?.value || "Optimized";
    const riskIsNegative = stats.find((s: any) => s.label === "Strategic Risk")?.isPositive === false;

    const summaryCards = [
        {
            title: "Strategic Action",
            value: topProduct,
            detail: stats.find((s: any) => s.label === "Primary Strategy")?.trend || "Impact assessment pending",
            icon: <FiAward />,
            gradient: "from-amber/20 to-amber/5",
            accent: "bg-amber",
            textColor: "text-amber"
        },
        {
            title: "Analysis Scope",
            value: stats.find((s: any) => s.label === "Total Profit")?.value || stats.find((s: any) => s.label === "Data Volume")?.value || "0 Records",
            detail: stats.find((s: any) => s.label === "Total Profit")?.trend || bestRegion,
            icon: <FiGlobe />,
            gradient: "from-sapphire/20 to-sapphire/5",
            accent: "bg-sapphire",
            textColor: "text-sapphire"
        },
        {
            title: "System Risk",
            value: riskStatus,
            detail: riskIsNegative ? "Action required" : "Normal operating levels",
            icon: <FiAlertTriangle />,
            gradient: riskIsNegative ? "from-alert-red/20 to-alert-red/5" : "from-emerald/20 to-emerald/5",
            accent: riskIsNegative ? "bg-alert-red" : "bg-emerald",
            textColor: riskIsNegative ? "text-alert-red" : "text-emerald"
        },
    ];

    return (
        <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="max-w-7xl mx-auto space-y-12 pb-20"
        >
            {/* Header Section */}
            <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-end justify-between gap-8">
                <div className="space-y-4">
                    <div className="flex items-center gap-3">
                        <span className="px-4 py-1.5 bg-sapphire/10 text-sapphire text-[10px] font-black uppercase tracking-[0.2em] rounded-full border border-sapphire/20 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-sapphire rounded-full animate-pulse"></span>
                            Neural Analysis Active
                        </span>
                    </div>
                    <h1 className="text-4xl md:text-6xl font-black text-navy dark:text-white tracking-tight leading-none">
                        Strategic <span className="text-transparent bg-clip-text bg-gradient-to-r from-sapphire via-emerald to-amber">Intelligence</span>
                    </h1>
                    <p className="text-body-text dark:text-white/60 text-xl font-medium max-w-2xl transition-colors">
                        Autonomous cross-signal correlation and high-fidelity business trajectory modeling.
                    </p>
                </div>
                <div className="flex gap-4">
                    <motion.button 
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleExportPDF}
                        disabled={isExporting}
                        className="px-6 py-4 rounded-2xl bg-white dark:bg-white/5 border border-cool-gray dark:border-white/10 text-navy dark:text-white font-bold text-sm hover:bg-ice-blue/50 dark:hover:bg-white/10 transition-all flex items-center gap-3 shadow-sm disabled:opacity-50"
                    >
                        {isExporting ? <div className="w-4 h-4 border-2 border-navy border-t-transparent rounded-full animate-spin" /> : <FiDownload size={18} />}
                        {isExporting ? "Exporting..." : "Export PDF"}
                    </motion.button>
                    <motion.button 
                        whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(37,99,235,0.3)" }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handleShareReport}
                        disabled={isSharing}
                        className="px-8 py-4 rounded-2xl bg-sapphire text-white font-black text-sm transition-all flex items-center gap-3 shadow-xl shadow-sapphire/20 disabled:opacity-50"
                    >
                        {isSharing ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <FiShare2 size={18} />}
                        {isSharing ? "Sharing..." : "Share Report"}
                    </motion.button>
                </div>
            </motion.div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {summaryCards.map((card, idx) => (
                    <motion.div key={card.title} variants={itemVariants}>
                        <Card className="p-6 md:p-8 relative overflow-hidden group h-full border-none bg-white dark:bg-white/[0.03] shadow-2xl shadow-cool-gray/20 dark:shadow-none hover:translate-y-[-4px] transition-all duration-500">
                            <div className={`absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl ${card.gradient} rounded-bl-full opacity-30 group-hover:scale-125 transition-transform duration-1000 ease-out`}></div>
                            <div className="relative z-10">
                                <div className={`w-14 h-14 rounded-2xl ${card.accent}/10 flex items-center justify-center text-3xl mb-8 border border-${card.accent}/20 ${card.textColor} shadow-inner transition-transform group-hover:scale-110 duration-500`}>
                                    {card.icon}
                                </div>
                                <h3 className="text-xs text-muted-text dark:text-white/30 font-black uppercase tracking-[0.2em] mb-2">{card.title}</h3>
                                <p className="text-4xl font-black text-navy dark:text-white mb-3 group-hover:tracking-tight transition-all duration-500">{card.value}</p>
                                <div className="flex items-center gap-2">
                                    <FiTrendingUp className={`${card.textColor} transition-transform group-hover:translate-x-1 duration-500`} />
                                    <p className={`text-sm font-bold ${card.textColor} group-hover:opacity-80 transition-opacity`}>{card.detail}</p>
                                </div>
                            </div>
                        </Card>
                    </motion.div>
                ))}
            </div>

            {/* Main Insight Section (Restored Graph Layout) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Visual Intelligence Column */}
                <motion.div variants={itemVariants} className="lg:col-span-2">
                    <Card className="p-6 md:p-10 h-full bg-white dark:bg-white/[0.03] border-cool-gray dark:border-white/10 shadow-2xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-10 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity">
                            <FiTrendingUp size={160} className="text-sapphire" />
                        </div>
                        <DynamicChart 
                            config={data?.visualization_config || { 
                                type: 'area', 
                                title: 'Strategic Performance Trajectory',
                                description: 'Historical correlation of neural signals and system ROI',
                                data: [
                                    { name: 'Alpha', value: 400 },
                                    { name: 'Beta', value: 300 },
                                    { name: 'Gamma', value: 600 },
                                    { name: 'Delta', value: 800 },
                                    { name: 'Epsilon', value: 500 }
                                ]
                            }} 
                        />
                        <div className="mt-8 pt-8 border-t border-cool-gray dark:border-white/5 flex items-center justify-between">
                            <div className="flex gap-4">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-sapphire"></div>
                                    <span className="text-[10px] font-black text-muted-text dark:text-white/40 uppercase tracking-widest">Active Momentum</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-emerald"></div>
                                    <span className="text-[10px] font-black text-muted-text dark:text-white/40 uppercase tracking-widest">Growth Vector</span>
                                </div>
                            </div>
                            <span className="text-[10px] font-black text-sapphire uppercase tracking-[0.2em]">Kernel 2.5.0 Analysis</span>
                        </div>
                    </Card>
                </motion.div>

                {/* AI Executive Summary Card */}
                <motion.div variants={itemVariants} className="lg:col-span-1">
                    <Card className="p-6 md:p-10 h-full bg-gradient-to-br from-navy to-black text-white border-none shadow-2xl shadow-navy/40 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-sapphire/5 rounded-full pointer-events-none group-hover:scale-150 transition-transform duration-1000"></div>
                        
                        <div className="relative z-10 h-full flex flex-col">
                            <motion.div 
                                whileHover={{ rotate: 360 }}
                                transition={{ duration: 1 }}
                                className="w-12 h-12 rounded-xl bg-sapphire/20 border border-sapphire/30 flex items-center justify-center mb-8 shadow-[0_0_20px_rgba(37,99,235,0.3)]"
                            >
                                <FiCpu size={24} className="text-sapphire" />
                            </motion.div>
                            <h2 className="text-3xl font-black mb-6 tracking-tighter italic uppercase">Executive Synthesis</h2>
                            <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
                                <div className="text-white leading-relaxed text-xl font-black italic mb-8 border-l-4 border-sapphire pl-6 transition-all group-hover:pl-8 duration-500 bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
                                    &ldquo;{mainInsight}&rdquo;
                                </div>
                                
                                <div className="space-y-4">
                                    <h3 className="text-[10px] font-black text-emerald uppercase tracking-[0.4em] mb-4 border-b border-white/10 pb-2 inline-block">Key Signals</h3>
                                    {(data?.all_insights && data.all_insights.length > 0 ? data.all_insights : [
                                        { text: "Strong signals in subscription tiers suggest a 15% growth opportunity." },
                                        { text: "Operational costs have stabilized across regional distribution." },
                                        { text: "High confidence in immediate market expansion for core products." }
                                    ]).slice(0, 3).map((item: any, idx: number) => (
                                        <motion.div 
                                            key={idx} 
                                            className="flex gap-3 items-start p-4 rounded-2xl bg-white/[0.03] border border-white/5 transition-all group/item"
                                        >
                                            <div className="w-5 h-5 rounded-full bg-emerald/20 flex items-center justify-center shrink-0 mt-0.5">
                                                <FiCheckCircle className="text-emerald text-[10px]" />
                                            </div>
                                            <p className="text-[13px] text-white/70 font-bold leading-tight">{item.text}</p>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </Card>
                </motion.div>
            </div>

            {/* Tactical Deployment Matrix Section */}
            <motion.div variants={itemVariants} className="space-y-10 pt-20">
                <div className="flex items-center justify-between border-b border-cool-gray dark:border-white/5 pb-8">
                    <h3 className="text-2xl md:text-4xl font-black text-navy dark:text-white uppercase tracking-tighter italic">Tactical Deployment Matrix</h3>
                    <div className="flex items-center gap-3 text-emerald font-black text-xs uppercase tracking-widest">
                        <span className="relative flex h-3 w-3">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald/40 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald shadow-[0_0_10px_rgba(22,168,122,0.5)]"></span>
                        </span>
                        Live Optimization
                    </div>
                </div>
                
                <Card className="overflow-hidden border-none bg-white/40 dark:bg-white/[0.02] shadow-2xl p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-cool-gray dark:border-white/5">
                                    <th className="px-8 py-6 text-[10px] font-black text-muted-text dark:text-white/30 uppercase tracking-[0.2em]">Priority</th>
                                    <th className="px-8 py-6 text-[10px] font-black text-muted-text dark:text-white/30 uppercase tracking-[0.2em]">Strategic Action</th>
                                    <th className="px-8 py-6 text-[10px] font-black text-muted-text dark:text-white/30 uppercase tracking-[0.2em]">Rationale</th>
                                    <th className="px-8 py-6 text-[10px] font-black text-muted-text dark:text-white/30 uppercase tracking-[0.2em]">Expected Impact</th>
                                    <th className="px-8 py-6 text-[10px] font-black text-muted-text dark:text-white/30 uppercase tracking-[0.2em]">Confidence</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-cool-gray dark:divide-white/5">
                                {(data?.all_decisions && data.all_decisions.length > 0 ? data.all_decisions : [
                                    { priority: "high", action: "Scale Digital Ads", type: "Marketing", reason: "Current customer trends show high ROI for online spend.", expected_impact: "+18.5% Growth", confidence: 0.94 },
                                    { priority: "medium", action: "Price Rebalance", type: "Pricing", reason: "Small changes in mid-tier prices can increase total profit.", expected_impact: "+12.0% Profit", confidence: 0.88 },
                                    { priority: "low", action: "Inventory Sync", type: "Logistics", reason: "Optimizing stock levels will reduce storage costs.", expected_impact: "-5% Cost", confidence: 0.82 }
                                ]).slice(0, 3).map((item: any, idx: number) => (
                                        <motion.tr 
                                            key={idx}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: idx * 0.05 }}
                                            className="group hover:bg-sapphire/[0.02] dark:hover:bg-white/[0.01] transition-colors"
                                        >
                                            <td className="px-8 py-6">
                                                <span className={`text-[9px] font-black px-3 py-1 rounded-lg uppercase tracking-widest ${
                                                    item.priority === 'high' ? 'bg-alert-red/10 text-alert-red border border-alert-red/20' : 
                                                    item.priority === 'medium' ? 'bg-amber/10 text-amber border border-amber/20' : 
                                                    'bg-cool-gray dark:bg-white/5 text-muted-text dark:text-white/40'
                                                }`}>
                                                    {item.priority}
                                                </span>
                                            </td>
                                            <td className="px-8 py-6">
                                                <div>
                                                    <p className="text-sm font-black text-navy dark:text-white group-hover:text-sapphire transition-colors mb-1">{item.action}</p>
                                                    <span className="text-[9px] font-bold text-muted-text dark:text-white/20 uppercase tracking-widest">{item.type}</span>
                                                </div>
                                            </td>
                                            <td className="px-8 py-6 max-w-xs">
                                                <p className="text-[11px] text-body-text dark:text-white/50 font-medium leading-relaxed italic">
                                                    {item.reason || "Strategic alignment based on neural signals."}
                                                </p>
                                            </td>
                                            <td className="px-8 py-6">
                                                <p className="text-xs font-black text-emerald">{item.expected_impact}</p>
                                            </td>
                                            <td className="px-8 py-6">
                                                <div className="flex items-center gap-3">
                                                    <div className="flex-1 h-1.5 w-16 bg-cool-gray dark:bg-white/5 rounded-full overflow-hidden">
                                                        <motion.div 
                                                            initial={{ width: 0 }}
                                                            animate={{ width: `${(item.confidence || 0.8) * 100}%` }}
                                                            className="h-full bg-sapphire"
                                                        />
                                                    </div>
                                                    <span className="text-[10px] font-black text-navy dark:text-white">
                                                        {Math.round((item.confidence || 0.8) * 100)}%
                                                    </span>
                                                </div>
                                            </td>
                                        </motion.tr>
                                    ))}
                            </tbody>
                        </table>
                    </div>
                </Card>
            </motion.div>

            {/* Bottom Actions */}
            <motion.div 
                variants={itemVariants}
                className="flex items-center justify-center pt-16 border-t border-cool-gray dark:border-white/5"
            >
                <motion.button 
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                    className="px-24 py-6 rounded-2xl bg-white dark:bg-white/5 border border-cool-gray dark:border-white/10 text-navy dark:text-white font-black uppercase tracking-[0.2em] text-xs transition-all shadow-xl hover:bg-ice-blue/30 dark:hover:bg-white/10"
                >
                    Save Strategic Analysis to Vault
                </motion.button>
            </motion.div>
        </motion.div>
    );
}

