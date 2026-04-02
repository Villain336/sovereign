import { Drop } from '@/types';

export const drops: Drop[] = [
  {
    id: 'drop-001',
    name: 'DROP 001 — GENESIS',
    description: 'The inaugural collection. 28 pieces. Neutral palette. No compromises.',
    date: '2026-05-01T12:00:00Z',
    products: ['essential-tee-01', 'oversized-hoodie-01', 'utility-trouser-01', 'field-jacket-01', 'canvas-cap-01', 'crossbody-01'],
    isLive: true,
    gradient: ['#1A1A1A', '#928E85'],
  },
  {
    id: 'drop-002',
    name: 'DROP 002 — TERRAIN',
    description: 'Outdoor-ready essentials. Technical fabrics. Earth-forward.',
    date: '2026-06-15T12:00:00Z',
    products: ['rain-shell-01', 'hiking-short-01', 'fleece-jacket-01', 'tool-belt-01'],
    isLive: false,
    gradient: ['#708238', '#36454F'],
  },
  {
    id: 'drop-003',
    name: 'DROP 003 — NOCTURNE',
    description: 'After dark. Deep tones. Elevated staples for the evening.',
    date: '2026-08-01T12:00:00Z',
    products: ['wool-overcoat-01', 'mock-neck-01', 'wide-trouser-01'],
    isLive: false,
    gradient: ['#36454F', '#1A1A1A'],
  },
];
