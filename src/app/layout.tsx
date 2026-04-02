import type { Metadata } from 'next';
import './globals.css';
import { CartProvider } from '@/context/CartContext';
import Navigation from '@/components/layout/Navigation';
import CartSidebar from '@/components/layout/CartSidebar';
import Footer from '@/components/layout/Footer';
import AnnouncementBar from '@/components/layout/AnnouncementBar';
import ProgressBar from '@/components/ui/ProgressBar';
import BackToTop from '@/components/ui/BackToTop';

export const metadata: Metadata = {
  title: 'SOVEREIGN — The Future of Essential Clothing',
  description:
    'Precision-engineered garments for the modern human. No logos. No noise. Just essential clothing at accessible prices. Free shipping over $100.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <CartProvider>
          <AnnouncementBar />
          <ProgressBar />
          <Navigation />
          <CartSidebar />
          <main>{children}</main>
          <Footer />
          <BackToTop />
        </CartProvider>
      </body>
    </html>
  );
}
