"use client";

import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen bg-neutral-950 text-white selection:bg-indigo-500/30 overflow-hidden">

      {/* Background Gradients */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-600/20 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/20 blur-[120px]" />
      </div>

      <main className="relative z-10 max-w-6xl mx-auto px-6">

        {/* HERO */}
        <section className="py-20 flex flex-col items-center text-center mt-10">
          <Image
            src="/logo.png"
            alt="DeciFlow AI Logo"
            width={96}
            height={96}
            className="object-contain mb-8 hover:scale-105 transition-all duration-300"
          />
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            DeciFlow AI
          </h1>
          <p className="text-2xl md:text-3xl font-medium text-gray-300 mb-4 max-w-3xl">
            From data to decisions without needing an expert.
          </p>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl">
            Analyze, simulate, and act on your data with AI-powered intelligence.
          </p>
        </section>

        {/* FEATURES */}
        <section className="py-20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            <div className="p-8 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all duration-300 hover:scale-105 hover:shadow-[0_0_30px_rgba(99,102,241,0.15)] group">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">💡</div>
              <h3 className="text-xl font-bold mb-3">AI Insights</h3>
              <p className="text-gray-400">
                Get intelligent recommendations from your data instantly.
              </p>
            </div>

            <div className="p-8 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all duration-300 hover:scale-105 hover:shadow-[0_0_30px_rgba(168,85,247,0.15)] group">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">🧪</div>
              <h3 className="text-xl font-bold mb-3">Simulation</h3>
              <p className="text-gray-400">
                Test decisions before applying them in real scenarios.
              </p>
            </div>

            <div className="p-8 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all duration-300 hover:scale-105 hover:shadow-[0_0_30px_rgba(236,72,153,0.15)] group">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">💬</div>
              <h3 className="text-xl font-bold mb-3">Smart Chat</h3>
              <p className="text-gray-400">
                Interact with your data using AI-powered chat.
              </p>
            </div>

          </div>
        </section>

        {/* HOW IT WORKS */}
        <section className="py-20">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            How It Works
          </h2>

          <div className="flex flex-col md:flex-row items-center justify-between gap-4 md:gap-2">

            {["Upload", "Analyze", "Generate Insights", "Decide"].map((step, i) => (
              <div key={i} className="w-full md:w-1/4 p-6 rounded-2xl border border-white/10 bg-white/5 text-center hover:bg-white/10 transition-all duration-300 hover:scale-105">
                <h4 className="font-semibold text-lg">{step}</h4>
              </div>
            ))}

          </div>
        </section>

        {/* CTA */}
        <section className="py-20 text-center">
          <div className="p-12 md:p-16 rounded-3xl bg-gradient-to-b from-white/5 to-transparent border-t border-white/10">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Start making smarter decisions today.
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              DeciFlow AI helps you move from raw data to real impact.
            </p>
          </div>
        </section>

      </main>
    </div>
  );
}