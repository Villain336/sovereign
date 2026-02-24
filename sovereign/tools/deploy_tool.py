"""Deploy Pipeline Tool - Generate, Preview, and Deploy sites.

Supports deploying static sites to Netlify and Vercel,
and provides a local preview server for testing.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import httpx

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class DeployTool(Tool):
    """Deploy a static site to a hosting provider or start a local preview."""

    name = "deploy_site"
    description = (
        "Deploy a static site directory to Netlify or Vercel, or start a local "
        "preview server. Use this after generating a site with the design engine "
        "or site generator to make it live on the internet."
    )
    parameters = [
        ToolParameter(
            name="site_dir",
            description="Path to the site directory containing index.html",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="provider",
            description="Deployment provider: netlify, vercel, local",
            param_type="string",
            required=False,
            default="netlify",
            enum=["netlify", "vercel", "local"],
        ),
        ToolParameter(
            name="site_name",
            description="Site name for the deployment (used in URL slug)",
            param_type="string",
            required=False,
            default="sovereign-site",
        ),
        ToolParameter(
            name="api_token",
            description="API token for the hosting provider (Netlify or Vercel)",
            param_type="string",
            required=False,
        ),
    ]
    category = "deploy"
    risk_level = 0.4

    async def execute(self, **kwargs: Any) -> ToolResult:
        site_dir = kwargs.get("site_dir", "")
        provider = kwargs.get("provider", "netlify")
        site_name = kwargs.get("site_name", "sovereign-site")
        api_token = kwargs.get("api_token", "")

        if not site_dir:
            return ToolResult(success=False, error="site_dir is required")

        site_path = Path(site_dir)
        if not site_path.exists():
            return ToolResult(success=False, error=f"Directory not found: {site_dir}")

        index_file = site_path / "index.html"
        if not index_file.exists():
            return ToolResult(success=False, error="No index.html found in site directory")

        try:
            if provider == "netlify":
                return await self._deploy_netlify(site_path, site_name, api_token)
            elif provider == "vercel":
                return await self._deploy_vercel(site_path, site_name, api_token)
            elif provider == "local":
                return await self._start_local_server(site_path)
            else:
                return ToolResult(success=False, error=f"Unknown provider: {provider}")
        except Exception as e:
            return ToolResult(success=False, error=f"Deploy failed: {e!s}")

    async def _deploy_netlify(
        self, site_dir: Path, site_name: str, api_token: str,
    ) -> ToolResult:
        """Deploy to Netlify using their API."""
        token = api_token or os.environ.get("NETLIFY_TOKEN", "")
        if not token:
            return ToolResult(
                success=False,
                error=(
                    "Netlify API token required. Set NETLIFY_TOKEN env var "
                    "or pass api_token parameter."
                ),
            )

        # Create a zip of the site
        zip_path = os.path.join(tempfile.gettempdir(), "sovereign_deploy.zip")
        shutil.make_archive(zip_path.replace(".zip", ""), "zip", str(site_dir))

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/zip",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Create new site or deploy to existing
            with open(zip_path, "rb") as f:
                response = await client.post(
                    "https://api.netlify.com/api/v1/sites",
                    headers=headers,
                    content=f.read(),
                )

            if response.status_code in (200, 201):
                data = response.json()
                url = data.get("ssl_url") or data.get("url", "")
                site_id = data.get("id", "")
                return ToolResult(
                    success=True,
                    output=f"Deployed to Netlify: {url}",
                    metadata={
                        "url": url,
                        "site_id": site_id,
                        "provider": "netlify",
                    },
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Netlify deploy failed ({response.status_code}): {response.text[:300]}",
                )

    async def _deploy_vercel(
        self, site_dir: Path, site_name: str, api_token: str,
    ) -> ToolResult:
        """Deploy to Vercel using their API."""
        token = api_token or os.environ.get("VERCEL_TOKEN", "")
        if not token:
            return ToolResult(
                success=False,
                error=(
                    "Vercel API token required. Set VERCEL_TOKEN env var "
                    "or pass api_token parameter."
                ),
            )

        # Build file list
        files = []
        for path in site_dir.rglob("*"):
            if path.is_file():
                rel = str(path.relative_to(site_dir))
                content = path.read_text(encoding="utf-8", errors="replace")
                files.append({"file": rel, "data": content})

        payload = {
            "name": site_name,
            "files": files,
            "projectSettings": {"framework": None},
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.vercel.com/v13/deployments",
                headers=headers,
                json=payload,
            )

            if response.status_code in (200, 201):
                data = response.json()
                url = f"https://{data.get('url', '')}"
                return ToolResult(
                    success=True,
                    output=f"Deployed to Vercel: {url}",
                    metadata={
                        "url": url,
                        "deployment_id": data.get("id", ""),
                        "provider": "vercel",
                    },
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Vercel deploy failed ({response.status_code}): {response.text[:300]}",
                )

    async def _start_local_server(self, site_dir: Path) -> ToolResult:
        """Start a local HTTP server for preview."""
        port = 8765
        try:
            # Start Python's built-in HTTP server in the background
            proc = subprocess.Popen(
                ["python3", "-m", "http.server", str(port)],
                cwd=str(site_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return ToolResult(
                success=True,
                output=f"Local preview running at http://localhost:{port}",
                metadata={
                    "url": f"http://localhost:{port}",
                    "pid": proc.pid,
                    "provider": "local",
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Local server failed: {e!s}")


class ScreenshotTool(Tool):
    """Take a screenshot of a URL or local HTML file."""

    name = "screenshot"
    description = (
        "Take a screenshot of a website URL or local HTML file for preview. "
        "Uses headless Selenium/ChromeDriver. Returns path to the screenshot image."
    )
    parameters = [
        ToolParameter(
            name="url",
            description="URL to screenshot (can be http://, https://, or file://)",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="output_path",
            description="Path to save screenshot (auto-generated if empty)",
            param_type="string",
            required=False,
        ),
        ToolParameter(
            name="width",
            description="Viewport width in pixels",
            param_type="string",
            required=False,
            default="1440",
        ),
        ToolParameter(
            name="height",
            description="Viewport height in pixels",
            param_type="string",
            required=False,
            default="900",
        ),
        ToolParameter(
            name="full_page",
            description="Capture full page scroll (true/false)",
            param_type="string",
            required=False,
            default="false",
        ),
    ]
    category = "design"
    risk_level = 0.1

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", "")
        output_path = kwargs.get("output_path", "")
        width = int(kwargs.get("width", "1440"))
        height = int(kwargs.get("height", "900"))

        if not url:
            return ToolResult(success=False, error="URL is required")

        # If it's a local file path, convert to file:// URL
        if url.startswith("/") or url.startswith("./"):
            url = f"file://{os.path.abspath(url)}"

        if not output_path:
            output_path = os.path.join(
                tempfile.gettempdir(),
                "sovereign_screenshots",
                f"screenshot_{os.getpid()}.png",
            )
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--window-size={width},{height}")
            options.add_argument("--disable-gpu")
            options.add_argument("--hide-scrollbars")

            driver = webdriver.Chrome(options=options)
            driver.set_window_size(width, height)

            try:
                driver.get(url)
                # Wait for page load
                driver.implicitly_wait(3)
                driver.save_screenshot(output_path)
            finally:
                driver.quit()

            return ToolResult(
                success=True,
                output=f"Screenshot saved to {output_path}",
                metadata={
                    "output_path": output_path,
                    "url": url,
                    "width": width,
                    "height": height,
                },
            )

        except ImportError:
            return ToolResult(
                success=False,
                error=(
                    "Selenium not installed. Run: pip install selenium\n"
                    "Also needs Chrome/Chromium and chromedriver."
                ),
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Screenshot failed: {e!s}")
