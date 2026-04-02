import Link from 'next/link';
import Divider from '@/components/ui/Divider';

export default function Footer() {
  return (
    <footer className="bg-sovereign-white">
      <Divider />
      <div className="max-w-7xl mx-auto px-6 py-16 md:py-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {/* Brand */}
          <div>
            <Link href="/" className="font-mono text-xs tracking-[0.4em] text-sovereign-carbon">
              SOVEREIGN
            </Link>
            <p className="font-mono text-[10px] text-sovereign-graphite tracking-[0.15em] mt-3 leading-relaxed max-w-xs">
              THE FUTURE OF ESSENTIAL CLOTHING.
              <br />
              PRECISION-ENGINEERED FOR THE MODERN HUMAN.
            </p>
          </div>

          {/* Links */}
          <div className="flex flex-col gap-3">
            {['Collections', 'About', 'Shipping & Returns', 'Contact'].map((link) => (
              <Link
                key={link}
                href={link === 'Collections' ? '/collections' : link === 'About' ? '/about' : '#'}
                className="font-mono text-[10px] tracking-[0.2em] text-sovereign-graphite hover:text-sovereign-carbon transition-colors"
              >
                {link.toUpperCase()}
              </Link>
            ))}
          </div>

          {/* Newsletter */}
          <div>
            <p className="font-mono text-[10px] tracking-[0.2em] text-sovereign-graphite mb-3">
              JOIN THE FUTURE
            </p>
            <div className="flex border-b border-sovereign-silver pb-2">
              <input
                type="email"
                placeholder="EMAIL"
                className="flex-1 bg-transparent font-mono text-xs tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none"
              />
              <button className="font-mono text-[10px] tracking-[0.2em] text-sovereign-carbon hover:text-sovereign-graphite">
                SUBMIT
              </button>
            </div>
          </div>
        </div>

        <div className="mt-16 font-mono text-[9px] text-sovereign-chrome tracking-[0.2em]">
          &copy; 2026 SOVEREIGN. ALL RIGHTS RESERVED.
        </div>
      </div>
    </footer>
  );
}
