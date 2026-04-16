import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  glowOnHover?: boolean;
}

export default function Card({ children, className = '', glowOnHover = true }: CardProps) {
  return (
    <div className={`
      bg-white/5 border border-white/10 backdrop-blur-lg rounded-2xl p-6
      transition-all duration-300 ease-in-out
      ${glowOnHover ? 'hover:bg-white/10 hover:shadow-[0_4px_30px_rgba(99,102,241,0.2)] hover:-translate-y-1' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
}
