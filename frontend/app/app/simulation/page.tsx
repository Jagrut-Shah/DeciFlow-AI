"use client";

import React, { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";

export default function SimulationPage() {
  const [price, setPrice] = useState(150);
  const [demand, setDemand] = useState(5000);
  const [isSimulating, setIsSimulating] = useState(false);
  const [results, setResults] = useState<{ profit: number; margin: number } | null>(null);

  const runSimulation = () => {
    setIsSimulating(true);
    // Fake simulation delay
    setTimeout(() => {
      setIsSimulating(false);
      // Fake math to make it look dynamic
      const generatedProfit = (price * demand) * 0.35 * (Math.random() * 0.2 + 0.9);
      const generatedMargin = 35 + (price - 100) * 0.1 - (demand / 1000);
      setResults({
        profit: generatedProfit,
        margin: generatedMargin,
      });
    }, 1500);
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div>
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 mb-2">
          Simulation Engine ⚙️
        </h1>
        <p className="text-gray-400 text-lg">Test hypothetical scenarios and forecast outcomes using our predictive models.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Controls */}
        <Card className="p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Input Variables</h2>
          
          <div className="space-y-8">
            <div>
              <div className="flex justify-between mb-2">
                <label className="text-gray-300 font-medium">Pricing Point ($)</label>
                <span className="text-cyan-400 font-bold">${price}</span>
              </div>
              <input 
                type="range" 
                min="50" 
                max="500" 
                step="5"
                value={price} 
                onChange={(e) => setPrice(Number(e.target.value))}
                className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-cyan-500 hover:accent-cyan-400 transition-all"
              />
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <label className="text-gray-300 font-medium">Expected Demand (Units)</label>
                <span className="text-indigo-400 font-bold">{demand.toLocaleString()}</span>
              </div>
              <input 
                type="range" 
                min="1000" 
                max="20000" 
                step="500"
                value={demand} 
                onChange={(e) => setDemand(Number(e.target.value))}
                className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-indigo-500 hover:accent-indigo-400 transition-all"
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
          <h2 className="text-2xl font-bold text-white mb-6">Prediction Results</h2>
          
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
                  <p className="text-5xl font-extrabold text-white">
                    ${results.profit.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-center">
                    <p className="text-gray-400 text-sm mb-1">Profit Margin</p>
                    <p className="text-2xl font-bold text-cyan-400">{results.margin.toFixed(1)}%</p>
                  </div>
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-center">
                    <p className="text-gray-400 text-sm mb-1">Risk Factor</p>
                    <p className="text-2xl font-bold text-amber-400">Low (12%)</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500">
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