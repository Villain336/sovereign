"""Website Builder Tool - create and deploy websites and landing pages.

Enables the agent to:
- Generate HTML/CSS/JS websites from descriptions
- Deploy static sites to hosting providers
- Create landing pages for lead capture
- Set up simple web applications
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import httpx

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class WebsiteGeneratorTool(Tool):
    """Generate website files from a description."""

    name = "website_generate"
    description = (
        "Generate a complete website (HTML, CSS, JS) from a description. "
        "Use this to create landing pages, portfolio sites, product pages, "
        "business websites, and lead capture forms. Returns the path to "
        "the generated site directory."
    )
    parameters = [
        ToolParameter(
            name="site_type",
            description="Type of site: landing_page, business, portfolio, product, form",
            param_type="string",
            required=True,
            enum=["landing_page", "business", "portfolio", "product", "form"],
        ),
        ToolParameter(
            name="title",
            description="Website title / business name",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="description",
            description="Detailed description of what the site should contain",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="output_dir",
            description="Directory to output the site files (default: auto-generated)",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="sections",
            description="Comma-separated list of sections (e.g., hero,features,pricing,contact)",
            param_type="string",
            required=False,
            default="hero,features,cta",
        ),
        ToolParameter(
            name="color_scheme",
            description="Primary color hex (e.g., #2563eb)",
            param_type="string",
            required=False,
            default="#2563eb",
        ),
    ]
    category = "builder"
    risk_level = 0.2

    async def execute(self, **kwargs: Any) -> ToolResult:
        site_type = kwargs.get("site_type", "landing_page")
        title = kwargs.get("title", "My Website")
        description = kwargs.get("description", "")
        output_dir = kwargs.get("output_dir", "")
        sections = kwargs.get("sections", "hero,features,cta")
        color = kwargs.get("color_scheme", "#2563eb")

        if not description:
            return ToolResult(success=False, error="Description is required")

        # Create output directory
        if not output_dir:
            output_dir = os.path.join(
                tempfile.gettempdir(), "sovereign_sites", title.lower().replace(" ", "_")
            )
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        try:
            section_list = [s.strip() for s in sections.split(",")]
            html = self._generate_html(title, description, section_list, color, site_type)
            css = self._generate_css(color, section_list)
            js = self._generate_js(section_list)

            # Write files
            (Path(output_dir) / "index.html").write_text(html, encoding="utf-8")
            (Path(output_dir) / "styles.css").write_text(css, encoding="utf-8")
            (Path(output_dir) / "script.js").write_text(js, encoding="utf-8")

            return ToolResult(
                success=True,
                output=f"Website generated at {output_dir}",
                metadata={
                    "output_dir": output_dir,
                    "files": ["index.html", "styles.css", "script.js"],
                    "site_type": site_type,
                    "title": title,
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Website generation failed: {str(e)}")

    def _generate_html(
        self,
        title: str,
        description: str,
        sections: list[str],
        color: str,
        site_type: str,
    ) -> str:
        """Generate the HTML file."""
        section_html = ""

        for section in sections:
            if section == "hero":
                section_html += f"""
    <section class="hero" id="hero">
        <div class="container">
            <h1>{title}</h1>
            <p class="hero-subtitle">{description[:200]}</p>
            <a href="#contact" class="btn-primary">Get Started</a>
            <a href="#features" class="btn-secondary">Learn More</a>
        </div>
    </section>"""
            elif section == "features":
                section_html += """
    <section class="features" id="features">
        <div class="container">
            <h2>Why Choose Us</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>Fast & Reliable</h3>
                    <p>Built for speed and reliability so you can focus on what matters.</p>
                </div>
                <div class="feature-card">
                    <h3>Easy to Use</h3>
                    <p>Intuitive design that anyone can use without technical knowledge.</p>
                </div>
                <div class="feature-card">
                    <h3>24/7 Support</h3>
                    <p>Our team is always available to help you succeed.</p>
                </div>
            </div>
        </div>
    </section>"""
            elif section == "pricing":
                section_html += """
    <section class="pricing" id="pricing">
        <div class="container">
            <h2>Simple Pricing</h2>
            <div class="pricing-grid">
                <div class="pricing-card">
                    <h3>Starter</h3>
                    <div class="price">$29<span>/mo</span></div>
                    <ul><li>Core features</li><li>Email support</li><li>5 users</li></ul>
                    <a href="#contact" class="btn-primary">Start Free Trial</a>
                </div>
                <div class="pricing-card featured">
                    <h3>Professional</h3>
                    <div class="price">$79<span>/mo</span></div>
                    <ul><li>All features</li><li>Priority support</li><li>50 users</li></ul>
                    <a href="#contact" class="btn-primary">Start Free Trial</a>
                </div>
                <div class="pricing-card">
                    <h3>Enterprise</h3>
                    <div class="price">Custom</div>
                    <ul><li>Unlimited</li><li>Dedicated support</li><li>Custom integrations</li></ul>
                    <a href="#contact" class="btn-primary">Contact Sales</a>
                </div>
            </div>
        </div>
    </section>"""
            elif section in ("cta", "contact"):
                section_html += """
    <section class="contact" id="contact">
        <div class="container">
            <h2>Get In Touch</h2>
            <form class="contact-form" id="contactForm">
                <input type="text" name="name" placeholder="Your Name" required>
                <input type="email" name="email" placeholder="Your Email" required>
                <input type="tel" name="phone" placeholder="Your Phone (optional)">
                <textarea name="message" placeholder="How can we help?" rows="4"></textarea>
                <button type="submit" class="btn-primary">Send Message</button>
            </form>
            <p class="form-note">We'll get back to you within 24 hours.</p>
        </div>
    </section>"""
            elif section == "testimonials":
                section_html += """
    <section class="testimonials" id="testimonials">
        <div class="container">
            <h2>What Our Clients Say</h2>
            <div class="testimonial-grid">
                <div class="testimonial-card">
                    <p>"Absolutely transformed our business. Highly recommended!"</p>
                    <span class="author">- Happy Customer</span>
                </div>
                <div class="testimonial-card">
                    <p>"The best investment we've made this year."</p>
                    <span class="author">- Business Owner</span>
                </div>
            </div>
        </div>
    </section>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav class="navbar">
        <div class="container nav-content">
            <a href="#" class="logo">{title}</a>
            <div class="nav-links">
                {"".join(f'<a href="#{s}">{s.replace("_", " ").title()}</a>' for s in sections)}
            </div>
        </div>
    </nav>
{section_html}

    <footer>
        <div class="container">
            <p>&copy; 2026 {title}. All rights reserved.</p>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>"""

    def _generate_css(self, color: str, sections: list[str]) -> str:
        """Generate the CSS file."""
        return f"""/* Generated by Sovereign AI */
:root {{
    --primary: {color};
    --primary-dark: {color}dd;
    --bg: #ffffff;
    --bg-alt: #f8fafc;
    --text: #1e293b;
    --text-light: #64748b;
    --radius: 12px;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: var(--text);
    line-height: 1.6;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
}}

/* Navbar */
.navbar {{
    position: fixed;
    top: 0;
    width: 100%;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    z-index: 100;
    border-bottom: 1px solid #e2e8f0;
}}

.nav-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 64px;
}}

.logo {{
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--primary);
    text-decoration: none;
}}

.nav-links a {{
    margin-left: 32px;
    text-decoration: none;
    color: var(--text-light);
    font-weight: 500;
    transition: color 0.2s;
}}

.nav-links a:hover {{ color: var(--primary); }}

/* Hero */
.hero {{
    padding: 160px 0 100px;
    text-align: center;
    background: linear-gradient(135deg, var(--bg) 0%, var(--bg-alt) 100%);
}}

.hero h1 {{
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 24px;
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.hero-subtitle {{
    font-size: 1.25rem;
    color: var(--text-light);
    max-width: 600px;
    margin: 0 auto 40px;
}}

.btn-primary {{
    display: inline-block;
    background: var(--primary);
    color: white;
    padding: 14px 32px;
    border-radius: var(--radius);
    text-decoration: none;
    font-weight: 600;
    border: none;
    cursor: pointer;
    font-size: 1rem;
    transition: transform 0.2s, box-shadow 0.2s;
}}

.btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}}

.btn-secondary {{
    display: inline-block;
    color: var(--primary);
    padding: 14px 32px;
    border-radius: var(--radius);
    text-decoration: none;
    font-weight: 600;
    margin-left: 16px;
    border: 2px solid var(--primary);
    transition: background 0.2s;
}}

.btn-secondary:hover {{
    background: var(--primary);
    color: white;
}}

/* Features */
.features {{
    padding: 100px 0;
    background: var(--bg-alt);
}}

.features h2 {{
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 60px;
}}

.feature-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 32px;
}}

.feature-card {{
    background: white;
    padding: 40px;
    border-radius: var(--radius);
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    transition: transform 0.2s;
}}

.feature-card:hover {{ transform: translateY(-4px); }}
.feature-card h3 {{ margin-bottom: 12px; color: var(--primary); }}

/* Pricing */
.pricing {{
    padding: 100px 0;
}}

.pricing h2 {{
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 60px;
}}

.pricing-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 32px;
    max-width: 960px;
    margin: 0 auto;
}}

.pricing-card {{
    background: white;
    padding: 40px;
    border-radius: var(--radius);
    border: 2px solid #e2e8f0;
    text-align: center;
}}

.pricing-card.featured {{
    border-color: var(--primary);
    position: relative;
}}

.price {{
    font-size: 3rem;
    font-weight: 800;
    margin: 20px 0;
    color: var(--primary);
}}

.price span {{ font-size: 1rem; color: var(--text-light); }}

.pricing-card ul {{
    list-style: none;
    margin: 24px 0;
}}

.pricing-card ul li {{
    padding: 8px 0;
    border-bottom: 1px solid #f1f5f9;
}}

/* Contact Form */
.contact {{
    padding: 100px 0;
    background: var(--bg-alt);
}}

.contact h2 {{
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 40px;
}}

.contact-form {{
    max-width: 600px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
}}

.contact-form input,
.contact-form textarea {{
    padding: 14px 18px;
    border: 2px solid #e2e8f0;
    border-radius: var(--radius);
    font-size: 1rem;
    transition: border-color 0.2s;
}}

.contact-form input:focus,
.contact-form textarea:focus {{
    border-color: var(--primary);
    outline: none;
}}

.form-note {{
    text-align: center;
    color: var(--text-light);
    margin-top: 16px;
}}

/* Testimonials */
.testimonials {{
    padding: 100px 0;
}}

.testimonials h2 {{
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 60px;
}}

.testimonial-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 32px;
}}

.testimonial-card {{
    background: var(--bg-alt);
    padding: 32px;
    border-radius: var(--radius);
    font-style: italic;
}}

.testimonial-card .author {{
    display: block;
    margin-top: 16px;
    font-style: normal;
    font-weight: 600;
    color: var(--primary);
}}

/* Footer */
footer {{
    padding: 40px 0;
    text-align: center;
    color: var(--text-light);
    border-top: 1px solid #e2e8f0;
}}

/* Responsive */
@media (max-width: 768px) {{
    .hero h1 {{ font-size: 2.5rem; }}
    .nav-links {{ display: none; }}
    .feature-grid {{ grid-template-columns: 1fr; }}
    .pricing-grid {{ grid-template-columns: 1fr; }}
}}
"""

    def _generate_js(self, sections: list[str]) -> str:
        """Generate the JS file."""
        return """// Generated by Sovereign AI
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Form submission
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            console.log('Form submission:', data);

            // Store lead locally
            const leads = JSON.parse(localStorage.getItem('sovereign_leads') || '[]');
            leads.push({...data, timestamp: new Date().toISOString()});
            localStorage.setItem('sovereign_leads', JSON.stringify(leads));

            // Show success
            form.innerHTML = '<div style="text-align:center;padding:40px;"><h3 style="color:var(--primary)">Thank you!</h3><p>We\\'ll be in touch soon.</p></div>';
        });
    }

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    });

    // Animate on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-card, .pricing-card, .testimonial-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s, transform 0.6s';
        observer.observe(el);
    });
});
"""


class WebsiteDeployTool(Tool):
    """Deploy a website directory to the web."""

    name = "website_deploy"
    description = (
        "Deploy a website directory to make it live on the internet. "
        "Supports deploying to Netlify (free tier, no API key needed for "
        "manual deploys) or a simple Python HTTP server for local testing."
    )
    parameters = [
        ToolParameter(
            name="site_dir",
            description="Path to the directory containing the website files",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="method",
            description="Deploy method: netlify_drop, local_server, zip",
            param_type="string",
            required=False,
            default="zip",
            enum=["netlify_drop", "local_server", "zip"],
        ),
        ToolParameter(
            name="port",
            description="Port for local server (default 8080)",
            param_type="integer",
            required=False,
            default=8080,
        ),
    ]
    category = "builder"
    risk_level = 0.3

    async def execute(self, **kwargs: Any) -> ToolResult:
        site_dir = kwargs.get("site_dir", "")
        method = kwargs.get("method", "zip")
        port = kwargs.get("port", 8080)

        if not site_dir:
            return ToolResult(success=False, error="site_dir is required")

        site_path = Path(site_dir)
        if not site_path.exists() or not site_path.is_dir():
            return ToolResult(success=False, error=f"Directory not found: {site_dir}")

        if not (site_path / "index.html").exists():
            return ToolResult(success=False, error="No index.html found in site directory")

        try:
            if method == "zip":
                return await self._deploy_zip(site_path)
            elif method == "local_server":
                return await self._deploy_local(site_path, port)
            elif method == "netlify_drop":
                return await self._deploy_netlify(site_path)
            else:
                return ToolResult(success=False, error=f"Unknown method: {method}")
        except Exception as e:
            return ToolResult(success=False, error=f"Deploy failed: {str(e)}")

    async def _deploy_zip(self, site_path: Path) -> ToolResult:
        """Create a deployable zip archive."""
        zip_path = site_path.parent / f"{site_path.name}.zip"
        shutil.make_archive(str(zip_path.with_suffix("")), "zip", str(site_path))
        return ToolResult(
            success=True,
            output=f"Site packaged as {zip_path}. Ready for deployment.",
            metadata={"zip_path": str(zip_path), "method": "zip"},
        )

    async def _deploy_local(self, site_path: Path, port: int) -> ToolResult:
        """Start a local HTTP server."""
        import asyncio

        process = await asyncio.create_subprocess_exec(
            "python3", "-m", "http.server", str(port),
            cwd=str(site_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return ToolResult(
            success=True,
            output=f"Local server running at http://localhost:{port}",
            metadata={
                "url": f"http://localhost:{port}",
                "pid": process.pid,
                "method": "local_server",
            },
        )

    async def _deploy_netlify(self, site_path: Path) -> ToolResult:
        """Deploy to Netlify using their API."""
        netlify_token = os.environ.get("NETLIFY_TOKEN", "")
        if not netlify_token:
            # Create a zip and provide instructions
            zip_result = await self._deploy_zip(site_path)
            return ToolResult(
                success=True,
                output=(
                    f"Site zipped at {zip_result.metadata.get('zip_path')}. "
                    "To deploy to Netlify:\n"
                    "1. Go to https://app.netlify.com/drop\n"
                    "2. Drag and drop the site folder\n"
                    "Or set NETLIFY_TOKEN for automated deploys."
                ),
                metadata={"method": "netlify_manual", **zip_result.metadata},
            )

        # Automated Netlify deploy
        try:
            zip_path = site_path.parent / f"{site_path.name}_deploy.zip"
            shutil.make_archive(str(zip_path.with_suffix("")), "zip", str(site_path))

            async with httpx.AsyncClient() as client:
                # Create a new site
                response = await client.post(
                    "https://api.netlify.com/api/v1/sites",
                    headers={"Authorization": f"Bearer {netlify_token}"},
                    json={"name": site_path.name},
                )

                if response.status_code in (200, 201):
                    site_data = response.json()
                    site_id = site_data["id"]
                    site_url = site_data.get("ssl_url", site_data.get("url", ""))

                    # Deploy the zip
                    with open(zip_path, "rb") as f:
                        deploy_response = await client.post(
                            f"https://api.netlify.com/api/v1/sites/{site_id}/deploys",
                            headers={
                                "Authorization": f"Bearer {netlify_token}",
                                "Content-Type": "application/zip",
                            },
                            content=f.read(),
                        )

                    if deploy_response.status_code in (200, 201):
                        deploy_data = deploy_response.json()
                        return ToolResult(
                            success=True,
                            output=f"Site deployed to {site_url}",
                            metadata={
                                "url": site_url,
                                "site_id": site_id,
                                "deploy_id": deploy_data.get("id", ""),
                                "method": "netlify",
                            },
                        )

                return ToolResult(
                    success=False,
                    error=f"Netlify deploy failed: {response.text}",
                )
        except Exception as e:
            return ToolResult(success=False, error=f"Netlify deploy error: {str(e)}")
