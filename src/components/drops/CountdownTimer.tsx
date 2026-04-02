'use client';

import { useState, useEffect } from 'react';

interface CountdownTimerProps {
  targetDate: string;
  className?: string;
}

function getTimeLeft(target: string) {
  const diff = new Date(target).getTime() - Date.now();
  if (diff <= 0) return { days: 0, hours: 0, minutes: 0, seconds: 0 };
  return {
    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
    hours: Math.floor((diff / (1000 * 60 * 60)) % 24),
    minutes: Math.floor((diff / (1000 * 60)) % 60),
    seconds: Math.floor((diff / 1000) % 60),
  };
}

export default function CountdownTimer({ targetDate, className = '' }: CountdownTimerProps) {
  const [time, setTime] = useState(getTimeLeft(targetDate));

  useEffect(() => {
    const interval = setInterval(() => setTime(getTimeLeft(targetDate)), 1000);
    return () => clearInterval(interval);
  }, [targetDate]);

  const blocks = [
    { value: time.days, label: 'DAYS' },
    { value: time.hours, label: 'HRS' },
    { value: time.minutes, label: 'MIN' },
    { value: time.seconds, label: 'SEC' },
  ];

  return (
    <div className={`flex gap-3 md:gap-4 ${className}`}>
      {blocks.map((block, i) => (
        <div key={block.label} className="flex items-center gap-3 md:gap-4">
          <div className="text-center">
            <span className="font-mono text-3xl md:text-5xl tracking-tight block">
              {String(block.value).padStart(2, '0')}
            </span>
            <span className="font-mono text-[8px] tracking-[0.3em] text-sovereign-graphite mt-1 block">
              {block.label}
            </span>
          </div>
          {i < blocks.length - 1 && (
            <span className="font-mono text-2xl md:text-4xl text-sovereign-chrome">:</span>
          )}
        </div>
      ))}
    </div>
  );
}
