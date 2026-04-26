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
      className={`
        relative overflow-hidden
        bg-white dark:bg-white/[0.02] border border-cool-gray dark:border-white/[0.05] backdrop-blur-xl rounded-2xl
        transition-colors duration-500 ease-out shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.4)]
        ${glowOnHover ? 'hover:border-sapphire/40 dark:hover:border-sapphire/30 hover:shadow-[0_20px_50px_rgba(37,99,235,0.1)] dark:hover:shadow-[0_20px_50px_rgba(37,99,235,0.15)]' : ''}
        ${className}
      `}
    >
      {/* Subtle Inner Glow */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cool-gray dark:via-white/10 to-transparent pointer-events-none" />
      <div className="relative z-10 w-full h-full">
        {children}
      </div>
    </motion.div>
  );
}

