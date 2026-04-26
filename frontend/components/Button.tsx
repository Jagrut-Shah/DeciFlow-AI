import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  children: React.ReactNode;
}

export default function Button({ variant = 'primary', className = '', children, ...props }: ButtonProps) {
  const baseStyles = "px-6 py-3 rounded-2xl font-semibold transition-all duration-300 ease-out active:scale-95 flex items-center justify-center gap-2";
  
  const variants = {
    primary: "bg-sapphire text-white hover:shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:scale-105",
    secondary: "bg-ice-blue text-sapphire border border-sapphire/20 hover:bg-sapphire/10 hover:shadow-lg",
    ghost: "text-muted-text hover:text-navy dark:text-white hover:bg-ice-blue dark:hover:bg-white/5",
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

