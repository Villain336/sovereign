"""Knowledge Graph - entity and relationship storage.

Maintains a graph of entities (people, companies, concepts) and their
relationships, enabling the agent to reason about connections and context.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from sovereign.config import SovereignConfig


class Entity(BaseModel):
    """A node in the knowledge graph."""

    id: str
    name: str
    entity_type: str  # person, company, concept, tool, etc.
    properties: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Relationship(BaseModel):
    """An edge in the knowledge graph."""

    source_id: str
    target_id: str
    relationship_type: str  # works_for, knows, uses, depends_on, etc.
    properties: dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeGraph:
    """Graph-based knowledge storage for entity relationships.

    Stores entities (nodes) and relationships (edges) to help the agent
    understand connections between people, companies, concepts, and tools.

    This enables reasoning like:
    - "Who works at Company X?"
    - "What tools are commonly used for task Y?"
    - "What's the relationship between A and B?"
    """

    def __init__(self, config: SovereignConfig) -> None:
        self.config = config
        self._entities: dict[str, Entity] = {}
        self._relationships: list[Relationship] = []
        self._graph_path = Path(config.memory.knowledge_graph_path)
        self._graph_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        """Load graph from disk."""
        if self._graph_path.exists():
            try:
                data = json.loads(self._graph_path.read_text())
                self._entities = {
                    eid: Entity(**edata)
                    for eid, edata in data.get("entities", {}).items()
                }
                self._relationships = [
                    Relationship(**rdata) for rdata in data.get("relationships", [])
                ]
            except (json.JSONDecodeError, Exception):
                self._entities = {}
                self._relationships = []

    def _save(self) -> None:
        """Save graph to disk."""
        data = {
            "entities": {
                eid: entity.model_dump(mode="json")
                for eid, entity in self._entities.items()
            },
            "relationships": [r.model_dump(mode="json") for r in self._relationships],
        }
        self._graph_path.write_text(json.dumps(data, indent=2, default=str))

    def add_entity(self, entity: Entity) -> None:
        """Add or update an entity in the graph."""
        if entity.id in self._entities:
            existing = self._entities[entity.id]
            existing.properties.update(entity.properties)
            existing.tags = list(set(existing.tags + entity.tags))
            existing.updated_at = datetime.now(timezone.utc)
        else:
            self._entities[entity.id] = entity
        self._save()

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship between two entities."""
        # Verify both entities exist
        if relationship.source_id not in self._entities:
            return
        if relationship.target_id not in self._entities:
            return

        # Check for duplicate
        for existing in self._relationships:
            if (
                existing.source_id == relationship.source_id
                and existing.target_id == relationship.target_id
                and existing.relationship_type == relationship.relationship_type
            ):
                existing.weight = relationship.weight
                existing.properties.update(relationship.properties)
                self._save()
                return

        self._relationships.append(relationship)
        self._save()

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get an entity by ID."""
        return self._entities.get(entity_id)

    def find_entities(
        self,
        entity_type: str | None = None,
        name_query: str | None = None,
        tags: list[str] | None = None,
    ) -> list[Entity]:
        """Find entities matching criteria."""
        results: list[Entity] = []

        for entity in self._entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            if name_query and name_query.lower() not in entity.name.lower():
                continue
            if tags and not set(tags) & set(entity.tags):
                continue
            results.append(entity)

        return results

    def get_relationships(
        self,
        entity_id: str,
        relationship_type: str | None = None,
        direction: str = "both",  # "outgoing", "incoming", "both"
    ) -> list[tuple[Relationship, Entity]]:
        """Get relationships for an entity with the connected entities."""
        results: list[tuple[Relationship, Entity]] = []

        for rel in self._relationships:
            if direction in ("outgoing", "both") and rel.source_id == entity_id:
                if relationship_type and rel.relationship_type != relationship_type:
                    continue
                target = self._entities.get(rel.target_id)
                if target:
                    results.append((rel, target))

            if direction in ("incoming", "both") and rel.target_id == entity_id:
                if relationship_type and rel.relationship_type != relationship_type:
                    continue
                source = self._entities.get(rel.source_id)
                if source:
                    results.append((rel, source))

        return results

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5,
    ) -> list[tuple[Entity, Relationship]] | None:
        """Find a path between two entities using BFS."""
        if source_id not in self._entities or target_id not in self._entities:
            return None

        visited: set[str] = set()
        queue: list[tuple[str, list[tuple[Entity, Relationship]]]] = [
            (source_id, [])
        ]

        while queue:
            current_id, path = queue.pop(0)

            if current_id == target_id:
                return path

            if current_id in visited or len(path) >= max_depth:
                continue

            visited.add(current_id)

            for rel in self._relationships:
                next_id = None
                if rel.source_id == current_id:
                    next_id = rel.target_id
                elif rel.target_id == current_id:
                    next_id = rel.source_id

                if next_id and next_id not in visited:
                    next_entity = self._entities.get(next_id)
                    if next_entity:
                        queue.append((next_id, path + [(next_entity, rel)]))

        return None

    def get_context_for_entity(self, entity_id: str) -> str:
        """Get a rich context string about an entity and its connections."""
        entity = self._entities.get(entity_id)
        if not entity:
            return ""

        parts = [f"Entity: {entity.name} ({entity.entity_type})"]

        if entity.properties:
            for key, value in entity.properties.items():
                parts.append(f"  {key}: {value}")

        relationships = self.get_relationships(entity_id)
        if relationships:
            parts.append("Connections:")
            for rel, connected in relationships:
                parts.append(
                    f"  --[{rel.relationship_type}]--> {connected.name} ({connected.entity_type})"
                )

        return "\n".join(parts)

    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity and its relationships."""
        if entity_id not in self._entities:
            return False

        del self._entities[entity_id]
        self._relationships = [
            r
            for r in self._relationships
            if r.source_id != entity_id and r.target_id != entity_id
        ]
        self._save()
        return True

    @property
    def entity_count(self) -> int:
        return len(self._entities)

    @property
    def relationship_count(self) -> int:
        return len(self._relationships)
