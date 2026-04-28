"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { FiTrendingUp, FiArrowRight, FiShield, FiZap, FiTarget, FiActivity } from "react-icons/fi";

export default function Home() {
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    setHasMounted(true);
  }, []);

  if (!hasMounted) return null;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.8, ease: [0.22, 1, 0.36, 1] }
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-sapphire/30 overflow-x-hidden relative transition-colors duration-500">
      
      {/* Premium Texture Overlay */}
      <div className="fixed inset-0 pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] dark:opacity-[0.05] mix-blend-overlay z-50"></div>

      {/* High-Tech Grid Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:60px_60px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-40"></div>
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.4 }}
          transition={{ duration: 2 }}
          className="absolute inset-0 bg-gradient-to-b from-sapphire/5 via-transparent to-transparent"
        />
        
        {/* Subtle Neural Pulse */}
        <motion.div
          animate={{ opacity: [0.1, 0.3, 0.1] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute inset-0 bg-gradient-to-br from-sapphire/5 to-transparent z-10"
        />

        {/* Floating Data Nodes */}
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0 }}
            animate={{ 
              opacity: [0, 0.4, 0],
              y: [-20, -120],
              x: i % 2 === 0 ? [0, 30] : [0, -30],
              scale: [0.8, 1.2, 0.8]
            }}
            transition={{ 
              duration: 7 + (i % 5), 
              repeat: Infinity, 
              delay: i * 0.4,
              ease: "easeInOut"
            }}
            className="absolute w-1.5 h-1.5 bg-sapphire rounded-full"
            style={{ 
              left: `${(i * 13) % 100}%`, 
              top: `${(i * 23) % 100}%` 
            }}
          />
        ))}

        {/* Ambient Glows */}
        <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-sapphire/5 rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-emerald/5 rounded-full" />
      </div>

      <motion.main 
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="relative z-10 max-w-7xl mx-auto px-6"
      >
        
        {/* NAVIGATION / LOGO SECTION */}
        <motion.nav variants={itemVariants} className="py-10 flex justify-between items-center">
            <Link href="/" className="flex items-center gap-4 group cursor-pointer">
                <div className="relative">
                    {/* Logo Pulse Rings */}
                    <motion.div 
                        animate={{ scale: [1, 1.3, 1], opacity: [0.2, 0, 0.2] }}
                        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                        className="absolute inset-[-8px] rounded-[22px] bg-sapphire/10 -z-10"
                    />
                    <div className="w-12 h-12 rounded-[18px] bg-gradient-to-br from-sapphire via-emerald to-amber p-[1px] shadow-2xl group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 relative overflow-hidden">
                        <div className="w-full h-full rounded-[17px] bg-white dark:bg-[#0b0f19] flex items-center justify-center relative">
                             {/* Neural Net Dot Background */}
                             <div className="absolute inset-0 opacity-20 pointer-events-none">
                                {[...Array(5)].map((_, i) => (
                                    <motion.div
                                        key={i}
                                        animate={{ 
                                            opacity: [0.1, 0.4, 0.1],
                                            scale: [1, 1.3, 1]
                                        }}
                                        transition={{ duration: 3 + i, repeat: Infinity }}
                                        className="absolute w-0.5 h-0.5 bg-navy dark:bg-white rounded-full"
                                        style={{ 
                                            top: `${(i * 20) % 100}%`, 
                                            left: `${(i * 25) % 100}%` 
                                        }}
                                    />
                                ))}
                             </div>

                             {/* Enhanced Growth Chart SVG */}
                             <svg className="w-7 h-7 text-navy dark:text-white drop-shadow-xl relative z-10" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <motion.path 
                                    initial={{ pathLength: 0, opacity: 0 }}
                                    animate={{ pathLength: 1, opacity: 1 }}
                                    transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 3, ease: "easeInOut" }}
                                    d="M4 18L9 13L13 17L20 7" 
                                    stroke="currentColor" 
                                    strokeWidth="3" 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round" 
                                />
                                <motion.path 
                                    initial={{ scale: 0 }}
                                    animate={{ scale: [0, 1.2, 1] }}
                                    transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 4 }}
                                    d="M20 7L16 7M20 7L20 11" 
                                    stroke="currentColor" 
                                    strokeWidth="3" 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round"
                                />
                             </svg>
                             <div className="absolute inset-0 bg-gradient-to-t from-sapphire/5 to-transparent"></div>
                        </div>
                    </div>
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald rounded-full border-2 border-white dark:border-background shadow-[0_0_10px_rgba(22,168,122,0.8)] animate-pulse" />
                </div>
                <span className="text-2xl font-black tracking-tighter text-navy dark:text-white group-hover:text-sapphire transition-colors duration-500">
                    DeciFlow <span className="text-sapphire">AI</span>
                </span>
            </Link>

            <div className="hidden md:flex items-center gap-10">
                <Link href="/dashboard" className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-text hover:text-sapphire transition-colors">Dashboard</Link>
                <Link href="/simulation" className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-text hover:text-sapphire transition-colors">Simulation</Link>
                <Link href="/chat" className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-text hover:text-sapphire transition-colors">AI Chat</Link>
            </div>
        </motion.nav>

        {/* HERO SECTION */}
        <section className="py-24 md:py-40 flex flex-col items-center text-center">
          <motion.div
            variants={itemVariants}
            className="inline-flex items-center gap-3 px-5 py-2.5 bg-sapphire/5 dark:bg-sapphire/10 border border-sapphire/20 rounded-full mb-12 shadow-sm"
          >
            <div className="w-2.5 h-2.5 bg-sapphire rounded-full animate-pulse shadow-[0_0_10px_rgba(37,99,235,0.8)]" />
            <span className="text-[11px] font-black uppercase tracking-[0.3em] text-sapphire">The OS for Strategic Supremacy</span>
          </motion.div>

          <motion.h1 
            variants={itemVariants}
            className="text-6xl md:text-9xl font-black tracking-tight mb-10 leading-[0.85] text-navy dark:text-white"
          >
            Predictive Intelligence <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-sapphire via-indigo-500 to-emerald">for Scalable Growth.</span>
          </motion.h1>

          <motion.p 
            variants={itemVariants}
            className="text-xl md:text-2xl text-body-text dark:text-white/60 max-w-4xl mb-16 font-medium leading-relaxed"
          >
            DeciFlow AI analyzes your data to predict market shifts, automate insights, and simulate winning strategies. Simple, powerful, and built for leaders.
          </motion.p>
          
          <motion.div 
            variants={itemVariants}
            className="flex flex-col sm:flex-row gap-6 items-center"
          >
            <Link href="/upload">
                <motion.button 
                    whileHover={{ scale: 1.05, y: -4, boxShadow: "0 25px 60px rgba(37,99,235,0.5)" }}
                    whileTap={{ scale: 0.98 }}
                    className="px-16 py-8 bg-sapphire text-white rounded-3xl font-black uppercase tracking-[0.3em] text-sm shadow-[0_30px_70px_rgba(37,99,235,0.4)] flex items-center gap-4 group transition-all"
                >
                    Start Analysis
                    <FiArrowRight size={22} className="group-hover:translate-x-2 transition-transform" />
                </motion.button>
            </Link>
          </motion.div>
        </section>

        {/* PREMIUM FEATURE GRID */}
        <section className="py-20 grid grid-cols-1 md:grid-cols-3 gap-10">
            {[
                { 
                    title: "Smart Insights", 
                    desc: "We scan your numbers to find hidden patterns and growth opportunities that most people miss.", 
                    icon: <FiZap />, 
                    color: "sapphire" 
                },
                { 
                    title: "Safe Predictions", 
                    desc: "See the future of your business. Test new ideas safely before you spend a single rupee.", 
                    icon: <FiShield />, 
                    color: "emerald" 
                },
                { 
                    title: "Clear Direction", 
                    desc: "Get simple advice on exactly what to do next to grow your business with confidence.", 
                    icon: <FiTarget />, 
                    color: "amber" 
                }
            ].map((feature, i) => (
                <motion.div
                    key={i}
                    variants={itemVariants}
                    whileHover={{ 
                        y: -10,
                        boxShadow: "0 30px 60px -15px rgba(37, 99, 235, 0.1)",
                        borderColor: "rgba(37, 99, 235, 0.3)"
                    }}
                    className="relative group p-12 rounded-[3rem] border border-cool-gray dark:border-white/10 bg-white dark:bg-white/[0.03] overflow-hidden transition-all duration-500 shadow-sm"
                >
                    <div className={`w-20 h-20 rounded-[2rem] bg-${feature.color}/10 text-${feature.color} flex items-center justify-center text-4xl mb-10 group-hover:scale-110 transition-all duration-500`}>
                        {feature.icon}
                    </div>
                    <h3 className="text-3xl font-black mb-5 text-navy dark:text-white tracking-tight leading-none">{feature.title}</h3>
                    <p className="text-body-text dark:text-white/40 leading-relaxed font-medium text-lg">
                        {feature.desc}
                    </p>
                </motion.div>
            ))}
        </section>

        {/* VALUE PROPOSITION SECTION */}
        <section className="py-40 border-t border-cool-gray dark:border-white/5">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
                <motion.div variants={itemVariants}>
                    <h2 className="text-5xl md:text-7xl font-black mb-12 text-navy dark:text-white tracking-tight leading-[0.9]">
                        Engineered for <br />
                        <span className="text-sapphire">Strategic Mastery.</span>
                    </h2>
                    <div className="space-y-12">
                        {[
                            "Smart growth insights",
                            "Simple market predictions",
                            "Low-risk expansion plans",
                            "Automated business reports"
                        ].map((item, i) => (
                            <motion.div 
                                key={i} 
                                initial={{ opacity: 0, x: -20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="flex items-start gap-6 group"
                            >
                                <div className="mt-1.5 w-8 h-8 rounded-xl bg-emerald/10 flex items-center justify-center text-emerald group-hover:scale-125 transition-transform">
                                    <FiTrendingUp size={18} />
                                </div>
                                <div className="flex flex-col gap-1">
                                    <span className="text-2xl font-black text-navy dark:text-white/90 group-hover:text-sapphire transition-colors tracking-tight">{item}</span>
                                    <div className="w-12 h-1 bg-cool-gray/20 rounded-full group-hover:w-full group-hover:bg-sapphire/30 transition-all duration-500" />
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
                <motion.div 
                    variants={itemVariants}
                    className="relative"
                >
                    <div className="absolute inset-0 bg-gradient-to-br from-sapphire via-indigo-500 to-emerald opacity-10 rounded-full" />
                    <CardMockup />
                </motion.div>
            </div>
        </section>

        {/* FINAL CTA */}
        <section className="py-40 text-center relative">
            <motion.div 
                variants={itemVariants}
                className="p-24 rounded-[5rem] bg-navy dark:bg-white/[0.02] text-white relative overflow-hidden shadow-2xl border border-white/5"
            >
                <div className="absolute top-0 right-0 p-24 opacity-[0.03] rotate-12">
                    <FiTrendingUp size={500} />
                </div>
                <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-sapphire/20 rounded-full pointer-events-none" />
                
                <h2 className="text-6xl md:text-8xl font-black mb-10 tracking-tighter relative z-10 leading-none">
                    Start Your <br/><span className="text-sapphire">Growth.</span>
                </h2>
                <p className="text-2xl text-white/40 max-w-3xl mx-auto mb-16 font-medium relative z-10 leading-relaxed">
                    DeciFlow AI analyzes your data to predict market shifts and simulate winning strategies.
                </p>
                <Link href="/upload">
                    <motion.button 
                        whileHover={{ scale: 1.05, y: -4, boxShadow: "0 25px 60px rgba(37,99,235,0.5)" }}
                        whileTap={{ scale: 0.98 }}
                        className="px-16 py-8 bg-sapphire text-white rounded-3xl font-black uppercase tracking-[0.3em] text-sm shadow-2xl relative z-10 transition-all"
                    >
                        Initiate Strategic Analysis
                    </motion.button>
                </Link>
            </motion.div>
        </section>

      </motion.main>

      <footer className="py-24 border-t border-cool-gray dark:border-white/5 text-center relative z-10 bg-background/50">
          <div className="flex justify-center gap-10 mb-10 opacity-30">
              <FiZap size={24} />
              <FiShield size={24} />
              <FiTarget size={24} />
          </div>
          <span className="text-[11px] font-black uppercase tracking-[0.8em] text-muted-text dark:text-white/20">
              © 2026 DeciFlow AI Neural Network. Strategic Supremacy.
          </span>
      </footer>
    </div>
  );
}

function CardMockup() {
    return (
        <motion.div 
            whileHover={{ y: -8, scale: 1.02 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="relative z-10 p-12 rounded-[4rem] bg-white dark:bg-white/[0.03] border border-white/40 dark:border-white/10 shadow-2xl dark:shadow-none transition-all"
        >
            <div className="flex justify-between items-center mb-12">
                <div className="w-16 h-16 rounded-[2rem] bg-sapphire/10 flex items-center justify-center text-sapphire shadow-inner">
                    <FiActivity size={32} />
                </div>
                <div className="px-6 py-2 bg-emerald/10 text-emerald rounded-full text-[11px] font-black uppercase tracking-[0.2em] border border-emerald/20 shadow-sm">
                    Strategic Peak
                </div>
            </div>
            <div className="space-y-8 mb-12">
                <div className="h-5 w-3/4 bg-cool-gray/20 dark:bg-white/10 rounded-full" />
                <div className="h-5 w-1/2 bg-cool-gray/20 dark:bg-white/10 rounded-full" />
                <div className="h-14 w-full bg-sapphire/5 dark:bg-white/5 rounded-3xl flex items-center px-6 border border-white/20">
                    <div className="h-2.5 w-full bg-sapphire/20 rounded-full overflow-hidden">
                        <motion.div 
                            initial={{ width: 0 }}
                            whileInView={{ width: "85%" }}
                            transition={{ delay: 1, duration: 2, ease: "easeOut" }}
                            className="h-full bg-gradient-to-r from-sapphire to-emerald shadow-[0_0_15px_rgba(37,99,235,0.6)]" 
                        />
                    </div>
                </div>
            </div>
            <div className="grid grid-cols-2 gap-6">
                <div className="p-6 rounded-[2.5rem] bg-white dark:bg-white/5 border border-cool-gray dark:border-white/10 shadow-xl group cursor-default transition-all duration-500 hover:border-sapphire/30">
                    <div className="text-[11px] font-black text-muted-text dark:text-white/40 uppercase mb-2 tracking-widest">ROI Projected</div>
                    <div className="text-4xl font-black text-navy dark:text-white group-hover:text-sapphire transition-colors tracking-tighter">5.8x</div>
                </div>
                <div className="p-6 rounded-[2.5rem] bg-white dark:bg-white/5 border border-cool-gray dark:border-white/10 shadow-xl group cursor-default transition-all duration-500 hover:border-emerald/30">
                    <div className="text-[11px] font-black text-muted-text dark:text-white/40 uppercase mb-2 tracking-widest">Risk Level</div>
                    <div className="text-4xl font-black text-emerald group-hover:scale-110 transition-transform tracking-tighter">LOW</div>
                </div>
            </div>
        </motion.div>
    );
}