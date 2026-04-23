"""AI Design Engine - Claude-powered UI generation with Tailwind CSS.

Generates professional, modern UIs rivaling DesignJoy quality using
Claude for intelligent component generation and a curated design system
with Tailwind CSS, glass morphism, gradients, and responsive layouts.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from sovereign.tools.base import Tool, ToolParameter, ToolResult

# ---------------------------------------------------------------------------
# Design system tokens
# ---------------------------------------------------------------------------

DESIGN_SYSTEM = {
    "color_palettes": {
        "midnight": {
            "primary": "#6366f1",
            "secondary": "#8b5cf6",
            "accent": "#f59e0b",
            "bg": "#0f172a",
            "surface": "#1e293b",
            "text": "#f8fafc",
            "text_muted": "#94a3b8",
            "border": "#334155",
        },
        "ocean": {
            "primary": "#0ea5e9",
            "secondary": "#06b6d4",
            "accent": "#f97316",
            "bg": "#ffffff",
            "surface": "#f0f9ff",
            "text": "#0c4a6e",
            "text_muted": "#64748b",
            "border": "#e0f2fe",
        },
        "forest": {
            "primary": "#10b981",
            "secondary": "#059669",
            "accent": "#f59e0b",
            "bg": "#ffffff",
            "surface": "#ecfdf5",
            "text": "#064e3b",
            "text_muted": "#64748b",
            "border": "#d1fae5",
        },
        "sunset": {
            "primary": "#f43f5e",
            "secondary": "#e11d48",
            "accent": "#a855f7",
            "bg": "#ffffff",
            "surface": "#fff1f2",
            "text": "#1e293b",
            "text_muted": "#64748b",
            "border": "#ffe4e6",
        },
        "monochrome": {
            "primary": "#18181b",
            "secondary": "#3f3f46",
            "accent": "#6366f1",
            "bg": "#ffffff",
            "surface": "#fafafa",
            "text": "#18181b",
            "text_muted": "#71717a",
            "border": "#e4e4e7",
        },
        "aurora": {
            "primary": "#8b5cf6",
            "secondary": "#ec4899",
            "accent": "#06b6d4",
            "bg": "#020617",
            "surface": "#0f172a",
            "text": "#f8fafc",
            "text_muted": "#94a3b8",
            "border": "#1e293b",
        },
    },
    "typography": {
        "font_stack": (
            "'Inter', -apple-system, BlinkMacSystemFont, "
            "'Segoe UI', Roboto, sans-serif"
        ),
        "heading_sizes": {
            "h1": "text-5xl md:text-6xl lg:text-7xl",
            "h2": "text-3xl md:text-4xl lg:text-5xl",
            "h3": "text-xl md:text-2xl",
            "h4": "text-lg md:text-xl",
        },
    },
    "spacing": {
        "section_y": "py-20 md:py-28 lg:py-32",
        "container": "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
    },
}


# ---------------------------------------------------------------------------
# Template fragments used to compose pages
# ---------------------------------------------------------------------------

SECTION_TEMPLATES: dict[str, str] = {}

SECTION_TEMPLATES["hero_gradient"] = """
<section class="relative overflow-hidden {section_y}">
  <div class="absolute inset-0 bg-gradient-to-br from-[{primary}]/10 via-transparent to-[{secondary}]/10"></div>
  <div class="absolute top-20 left-10 w-72 h-72 bg-[{primary}]/20 rounded-full blur-3xl"></div>
  <div class="absolute bottom-10 right-10 w-96 h-96 bg-[{secondary}]/20 rounded-full blur-3xl"></div>
  <div class="{container} relative z-10 text-center">
    <div class="inline-flex items-center px-4 py-1.5 rounded-full bg-[{primary}]/10 text-[{primary}] text-sm font-medium mb-8">
      {badge_text}
    </div>
    <h1 class="{h1} font-extrabold tracking-tight text-[{text}] mb-6">
      {headline}
    </h1>
    <p class="text-lg md:text-xl text-[{text_muted}] max-w-2xl mx-auto mb-10">
      {subheadline}
    </p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a href="#contact" class="inline-flex items-center justify-center px-8 py-4 rounded-xl bg-[{primary}] text-white font-semibold shadow-lg shadow-[{primary}]/25 hover:shadow-xl hover:shadow-[{primary}]/30 hover:-translate-y-0.5 transition-all duration-200">
        {cta_primary}
        <svg class="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
      </a>
      <a href="#features" class="inline-flex items-center justify-center px-8 py-4 rounded-xl border-2 border-[{border}] text-[{text}] font-semibold hover:border-[{primary}] hover:text-[{primary}] transition-all duration-200">
        {cta_secondary}
      </a>
    </div>
  </div>
</section>
"""

SECTION_TEMPLATES["features_grid"] = """
<section id="features" class="{section_y} bg-[{surface}]">
  <div class="{container}">
    <div class="text-center mb-16">
      <h2 class="{h2} font-bold text-[{text}] mb-4">{features_title}</h2>
      <p class="text-lg text-[{text_muted}] max-w-2xl mx-auto">{features_subtitle}</p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {feature_cards}
    </div>
  </div>
</section>
"""

SECTION_TEMPLATES["feature_card"] = """
      <div class="group p-8 rounded-2xl bg-[{bg}] border border-[{border}] hover:border-[{primary}]/50 hover:shadow-xl hover:shadow-[{primary}]/5 transition-all duration-300">
        <div class="w-12 h-12 rounded-xl bg-[{primary}]/10 flex items-center justify-center mb-6 group-hover:bg-[{primary}]/20 transition-colors">
          <svg class="w-6 h-6 text-[{primary}]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{icon_path}"/></svg>
        </div>
        <h3 class="text-xl font-semibold text-[{text}] mb-3">{feature_name}</h3>
        <p class="text-[{text_muted}] leading-relaxed">{feature_desc}</p>
      </div>
"""

SECTION_TEMPLATES["pricing"] = """
<section id="pricing" class="{section_y}">
  <div class="{container}">
    <div class="text-center mb-16">
      <h2 class="{h2} font-bold text-[{text}] mb-4">Simple, Transparent Pricing</h2>
      <p class="text-lg text-[{text_muted}] max-w-2xl mx-auto">No hidden fees. Cancel anytime.</p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
      {pricing_cards}
    </div>
  </div>
</section>
"""

SECTION_TEMPLATES["pricing_card"] = """
      <div class="relative p-8 rounded-2xl {card_classes}">
        {popular_badge}
        <h3 class="text-xl font-semibold text-[{text}] mb-2">{plan_name}</h3>
        <p class="text-[{text_muted}] mb-6">{plan_desc}</p>
        <div class="mb-6">
          <span class="text-5xl font-extrabold text-[{text}]">{plan_price}</span>
          <span class="text-[{text_muted}]">/month</span>
        </div>
        <ul class="space-y-3 mb-8">
          {plan_features}
        </ul>
        <a href="#contact" class="block w-full text-center py-3 rounded-xl {btn_classes} font-semibold transition-all duration-200">
          Get Started
        </a>
      </div>
"""

SECTION_TEMPLATES["testimonials"] = """
<section id="testimonials" class="{section_y} bg-[{surface}]">
  <div class="{container}">
    <div class="text-center mb-16">
      <h2 class="{h2} font-bold text-[{text}] mb-4">Loved by Thousands</h2>
      <p class="text-lg text-[{text_muted}]">See what our customers say</p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {testimonial_cards}
    </div>
  </div>
</section>
"""

SECTION_TEMPLATES["testimonial_card"] = """
      <div class="p-8 rounded-2xl bg-[{bg}] border border-[{border}]">
        <div class="flex gap-1 mb-4">
          <svg class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <svg class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <svg class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <svg class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <svg class="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
        </div>
        <p class="text-[{text}] mb-6 leading-relaxed">"{quote}"</p>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-[{primary}]/10 flex items-center justify-center text-[{primary}] font-bold">{author_initial}</div>
          <div>
            <p class="font-semibold text-[{text}]">{author_name}</p>
            <p class="text-sm text-[{text_muted}]">{author_role}</p>
          </div>
        </div>
      </div>
"""

SECTION_TEMPLATES["cta_section"] = """
<section id="contact" class="{section_y}">
  <div class="{container}">
    <div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[{primary}] to-[{secondary}] p-12 md:p-20 text-center">
      <div class="absolute top-0 left-0 w-full h-full bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRoLTJ2LTRoMnYtNGgydjRoNHYyaC00djRoLTJ6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-20"></div>
      <div class="relative z-10">
        <h2 class="{h2} font-bold text-white mb-4">{cta_title}</h2>
        <p class="text-lg text-white/80 max-w-xl mx-auto mb-8">{cta_subtitle}</p>
        <form class="max-w-md mx-auto flex flex-col sm:flex-row gap-3" id="ctaForm">
          <input type="email" name="email" placeholder="Enter your email" required
            class="flex-1 px-5 py-3.5 rounded-xl bg-white/10 backdrop-blur border border-white/20 text-white placeholder-white/50 focus:outline-none focus:border-white/50 transition-colors"/>
          <button type="submit" class="px-8 py-3.5 rounded-xl bg-white text-[{primary}] font-semibold hover:bg-white/90 transition-colors shadow-lg">
            {cta_button}
          </button>
        </form>
      </div>
    </div>
  </div>
</section>
"""

SECTION_TEMPLATES["contact_form"] = """
<section id="contact" class="{section_y} bg-[{surface}]">
  <div class="{container}">
    <div class="max-w-2xl mx-auto">
      <div class="text-center mb-12">
        <h2 class="{h2} font-bold text-[{text}] mb-4">Get In Touch</h2>
        <p class="text-lg text-[{text_muted}]">We'd love to hear from you. Send us a message.</p>
      </div>
      <form id="contactForm" class="space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-[{text}] mb-2">Name</label>
            <input type="text" name="name" required class="w-full px-4 py-3 rounded-xl bg-[{bg}] border border-[{border}] text-[{text}] focus:border-[{primary}] focus:ring-2 focus:ring-[{primary}]/20 outline-none transition-all"/>
          </div>
          <div>
            <label class="block text-sm font-medium text-[{text}] mb-2">Email</label>
            <input type="email" name="email" required class="w-full px-4 py-3 rounded-xl bg-[{bg}] border border-[{border}] text-[{text}] focus:border-[{primary}] focus:ring-2 focus:ring-[{primary}]/20 outline-none transition-all"/>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-[{text}] mb-2">Subject</label>
          <input type="text" name="subject" class="w-full px-4 py-3 rounded-xl bg-[{bg}] border border-[{border}] text-[{text}] focus:border-[{primary}] focus:ring-2 focus:ring-[{primary}]/20 outline-none transition-all"/>
        </div>
        <div>
          <label class="block text-sm font-medium text-[{text}] mb-2">Message</label>
          <textarea name="message" rows="5" required class="w-full px-4 py-3 rounded-xl bg-[{bg}] border border-[{border}] text-[{text}] focus:border-[{primary}] focus:ring-2 focus:ring-[{primary}]/20 outline-none transition-all resize-none"></textarea>
        </div>
        <button type="submit" class="w-full py-4 rounded-xl bg-[{primary}] text-white font-semibold shadow-lg shadow-[{primary}]/25 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200">
          Send Message
        </button>
      </form>
    </div>
  </div>
</section>
"""

SECTION_TEMPLATES["footer"] = """
<footer class="border-t border-[{border}] {section_y}">
  <div class="{container}">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
      <div class="md:col-span-1">
        <a href="#" class="text-2xl font-bold text-[{primary}]">{brand}</a>
        <p class="text-[{text_muted}] mt-4">{brand_tagline}</p>
      </div>
      <div>
        <h4 class="font-semibold text-[{text}] mb-4">Product</h4>
        <ul class="space-y-2 text-[{text_muted}]">
          <li><a href="#features" class="hover:text-[{primary}] transition-colors">Features</a></li>
          <li><a href="#pricing" class="hover:text-[{primary}] transition-colors">Pricing</a></li>
          <li><a href="#" class="hover:text-[{primary}] transition-colors">Changelog</a></li>
          <li><a href="#" class="hover:text-[{primary}] transition-colors">Docs</a></li>
        </ul>
      </div>
      <div>
        <h4 class="font-semibold text-[{text}] mb-4">Company</h4>
        <ul class="space-y-2 text-[{text_muted}]">
          <li><a href="#" class="hover:text-[{primary}] transition-colors">About</a></li>
          <li><a href="#" class="hover:text-[{primary}] transition-colors">Blog</a></li>
          <li><a href="#" class="hover:text-[{primary}] transition-colors">Careers</a></li>
          <li><a href="#contact" class="hover:text-[{primary}] transition-colors">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4 class="font-semibold text-[{text}] mb-4">Legal</h4>
        <ul class="space-y-2 text-[{text_muted}]">
          <li><a href="#" class="hover:text-[{primary}] transition-colors">Privacy</a></li>
          <li><a href="#" class="hover:text-[{primary}] transition-colors">Terms</a></li>
        </ul>
      </div>
    </div>
    <div class="pt-8 border-t border-[{border}] flex flex-col md:flex-row justify-between items-center gap-4">
      <p class="text-[{text_muted}] text-sm">&copy; 2026 {brand}. All rights reserved.</p>
      <div class="flex gap-4">
        <a href="#" class="text-[{text_muted}] hover:text-[{primary}] transition-colors">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
        </a>
        <a href="#" class="text-[{text_muted}] hover:text-[{primary}] transition-colors">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
        </a>
      </div>
    </div>
  </div>
</footer>
"""

SECTION_TEMPLATES["navbar"] = """
<nav class="fixed top-0 w-full z-50 backdrop-blur-xl bg-[{bg}]/80 border-b border-[{border}]">
  <div class="{container} flex items-center justify-between h-16">
    <a href="#" class="text-xl font-bold text-[{primary}]">{brand}</a>
    <div class="hidden md:flex items-center gap-8">
      {nav_links}
    </div>
    <a href="#contact" class="hidden md:inline-flex items-center px-5 py-2.5 rounded-lg bg-[{primary}] text-white text-sm font-semibold hover:opacity-90 transition-opacity">
      {nav_cta}
    </a>
    <button class="md:hidden text-[{text}]" id="mobileMenuBtn">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>
  </div>
  <div class="hidden md:hidden" id="mobileMenu">
    <div class="px-4 py-4 space-y-2 bg-[{bg}] border-b border-[{border}]">
      {mobile_nav_links}
    </div>
  </div>
</nav>
"""

SVG_ICON_PATHS = [
    "M13 10V3L4 14h7v7l9-11h-7z",  # lightning bolt
    "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",  # check circle
    "M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4",  # adjustments
    "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",  # cube
    "M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064",  # globe
    "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",  # chart
]


def _safe_format(template: str, values: dict[str, str]) -> str:
    """Format template with values, replacing {key} patterns safely."""
    result = template
    for key, val in values.items():
        result = result.replace("{" + key + "}", val)
    return result


class AIDesignTool(Tool):
    """Generate professional UI pages using Claude + Tailwind CSS design system."""

    name = "ai_design"
    description = (
        "Generate a professional, modern website page using AI and the Sovereign "
        "design system (Tailwind CSS, glass morphism, gradients, responsive). "
        "Supports landing pages, SaaS sites, portfolios, dashboards. Returns "
        "the path to the generated site directory with all HTML/CSS/JS files."
    )
    parameters = [
        ToolParameter(
            name="page_type",
            description=(
                "Type of page: saas_landing, portfolio, agency, ecommerce, "
                "dashboard, blog, startup"
            ),
            param_type="string",
            required=True,
            enum=[
                "saas_landing", "portfolio", "agency", "ecommerce",
                "dashboard", "blog", "startup",
            ],
        ),
        ToolParameter(
            name="brand_name",
            description="Brand / company name",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="description",
            description=(
                "Detailed description of the site: what it does, target audience, "
                "key features, tone (professional/playful/bold)"
            ),
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="palette",
            description=(
                "Color palette: midnight, ocean, forest, sunset, monochrome, aurora"
            ),
            param_type="string",
            required=False,
            default="midnight",
            enum=["midnight", "ocean", "forest", "sunset", "monochrome", "aurora"],
        ),
        ToolParameter(
            name="sections",
            description=(
                "Comma-separated sections: hero,features,pricing,testimonials,"
                "cta,contact,footer"
            ),
            param_type="string",
            required=False,
            default="hero,features,pricing,testimonials,cta,footer",
        ),
        ToolParameter(
            name="output_dir",
            description="Output directory (auto-generated if not specified)",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="use_llm",
            description="Use Claude to generate custom content (true/false)",
            param_type="string",
            required=False,
            default="true",
        ),
    ]
    category = "design"
    risk_level = 0.1

    def __init__(self) -> None:
        self._llm_router: Any = None

    def set_llm_router(self, router: Any) -> None:
        """Inject the LLM router for AI-powered content generation."""
        self._llm_router = router

    async def execute(self, **kwargs: Any) -> ToolResult:
        page_type = kwargs.get("page_type", "saas_landing")
        brand_name = kwargs.get("brand_name", "My Brand")
        description = kwargs.get("description", "")
        palette_name = kwargs.get("palette", "midnight")
        sections_str = kwargs.get("sections", "hero,features,pricing,testimonials,cta,footer")
        output_dir = kwargs.get("output_dir", "")
        use_llm = kwargs.get("use_llm", "true").lower() == "true"

        if not description:
            return ToolResult(success=False, error="Description is required")

        palette = DESIGN_SYSTEM["color_palettes"].get(
            palette_name,
            DESIGN_SYSTEM["color_palettes"]["midnight"],
        )
        sections = [s.strip() for s in sections_str.split(",")]

        if not output_dir:
            output_dir = os.path.join(
                tempfile.gettempdir(),
                "sovereign_designs",
                brand_name.lower().replace(" ", "_"),
            )
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        try:
            # Generate content with LLM if available
            content = await self._generate_content(
                page_type, brand_name, description, sections, use_llm,
            )

            # Build the HTML page
            html = self._build_page(
                brand_name, palette, sections, content, page_type,
            )

            # Write files
            (Path(output_dir) / "index.html").write_text(html, encoding="utf-8")

            return ToolResult(
                success=True,
                output=f"Design generated at {output_dir}/index.html",
                metadata={
                    "output_dir": output_dir,
                    "files": ["index.html"],
                    "page_type": page_type,
                    "palette": palette_name,
                    "sections": sections,
                    "brand": brand_name,
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Design generation failed: {e!s}")

    async def _generate_content(
        self,
        page_type: str,
        brand_name: str,
        description: str,
        sections: list[str],
        use_llm: bool,
    ) -> dict[str, Any]:
        """Generate page content, optionally using LLM."""
        content: dict[str, Any] = {
            "badge_text": "Now Available",
            "headline": brand_name,
            "subheadline": description[:200],
            "cta_primary": "Get Started Free",
            "cta_secondary": "Learn More",
            "nav_cta": "Get Started",
            "brand_tagline": description[:100],
            "features_title": "Everything You Need",
            "features_subtitle": "Powerful features to help you succeed",
            "features": [
                {"name": "Lightning Fast", "desc": "Built for speed and performance."},
                {"name": "Secure by Default", "desc": "Enterprise-grade security built in."},
                {"name": "Easy Integration", "desc": "Connect with your favorite tools."},
                {"name": "Analytics", "desc": "Deep insights into your data."},
                {"name": "Global Scale", "desc": "Deploy anywhere in the world."},
                {"name": "24/7 Support", "desc": "Our team is always here to help."},
            ],
            "pricing_plans": [
                {
                    "name": "Starter",
                    "desc": "For individuals",
                    "price": "$19",
                    "features": ["5 projects", "10GB storage", "Email support"],
                    "popular": False,
                },
                {
                    "name": "Pro",
                    "desc": "For growing teams",
                    "price": "$49",
                    "features": ["Unlimited projects", "100GB storage", "Priority support", "API access"],
                    "popular": True,
                },
                {
                    "name": "Enterprise",
                    "desc": "For large organizations",
                    "price": "$99",
                    "features": ["Everything in Pro", "Unlimited storage", "Dedicated support", "Custom integrations", "SLA"],
                    "popular": False,
                },
            ],
            "testimonials": [
                {"quote": "This transformed how we work. Absolutely incredible.", "name": "Sarah Chen", "role": "CEO, TechFlow", "initial": "S"},
                {"quote": "The best investment we've made this year. ROI was immediate.", "name": "Marcus Johnson", "role": "CTO, ScaleUp", "initial": "M"},
                {"quote": "Simple, powerful, and beautifully designed. A joy to use.", "name": "Emily Rodriguez", "role": "Founder, DesignLab", "initial": "E"},
            ],
            "cta_title": "Ready to Get Started?",
            "cta_subtitle": "Join thousands of happy customers. Start your free trial today.",
            "cta_button": "Start Free Trial",
        }

        if use_llm and self._llm_router:
            try:
                content = await self._generate_content_with_llm(
                    page_type, brand_name, description, sections, content,
                )
            except Exception:
                pass  # Fall back to defaults

        return content

    async def _generate_content_with_llm(
        self,
        page_type: str,
        brand_name: str,
        description: str,
        sections: list[str],
        defaults: dict[str, Any],
    ) -> dict[str, Any]:
        """Use Claude to generate custom content for the page."""
        from sovereign.llm.provider import Message, MessageRole

        prompt = (
            f"Generate website copy for a {page_type} page.\n"
            f"Brand: {brand_name}\n"
            f"Description: {description}\n"
            f"Sections: {', '.join(sections)}\n\n"
            "Return a JSON object with these keys:\n"
            '- "badge_text": short badge text (3-5 words)\n'
            '- "headline": compelling headline (5-10 words)\n'
            '- "subheadline": supporting text (15-25 words)\n'
            '- "cta_primary": primary CTA button text (2-4 words)\n'
            '- "cta_secondary": secondary CTA text (2-4 words)\n'
            '- "features_title": features section heading\n'
            '- "features_subtitle": features section subheading\n'
            '- "features": array of 6 objects with "name" and "desc"\n'
            '- "pricing_plans": array of 3 plans with "name", "desc", "price", "features" (array of strings), "popular" (bool)\n'
            '- "testimonials": array of 3 with "quote", "name", "role", "initial"\n'
            '- "cta_title": CTA section heading\n'
            '- "cta_subtitle": CTA section subtext\n'
            '- "cta_button": CTA button text\n'
            '- "brand_tagline": short tagline for footer\n\n'
            "Make the copy compelling, specific to the brand, and professional.\n"
            "Respond ONLY with valid JSON. No markdown."
        )

        messages = [
            Message(role=MessageRole.SYSTEM, content="You are an expert copywriter and UI designer. Generate compelling website copy as JSON."),
            Message(role=MessageRole.USER, content=prompt),
        ]

        response = await self._llm_router.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )

        try:
            text = response.content.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            parsed = json.loads(text)
            # Merge with defaults so nothing is missing
            defaults.update(parsed)
        except (json.JSONDecodeError, IndexError):
            pass

        return defaults

    def _build_page(
        self,
        brand_name: str,
        palette: dict[str, str],
        sections: list[str],
        content: dict[str, Any],
        page_type: str,
    ) -> str:
        """Build the complete HTML page."""
        tokens = {
            **palette,
            "brand": brand_name,
            "container": DESIGN_SYSTEM["spacing"]["container"],
            "section_y": DESIGN_SYSTEM["spacing"]["section_y"],
            "h1": DESIGN_SYSTEM["typography"]["heading_sizes"]["h1"],
            "h2": DESIGN_SYSTEM["typography"]["heading_sizes"]["h2"],
            "h3": DESIGN_SYSTEM["typography"]["heading_sizes"]["h3"],
        }

        # Build navbar
        nav_links_html = ""
        mobile_links_html = ""
        for s in sections:
            if s in ("hero", "footer"):
                continue
            label = s.replace("_", " ").title()
            if s == "cta":
                label = "Contact"
            nav_links_html += (
                f'<a href="#{s}" class="text-[{palette["text_muted"]}] '
                f'hover:text-[{palette["primary"]}] transition-colors '
                f'text-sm font-medium">{label}</a>\n      '
            )
            mobile_links_html += (
                f'<a href="#{s}" class="block py-2 text-[{palette["text_muted"]}] '
                f'hover:text-[{palette["primary"]}]">{label}</a>\n      '
            )

        tokens["nav_links"] = nav_links_html
        tokens["mobile_nav_links"] = mobile_links_html
        tokens["nav_cta"] = content.get("cta_primary", "Get Started")

        parts: list[str] = []
        parts.append(_safe_format(SECTION_TEMPLATES["navbar"], tokens))

        for section in sections:
            if section == "hero":
                tokens.update({
                    "badge_text": content.get("badge_text", ""),
                    "headline": content.get("headline", brand_name),
                    "subheadline": content.get("subheadline", ""),
                    "cta_primary": content.get("cta_primary", "Get Started"),
                    "cta_secondary": content.get("cta_secondary", "Learn More"),
                })
                parts.append(_safe_format(SECTION_TEMPLATES["hero_gradient"], tokens))

            elif section == "features":
                features = content.get("features", [])
                cards_html = ""
                for i, feat in enumerate(features[:6]):
                    icon_path = SVG_ICON_PATHS[i % len(SVG_ICON_PATHS)]
                    card_tokens = {
                        **tokens,
                        "icon_path": icon_path,
                        "feature_name": feat.get("name", "Feature"),
                        "feature_desc": feat.get("desc", "Description"),
                    }
                    cards_html += _safe_format(
                        SECTION_TEMPLATES["feature_card"], card_tokens,
                    )
                tokens["feature_cards"] = cards_html
                tokens["features_title"] = content.get("features_title", "Features")
                tokens["features_subtitle"] = content.get("features_subtitle", "")
                parts.append(_safe_format(SECTION_TEMPLATES["features_grid"], tokens))

            elif section == "pricing":
                plans = content.get("pricing_plans", [])
                cards_html = ""
                for plan in plans[:3]:
                    is_popular = plan.get("popular", False)
                    features_html = ""
                    for feat in plan.get("features", []):
                        features_html += (
                            f'<li class="flex items-center gap-2 text-[{palette["text_muted"]}]">'
                            f'<svg class="w-5 h-5 text-[{palette["primary"]}]" fill="none" '
                            f'stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" '
                            f'stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>'
                            f"{feat}</li>\n          "
                        )
                    card_tokens = {
                        **tokens,
                        "plan_name": plan.get("name", "Plan"),
                        "plan_desc": plan.get("desc", ""),
                        "plan_price": plan.get("price", "$0"),
                        "plan_features": features_html,
                        "card_classes": (
                            f"border-2 border-[{palette['primary']}] bg-[{palette['bg']}] shadow-xl shadow-[{palette['primary']}]/10"
                            if is_popular
                            else f"border border-[{palette['border']}] bg-[{palette['bg']}]"
                        ),
                        "popular_badge": (
                            f'<div class="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-[{palette["primary"]}] text-white text-sm font-medium">Most Popular</div>'
                            if is_popular
                            else ""
                        ),
                        "btn_classes": (
                            f"bg-[{palette['primary']}] text-white hover:opacity-90"
                            if is_popular
                            else f"border border-[{palette['border']}] text-[{palette['text']}] hover:border-[{palette['primary']}]"
                        ),
                    }
                    cards_html += _safe_format(
                        SECTION_TEMPLATES["pricing_card"], card_tokens,
                    )
                tokens["pricing_cards"] = cards_html
                parts.append(_safe_format(SECTION_TEMPLATES["pricing"], tokens))

            elif section == "testimonials":
                testimonials = content.get("testimonials", [])
                cards_html = ""
                for t in testimonials[:3]:
                    card_tokens = {
                        **tokens,
                        "quote": t.get("quote", ""),
                        "author_name": t.get("name", "Customer"),
                        "author_role": t.get("role", ""),
                        "author_initial": t.get("initial", "C"),
                    }
                    cards_html += _safe_format(
                        SECTION_TEMPLATES["testimonial_card"], card_tokens,
                    )
                tokens["testimonial_cards"] = cards_html
                parts.append(_safe_format(SECTION_TEMPLATES["testimonials"], tokens))

            elif section == "cta":
                tokens.update({
                    "cta_title": content.get("cta_title", "Ready to Get Started?"),
                    "cta_subtitle": content.get("cta_subtitle", ""),
                    "cta_button": content.get("cta_button", "Start Free Trial"),
                })
                parts.append(_safe_format(SECTION_TEMPLATES["cta_section"], tokens))

            elif section == "contact":
                parts.append(_safe_format(SECTION_TEMPLATES["contact_form"], tokens))

            elif section == "footer":
                tokens["brand_tagline"] = content.get("brand_tagline", "")
                parts.append(_safe_format(SECTION_TEMPLATES["footer"], tokens))

        body_html = "\n".join(parts)

        js_code = self._generate_js()

        return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{brand_name}</title>
  <meta name="description" content="{content.get('subheadline', '')}"/>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet"/>
  <style>
    * {{ font-family: {DESIGN_SYSTEM["typography"]["font_stack"]}; }}
    html {{ scroll-behavior: smooth; }}
    body {{ background: {palette["bg"]}; }}
  </style>
</head>
<body class="antialiased">
{body_html}
<script>
{js_code}
</script>
</body>
</html>"""

    def _generate_js(self) -> str:
        """Generate JavaScript for interactivity."""
        return """
document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle
  const btn = document.getElementById('mobileMenuBtn');
  const menu = document.getElementById('mobileMenu');
  if (btn && menu) {
    btn.addEventListener('click', () => menu.classList.toggle('hidden'));
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      const t = document.querySelector(a.getAttribute('href'));
      if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
      if (menu) menu.classList.add('hidden');
    });
  });

  // Form handling
  ['contactForm', 'ctaForm'].forEach(id => {
    const form = document.getElementById(id);
    if (form) {
      form.addEventListener('submit', e => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(form).entries());
        const leads = JSON.parse(localStorage.getItem('sovereign_leads') || '[]');
        leads.push({...data, timestamp: new Date().toISOString(), source: id});
        localStorage.setItem('sovereign_leads', JSON.stringify(leads));
        form.innerHTML = '<div class=\"text-center py-8\"><p class=\"text-2xl font-bold mb-2\">Thank you!</p><p class=\"opacity-70\">We\\'ll be in touch soon.</p></div>';
      });
    }
  });

  // Intersection Observer for animations
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('section').forEach(s => observer.observe(s));
});
"""
