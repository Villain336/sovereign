export default function Badge({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={`font-mono text-[9px] uppercase tracking-[0.3em] px-2 py-1 border border-sovereign-silver text-sovereign-graphite ${className}`}>
      {children}
    </span>
  );
}
