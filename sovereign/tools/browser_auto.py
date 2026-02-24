"""Browser Automation Tool - Headless Selenium-based web interaction.

Enables the agent to autonomously browse the web, fill forms,
click buttons, extract data, and interact with web applications
using headless Chrome via Selenium.
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Any

from sovereign.tools.base import Tool, ToolParameter, ToolResult


def _get_driver() -> Any:
    """Create a headless Chrome Selenium WebDriver."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,900")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


class BrowserNavigateTool(Tool):
    """Navigate to a URL and extract page content."""

    name = "browser_navigate"
    description = (
        "Navigate to a URL using a headless browser, wait for the page to load, "
        "and extract text content. Unlike the basic browser tool, this renders "
        "JavaScript and can interact with SPAs and dynamic pages."
    )
    parameters = [
        ToolParameter(
            name="url",
            description="URL to navigate to",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="wait_seconds",
            description="Seconds to wait for page to load (default 3)",
            param_type="string",
            required=False,
            default="3",
        ),
        ToolParameter(
            name="extract",
            description="What to extract: text, html, links, screenshot, all",
            param_type="string",
            required=False,
            default="text",
            enum=["text", "html", "links", "screenshot", "all"],
        ),
    ]
    category = "browser"
    risk_level = 0.3

    async def execute(self, **kwargs: Any) -> ToolResult:
        url = kwargs.get("url", "")
        wait_secs = int(kwargs.get("wait_seconds", "3"))
        extract = kwargs.get("extract", "text")

        if not url:
            return ToolResult(success=False, error="URL is required")

        try:
            driver = _get_driver()
        except ImportError:
            return ToolResult(
                success=False,
                error="Selenium not installed. Run: pip install selenium",
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Browser init failed: {e!s}")

        try:
            driver.get(url)
            time.sleep(wait_secs)

            page_title = driver.title
            current_url = driver.current_url

            output_parts: list[str] = []
            metadata: dict[str, Any] = {
                "url": current_url,
                "title": page_title,
            }

            if extract in ("text", "all"):
                text = driver.find_element("tag name", "body").text
                output_parts.append(f"=== TEXT ===\n{text[:10000]}")

            if extract in ("html", "all"):
                html = driver.page_source[:20000]
                output_parts.append(f"=== HTML (truncated) ===\n{html}")

            if extract in ("links", "all"):
                links = []
                elements = driver.find_elements("tag name", "a")
                for elem in elements[:100]:
                    href = elem.get_attribute("href") or ""
                    text = elem.text.strip()
                    if href and not href.startswith("javascript:"):
                        links.append(f"{text}: {href}")
                output_parts.append("=== LINKS ===\n" + "\n".join(links))
                metadata["link_count"] = len(links)

            if extract in ("screenshot", "all"):
                screenshot_dir = os.path.join(
                    tempfile.gettempdir(), "sovereign_screenshots",
                )
                Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
                screenshot_path = os.path.join(
                    screenshot_dir, f"nav_{int(time.time())}.png",
                )
                driver.save_screenshot(screenshot_path)
                output_parts.append(f"=== SCREENSHOT ===\n{screenshot_path}")
                metadata["screenshot"] = screenshot_path

            return ToolResult(
                success=True,
                output="\n\n".join(output_parts) if output_parts else f"Page loaded: {page_title}",
                metadata=metadata,
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Navigation failed: {e!s}")
        finally:
            driver.quit()


class BrowserInteractTool(Tool):
    """Interact with web page elements (click, type, select)."""

    name = "browser_interact"
    description = (
        "Interact with elements on a web page: click buttons, fill forms, "
        "select options. First navigate to a page with browser_navigate, then "
        "use this tool to interact with elements by CSS selector or XPath."
    )
    parameters = [
        ToolParameter(
            name="url",
            description="URL of the page to interact with",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="actions",
            description=(
                "JSON array of actions, e.g. "
                '[{"action":"type","selector":"input[name=email]","value":"test@example.com"},'
                '{"action":"click","selector":"button[type=submit]"}]'
                '\nSupported actions: click, type, select, scroll, wait'
            ),
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="wait_after",
            description="Seconds to wait after all actions (default 2)",
            param_type="string",
            required=False,
            default="2",
        ),
        ToolParameter(
            name="screenshot_after",
            description="Take a screenshot after actions (true/false)",
            param_type="string",
            required=False,
            default="true",
        ),
    ]
    category = "browser"
    risk_level = 0.4

    async def execute(self, **kwargs: Any) -> ToolResult:
        import json as json_mod

        url = kwargs.get("url", "")
        actions_json = kwargs.get("actions", "[]")
        wait_after = int(kwargs.get("wait_after", "2"))
        screenshot_after = kwargs.get("screenshot_after", "true").lower() == "true"

        if not url:
            return ToolResult(success=False, error="URL is required")

        try:
            actions = json_mod.loads(actions_json) if isinstance(actions_json, str) else actions_json
        except json_mod.JSONDecodeError:
            return ToolResult(success=False, error="Invalid actions JSON")

        try:
            driver = _get_driver()
        except ImportError:
            return ToolResult(
                success=False,
                error="Selenium not installed. Run: pip install selenium",
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Browser init failed: {e!s}")

        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import (
                expected_conditions as ec,
            )
            from selenium.webdriver.support.ui import Select, WebDriverWait

            driver.get(url)
            time.sleep(2)

            results: list[str] = []

            for i, action_def in enumerate(actions):
                action = action_def.get("action", "")
                selector = action_def.get("selector", "")
                value = action_def.get("value", "")

                # Determine selector type
                by = By.CSS_SELECTOR
                if selector.startswith("//"):
                    by = By.XPATH

                try:
                    if action == "click":
                        element = WebDriverWait(driver, 10).until(
                            ec.element_to_be_clickable((by, selector)),
                        )
                        element.click()
                        results.append(f"Action {i + 1}: Clicked {selector}")

                    elif action == "type":
                        element = WebDriverWait(driver, 10).until(
                            ec.presence_of_element_located((by, selector)),
                        )
                        element.clear()
                        element.send_keys(value)
                        results.append(f"Action {i + 1}: Typed into {selector}")

                    elif action == "select":
                        element = WebDriverWait(driver, 10).until(
                            ec.presence_of_element_located((by, selector)),
                        )
                        select = Select(element)
                        select.select_by_visible_text(value)
                        results.append(f"Action {i + 1}: Selected '{value}' in {selector}")

                    elif action == "scroll":
                        scroll_amount = int(value) if value else 500
                        driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                        results.append(f"Action {i + 1}: Scrolled {scroll_amount}px")

                    elif action == "wait":
                        wait_time = float(value) if value else 1.0
                        time.sleep(wait_time)
                        results.append(f"Action {i + 1}: Waited {wait_time}s")

                    else:
                        results.append(f"Action {i + 1}: Unknown action '{action}'")

                except Exception as e:
                    results.append(f"Action {i + 1}: FAILED - {e!s}")

            # Wait after actions
            time.sleep(wait_after)

            metadata: dict[str, Any] = {
                "url": driver.current_url,
                "title": driver.title,
                "actions_completed": len(results),
            }

            # Screenshot if requested
            if screenshot_after:
                screenshot_dir = os.path.join(
                    tempfile.gettempdir(), "sovereign_screenshots",
                )
                Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
                screenshot_path = os.path.join(
                    screenshot_dir, f"interact_{int(time.time())}.png",
                )
                driver.save_screenshot(screenshot_path)
                results.append(f"Screenshot saved: {screenshot_path}")
                metadata["screenshot"] = screenshot_path

            # Get page text after interactions
            page_text = driver.find_element("tag name", "body").text[:3000]
            results.append(f"\n=== PAGE STATE ===\n{page_text}")

            return ToolResult(
                success=True,
                output="\n".join(results),
                metadata=metadata,
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Interaction failed: {e!s}")
        finally:
            driver.quit()


class BrowserScrapeTool(Tool):
    """Scrape structured data from a web page."""

    name = "browser_scrape"
    description = (
        "Scrape structured data from a web page using CSS selectors. "
        "Renders JavaScript before extracting, so works with SPAs and "
        "dynamic content. Returns data as JSON."
    )
    parameters = [
        ToolParameter(
            name="url",
            description="URL to scrape",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="selectors",
            description=(
                "JSON object mapping field names to CSS selectors, e.g. "
                '{"title":"h1","prices":".price","links":"a.product-link"}'
            ),
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="multiple",
            description="Extract multiple matches per selector (true/false)",
            param_type="string",
            required=False,
            default="false",
        ),
    ]
    category = "browser"
    risk_level = 0.2

    async def execute(self, **kwargs: Any) -> ToolResult:
        import json as json_mod

        url = kwargs.get("url", "")
        selectors_json = kwargs.get("selectors", "{}")
        multiple = kwargs.get("multiple", "false").lower() == "true"

        if not url:
            return ToolResult(success=False, error="URL is required")

        try:
            selectors = json_mod.loads(selectors_json) if isinstance(selectors_json, str) else selectors_json
        except json_mod.JSONDecodeError:
            return ToolResult(success=False, error="Invalid selectors JSON")

        try:
            driver = _get_driver()
        except ImportError:
            return ToolResult(
                success=False,
                error="Selenium not installed. Run: pip install selenium",
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Browser init failed: {e!s}")

        try:
            driver.get(url)
            time.sleep(3)

            data: dict[str, Any] = {}

            for field_name, selector in selectors.items():
                try:
                    if multiple:
                        elements = driver.find_elements("css selector", selector)
                        data[field_name] = [
                            el.text.strip() for el in elements if el.text.strip()
                        ]
                    else:
                        element = driver.find_element("css selector", selector)
                        data[field_name] = element.text.strip()
                except Exception:
                    data[field_name] = None if not multiple else []

            return ToolResult(
                success=True,
                output=json_mod.dumps(data, indent=2),
                metadata={
                    "url": url,
                    "fields_extracted": len(data),
                    "data": data,
                },
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Scrape failed: {e!s}")
        finally:
            driver.quit()
