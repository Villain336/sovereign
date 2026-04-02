import Link from 'next/link';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

export default function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav className="flex items-center gap-2 mb-6">
      <Link href="/" className="font-mono text-[9px] tracking-[0.2em] text-sovereign-chrome hover:text-sovereign-graphite transition-colors">
        HOME
      </Link>
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-2">
          <span className="font-mono text-[9px] text-sovereign-silver">/</span>
          {item.href ? (
            <Link href={item.href} className="font-mono text-[9px] tracking-[0.2em] text-sovereign-chrome hover:text-sovereign-graphite transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className="font-mono text-[9px] tracking-[0.2em] text-sovereign-graphite">
              {item.label}
            </span>
          )}
        </span>
      ))}
    </nav>
  );
}
