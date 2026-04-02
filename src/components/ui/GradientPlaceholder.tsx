interface GradientPlaceholderProps {
  gradient: [string, string];
  className?: string;
  children?: React.ReactNode;
}

export default function GradientPlaceholder({ gradient, className = '', children }: GradientPlaceholderProps) {
  return (
    <div
      className={`w-full h-full ${className}`}
      style={{
        background: `linear-gradient(145deg, ${gradient[0]}, ${gradient[1]})`,
      }}
    >
      {children}
    </div>
  );
}
