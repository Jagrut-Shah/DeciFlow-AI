import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  children: React.ReactNode;
}

export default function Button({ variant = 'primary', className = '', children, ...props }: ButtonProps) {
  const baseStyles = "px-6 py-3 rounded-2xl font-semibold transition-all duration-300 ease-out active:scale-95 flex items-center justify-center gap-2";
  
  const variants = {
    primary: "bg-gradient-to-r from-cyan-500 to-indigo-600 text-white hover:shadow-[0_0_20px_rgba(99,102,241,0.5)] hover:scale-105",
    secondary: "bg-[#1E253A] text-white hover:bg-[#2A344F] border border-[#2E364F] hover:shadow-lg",
    ghost: "text-gray-400 hover:text-white hover:bg-white/5",
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
