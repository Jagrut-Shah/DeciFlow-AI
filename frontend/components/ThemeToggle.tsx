"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { Moon, Sun } from "lucide-react";
import { motion } from "framer-motion";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return <div className="w-10 h-10" />;

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-white/60 dark:bg-white/5 border border-slate-200 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors shadow-sm dark:shadow-lg overflow-hidden group"
      aria-label="Toggle Theme"
    >
      <div className="absolute inset-0 bg-gradient-to-tr from-sky-500/10 via-rose-500/10 to-amber-400/10 opacity-0 group-hover:opacity-100 transition-opacity" />
      
      {theme === "dark" ? (
        <Sun className="w-5 h-5 text-rose-400 z-10 drop-shadow-[0_0_8px_rgba(244,63,94,0.5)]" />
      ) : (
        <Moon className="w-5 h-5 text-sky-600 z-10" />
      )}
    </motion.button>
  );
}

