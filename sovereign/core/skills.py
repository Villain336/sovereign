"""Portable Skill System - community-extensible YAML skill definitions.

Like OpenClaw's portable skill format, skills are simple YAML files
that define reusable workflows. Anyone can create and share skills
by dropping a .yaml file into ~/.sovereign/skills/

Skill format:
    name: research_competitor
    description: Research a competitor company
    version: "1.0"
    tags: [research, business]
    inputs:
      - name: company_name
        type: string
        required: true
    steps:
      - tool: web_search
        params:
          query: "{company_name} company overview revenue"
      - tool: llm_reason
        params:
          prompt: "Summarize findings about {company_name}"
    output: "Competitor analysis for {company_name}"
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from sovereign.config import SovereignConfig


class SkillInput:
    """An input parameter for a skill."""

    def __init__(
        self,
        name: str,
        input_type: str = "string",
        description: str = "",
        required: bool = True,
        default: Any = None,
    ) -> None:
        self.name = name
        self.input_type = input_type
        self.description = description
        self.required = required
        self.default = default


class SkillStep:
    """A single step in a skill workflow."""

    def __init__(
        self,
        tool: str,
        params: dict[str, Any] | None = None,
        description: str = "",
        on_failure: str = "stop",
        save_as: str = "",
    ) -> None:
        self.tool = tool
        self.params = params or {}
        self.description = description
        self.on_failure = on_failure  # stop, continue, retry
        self.save_as = save_as  # Variable name to store result


class Skill:
    """A portable, reusable workflow definition."""

    def __init__(
        self,
        name: str,
        description: str = "",
        version: str = "1.0",
        author: str = "",
        tags: list[str] | None = None,
        inputs: list[SkillInput] | None = None,
        steps: list[SkillStep] | None = None,
        output_template: str = "",
        source_file: str = "",
    ) -> None:
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.tags = tags or []
        self.inputs = inputs or []
        self.steps = steps or []
        self.output_template = output_template
        self.source_file = source_file


class SkillRegistry:
    """Manages loading, discovering, and executing skills.

    Skills are loaded from:
    1. Built-in skills (bundled with Sovereign)
    2. User skills (~/.sovereign/skills/)
    3. Community skills (downloaded/shared)
    """

    def __init__(self, config: SovereignConfig | None = None) -> None:
        self._skills: dict[str, Skill] = {}
        self._skills_dir = os.path.join(
            os.path.expanduser("~"), ".sovereign", "skills",
        )
        if config:
            self._skills_dir = os.path.join(config.data_dir, "skills")
        Path(self._skills_dir).mkdir(parents=True, exist_ok=True)

        # Load built-in skills
        self._register_builtins()
        # Load user skills from disk
        self.load_from_directory(self._skills_dir)

    def _register_builtins(self) -> None:
        """Register built-in skills."""
        builtins = [
            Skill(
                name="research_company",
                description="Research a company and produce a summary report",
                tags=["research", "business"],
                inputs=[
                    SkillInput(name="company_name", description="Company to research"),
                ],
                steps=[
                    SkillStep(
                        tool="web_search",
                        params={"query": "{company_name} company overview products revenue"},
                        description="Search for company info",
                        save_as="search_results",
                    ),
                    SkillStep(
                        tool="web_search",
                        params={"query": "{company_name} reviews customer feedback"},
                        description="Search for reviews",
                        save_as="reviews",
                    ),
                    SkillStep(
                        tool="llm_reason",
                        params={
                            "prompt": (
                                "Based on these search results, create a comprehensive "
                                "company report for {company_name}:\n\n"
                                "Search: {search_results}\n\nReviews: {reviews}"
                            ),
                        },
                        description="Synthesize research into report",
                        save_as="report",
                    ),
                ],
                output_template="## Company Report: {company_name}\n\n{report}",
            ),
            Skill(
                name="generate_leads",
                description="Find potential leads in a given industry",
                tags=["leads", "sales", "business"],
                inputs=[
                    SkillInput(name="industry", description="Target industry"),
                    SkillInput(name="count", input_type="integer", default=10),
                ],
                steps=[
                    SkillStep(
                        tool="lead_scraper",
                        params={
                            "query": "{industry} companies",
                            "max_results": "{count}",
                        },
                        description="Scrape leads from web",
                        save_as="leads",
                    ),
                    SkillStep(
                        tool="llm_reason",
                        params={
                            "prompt": (
                                "Rank these leads by potential value and add "
                                "a brief note for each:\n\n{leads}"
                            ),
                        },
                        description="Rank and annotate leads",
                        save_as="ranked_leads",
                    ),
                ],
                output_template="## Leads in {industry}\n\n{ranked_leads}",
            ),
            Skill(
                name="build_landing_page",
                description="Generate and deploy a landing page for a business",
                tags=["design", "website", "business"],
                inputs=[
                    SkillInput(name="business_name", description="Business name"),
                    SkillInput(name="description", description="What the business does"),
                    SkillInput(name="palette", default="midnight"),
                ],
                steps=[
                    SkillStep(
                        tool="ai_design",
                        params={
                            "brand_name": "{business_name}",
                            "page_type": "landing",
                            "palette": "{palette}",
                            "description": "{description}",
                        },
                        description="Generate landing page",
                        save_as="site_dir",
                    ),
                    SkillStep(
                        tool="screenshot",
                        params={"url": "{site_dir}/index.html"},
                        description="Take preview screenshot",
                        save_as="screenshot",
                        on_failure="continue",
                    ),
                ],
                output_template=(
                    "Landing page generated for {business_name} at {site_dir}"
                ),
            ),
            Skill(
                name="daily_report",
                description="Generate a daily business status report",
                tags=["reporting", "business", "daily"],
                inputs=[],
                steps=[
                    SkillStep(
                        tool="crm_list_leads",
                        params={"stage": "all"},
                        description="Get CRM pipeline status",
                        save_as="pipeline",
                        on_failure="continue",
                    ),
                    SkillStep(
                        tool="llm_reason",
                        params={
                            "prompt": (
                                "Generate a concise daily business report based on:\n"
                                "Pipeline: {pipeline}\n\n"
                                "Include: metrics summary, key activities, "
                                "recommendations for today."
                            ),
                        },
                        description="Generate daily report",
                        save_as="report",
                    ),
                ],
                output_template="## Daily Report\n\n{report}",
            ),
        ]

        for skill in builtins:
            self._skills[skill.name] = skill

    def load_from_directory(self, directory: str) -> int:
        """Load YAML skill files from a directory. Returns count loaded."""
        loaded = 0
        if not os.path.exists(directory):
            return 0

        for fname in os.listdir(directory):
            if not fname.endswith((".yaml", ".yml")):
                continue
            filepath = os.path.join(directory, fname)
            try:
                skill = self._load_yaml_skill(filepath)
                if skill:
                    self._skills[skill.name] = skill
                    loaded += 1
            except Exception:
                continue
        return loaded

    def _load_yaml_skill(self, filepath: str) -> Skill | None:
        """Load a single YAML skill file."""
        try:
            import yaml
        except ImportError:
            # Fall back to basic parsing if PyYAML not available
            return self._load_yaml_fallback(filepath)

        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict) or "name" not in data:
            return None

        inputs = []
        for inp in data.get("inputs", []):
            if isinstance(inp, dict):
                inputs.append(SkillInput(
                    name=inp.get("name", ""),
                    input_type=inp.get("type", "string"),
                    description=inp.get("description", ""),
                    required=inp.get("required", True),
                    default=inp.get("default"),
                ))

        steps = []
        for step in data.get("steps", []):
            if isinstance(step, dict):
                steps.append(SkillStep(
                    tool=step.get("tool", ""),
                    params=step.get("params", {}),
                    description=step.get("description", ""),
                    on_failure=step.get("on_failure", "stop"),
                    save_as=step.get("save_as", ""),
                ))

        return Skill(
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            inputs=inputs,
            steps=steps,
            output_template=data.get("output", ""),
            source_file=filepath,
        )

    @staticmethod
    def _load_yaml_fallback(filepath: str) -> Skill | None:
        """Basic YAML parsing without PyYAML dependency."""
        with open(filepath, encoding="utf-8") as f:
            text = f.read()

        # Extract name at minimum
        name = ""
        description = ""
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip("'\"")
            elif line.startswith("description:"):
                description = line.split(":", 1)[1].strip().strip("'\"")

        if not name:
            return None

        return Skill(
            name=name,
            description=description,
            source_file=filepath,
        )

    def register(self, skill: Skill) -> None:
        """Register a skill."""
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self._skills.get(name)

    def list_skills(
        self, tags: list[str] | None = None,
    ) -> list[Skill]:
        """List all skills, optionally filtered by tags."""
        skills = list(self._skills.values())
        if tags:
            tag_set = set(tags)
            skills = [s for s in skills if tag_set.intersection(s.tags)]
        return sorted(skills, key=lambda s: s.name)

    def search(self, query: str) -> list[Skill]:
        """Search skills by name, description, or tags."""
        query_lower = query.lower()
        results: list[tuple[float, Skill]] = []

        for skill in self._skills.values():
            score = 0.0
            if query_lower in skill.name.lower():
                score += 1.0
            if query_lower in skill.description.lower():
                score += 0.5
            for tag in skill.tags:
                if query_lower in tag.lower():
                    score += 0.3
            if score > 0:
                results.append((score, skill))

        results.sort(key=lambda r: r[0], reverse=True)
        return [r[1] for r in results]

    def save_skill(self, skill: Skill) -> str:
        """Save a skill to the user's skill directory as YAML."""
        filepath = os.path.join(self._skills_dir, f"{skill.name}.yaml")

        lines = [
            f"name: {skill.name}",
            f"description: \"{skill.description}\"",
            f"version: \"{skill.version}\"",
        ]
        if skill.author:
            lines.append(f"author: \"{skill.author}\"")
        if skill.tags:
            lines.append(f"tags: [{', '.join(skill.tags)}]")

        if skill.inputs:
            lines.append("inputs:")
            for inp in skill.inputs:
                lines.append(f"  - name: {inp.name}")
                lines.append(f"    type: {inp.input_type}")
                if inp.description:
                    lines.append(f"    description: \"{inp.description}\"")
                lines.append(f"    required: {str(inp.required).lower()}")
                if inp.default is not None:
                    lines.append(f"    default: {inp.default}")

        if skill.steps:
            lines.append("steps:")
            for step in skill.steps:
                lines.append(f"  - tool: {step.tool}")
                if step.description:
                    lines.append(f"    description: \"{step.description}\"")
                if step.params:
                    lines.append("    params:")
                    for k, v in step.params.items():
                        lines.append(f"      {k}: \"{v}\"")
                if step.on_failure != "stop":
                    lines.append(f"    on_failure: {step.on_failure}")
                if step.save_as:
                    lines.append(f"    save_as: {step.save_as}")

        if skill.output_template:
            lines.append(f"output: \"{skill.output_template}\"")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        skill.source_file = filepath
        self._skills[skill.name] = skill
        return filepath


class SkillExecutor:
    """Executes skills by running their steps through the tool system."""

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config

    async def execute(
        self,
        skill: Skill,
        inputs: dict[str, Any],
        stream_callback: Any = None,
    ) -> dict[str, Any]:
        """Execute a skill with given inputs."""
        # Validate required inputs
        for inp in skill.inputs:
            if inp.required and inp.name not in inputs:
                if inp.default is not None:
                    inputs[inp.name] = inp.default
                else:
                    return {
                        "success": False,
                        "error": f"Missing required input: {inp.name}",
                    }

        variables: dict[str, Any] = dict(inputs)
        step_results: list[dict[str, Any]] = []

        for i, step in enumerate(skill.steps):
            if stream_callback:
                stream_callback(
                    f"[SKILL] Step {i + 1}/{len(skill.steps)}: {step.description or step.tool}"
                )

            # Substitute variables into params
            resolved_params = self._resolve_params(step.params, variables)

            try:
                result = await self._execute_step(step.tool, resolved_params)

                step_results.append({
                    "step": i + 1,
                    "tool": step.tool,
                    "success": result.get("success", False),
                    "output": result.get("output", ""),
                })

                # Save result to variables if save_as is set
                if step.save_as:
                    variables[step.save_as] = result.get("output", "")

                if not result.get("success") and step.on_failure == "stop":
                    return {
                        "success": False,
                        "error": f"Step {i + 1} failed: {result.get('error', '')}",
                        "steps": step_results,
                        "variables": variables,
                    }

            except Exception as e:
                step_results.append({
                    "step": i + 1,
                    "tool": step.tool,
                    "success": False,
                    "error": str(e),
                })
                if step.on_failure == "stop":
                    return {
                        "success": False,
                        "error": f"Step {i + 1} error: {e!s}",
                        "steps": step_results,
                        "variables": variables,
                    }

        # Format output
        output = skill.output_template
        if output:
            output = self._resolve_template(output, variables)

        return {
            "success": True,
            "output": output or str(variables),
            "steps": step_results,
            "variables": variables,
        }

    async def _execute_step(
        self, tool_name: str, params: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a single skill step using the tool registry."""
        from sovereign.tools.registry import ToolRegistry

        registry = ToolRegistry()

        # Register tools if empty
        if not registry._tools:
            from sovereign.core.agent import Agent

            agent = Agent(config=self.config)
            registry = agent.tool_registry

        tool = registry.get(tool_name)
        if not tool:
            # Try LLM reasoning as a special step
            if tool_name == "llm_reason":
                return await self._llm_reason_step(params)
            return {"success": False, "error": f"Tool not found: {tool_name}"}

        result = await tool.execute(**params)
        return {
            "success": result.success,
            "output": result.output or "",
            "error": result.error,
        }

    async def _llm_reason_step(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute an LLM reasoning step."""
        from sovereign.llm.provider import Message
        from sovereign.llm.router import ModelRouter

        router = ModelRouter(self.config)
        prompt = params.get("prompt", "")
        if not prompt:
            return {"success": False, "error": "No prompt provided"}

        try:
            response = await router.generate(
                messages=[Message(role="user", content=prompt)],
            )
            return {"success": True, "output": response.content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _resolve_params(
        params: dict[str, Any], variables: dict[str, Any],
    ) -> dict[str, Any]:
        """Substitute {variable} placeholders in params."""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str):
                for var_name, var_value in variables.items():
                    value = value.replace(f"{{{var_name}}}", str(var_value))
            resolved[key] = value
        return resolved

    @staticmethod
    def _resolve_template(template: str, variables: dict[str, Any]) -> str:
        """Substitute variables in an output template."""
        result = template
        for var_name, var_value in variables.items():
            result = result.replace(f"{{{var_name}}}", str(var_value))
        return result
