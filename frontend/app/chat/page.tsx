"use client";

import React, { useState, useRef, useEffect } from "react";
import Card from "@/components/Card";
import { FiSend, FiUser, FiInfo } from "react-icons/fi";
import { FaRobot } from "react-icons/fa";
import { apiClient } from "@/services/api";
import { motion, AnimatePresence } from "framer-motion";

import { useSearchParams } from "next/navigation";

interface Message {
    id: number;
    text: string;
    sender: "ai" | "user";
}

export default function ChatPage() {
    const searchParams = useSearchParams();
    const sessionId = searchParams.get('session');
    
    const [messages, setMessages] = useState<Message[]>([
        { id: 1, text: "Welcome to DeciFlow AI Copilot. I'm connected to your system data and ready to assist with strategic analysis. How can I help you today?", sender: "ai" }
    ]);
    const [inputValue, setInputValue] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [mounted, setMounted] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    const handleSend = async (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        if (!inputValue.trim()) return;

        const userMessage: Message = {
            id: Date.now(),
            text: inputValue,
            sender: "user",
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputValue("");
        setIsTyping(true);

        try {
            const result = await apiClient.post("/chat/", {
                message: inputValue,
                history: messages.map(m => ({
                    role: m.sender === 'ai' ? 'assistant' : 'user',
                    content: m.text
                })),
                session_id: sessionId
            });
            
            if (result.status === 'success') {
                const aiResponse: Message = {
                    id: Date.now() + 1,
                    text: result.data.response,
                    sender: "ai",
                };
                setMessages((prev) => [...prev, aiResponse]);
            } else {
                throw new Error("Failed to get response");
            }
        } catch (error) {
            console.error("Chat error:", error);
            const errorMsg: Message = {
                id: Date.now() + 1,
                text: "My neural link is experiencing high latency. Please ensure the kernel service is active and try resending your query.",
                sender: "ai",
            };
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-6rem)] max-w-5xl mx-auto">
            {/* Header / Context Indicator */}
            <motion.div 
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="px-6 py-4 border-b border-cool-gray dark:border-white/5 flex items-center justify-between"
            >
                <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-emerald rounded-full animate-pulse shadow-[0_0_8px_rgba(22,168,122,0.8)]"></div>
                    <span className="text-[10px] font-black text-navy dark:text-white uppercase tracking-[0.2em]">Neural Connection Active</span>
                </div>
                <div className="text-[10px] font-bold text-muted-text dark:text-white/20 uppercase tracking-widest">
                    Kernel 2.5.0-Flash
                </div>
            </motion.div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto px-6 py-10 space-y-10 custom-scrollbar">
                <AnimatePresence mode="popLayout">
                    {messages.map((msg, index) => (
                        <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            transition={{ type: "spring", stiffness: 260, damping: 25 }}
                            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} group`}
                        >
                            <div className={`flex gap-3 md:gap-5 max-w-[90%] md:max-w-[75%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                <motion.div 
                                    whileHover={{ scale: 1.1, rotate: 5 }}
                                    className={`w-10 h-10 md:w-12 md:h-12 rounded-xl md:rounded-2xl flex items-center justify-center shrink-0 border transition-all duration-500 shadow-lg ${
                                        msg.sender === 'user' 
                                        ? 'bg-white dark:bg-white/5 border-cool-gray dark:border-white/10' 
                                        : 'bg-sapphire/10 border-sapphire/20 shadow-sapphire/5'
                                    }`}
                                >
                                    {msg.sender === 'user' ? <FiUser size={18} className="text-navy dark:text-white/60" /> : <FaRobot size={20} className="text-sapphire animate-pulse" />}
                                </motion.div>
                                
                                <div className={`
                                    p-4 md:p-6 rounded-[1.5rem] md:rounded-[2rem] shadow-2xl transition-all duration-500 relative group-hover:shadow-sapphire/5
                                    ${msg.sender === 'user'
                                         ? 'bg-gradient-to-br from-sapphire via-sapphire to-navy text-white rounded-tr-none shadow-sapphire/20'
                                         : 'bg-white dark:bg-white/[0.03] border border-cool-gray dark:border-white/10 text-navy dark:text-white/80 rounded-tl-none'}
                                `}>
                                    <div className="leading-relaxed text-[16px] font-medium selection:bg-white/20 whitespace-pre-wrap">{msg.text}</div>
                                    
                                    <div className={`absolute bottom-[-20px] ${msg.sender === 'user' ? 'right-0' : 'left-0'} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}>
                                        <span className="text-[10px] font-black text-muted-text dark:text-white/20 uppercase tracking-widest">
                                            {mounted ? new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "--:--"}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {isTyping && (
                    <motion.div 
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex justify-start"
                    >
                        <div className="flex gap-5 items-center">
                            <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl md:rounded-2xl bg-sapphire/10 border border-sapphire/20 flex items-center justify-center shrink-0">
                                <FaRobot size={20} className="text-sapphire/50 animate-pulse" />
                            </div>
                            <div className="bg-white/[0.03] border border-cool-gray dark:border-white/5 py-5 px-8 rounded-[2rem] rounded-tl-none flex items-center gap-3">
                                <motion.span 
                                    animate={{ scale: [1, 1.5, 1] }}
                                    transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                                    className="w-2 h-2 bg-sapphire/40 rounded-full"
                                ></motion.span>
                                <motion.span 
                                    animate={{ scale: [1, 1.5, 1] }}
                                    transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                                    className="w-2 h-2 bg-sapphire/40 rounded-full"
                                ></motion.span>
                                <motion.span 
                                    animate={{ scale: [1, 1.5, 1] }}
                                    transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                                    className="w-2 h-2 bg-sapphire/40 rounded-full"
                                ></motion.span>
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 md:p-8"
            >
                <div className="relative">
                    <div className="absolute top-[-30px] left-6 flex items-center gap-2 text-muted-text dark:text-white/20 text-[10px] font-black uppercase tracking-[0.2em] pointer-events-none">
                        <FiInfo size={12} />
                        <span>Connected to Intelligence Layer</span>
                    </div>
                    
                    <Card className="p-1.5 bg-white dark:bg-white/[0.03] border border-cool-gray dark:border-white/10 rounded-[3rem] shadow-2xl overflow-hidden focus-within:border-sapphire/40 focus-within:shadow-sapphire/5 transition-all duration-500">
                        <form
                            onSubmit={handleSend}
                            className="flex gap-3"
                        >
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                placeholder="Query the system intelligence..."
                                className="flex-1 bg-transparent border-none px-4 md:px-10 py-4 md:py-6 text-navy dark:text-white focus:outline-none focus:ring-0 placeholder:text-muted-text/50 font-medium text-[15px] md:text-[17px]"
                            />
                            <motion.button
                                whileHover={{ scale: 1.05, x: 2 }}
                                whileTap={{ scale: 0.95 }}
                                type="submit"
                                disabled={!inputValue.trim() || isTyping}
                                className="bg-gradient-to-br from-sapphire to-navy hover:shadow-sapphire/30 disabled:opacity-20 text-white w-12 h-12 md:w-16 md:h-16 rounded-xl md:rounded-[2rem] flex items-center justify-center transition-all shadow-2xl shadow-sapphire/20 shrink-0"
                            >
                                <FiSend size={18} className={inputValue.trim() ? "translate-x-0.5 -translate-y-0.5" : ""} />
                            </motion.button>
                        </form>
                    </Card>
                </div>
            </motion.div>
        </div>
    );
}

