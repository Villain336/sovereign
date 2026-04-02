export default function Divider({ className = '' }: { className?: string }) {
  return (
    <div className={`w-full h-px chrome-gradient ${className}`} />
  );
}
