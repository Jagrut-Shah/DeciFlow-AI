"use client";

import React, { useState, useRef, useEffect } from "react";
import Card from "@/components/Card";
import { FiSend, FiUser, FiInfo } from "react-icons/fi";
import { FaRobot } from "react-icons/fa";
import { apiClient } from "@/services/api";

interface Message {
    id: number;
    text: string;
    sender: "user" | "ai";
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        { id: 1, text: "Welcome to DeciFlow AI Copilot. I'm connected to your system data and ready to assist with strategic analysis. How can I help you today?", sender: "ai" }
    ]);
    const [inputValue, setInputValue] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

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
                }))
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
        <div className="flex flex-col h-[calc(100vh-6rem)] max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-1000">
            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto px-4 py-8 space-y-8 custom-scrollbar">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} group`}
                    >
                        <div className={`flex gap-4 max-w-[85%] md:max-w-[70%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                            <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 border transition-all duration-500 ${
                                msg.sender === 'user' 
                                ? 'bg-slate-100 dark:bg-white/5 border-slate-300 dark:border-white/10 group-hover:bg-slate-200 dark:bg-white/10' 
                                : 'bg-indigo-500/20 border-indigo-500/30 group-hover:bg-indigo-500/30 shadow-[0_0_15px_rgba(99,102,241,0.1)]'
                            }`}>
                                {msg.sender === 'user' ? <FiUser className="text-slate-500 dark:text-gray-400" /> : <FaRobot className="text-indigo-400" />}
                            </div>
                            
                            <div className={`
                                p-5 rounded-3xl shadow-2xl transition-all duration-500
                                ${msg.sender === 'user'
                                    ? 'bg-gradient-to-br from-indigo-600 to-indigo-800 text-slate-900 dark:text-white rounded-tr-none'
                                    : 'bg-white/[0.03] border border-slate-300 dark:border-white/10 text-slate-700 dark:text-gray-200 rounded-tl-none backdrop-blur-3xl hover:bg-white/[0.05]'}
                            `}>
                                <p className="leading-relaxed text-[15px] selection:bg-white/20">{msg.text}</p>
                            </div>
                        </div>
                    </div>
                ))}

                {isTyping && (
                    <div className="flex justify-start">
                        <div className="flex gap-4 items-center">
                            <div className="w-10 h-10 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0">
                                <FaRobot className="text-indigo-400/50 animate-pulse" />
                            </div>
                            <div className="bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/5 text-slate-500 dark:text-gray-400 py-4 px-6 rounded-3xl rounded-tl-none backdrop-blur-md flex items-center gap-2">
                                <span className="w-1.5 h-1.5 bg-indigo-400/60 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                                <span className="w-1.5 h-1.5 bg-indigo-400/60 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                                <span className="w-1.5 h-1.5 bg-indigo-400/60 rounded-full animate-bounce"></span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Hint Box */}
            <div className="px-6 py-3 flex items-center gap-2 text-slate-500 dark:text-gray-500 text-xs font-semibold uppercase tracking-widest animate-pulse">
                <FiInfo size={14} />
                <span>AI uses historical context for enhanced reasoning</span>
            </div>

            {/* Input Area */}
            <div className="p-6 mb-4">
                <Card className="p-2 bg-white/[0.02] border-slate-300 dark:border-white/10 backdrop-blur-3xl shadow-2xl rounded-[2.5rem] group focus-within:border-indigo-500/30 transition-all">
                    <form
                        onSubmit={handleSend}
                        className="flex gap-2"
                    >
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder="Ask DeciFlow AI about your strategy..."
                            className="flex-1 bg-transparent border-none px-8 py-5 text-slate-900 dark:text-white focus:outline-none focus:ring-0 placeholder:text-slate-600 dark:text-gray-600 text-[16px]"
                        />
                        <button
                            type="submit"
                            disabled={!inputValue.trim() || isTyping}
                            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-slate-900 dark:text-white w-14 h-14 rounded-[1.8rem] flex items-center justify-center transition-all shadow-xl shadow-indigo-600/20 active:scale-90"
                        >
                            <FiSend size={20} />
                        </button>
                    </form>
                </Card>
            </div>
        </div>
    );
}
