# SOVEREIGN

The Future of Essential Clothing.

A futuristic e-commerce site for a budget-friendly fashion brand inspired by Yeezy and 1X aesthetics. Built with Next.js, Tailwind CSS, React Three Fiber, and Framer Motion.

## Design

- Bright white canvas with 3D chrome objects and geometric shapes
- Robotic typography (Space Grotesk + Space Mono)
- Non-traditional layout: modular discovery grid instead of typical hero + header
- Floating navigation with `mix-blend-mode: difference`
- Full-screen nav overlay with staggered animations
- Neutral/earthy color palette for products

## Tech Stack

- **Next.js 16** (App Router, TypeScript)
- **Tailwind CSS v4**
- **React Three Fiber** + **drei** (3D chrome elements)
- **Framer Motion** (animations)

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Pages

- `/` — Home with 3D hero, discovery grid, manifesto, featured drop
- `/collections` — All collections
- `/collections/[slug]` — Products in a collection
- `/product/[id]` — Product detail with gallery, sizing, add-to-cart
- `/about` — Brand story and values
