'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';

const CHARS = '░▒▓█▄▀■□▪▫●○◆◇';

interface TextScrambleProps {
  text: string;
  className?: string;
  as?: 'h1' | 'h2' | 'h3' | 'p' | 'span';
  delay?: number;
}

export default function TextScramble({ text, className = '', as: Tag = 'h2', delay = 0 }: TextScrambleProps) {
  const [display, setDisplay] = useState(text);
  const [hasAnimated, setHasAnimated] = useState(false);
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView || hasAnimated) return;

    let frame = 0;
    const totalFrames = 20;
    const delayFrames = Math.floor(delay * 60);
    let currentFrame = -delayFrames;

    const interval = setInterval(() => {
      currentFrame++;
      if (currentFrame < 0) return;

      frame = currentFrame;
      const progress = frame / totalFrames;

      const newText = text
        .split('')
        .map((char, i) => {
          if (char === ' ') return ' ';
          const charProgress = (progress * text.length - i) / 3;
          if (charProgress >= 1) return char;
          if (charProgress > 0) return CHARS[Math.floor(Math.random() * CHARS.length)];
          return CHARS[Math.floor(Math.random() * CHARS.length)];
        })
        .join('');

      setDisplay(newText);

      if (frame >= totalFrames) {
        setDisplay(text);
        setHasAnimated(true);
        clearInterval(interval);
      }
    }, 50);

    return () => clearInterval(interval);
  }, [isInView, text, delay, hasAnimated]);

  return (
    <motion.span ref={ref as React.RefObject<HTMLSpanElement>}>
      <Tag className={className}>{display}</Tag>
    </motion.span>
  );
}
