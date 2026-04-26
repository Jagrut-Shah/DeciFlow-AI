"use client";

import React, { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import { apiClient, API_BASE_URL } from "@/services/api";
import { motion, AnimatePresence } from "framer-motion";

export default function SimulationPage() {
    const [adSpend, setAdSpend] = useState(50000);
    const [cpc, setCpc] = useState(15.0);
    const [convRate, setConvRate] = useState(3.5);
    const [aov, setAov] = useState(1200);
    const [unitCost, setUnitCost] = useState(450);
    const [orderGoal, setOrderGoal] = useState(1500);

    const [isSimulating, setIsSimulating] = useState(false);
    const [results, setResults] = useState<{ 
        profit: number; 
        margin: number; 
        risk: string; 
        recommendation: string; 
        narrative?: string;
        conversions?: number;
        roas?: string;
        cac?: string;
        goal_achievement?: string;
    } | null>(null);
    const [isExporting, setIsExporting] = useState(false);

    const runSimulation = async () => {
        setIsSimulating(true);
        try {
            const result = await apiClient.post("/simulation/run", { 
                ad_spend: adSpend,
                cpc,
                conversion_rate: convRate,
                aov,
                unit_cost: unitCost,
                order_goal: orderGoal
            });
            if (result.status === 'success') {
                setResults({
                    profit: result.data.projected_profit,
                    margin: parseFloat(result.data.roi),
                    risk: result.data.risk_level,
                    recommendation: result.data.recommendation,
                    narrative: result.data.narrative,
                    conversions: result.data.projected_conversions,
                    roas: result.data.roas,
                    cac: result.data.cac,
                    goal_achievement: result.data.goal_achievement
                });
            }
        } catch (error) {
            console.error("Simulation failed:", error);
        } finally {
            setIsSimulating(false);
        }
    };

    const handleExportPDF = async () => {
        if (!results) return;
        setIsExporting(true);
        try {
            const reportData = {
                session_id: `sim_${Date.now()}`,
                data: {
                    ...results,
                    inputs: {
                        ad_spend: adSpend,
                        cpc,
                        conversion_rate: convRate,
                        aov,
                        unit_cost: unitCost,
                        order_goal: orderGoal
                    },
                    projected_profit: results.profit,
                    revenue: (results.conversions || 0) * aov,
                    projected_conversions: results.conversions,
                    roi: `${results.margin}%`,
                    risk_level: results.risk
                }
            };

            const response = await apiClient.post("/reports/generate", reportData);
            
            if (response.status === 'success') {
                const serverOrigin = API_BASE_URL.replace(/\/api\/v1\/?$/, '');
                const downloadUrl = `${serverOrigin}${response.data.report_url}`;
                window.open(downloadUrl, '_blank');
            }
        } catch (error) {
            console.error("Simulation export failed:", error);
            alert("Strategic export failed. Check neural link.");
        } finally {
            setIsExporting(false);
        }
    };

    const containerVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { 
            opacity: 1, 
            y: 0,
            transition: { 
                duration: 0.6,
                staggerChildren: 0.1
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, x: -10 },
        visible: { opacity: 1, x: 0 }
    };

    return (
        <motion.div 
            initial="hidden"
            animate="visible"
            variants={containerVariants}
            className="space-y-8"
        >
            <motion.div variants={itemVariants}>
                <h1 className="text-4xl font-extrabold text-navy dark:text-white mb-2">
                    Strategic <span className="text-sapphire">Simulation</span> Engine
                </h1>
                <p className="text-body-text dark:text-white/60 text-lg max-w-3xl">
                    Forecast business outcomes by modeling marketing efficiency, unit economics, and operational overhead in ₹.
                </p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Controls */}
                <motion.div variants={itemVariants} className="lg:col-span-2">
                    <Card className="p-8 h-full">
                        <h2 className="text-2xl font-bold text-navy dark:text-white mb-8 flex items-center gap-2">
                            <span className="w-8 h-8 rounded-lg bg-sapphire/10 flex items-center justify-center text-sapphire text-sm italic font-black">1</span>
                            Simulation Parameters
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10">
                            {/* Marketing Column */}
                            <div className="space-y-8">
                                <h3 className="text-xs font-black text-sapphire uppercase tracking-widest border-b border-sapphire/10 pb-2">Acquisition Strategy</h3>
                                
                                <SimulationInput 
                                    label="Marketing Investment"
                                    value={adSpend}
                                    onChange={setAdSpend}
                                    prefix="₹"
                                    colorClass="sapphire"
                                />

                                <SimulationInput 
                                    label="Cost per Website Visit"
                                    value={cpc}
                                    onChange={setCpc}
                                    prefix="₹"
                                    colorClass="sapphire"
                                />

                                <SimulationInput 
                                    label="Expected Order Success Rate"
                                    value={convRate}
                                    onChange={setConvRate}
                                    suffix="%"
                                    colorClass="sapphire"
                                />
                            </div>

                            {/* Economics Column */}
                            <div className="space-y-8">
                                <h3 className="text-xs font-black text-emerald uppercase tracking-widest border-b border-emerald/10 pb-2">Unit Economics & Scale</h3>
                                
                                <SimulationInput 
                                    label="Average Sale Value"
                                    value={aov}
                                    onChange={setAov}
                                    prefix="₹"
                                    colorClass="emerald"
                                />

                                <SimulationInput 
                                    label="Cost to Fulfill (per Order)"
                                    value={unitCost}
                                    onChange={setUnitCost}
                                    prefix="₹"
                                    colorClass="emerald"
                                />

                                <SimulationInput 
                                    label="Target Order Goal"
                                    value={orderGoal}
                                    onChange={setOrderGoal}
                                    suffix="Orders"
                                    colorClass="emerald"
                                />
                            </div>
                        </div>

                        <Button
                            className="w-full text-lg mt-12 py-5 shadow-xl shadow-sapphire/20 font-black tracking-widest uppercase relative overflow-hidden group"
                            onClick={runSimulation}
                            disabled={isSimulating}
                        >
                            <motion.div
                                initial={false}
                                animate={isSimulating ? { opacity: [0.3, 0.6, 0.3] } : { opacity: 0 }}
                                transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
                                className="absolute inset-0 bg-white/10"
                            />
                            <span className="relative z-10 flex items-center justify-center gap-3">
                                {isSimulating ? (
                                    <>
                                        <motion.div 
                                            animate={{ rotate: 360 }}
                                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                            className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full"
                                        />
                                        <span className="tracking-widest">CALIBRATING STRATEGY...</span>
                                    </>
                                ) : "Run AI Simulation"}
                            </span>
                        </Button>
                    </Card>
                </motion.div>

                {/* Results */}
                <motion.div variants={itemVariants} className="h-full">
                    <Card className="p-8 h-full bg-gradient-to-br from-sapphire/[0.03] via-ice-blue to-transparent dark:from-sapphire/[0.07] dark:via-transparent dark:to-transparent flex flex-col border-sapphire/10 dark:border-white/5 relative overflow-hidden">
                        {/* Interactive Background Elements */}
                        <motion.div 
                            animate={{ 
                                scale: [1, 1.2, 1],
                                rotate: [0, 90, 180, 270, 360]
                            }}
                            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                            className="absolute -top-20 -right-20 w-64 h-64 bg-sapphire/5 rounded-full blur-3xl pointer-events-none" 
                        />
                        
                        <h2 className="text-2xl font-bold text-navy dark:text-white mb-8 flex items-center gap-2 relative z-10">
                            <span className="w-8 h-8 rounded-lg bg-emerald/10 flex items-center justify-center text-emerald text-sm italic font-black">2</span>
                            Forecasted Outcomes
                        </h2>

                        <div className="flex-1 flex flex-col justify-center items-center relative z-10 min-h-[400px]">
                            <AnimatePresence mode="wait">
                                {isSimulating ? (
                                    <motion.div 
                                        key="loading"
                                        initial={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
                                        animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                                        exit={{ opacity: 0, scale: 1.1, filter: "blur(10px)" }}
                                        className="flex flex-col items-center gap-8"
                                    >
                                        <div className="relative w-56 h-56 flex items-center justify-center">
                                            {/* Strategic Scanning Grid */}
                                            <motion.div 
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                className="absolute inset-0 border border-sapphire/20 rounded-3xl overflow-hidden bg-sapphire/[0.02] dark:bg-white/[0.02] backdrop-blur-sm"
                                            >
                                                <div className="absolute inset-0 grid grid-cols-6 grid-rows-6 opacity-30">
                                                    {[...Array(36)].map((_, i) => (
                                                        <div key={i} className="border-[0.5px] border-sapphire/20" />
                                                    ))}
                                                </div>
                                                
                                                {/* Scanning Beam */}
                                                <motion.div 
                                                    animate={{ top: ["-10%", "110%", "-10%"] }}
                                                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                                                    className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-sapphire to-transparent shadow-[0_0_20px_rgba(14,165,233,0.5)] z-10"
                                                />

                                                {/* Neural Nodes */}
                                                {[...Array(6)].map((_, i) => (
                                                    <motion.div
                                                        key={i}
                                                        animate={{ 
                                                            opacity: [0.1, 0.8, 0.1],
                                                            scale: [0.8, 1.2, 0.8]
                                                        }}
                                                        transition={{ 
                                                            duration: 2.5, 
                                                            repeat: Infinity, 
                                                            delay: i * 0.4 
                                                        }}
                                                        className="absolute w-2 h-2 bg-sapphire/60 rounded-full blur-[1px]"
                                                        style={{ 
                                                            top: `${[20, 45, 70, 30, 60, 80][i]}%`, 
                                                            left: `${[30, 15, 60, 80, 25, 75][i]}%` 
                                                        }}
                                                    />
                                                ))}
                                            </motion.div>

                                            {/* Core Pulse */}
                                            <motion.div
                                                animate={{
                                                    scale: [1, 1.05, 1],
                                                    rotate: [0, 90, 180, 270, 360]
                                                }}
                                                transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                                                className="w-20 h-20 border border-sapphire/30 rounded-2xl flex items-center justify-center bg-white/5 backdrop-blur-xl relative z-20"
                                            >
                                                <motion.div 
                                                    animate={{ opacity: [0.4, 1, 0.4] }}
                                                    transition={{ duration: 2, repeat: Infinity }}
                                                    className="w-10 h-10 bg-sapphire rounded-lg shadow-[0_0_30px_rgba(14,165,233,0.4)]"
                                                />
                                            </motion.div>
                                        </div>
                                        <div className="text-center space-y-2">
                                            <p className="text-sapphire font-black uppercase tracking-[0.3em] text-[10px]">Processing Pipeline</p>
                                            <p className="text-navy dark:text-white/40 text-xs font-bold italic">Synthesizing multi-variable market dynamics...</p>
                                        </div>
                                    </motion.div>
                                ) : results ? (
                                    <motion.div 
                                        key="results"
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="w-full space-y-6"
                                    >
                                        <motion.div 
                                            whileHover={{ scale: 1.02 }}
                                            className="bg-white dark:bg-white/[0.03] border border-cool-gray dark:border-white/10 rounded-[2.5rem] p-10 text-center shadow-2xl shadow-sapphire/5 backdrop-blur-xl"
                                        >
                                            <p className="text-muted-text dark:text-white/40 text-[10px] font-black mb-4 uppercase tracking-[0.2em]">Predicted Net Profit</p>
                                            <motion.p 
                                                initial={{ scale: 0.5, opacity: 0 }}
                                                animate={{ scale: 1, opacity: 1 }}
                                                transition={{ type: "spring", stiffness: 200, damping: 15 }}
                                                className={`text-6xl font-black tracking-tighter transition-colors ${results.profit >= 0 ? 'text-emerald' : 'text-alert-red'}`}
                                            >
                                                {results.profit < 0 ? '-' : ''}₹{Math.abs(results.profit).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                                            </motion.p>
                                        </motion.div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <ResultMiniCard 
                                                label="Ad Spend Return" 
                                                value={results.roas} 
                                                color="sapphire"
                                            />
                                            <ResultMiniCard 
                                                label="Acquisition Cost" 
                                                value={results.cac} 
                                                color="amber"
                                            />
                                        </div>
 
                                        <div className="grid grid-cols-2 gap-4">
                                            <ResultMiniCard 
                                                label="Goal Completion" 
                                                value={results.goal_achievement} 
                                                color={results.goal_achievement?.includes('Goal') ? 'emerald' : parseFloat(results.goal_achievement || '0') > 90 ? 'emerald' : 'amber'}
                                            />
                                            <ResultMiniCard 
                                                label="Strategic Risk" 
                                                value={results.risk} 
                                                color={results.risk === 'High' ? 'alert-red' : results.risk === 'Low' ? 'emerald' : 'amber'}
                                            />
                                        </div>

 
                                        <motion.div 
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.3 }}
                                            className="mt-8 p-8 bg-gradient-to-br from-navy to-[#0b0f19] text-white rounded-[2rem] relative shadow-2xl shadow-navy/40 overflow-hidden group border border-white/5"
                                        >
                                            <div className="absolute top-0 right-0 p-6 opacity-20 group-hover:rotate-12 transition-transform duration-700">
                                                <div className="w-12 h-12 bg-emerald blur-2xl rounded-full" />
                                            </div>
                                            <p className="text-[15px] leading-relaxed font-medium text-white/80 line-clamp-4">
                                                &ldquo;{results.narrative?.replace(/^(\*\*|)(Executive Summary:|Summary:|Analysis:|Insight:)(\*\*|)\s*/i, '') || "System analysis complete. Strategic recommendation synchronized."}&rdquo;
                                            </p>
                                        </motion.div>

                                        <Button
                                            className="w-full bg-navy hover:bg-navy/90 text-white mt-6 py-4 rounded-2xl flex items-center justify-center gap-2 font-black uppercase tracking-widest text-xs border border-white/10 no-print disabled:opacity-50"
                                            onClick={handleExportPDF}
                                            disabled={isExporting}
                                        >
                                            {isExporting ? (
                                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                            ) : (
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                </svg>
                                            )}
                                            {isExporting ? "Generating Strategic Report..." : "Generate Strategy PDF"}
                                        </Button>
                                    </motion.div>
                                ) : (
                                    <motion.div 
                                        key="empty"
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 1.1 }}
                                        className="text-center py-20"
                                    >
                                        <div className="w-32 h-32 bg-gradient-to-br from-ice-blue to-white dark:from-white/5 dark:to-transparent rounded-[2.5rem] flex items-center justify-center mx-auto mb-10 shadow-2xl rotate-3">
                                            <motion.span 
                                                animate={{ rotate: [0, 5, -5, 0] }}
                                                transition={{ duration: 4, repeat: Infinity }}
                                                className="text-6xl grayscale opacity-40 filter drop-shadow-2xl"
                                            >
                                                📉
                                            </motion.span>
                                        </div>
                                        <h3 className="text-2xl font-black text-navy dark:text-white mb-4 tracking-tight">System Idle</h3>
                                        <p className="text-sm text-muted-text dark:text-white/40 max-w-[240px] mx-auto font-medium leading-relaxed">
                                            Awaiting multi-variable input data for strategic market synthesis.
                                        </p>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </Card>
                </motion.div>
            </div>
        </motion.div>
    );
}

const SimulationInput = ({ label, value, onChange, prefix, suffix }: any) => (
    <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative group"
    >
        <label className="block text-[10px] font-black text-muted-text dark:text-white/30 mb-3 uppercase tracking-[0.2em] group-focus-within:text-sapphire transition-colors">{label}</label>
        <div className="relative">
            {prefix && (
                <div className="absolute left-6 top-1/2 -translate-y-1/2 text-muted-text dark:text-white/20 group-focus-within:text-sapphire transition-colors font-bold text-2xl pointer-events-none">
                    {prefix}
                </div>
            )}
            <input
                type="number"
                min="0"
                value={value}
                onChange={(e) => onChange(e.target.value === '' ? 0 : Number(e.target.value))}
                className={`w-full bg-white dark:bg-white/[0.03] border-2 border-cool-gray dark:border-white/5 rounded-[1.5rem] py-6 ${prefix ? 'pl-14' : 'pl-8'} pr-14 text-2xl font-black text-navy dark:text-white focus:ring-0 focus:border-sapphire/40 transition-all outline-none shadow-sm hover:border-cool-gray/80 dark:hover:border-white/10`}
            />
            {suffix && (
                <div className="absolute right-6 top-1/2 -translate-y-1/2 text-muted-text dark:text-white/20 font-black text-sm uppercase pointer-events-none">
                    {suffix}
                </div>
            )}
        </div>
    </motion.div>
);

const ResultMiniCard = ({ label, value, trend, color }: any) => (
    <motion.div 
        whileHover={{ y: -5, scale: 1.02 }}
        className="bg-white dark:bg-white/[0.03] border border-cool-gray dark:border-white/10 rounded-[1.8rem] p-6 text-center backdrop-blur-md shadow-lg shadow-black/5"
    >
        <p className="text-muted-text dark:text-white/40 text-[9px] font-black mb-2 uppercase tracking-[0.2em]">{label}</p>
        <div className="flex items-center justify-center gap-2">
            <p className={`text-3xl font-black tracking-tighter text-${color}`}>
                {value}
            </p>
            {trend && (
                <span className={`text-[10px] ${trend === 'up' ? 'text-emerald' : 'text-alert-red'}`}>
                    {trend === 'up' ? '▲' : '▼'}
                </span>
            )}
        </div>
    </motion.div>
);


