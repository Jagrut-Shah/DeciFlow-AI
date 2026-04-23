import React from "react";
import Card from "@/components/Card";

export default function Dashboard() {
    const stats = [
        { label: "Revenue", value: "$42,500", trend: "+12.5%", isPositive: true },
        { label: "Growth", value: "84.2%", trend: "+5.2%", isPositive: true },
        { label: "Loss", value: "$1,200", trend: "-2.1%", isPositive: false },
    ];

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 mb-2">
                        Welcome back, Richa 👋
                    </h1>
                    <p className="text-gray-400 text-lg">Here's your AI-powered performance overview.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {stats.map((stat) => (
                    <Card key={stat.label} className="p-6">
                        <h3 className="text-lg text-gray-400 font-medium mb-2">{stat.label}</h3>
                        <div className="flex items-end justify-between">
                            <p className="text-3xl font-bold text-white">{stat.value}</p>
                            <span className={`text-sm font-semibold rounded-full px-3 py-1 ${stat.isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                                {stat.trend}
                            </span>
                        </div>
                    </Card>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Fake Line Chart UI */}
                <Card className="lg:col-span-2 p-6 flex flex-col min-h-[350px]">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold text-white">Performance Overview</h3>
                        <div className="flex gap-2">
                            {['1D', '1W', '1M', '1Y'].map((t) => (
                                <button key={t} className="px-3 py-1 text-sm bg-white/5 hover:bg-white/10 rounded-md text-gray-300 transition-colors">
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div className="flex-1 flex justify-center items-center bg-gradient-to-t from-indigo-900/20 to-transparent border border-indigo-500/10 border-dashed rounded-xl relative overflow-hidden">
                        {/* Abstract chart representation */}
                        <svg className="w-full h-32 px-4" viewBox="0 0 100 30" preserveAspectRatio="none">
                            <path d="M0,25 C20,15 30,28 50,15 C70,2 80,18 100,5" fill="none" stroke="url(#paint0_linear)" strokeWidth="0.5" />
                            <path d="M0,25 C20,15 30,28 50,15 C70,2 80,18 100,5 L100,30 L0,30 Z" fill="url(#paint1_linear)" opacity="0.3" />
                            <defs>
                                <linearGradient id="paint0_linear" x1="0" y1="0" x2="100" y2="0" gradientUnits="userSpaceOnUse">
                                    <stop stopColor="#22d3ee" />
                                    <stop offset="1" stopColor="#6366f1" />
                                </linearGradient>
                                <linearGradient id="paint1_linear" x1="50" y1="0" x2="50" y2="30" gradientUnits="userSpaceOnUse">
                                    <stop stopColor="#6366f1" />
                                    <stop offset="1" stopColor="transparent" stopOpacity="0" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                </Card>

                {/* AI Insight Box */}
                <Card className="p-6 flex flex-col justify-between bg-gradient-to-br from-indigo-900/40 to-[#0B0F1A] border-indigo-500/30">
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <span className="text-xl">✨</span>
                            <h3 className="text-xl font-bold text-white">AI Insight</h3>
                        </div>
                        <p className="text-gray-300 leading-relaxed">
                            We noticed a <span className="text-emerald-400 font-semibold">15% surge</span> in growth over the last 48 hours. Consider scaling up your ad spend to maximize current momentum.
                        </p>
                    </div>
                    <button className="mt-6 w-full py-3 rounded-xl bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 font-semibold transition-colors duration-300">
                        View Details
                    </button>
                </Card>
            </div>
        </div>
    );
}