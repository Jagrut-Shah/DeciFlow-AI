"use client";

import React, { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import { apiClient } from "@/services/api";

export default function SimulationPage() {
    const [price, setPrice] = useState(150);
    const [demand, setDemand] = useState(5000);
    const [isSimulating, setIsSimulating] = useState(false);
    const [results, setResults] = useState<{ 
        profit: number; 
        margin: number; 
        risk: string; 
        recommendation: string; 
        narrative?: string;
    } | null>(null);

    const runSimulation = async () => {
        setIsSimulating(true);
        try {
            const result = await apiClient.post("/simulation/run", { price, demand });
            if (result.status === 'success') {
                setResults({
                    profit: result.data.projected_profit,
                    margin: parseFloat(result.data.roi),
                    risk: result.data.risk_level,
                    recommendation: result.data.recommendation,
                    narrative: result.data.narrative
                });
            }
        } catch (error) {
            console.error("Simulation failed:", error);
        } finally {
            setIsSimulating(false);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div>
                <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-slate-900 to-slate-500 dark:from-white dark:to-gray-400 mb-2">
                    Simulation Engine ⚙️
                </h1>
                <p className="text-slate-500 dark:text-gray-400 text-lg">Test hypothetical scenarios and forecast outcomes using our predictive models.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Controls */}
                <Card className="p-8">
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Input Variables</h2>

                    <div className="space-y-8">
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-slate-600 dark:text-gray-300 font-medium">Pricing Point ($)</label>
                                <span className="text-cyan-400 font-bold">${price}</span>
                            </div>
                            <input
                                type="range"
                                min="50"
                                max="500"
                                step="5"
                                value={price}
                                onChange={(e) => setPrice(Number(e.target.value))}
                                className="w-full h-2 bg-slate-200 dark:bg-white/10 rounded-lg appearance-none cursor-pointer accent-cyan-500 hover:accent-cyan-400 transition-all"
                            />
                        </div>

                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-slate-600 dark:text-gray-300 font-medium">Expected Demand (Units)</label>
                                <span className="text-indigo-400 font-bold">{demand.toLocaleString()}</span>
                            </div>
                            <input
                                type="range"
                                min="1000"
                                max="20000"
                                step="500"
                                value={demand}
                                onChange={(e) => setDemand(Number(e.target.value))}
                                className="w-full h-2 bg-slate-200 dark:bg-white/10 rounded-lg appearance-none cursor-pointer accent-indigo-500 hover:accent-indigo-400 transition-all"
                            />
                        </div>

                        <Button
                            className="w-full text-lg mt-4 py-4"
                            onClick={runSimulation}
                            disabled={isSimulating}
                        >
                            {isSimulating ? "Running AI Models..." : "Run Simulation"}
                        </Button>
                    </div>
                </Card>

                {/* Results */}
                <Card className="p-8 bg-gradient-to-br from-indigo-900/20 to-transparent flex flex-col">
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">Prediction Results</h2>

                    <div className="flex-1 flex flex-col justify-center items-center">
                        {isSimulating ? (
                            <div className="flex flex-col items-center gap-4 animate-pulse">
                                <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                                <p className="text-indigo-300">Calculating multidimensional vectors...</p>
                            </div>
                        ) : results ? (
                            <div className="w-full space-y-6 animate-in zoom-in-95 duration-500">
                                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-6 text-center">
                                    <p className="text-emerald-400 text-sm font-semibold mb-2 uppercase tracking-wider">Projected Net Profit</p>
                                    <p className="text-5xl font-extrabold text-slate-900 dark:text-white">
                                        ${results.profit.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                                    </p>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-slate-100 dark:bg-white/5 border border-slate-300 dark:border-white/10 rounded-2xl p-4 text-center">
                                        <p className="text-slate-500 dark:text-gray-400 text-sm mb-1">Profit Margin</p>
                                        <p className="text-2xl font-bold text-cyan-400">{results.margin.toFixed(1)}%</p>
                                    </div>
                                    <div className="bg-slate-100 dark:bg-white/5 border border-slate-300 dark:border-white/10 rounded-2xl p-4 text-center">
                                        <p className="text-slate-500 dark:text-gray-400 text-sm mb-1">Risk Factor</p>
                                        <p className={`text-2xl font-bold ${results.risk === 'High' ? 'text-red-400' : 'text-amber-400'}`}>
                                            {results.risk}
                                        </p>
                                    </div>
                                </div>
                                <div className="mt-6 p-6 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl relative">
                                    <div className="absolute -top-3 left-4 px-2 bg-[#0d121f] text-indigo-400 text-xs font-bold uppercase tracking-widest">AI Strategic Analyst</div>
                                    <p className="text-slate-700 dark:text-gray-200 leading-relaxed italic">
                                        "{results.narrative || "Analysis in progress..."}"
                                    </p>
                                </div>
                                
                                {results.recommendation === "Generate PDF Report" && (
                                    <button className="w-full mt-6 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 text-slate-900 dark:text-white font-bold rounded-2xl shadow-xl hover:shadow-emerald-500/20 transition-all active:scale-95">
                                        📥 Generate Executive PDF Report
                                    </button>
                                )}
                            </div>
                        ) : (
                            <div className="text-center text-slate-500 dark:text-gray-500">
                                <span className="text-6xl mb-4 block opacity-50">📉</span>
                                <p>Adjust the inputs and run the simulation to see AI predictions.</p>
                            </div>
                        )}
                    </div>
                </Card>
            </div>
        </div>
    );
}
