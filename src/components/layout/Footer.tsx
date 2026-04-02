import Link from 'next/link';
import Divider from '@/components/ui/Divider';

export default function Footer() {
  return (
    <footer className="bg-sovereign-white">
      {/* Trust bar */}
      <div className="border-y border-sovereign-silver">
        <div className="max-w-7xl mx-auto px-6 md:px-16 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
            {[
              { title: 'FREE SHIPPING', desc: 'On orders over $100' },
              { title: '30-DAY RETURNS', desc: 'No questions asked' },
              { title: 'ETHICALLY MADE', desc: 'Sustainably sourced materials' },
              { title: 'SECURE CHECKOUT', desc: 'Encrypted payment processing' },
            ].map((item) => (
              <div key={item.title} className="text-center md:text-left">
                <span className="font-mono text-[9px] tracking-[0.3em] text-sovereign-carbon block">
                  {item.title}
                </span>
                <span className="font-mono text-[9px] tracking-[0.15em] text-sovereign-graphite mt-1 block">
                  {item.desc.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 md:px-16 py-16 md:py-20">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-10 md:gap-8">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="font-mono text-xs tracking-[0.4em] text-sovereign-carbon">
              SOVEREIGN
            </Link>
            <p className="font-mono text-[9px] text-sovereign-graphite tracking-[0.15em] mt-4 leading-[2] max-w-xs">
              PRECISION-ENGINEERED GARMENTS FOR THE MODERN HUMAN.
              UNISEX. SEASONLESS. BUILT TO LAST.
            </p>
          </div>

          {/* Shop */}
          <div>
            <span className="font-mono text-[9px] tracking-[0.3em] text-sovereign-carbon block mb-4">SHOP</span>
            <div className="flex flex-col gap-2.5">
              {[
                { label: 'All Collections', href: '/collections' },
                { label: 'T-Shirts', href: '/collections/tshirts' },
                { label: 'Hoodies', href: '/collections/hoodies' },
                { label: 'Pants', href: '/collections/pants' },
                { label: 'Outerwear', href: '/collections/outerwear' },
                { label: 'Accessories', href: '/collections/accessories' },
              ].map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="font-mono text-[9px] tracking-[0.15em] text-sovereign-graphite hover:text-sovereign-carbon transition-colors"
                >
                  {link.label.toUpperCase()}
                </Link>
              ))}
            </div>
          </div>

          {/* Company */}
          <div>
            <span className="font-mono text-[9px] tracking-[0.3em] text-sovereign-carbon block mb-4">COMPANY</span>
            <div className="flex flex-col gap-2.5">
              {[
                { label: 'About', href: '/about' },
                { label: 'Lookbook', href: '/lookbook' },
                { label: 'Drops', href: '/drops' },
                { label: 'Sustainability', href: '#' },
                { label: 'Careers', href: '#' },
                { label: 'Contact', href: '#' },
              ].map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  className="font-mono text-[9px] tracking-[0.15em] text-sovereign-graphite hover:text-sovereign-carbon transition-colors"
                >
                  {link.label.toUpperCase()}
                </Link>
              ))}
            </div>
          </div>

          {/* Newsletter + Help */}
          <div>
            <span className="font-mono text-[9px] tracking-[0.3em] text-sovereign-carbon block mb-4">STAY IN THE LOOP</span>
            <p className="font-mono text-[9px] text-sovereign-graphite tracking-[0.15em] leading-[2] mb-4">
              BE THE FIRST TO KNOW ABOUT NEW DROPS AND EXCLUSIVE RELEASES.
            </p>
            <div className="flex border-b border-sovereign-silver pb-2 mb-6">
              <input
                type="email"
                placeholder="EMAIL ADDRESS"
                className="flex-1 bg-transparent font-mono text-[10px] tracking-[0.2em] text-sovereign-carbon placeholder-sovereign-chrome outline-none"
              />
              <button className="font-mono text-[9px] tracking-[0.2em] text-sovereign-carbon hover:text-sovereign-graphite">
                JOIN
              </button>
            </div>

            <span className="font-mono text-[9px] tracking-[0.3em] text-sovereign-carbon block mb-3">HELP</span>
            <div className="flex flex-col gap-2.5">
              {['Shipping & Returns', 'Size Guide', 'FAQ', 'Privacy Policy', 'Terms of Service'].map((link) => (
                <Link
                  key={link}
                  href="#"
                  className="font-mono text-[9px] tracking-[0.15em] text-sovereign-graphite hover:text-sovereign-carbon transition-colors"
                >
                  {link.toUpperCase()}
                </Link>
              ))}
            </div>
          </div>
        </div>

        <Divider className="my-12" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <span className="font-mono text-[8px] text-sovereign-chrome tracking-[0.2em]">
            &copy; 2026 SOVEREIGN. ALL RIGHTS RESERVED.
          </span>
          <div className="flex gap-6">
            {['INSTAGRAM', 'TIKTOK', 'PINTEREST'].map((social) => (
              <span key={social} className="font-mono text-[8px] tracking-[0.2em] text-sovereign-graphite hover:text-sovereign-carbon cursor-pointer transition-colors">
                {social}
              </span>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
