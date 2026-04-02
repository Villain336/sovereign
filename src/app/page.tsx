import HeroBlock from '@/components/home/HeroBlock';
import DiscoveryGrid from '@/components/home/DiscoveryGrid';
import ManifestoBlock from '@/components/home/ManifestoBlock';
import FeaturedDrop from '@/components/home/FeaturedDrop';
import EditorialBlock from '@/components/home/EditorialBlock';

export default function Home() {
  return (
    <>
      <HeroBlock />
      <DiscoveryGrid />
      <ManifestoBlock />
      <FeaturedDrop />
      <EditorialBlock />
    </>
  );
}
