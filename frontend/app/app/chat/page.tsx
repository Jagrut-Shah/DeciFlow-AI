"use client";

import React, { useState, useRef, useEffect } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";

interface Message {
  id: number;
  text: string;
  sender: "user" | "ai";
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: "Hello! I am DeciFlow AI. How can I assist you with your data today?", sender: "ai" }
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

  const handleSend = (e?: React.FormEvent) => {
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

    // Fake AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: Date.now() + 1,
        text: "Based on the recent simulation run, I recommend aggressively adjusting the pricing strategy. I've noted the parameters and can generate a comprehensive PDF report if you'd like.",
        sender: "ai",
      };
      setMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)] max-h-[900px] animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="mb-6">
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 mb-2">
          AI Copilot 💬
        </h1>
        <p className="text-gray-400">Ask questions about your data, insights, or models.</p>
      </div>

      <Card className="flex-1 flex flex-col p-0 overflow-hidden relative border-indigo-500/20">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          {messages.map((msg) => (
            <div 
              key={msg.id} 
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}
            >
              <div className={`
                max-w-[80%] md:max-w-[70%] p-4 rounded-2xl
                ${msg.sender === 'user' 
                  ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-tr-sm' 
                  : 'bg-white/10 border border-white/5 text-gray-200 rounded-tl-sm backdrop-blur-md'}
              `}>
                <p className="leading-relaxed">{msg.text}</p>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start animate-in fade-in">
              <div className="bg-white/10 border border-white/5 text-gray-200 py-4 px-5 rounded-2xl rounded-tl-sm backdrop-blur-md flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-white/10 bg-[#0a0f1a]/80 backdrop-blur-lg">
          <form 
            onSubmit={handleSend}
            className="flex gap-3 max-w-4xl mx-auto items-end"
          >
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask DeciFlow AI anything..."
                className="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder:text-gray-500"
              />
            </div>
            <Button 
              type="submit" 
              disabled={!inputValue.trim() || isTyping}
              className="py-4 px-6 rounded-xl shrink-0"
            >
              Send <span className="ml-1">✈️</span>
            </Button>
          </form>
        </div>
      </Card>

      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(255, 255, 255, 0.1);
          border-radius: 20px;
        }
      `}} />
    </div>
  );
}