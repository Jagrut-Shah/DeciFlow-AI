"use client";

import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  glowOnHover?: boolean;
}

export default function Card({ children, className = '', glowOnHover = true }: CardProps) {
  return (
    <motion.div 
      whileHover={glowOnHover ? { y: -4 } : {}}
      onMouseMove={(e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        e.currentTarget.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
        e.currentTarget.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
      }}
      className={`
        relative overflow-hidden group
        bg-white dark:bg-white/[0.02] border border-cool-gray dark:border-white/[0.05] rounded-2xl
        transition-colors duration-500 ease-out shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.4)]
        ${glowOnHover ? 'hover:border-sapphire/40 dark:hover:border-sapphire/30 hover:shadow-[0_20px_50px_rgba(37,99,235,0.1)] dark:hover:shadow-[0_20px_50px_rgba(37,99,235,0.15)]' : ''}
        ${className}
      `}
    >
      <motion.div 
        className="absolute inset-0 z-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"
        style={{
          background: 'radial-gradient(600px circle at var(--mouse-x) var(--mouse-y), rgba(37, 99, 235, 0.08), transparent 40%)',
        }}
      />
      {/* Premium Border Glow */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sapphire/30 dark:via-sapphire/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald/30 dark:via-emerald/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
      
      <div className="relative z-10 w-full h-full group">
        {children}
      </div>
    </motion.div>
  );
}

