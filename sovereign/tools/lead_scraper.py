"""Lead Scraper Tool - find and qualify business leads from the web.

Enables the agent to:
- Search for potential leads by industry, location, or keywords
- Extract contact information from websites
- Score and qualify leads based on criteria
- Build prospect lists for outreach
"""

from __future__ import annotations

import re
from typing import Any

import httpx

from sovereign.tools.base import Tool, ToolParameter, ToolResult


class LeadScraperTool(Tool):
    """Find and extract business leads from the web."""

    name = "lead_scrape"
    description = (
        "Search the web and scrape business leads including company names, "
        "emails, phone numbers, and website URLs. Use this for building "
        "prospect lists, finding potential customers, and market research."
    )
    parameters = [
        ToolParameter(
            name="query",
            description="Search query to find leads (e.g., 'SaaS companies in Austin TX')",
            param_type="string",
            required=True,
        ),
        ToolParameter(
            name="num_results",
            description="Number of leads to find (default 10, max 50)",
            param_type="integer",
            required=False,
            default=10,
        ),
        ToolParameter(
            name="extract_emails",
            description="Whether to visit pages and extract emails (default: true)",
            param_type="boolean",
            required=False,
            default=True,
        ),
        ToolParameter(
            name="extract_phones",
            description="Whether to extract phone numbers (default: true)",
            param_type="boolean",
            required=False,
            default=True,
        ),
    ]
    category = "business"
    risk_level = 0.3

    async def execute(self, **kwargs: Any) -> ToolResult:
        query = kwargs.get("query", "")
        num_results = min(kwargs.get("num_results", 10), 50)
        extract_emails = kwargs.get("extract_emails", True)
        extract_phones = kwargs.get("extract_phones", True)

        if not query:
            return ToolResult(success=False, error="Query is required")

        try:
            # Step 1: Search DuckDuckGo for business listings
            search_results = await self._search(query, num_results)

            if not search_results:
                return ToolResult(
                    success=True,
                    output="No leads found for this query.",
                    metadata={"query": query, "lead_count": 0},
                )

            # Step 2: Extract contact info from each result
            leads: list[dict[str, Any]] = []
            for result in search_results[:num_results]:
                lead: dict[str, Any] = {
                    "company": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("snippet", ""),
                    "emails": [],
                    "phones": [],
                    "score": 0.0,
                }

                # Extract contact info from the page
                if (extract_emails or extract_phones) and result.get("url"):
                    contacts = await self._extract_contacts(
                        result["url"], extract_emails, extract_phones
                    )
                    lead["emails"] = contacts.get("emails", [])
                    lead["phones"] = contacts.get("phones", [])

                # Score the lead
                lead["score"] = self._score_lead(lead, query)
                leads.append(lead)

            # Sort by score
            leads.sort(key=lambda x: x["score"], reverse=True)

            # Format output
            output_lines: list[str] = [f"Found {len(leads)} leads for: {query}\n"]
            for i, lead in enumerate(leads, 1):
                output_lines.append(f"--- Lead #{i} (Score: {lead['score']:.1f}/10) ---")
                output_lines.append(f"  Company: {lead['company']}")
                output_lines.append(f"  URL: {lead['url']}")
                if lead["emails"]:
                    output_lines.append(f"  Emails: {', '.join(lead['emails'][:3])}")
                if lead["phones"]:
                    output_lines.append(f"  Phones: {', '.join(lead['phones'][:2])}")
                if lead["description"]:
                    output_lines.append(f"  About: {lead['description'][:150]}")
                output_lines.append("")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
                metadata={
                    "query": query,
                    "lead_count": len(leads),
                    "with_emails": sum(1 for ld in leads if ld["emails"]),
                    "with_phones": sum(1 for ld in leads if ld["phones"]),
                    "leads": leads,
                },
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Lead scraping failed: {str(e)}")

    async def _search(self, query: str, num_results: int) -> list[dict[str, str]]:
        """Search DuckDuckGo for business results."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (compatible; Sovereign/0.1)"},
            )

        results: list[dict[str, str]] = []
        text = response.text

        # Extract result links and snippets
        links = re.findall(
            r'class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', text
        )
        snippets = re.findall(
            r'class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL
        )

        for i, (url, title) in enumerate(links[:num_results]):
            snippet = snippets[i] if i < len(snippets) else ""
            snippet = re.sub(r"<[^>]+>", "", snippet).strip()

            # Extract actual URL from DuckDuckGo redirect
            actual_url = url
            if "uddg=" in url:
                from urllib.parse import parse_qs, urlparse

                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                if "uddg" in params:
                    actual_url = params["uddg"][0]

            results.append({
                "title": title.strip(),
                "url": actual_url,
                "snippet": snippet,
            })

        return results

    async def _extract_contacts(
        self,
        url: str,
        extract_emails: bool,
        extract_phones: bool,
    ) -> dict[str, list[str]]:
        """Extract contact information from a webpage."""
        contacts: dict[str, list[str]] = {"emails": [], "phones": []}

        try:
            async with httpx.AsyncClient(
                timeout=10.0,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (compatible; Sovereign/0.1)"},
            ) as client:
                response = await client.get(url)
                html = response.text

            if extract_emails:
                # Find email addresses
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = list(set(re.findall(email_pattern, html)))
                # Filter out common non-person emails and image files
                filtered_emails = [
                    e for e in emails
                    if not any(
                        x in e.lower()
                        for x in [".png", ".jpg", ".gif", ".svg", "example.com",
                                  "sentry.io", "webpack", "wixpress"]
                    )
                ]
                contacts["emails"] = filtered_emails[:5]

            if extract_phones:
                # Find phone numbers (US format)
                phone_patterns = [
                    r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
                    r'\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}',
                ]
                phones: list[str] = []
                for pattern in phone_patterns:
                    found = re.findall(pattern, html)
                    phones.extend(found)
                contacts["phones"] = list(set(phones))[:3]

        except Exception:
            pass  # Silently fail on individual pages

        return contacts

    def _score_lead(self, lead: dict[str, Any], query: str) -> float:
        """Score a lead from 0-10 based on quality signals."""
        score = 5.0  # Base score

        # Has contact info
        if lead["emails"]:
            score += 2.0
        if lead["phones"]:
            score += 1.0

        # Has a real website (not a directory listing)
        url = lead.get("url", "")
        if url and not any(
            d in url for d in ["yelp.com", "yellowpages", "bbb.org", "facebook.com"]
        ):
            score += 0.5

        # Description relevance to query
        desc = (lead.get("description", "") + " " + lead.get("company", "")).lower()
        query_words = query.lower().split()
        matching_words = sum(1 for w in query_words if w in desc)
        score += min(matching_words * 0.3, 1.5)

        return min(score, 10.0)
