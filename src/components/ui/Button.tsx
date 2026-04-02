'use client';

import { motion } from 'framer-motion';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'filled' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  className?: string;
  type?: 'button' | 'submit';
}

export default function Button({
  children,
  variant = 'filled',
  size = 'md',
  onClick,
  className = '',
  type = 'button',
}: ButtonProps) {
  const base = 'font-mono uppercase tracking-[0.2em] transition-all duration-300 inline-flex items-center justify-center';

  const variants = {
    filled: 'bg-sovereign-carbon text-sovereign-white hover:bg-sovereign-black',
    outline: 'border border-sovereign-carbon text-sovereign-carbon hover:bg-sovereign-carbon hover:text-sovereign-white',
    ghost: 'text-sovereign-carbon hover:text-sovereign-graphite',
  };

  const sizes = {
    sm: 'text-[10px] px-4 py-2',
    md: 'text-xs px-6 py-3',
    lg: 'text-sm px-8 py-4',
  };

  return (
    <motion.button
      type={type}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {children}
    </motion.button>
  );
}
