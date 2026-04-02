'use client';

import { useScrollPosition } from '@/hooks/useScrollPosition';
import { useEffect, useState } from 'react';

export default function ProgressBar() {
  const { scrollY } = useScrollPosition();
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    setProgress(docHeight > 0 ? (scrollY / docHeight) * 100 : 0);
  }, [scrollY]);

  if (progress <= 0) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-[60] h-[2px]">
      <div className="h-full chrome-gradient transition-all duration-100" style={{ width: `${progress}%` }} />
    </div>
  );
}
