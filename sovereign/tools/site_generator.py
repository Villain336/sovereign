"""Multi-page Site Generator & React/Next.js Scaffolding.

Generates complete multi-page websites with routing and navigation,
and can scaffold full React/Next.js projects ready for deployment.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class MultiPageSiteTool(Tool):
    """Generate a multi-page static website with shared navigation."""

    name = "site_multipage"
    description = (
        "Generate a complete multi-page website with shared navigation, "
        "consistent design, and proper routing. Uses Tailwind CSS via CDN. "
        "Each page gets its own HTML file with a shared layout."
    )
    parameters = [
        ToolParameter(
            name="brand_name",
            description="Brand / company name",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="pages",
            description=(
                "JSON array of page definitions, e.g. "
                '[{"slug":"index","title":"Home","sections":["hero","features"]},'
                '{"slug":"about","title":"About","sections":["hero","contact"]}]'
            ),
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="palette",
            description="Color palette: midnight, ocean, forest, sunset, monochrome, aurora",
            param_type="string",
            required=False,
            default="midnight",
        ),
        ToolParameter(
            name="output_dir",
            description="Output directory (auto-generated if empty)",
            param_type="string",
            required=False,
        ),
    ]
    category = "design"
    risk_level = 0.1

    async def execute(self, **kwargs: Any) -> ToolResult:
        brand_name = kwargs.get("brand_name", "My Site")
        pages_json = kwargs.get("pages", "[]")
        palette_name = kwargs.get("palette", "midnight")
        output_dir = kwargs.get("output_dir", "")

        try:
            pages = json.loads(pages_json) if isinstance(pages_json, str) else pages_json
        except json.JSONDecodeError:
            return ToolResult(success=False, error="Invalid pages JSON")

        if not pages:
            return ToolResult(success=False, error="At least one page is required")

        from sovereign.tools.design_engine import DESIGN_SYSTEM

        palette = DESIGN_SYSTEM["color_palettes"].get(
            palette_name,
            DESIGN_SYSTEM["color_palettes"]["midnight"],
        )

        if not output_dir:
            output_dir = os.path.join(
                tempfile.gettempdir(),
                "sovereign_sites",
                brand_name.lower().replace(" ", "_"),
            )
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        try:
            generated_files: list[str] = []
            nav_items = [
                {"slug": p.get("slug", "index"), "title": p.get("title", "Page")}
                for p in pages
            ]

            for page_def in pages:
                slug = page_def.get("slug", "index")
                title = page_def.get("title", "Page")
                sections = page_def.get("sections", ["hero"])
                content = page_def.get("content", {})

                html = self._build_page(
                    brand_name, title, slug, palette, sections, nav_items, content,
                )
                filename = f"{slug}.html"
                (Path(output_dir) / filename).write_text(html, encoding="utf-8")
                generated_files.append(filename)

            return ToolResult(
                success=True,
                output=f"Multi-page site generated at {output_dir} ({len(generated_files)} pages)",
                metadata={
                    "output_dir": output_dir,
                    "files": generated_files,
                    "pages": len(generated_files),
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Site generation failed: {e!s}")

    def _build_page(
        self,
        brand: str,
        title: str,
        slug: str,
        palette: dict[str, str],
        sections: list[str],
        nav_items: list[dict[str, str]],
        content: dict[str, Any],
    ) -> str:
        """Build a single page with shared navigation."""
        nav_html = ""
        for item in nav_items:
            href = f"{item['slug']}.html" if item["slug"] != "index" else "index.html"
            active_class = f"text-[{palette['primary']}] font-semibold" if item["slug"] == slug else f"text-[{palette['text_muted']}]"
            nav_html += (
                f'<a href="{href}" class="{active_class} '
                f"hover:text-[{palette['primary']}] transition-colors text-sm\">"
                f"{item['title']}</a>\n        "
            )

        sections_html = ""
        for section in sections:
            sections_html += self._render_section(section, palette, content, brand)

        return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title} - {brand}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
  <style>
    * {{ font-family: 'Inter', sans-serif; }}
    body {{ background: {palette['bg']}; }}
  </style>
</head>
<body class="antialiased">
  <nav class="fixed top-0 w-full z-50 backdrop-blur-xl bg-[{palette['bg']}]/80 border-b border-[{palette['border']}]">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
      <a href="index.html" class="text-xl font-bold text-[{palette['primary']}]">{brand}</a>
      <div class="flex items-center gap-6">
        {nav_html}
      </div>
    </div>
  </nav>
  <main class="pt-16">
{sections_html}
  </main>
  <footer class="border-t border-[{palette['border']}] py-8">
    <div class="max-w-7xl mx-auto px-4 text-center text-[{palette['text_muted']}] text-sm">
      &copy; 2026 {brand}. All rights reserved.
    </div>
  </footer>
</body>
</html>"""

    def _render_section(
        self,
        section: str,
        palette: dict[str, str],
        content: dict[str, Any],
        brand: str,
    ) -> str:
        """Render a single section."""
        p = palette
        if section == "hero":
            headline = content.get("headline", brand)
            subtitle = content.get("subtitle", "Welcome to our website")
            return f"""
    <section class="py-20 md:py-32 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-[{p['primary']}]/10 via-transparent to-[{p['secondary']}]/10"></div>
      <div class="max-w-4xl mx-auto px-4 relative z-10">
        <h1 class="text-5xl md:text-7xl font-extrabold text-[{p['text']}] mb-6">{headline}</h1>
        <p class="text-xl text-[{p['text_muted']}] mb-10 max-w-2xl mx-auto">{subtitle}</p>
        <a href="#contact" class="inline-flex px-8 py-4 rounded-xl bg-[{p['primary']}] text-white font-semibold shadow-lg hover:-translate-y-0.5 transition-all">Get Started</a>
      </div>
    </section>"""

        if section == "features":
            features = content.get("features", [
                {"name": "Fast", "desc": "Lightning fast performance"},
                {"name": "Secure", "desc": "Enterprise-grade security"},
                {"name": "Simple", "desc": "Easy to use for everyone"},
            ])
            cards = ""
            for feat in features[:6]:
                cards += f"""
        <div class="p-8 rounded-2xl bg-[{p['surface']}] border border-[{p['border']}] hover:border-[{p['primary']}]/50 transition-all">
          <h3 class="text-xl font-semibold text-[{p['text']}] mb-3">{feat.get('name', '')}</h3>
          <p class="text-[{p['text_muted']}]">{feat.get('desc', '')}</p>
        </div>"""
            return f"""
    <section id="features" class="py-20 bg-[{p['surface']}]">
      <div class="max-w-7xl mx-auto px-4">
        <h2 class="text-4xl font-bold text-[{p['text']}] text-center mb-16">Features</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">{cards}
        </div>
      </div>
    </section>"""

        if section == "contact":
            return f"""
    <section id="contact" class="py-20">
      <div class="max-w-xl mx-auto px-4">
        <h2 class="text-4xl font-bold text-[{p['text']}] text-center mb-12">Contact Us</h2>
        <form class="space-y-4" id="contactForm" onsubmit="event.preventDefault();this.innerHTML='<p class=\\'text-center text-xl py-8\\'>Thank you!</p>'">
          <input type="text" placeholder="Name" required class="w-full px-4 py-3 rounded-xl bg-[{p['bg']}] border border-[{p['border']}] text-[{p['text']}] focus:border-[{p['primary']}] outline-none"/>
          <input type="email" placeholder="Email" required class="w-full px-4 py-3 rounded-xl bg-[{p['bg']}] border border-[{p['border']}] text-[{p['text']}] focus:border-[{p['primary']}] outline-none"/>
          <textarea placeholder="Message" rows="4" class="w-full px-4 py-3 rounded-xl bg-[{p['bg']}] border border-[{p['border']}] text-[{p['text']}] focus:border-[{p['primary']}] outline-none resize-none"></textarea>
          <button type="submit" class="w-full py-4 rounded-xl bg-[{p['primary']}] text-white font-semibold hover:-translate-y-0.5 transition-all">Send Message</button>
        </form>
      </div>
    </section>"""

        if section == "about":
            about_text = content.get("about_text", "We are a team dedicated to building amazing products.")
            return f"""
    <section id="about" class="py-20">
      <div class="max-w-3xl mx-auto px-4 text-center">
        <h2 class="text-4xl font-bold text-[{p['text']}] mb-8">About Us</h2>
        <p class="text-lg text-[{p['text_muted']}] leading-relaxed">{about_text}</p>
      </div>
    </section>"""

        if section == "team":
            team = content.get("team", [
                {"name": "Jane Smith", "role": "CEO"},
                {"name": "John Doe", "role": "CTO"},
                {"name": "Alice Chen", "role": "Designer"},
            ])
            cards = ""
            for member in team[:6]:
                initial = member.get("name", "?")[0]
                cards += f"""
        <div class="text-center">
          <div class="w-20 h-20 rounded-full bg-[{p['primary']}]/10 flex items-center justify-center text-[{p['primary']}] text-2xl font-bold mx-auto mb-4">{initial}</div>
          <h3 class="font-semibold text-[{p['text']}]">{member.get('name', '')}</h3>
          <p class="text-sm text-[{p['text_muted']}]">{member.get('role', '')}</p>
        </div>"""
            return f"""
    <section id="team" class="py-20 bg-[{p['surface']}]">
      <div class="max-w-5xl mx-auto px-4">
        <h2 class="text-4xl font-bold text-[{p['text']}] text-center mb-16">Our Team</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-12">{cards}
        </div>
      </div>
    </section>"""

        return ""


class ReactScaffoldTool(Tool):
    """Scaffold a complete React + Tailwind CSS project."""

    name = "scaffold_react"
    description = (
        "Generate a complete React + Vite + Tailwind CSS project structure "
        "ready for deployment. Includes routing, components, and configuration. "
        "Returns the path to the generated project directory."
    )
    parameters = [
        ToolParameter(
            name="project_name",
            description="Name of the project (used for directory and package.json)",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="description",
            description="Project description for package.json",
            param_type="string",
            required=False,
            default="A Sovereign-generated React application",
        ),
        ToolParameter(
            name="pages",
            description=(
                "Comma-separated page names (e.g., Home,About,Features,Pricing,Contact)"
            ),
            param_type="string",
            required=False,
            default="Home,About,Contact",
        ),
        ToolParameter(
            name="palette",
            description="Color palette name from the design system",
            param_type="string",
            required=False,
            default="midnight",
        ),
        ToolParameter(
            name="output_dir",
            description="Output directory (auto-generated if empty)",
            param_type="string",
            required=False,
        ),
    ]
    category = "design"
    risk_level = 0.2

    async def execute(self, **kwargs: Any) -> ToolResult:
        project_name = kwargs.get("project_name", "my-app")
        description = kwargs.get("description", "A Sovereign-generated React application")
        pages_str = kwargs.get("pages", "Home,About,Contact")
        palette_name = kwargs.get("palette", "midnight")
        output_dir = kwargs.get("output_dir", "")

        pages = [p.strip() for p in pages_str.split(",")]

        from sovereign.tools.design_engine import DESIGN_SYSTEM
        palette = DESIGN_SYSTEM["color_palettes"].get(
            palette_name,
            DESIGN_SYSTEM["color_palettes"]["midnight"],
        )

        if not output_dir:
            output_dir = os.path.join(
                tempfile.gettempdir(), "sovereign_react", project_name,
            )
        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)

        try:
            generated_files = self._scaffold(
                root, project_name, description, pages, palette,
            )
            return ToolResult(
                success=True,
                output=(
                    f"React project scaffolded at {output_dir}\n"
                    f"Files: {len(generated_files)}\n"
                    f"Run: cd {output_dir} && npm install && npm run dev"
                ),
                metadata={
                    "output_dir": output_dir,
                    "files": generated_files,
                    "pages": pages,
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Scaffold failed: {e!s}")

    def _scaffold(
        self,
        root: Path,
        name: str,
        description: str,
        pages: list[str],
        palette: dict[str, str],
    ) -> list[str]:
        """Create all project files."""
        files: list[str] = []

        # package.json
        pkg = {
            "name": name,
            "private": True,
            "version": "0.1.0",
            "description": description,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
            },
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "react-router-dom": "^6.26.0",
            },
            "devDependencies": {
                "@types/react": "^18.3.3",
                "@types/react-dom": "^18.3.0",
                "@vitejs/plugin-react": "^4.3.1",
                "autoprefixer": "^10.4.19",
                "postcss": "^8.4.39",
                "tailwindcss": "^3.4.6",
                "vite": "^5.3.4",
            },
        }
        self._write(root / "package.json", json.dumps(pkg, indent=2))
        files.append("package.json")

        # vite.config.js
        self._write(root / "vite.config.js", """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
""")
        files.append("vite.config.js")

        # tailwind.config.js
        self._write(root / "tailwind.config.js", f"""/** @type {{import('tailwindcss').Config}} */
export default {{
  content: ['./index.html', './src/**/*.{{js,jsx,ts,tsx}}'],
  theme: {{
    extend: {{
      colors: {{
        primary: '{palette["primary"]}',
        secondary: '{palette["secondary"]}',
        accent: '{palette["accent"]}',
      }},
    }},
  }},
  plugins: [],
}}
""")
        files.append("tailwind.config.js")

        # postcss.config.js
        self._write(root / "postcss.config.js", """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""")
        files.append("postcss.config.js")

        # index.html
        self._write(root / "index.html", f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{name}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
""")
        files.append("index.html")

        # src/
        src = root / "src"
        src.mkdir(exist_ok=True)

        # src/index.css
        self._write(src / "index.css", f"""@tailwind base;
@tailwind components;
@tailwind utilities;

* {{ font-family: 'Inter', sans-serif; }}
body {{ background: {palette['bg']}; color: {palette['text']}; }}
""")
        files.append("src/index.css")

        # src/main.jsx
        self._write(src / "main.jsx", """import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
)
""")
        files.append("src/main.jsx")

        # src/App.jsx
        imports = "\n".join(
            f"import {p}Page from './pages/{p}'"
            for p in pages
        )
        routes = "\n          ".join(
            f'<Route path="{"/" if p == "Home" else "/" + p.lower()}" element={{<{p}Page />}} />'
            for p in pages
        )
        nav_links = "\n            ".join(
            f'<NavLink to="{"/" if p == "Home" else "/" + p.lower()}" '
            f'className={{({{isActive}}) => isActive ? "text-primary font-semibold" : "text-gray-400 hover:text-primary"}}>'
            f"{p}</NavLink>"
            for p in pages
        )

        self._write(src / "App.jsx", f"""import {{ Routes, Route, NavLink }} from 'react-router-dom'
{imports}

export default function App() {{
  return (
    <div className="min-h-screen">
      <nav className="fixed top-0 w-full z-50 backdrop-blur-xl bg-[{palette['bg']}]/80 border-b border-[{palette['border']}]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <span className="text-xl font-bold text-primary">{name}</span>
          <div className="flex items-center gap-6 text-sm">
            {nav_links}
          </div>
        </div>
      </nav>
      <main className="pt-16">
        <Routes>
          {routes}
        </Routes>
      </main>
    </div>
  )
}}
""")
        files.append("src/App.jsx")

        # src/pages/
        pages_dir = src / "pages"
        pages_dir.mkdir(exist_ok=True)

        for page in pages:
            page_content = self._generate_page_component(page, palette, name)
            self._write(pages_dir / f"{page}.jsx", page_content)
            files.append(f"src/pages/{page}.jsx")

        # .env
        self._write(root / ".env", "VITE_API_URL=http://localhost:8000\n")
        files.append(".env")

        return files

    def _generate_page_component(
        self, page: str, palette: dict[str, str], brand: str,
    ) -> str:
        """Generate a React page component."""
        p = palette
        if page == "Home":
            return f"""export default function HomePage() {{
  return (
    <>
      <section className="relative overflow-hidden py-20 md:py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-secondary/10" />
        <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
          <div className="inline-flex items-center px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8">
            Now Available
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6">
            Welcome to {brand}
          </h1>
          <p className="text-xl text-[{p['text_muted']}] max-w-2xl mx-auto mb-10">
            The next generation platform for modern businesses.
          </p>
          <div className="flex gap-4 justify-center">
            <a href="#" className="px-8 py-4 rounded-xl bg-primary text-white font-semibold shadow-lg hover:-translate-y-0.5 transition-all">
              Get Started
            </a>
            <a href="#" className="px-8 py-4 rounded-xl border-2 border-[{p['border']}] font-semibold hover:border-primary transition-all">
              Learn More
            </a>
          </div>
        </div>
      </section>
      <section className="py-20 bg-[{p['surface']}]">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16">Why Choose Us</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {{['Lightning Fast', 'Secure by Default', 'Easy to Use'].map((name, i) => (
              <div key={{i}} className="p-8 rounded-2xl bg-[{p['bg']}] border border-[{p['border']}] hover:border-primary/50 transition-all">
                <h3 className="text-xl font-semibold mb-3">{{name}}</h3>
                <p className="text-[{p['text_muted']}]">Built for the modern web with best practices baked in.</p>
              </div>
            ))}}
          </div>
        </div>
      </section>
    </>
  )
}}
"""
        if page == "About":
            return f"""export default function AboutPage() {{
  return (
    <section className="py-20 md:py-32">
      <div className="max-w-3xl mx-auto px-4">
        <h1 className="text-5xl font-extrabold mb-8 text-center">About Us</h1>
        <p className="text-lg text-[{p['text_muted']}] leading-relaxed text-center mb-16">
          We are building the future of autonomous technology. Our mission is to empower
          businesses with intelligent automation that works around the clock.
        </p>
        <div className="grid grid-cols-3 gap-8 text-center">
          {{[['1M+', 'Users'], ['99.9%', 'Uptime'], ['24/7', 'Support']].map(([num, label], i) => (
            <div key={{i}}>
              <div className="text-3xl font-extrabold text-primary">{{num}}</div>
              <div className="text-[{p['text_muted']}]">{{label}}</div>
            </div>
          ))}}
        </div>
      </div>
    </section>
  )
}}
"""
        if page == "Contact":
            return f"""import {{ useState }} from 'react'

export default function ContactPage() {{
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e) => {{
    e.preventDefault()
    setSubmitted(true)
  }}

  return (
    <section className="py-20 md:py-32">
      <div className="max-w-xl mx-auto px-4">
        <h1 className="text-5xl font-extrabold mb-4 text-center">Get In Touch</h1>
        <p className="text-[{p['text_muted']}] text-center mb-12">We'd love to hear from you.</p>
        {{submitted ? (
          <div className="text-center py-12">
            <p className="text-2xl font-bold mb-2">Thank you!</p>
            <p className="text-[{p['text_muted']}]">We'll be in touch soon.</p>
          </div>
        ) : (
          <form onSubmit={{handleSubmit}} className="space-y-4">
            <input type="text" placeholder="Name" required className="w-full px-4 py-3 rounded-xl bg-[{p['surface']}] border border-[{p['border']}] focus:border-primary outline-none transition-all" />
            <input type="email" placeholder="Email" required className="w-full px-4 py-3 rounded-xl bg-[{p['surface']}] border border-[{p['border']}] focus:border-primary outline-none transition-all" />
            <textarea placeholder="Message" rows={{4}} className="w-full px-4 py-3 rounded-xl bg-[{p['surface']}] border border-[{p['border']}] focus:border-primary outline-none transition-all resize-none" />
            <button type="submit" className="w-full py-4 rounded-xl bg-primary text-white font-semibold hover:-translate-y-0.5 transition-all">
              Send Message
            </button>
          </form>
        )}}
      </div>
    </section>
  )
}}
"""
        # Generic page
        return f"""export default function {page}Page() {{
  return (
    <section className="py-20 md:py-32">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h1 className="text-5xl font-extrabold mb-6">{page}</h1>
        <p className="text-lg text-[{p['text_muted']}]">Content for the {page} page.</p>
      </div>
    </section>
  )
}}
"""

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
