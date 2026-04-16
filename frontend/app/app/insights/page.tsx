import React from "react";
import Card from "@/components/Card";

export default function InsightsPage() {
    const insights = [
        {
            title: "Top Product",
            value: "Quantum Series X",
            detail: "32% of total revenue",
            icon: "🏆",
            gradient: "from-amber-400/20 to-orange-500/20",
            textColor: "text-amber-400"
        },
        {
            title: "Best Region",
            value: "North America",
            detail: "+18% YoY growth",
            icon: "🌎",
            gradient: "from-cyan-400/20 to-blue-500/20",
            textColor: "text-cyan-400"
        },
        {
            title: "Risk Alert",
            value: "Supply Chain",
            detail: "Logistics delay in EU",
            icon: "⚠️",
            gradient: "from-red-400/20 to-rose-500/20",
            textColor: "text-red-400"
        },
    ];

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="mb-10">
                <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 pb-2">
                    AI Insights 📊
                </h1>
                <p className="text-gray-400 text-lg">Deep drill-down into your business metrics powered by Machine Learning.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {insights.map((insight) => (
                    <Card key={insight.title} className="p-6 relative overflow-hidden group">
                        <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${insight.gradient} rounded-bl-full opacity-50 transition-transform group-hover:scale-110 duration-500`}></div>
                        <div className="relative z-10">
                            <span className="text-4xl mb-4 block">{insight.icon}</span>
                            <h3 className="text-lg text-gray-400 font-medium mb-1">{insight.title}</h3>
                            <p className="text-2xl font-bold text-white mb-2">{insight.value}</p>
                            <p className={`text-sm font-semibold ${insight.textColor}`}>{insight.detail}</p>
                        </div>
                    </Card>
                ))}
            </div>

            <Card className="p-8 mt-8 border-indigo-500/30 bg-gradient-to-br from-indigo-900/10 to-purple-900/10 backdrop-blur-xl">
                <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center shrink-0 border border-indigo-500/30">
                        <span className="text-2xl">🤖</span>
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-white mb-3">AI Strategic Recommendation</h2>
                        <p className="text-gray-300 leading-relaxed max-w-4xl text-lg mb-6">
                            Based on the recent correlation between <span className="text-cyan-400 font-medium">marketing spend in APAC</span> and the surging demand for <span className="text-amber-400 font-medium">Quantum Series X</span>, our models predict a <span className="text-emerald-400 font-bold">25% ROI increase</span> if you reallocate $15,000 from the EU logistics budget to APAC digital campaigns over the next 14 days.
                        </p>
                        <div className="flex gap-4">
                            <button className="px-6 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold hover:scale-105 transition-transform shadow-[0_0_15px_rgba(99,102,241,0.5)]">
                                Execute Strategy
                            </button>
                            <button className="px-6 py-2 rounded-xl bg-white/5 border border-white/10 text-white font-semibold hover:bg-white/10 transition-colors">
                                View Detailed Model
                            </button>
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    );
}