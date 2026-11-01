"""Versioned structured scientific visual-knowledge schema.

Coordinates are NORMALIZED 0..1 (storage) and converted to the Meta 0..1000
perception-grounding grid only at the provider boundary. See
https://dev.meta.ai/docs/image-understanding#perception-grounding
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

SCHEMA_VERSION = "atlas.visual-knowledge/v1"

ENTITY_CATEGORIES = {
    "anatomical-structure", "molecule", "protein", "cell-type",
    "component", "process", "function", "pathway", "other",
}

RELATIONSHIP_TYPES = {
    "activates", "inhibits", "projects-to", "receives-input-from",
    "produces", "regulates", "contains", "participates-in",
}


def _check_norm(value: float, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} must be a number in [0,1], got {value!r}")
    v = float(value)
    if not 0.0 <= v <= 1.0:
        raise ValueError(f"{name} must be in [0,1], got {v}")
    return v


@dataclass(frozen=True)
class BoundingBox:
    """Normalized box: (0,0) top-left, (1,1) bottom-right."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "x_min", _check_norm(self.x_min, "x_min"))
        object.__setattr__(self, "y_min", _check_norm(self.y_min, "y_min"))
        object.__setattr__(self, "x_max", _check_norm(self.x_max, "x_max"))
        object.__setattr__(self, "y_max", _check_norm(self.y_max, "y_max"))
        if not (self.x_min < self.x_max and self.y_min < self.y_max):
            raise ValueError(f"empty/inverted box {self}")

    def to_grid1000(self) -> list[int]:
        """Meta perception-grounding grid (0..1000). Docs: divide by 10 for CSS %."""
        return [round(self.x_min * 1000), round(self.y_min * 1000),
                round(self.x_max * 1000), round(self.y_max * 1000)]

    @classmethod
    def from_grid1000(cls, box: list[float]) -> "BoundingBox":
        if len(box) != 4:
            raise ValueError(f"box must have 4 entries, got {box!r}")
        lo = [min(max(float(v), 0.0), 1000.0) / 1000.0 for v in box]  # clamp edge 1001 etc.
        return cls(x_min=lo[0], y_min=lo[1], x_max=lo[2], y_max=lo[3])


@dataclass(frozen=True)
class VisualEntity:
    id: str
    name: str
    category: str
    description: str = ""
    bbox: BoundingBox | None = None
    source_evidence: str = ""
    confidence: float = 0.0
    uncertainty: str = ""
    mask_ref: str = ""  # segmentation reference, empty when bbox-only fallback
    model_inferred: bool = False

    def __post_init__(self) -> None:
        if not self.id or not self.name:
            raise ValueError("entity id and name are required")
        if self.category not in ENTITY_CATEGORIES:
            raise ValueError(f"unknown category {self.category!r}")
        c = float(self.confidence)
        if not 0.0 <= c <= 1.0:
            raise ValueError(f"confidence must be in [0,1], got {c}")
        object.__setattr__(self, "confidence", c)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["bbox"] = asdict(self.bbox) if self.bbox else None
        return d


@dataclass(frozen=True)
class VisualRelationship:
    source_id: str
    target_id: str
    rel_type: str
    explanation: str = ""
    supporting_evidence: str = ""
    confidence: float = 0.0
    provenance: str = "model"  # "model" | "source" | "user-correction"
    model_inferred: bool = True

    def __post_init__(self) -> None:
        if self.rel_type not in RELATIONSHIP_TYPES:
            raise ValueError(f"unknown relationship type {self.rel_type!r}")
        if not self.source_id or not self.target_id:
            raise ValueError("relationship endpoints are required")
        if self.source_id == self.target_id:
            raise ValueError("self-relationships are not allowed")
        c = float(self.confidence)
        if not 0.0 <= c <= 1.0:
            raise ValueError(f"confidence must be in [0,1], got {c}")
        object.__setattr__(self, "confidence", c)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VisualAnalysis:
    """One analyzed figure crop. Entities + relationships share IDs by construction."""

    analysis_version: str = SCHEMA_VERSION
    document_ref: str = ""
    source_page: int = 0
    figure_id: str = ""
    entities: list[VisualEntity] = field(default_factory=list)
    relationships: list[VisualRelationship] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        ids = {e.id for e in self.entities}
        if len(ids) != len(self.entities):
            errors.append("duplicate entity ids")
        for r in self.relationships:
            if r.source_id not in ids:
                errors.append(f"relationship from unknown entity {r.source_id}")
            if r.target_id not in ids:
                errors.append(f"relationship to unknown entity {r.target_id}")
        return errors

    def to_dict(self) -> dict:
        return {
            "analysis_version": self.analysis_version,
            "document_ref": self.document_ref,
            "source_page": self.source_page,
            "figure_id": self.figure_id,
            "entities": [e.to_dict() for e in self.entities],
            "relationships": [r.to_dict() for r in self.relationships],
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "VisualAnalysis":
        entities = []
        for e in raw.get("entities", []):
            bbox = None
            if e.get("bbox"):
                b = e["bbox"]
                bbox = BoundingBox(x_min=b["x_min"], y_min=b["y_min"],
                                   x_max=b["x_max"], y_max=b["y_max"])
            entities.append(VisualEntity(
                id=e["id"], name=e["name"], category=e.get("category", "other"),
                description=e.get("description", ""), bbox=bbox,
                source_evidence=e.get("source_evidence", ""),
                confidence=float(e.get("confidence", 0.0)),
                uncertainty=e.get("uncertainty", ""),
                mask_ref=e.get("mask_ref", ""),
                model_inferred=bool(e.get("model_inferred", False)),
            ))
        rels = [VisualRelationship(
            source_id=r["source_id"], target_id=r["target_id"],
            rel_type=r["rel_type"], explanation=r.get("explanation", ""),
            supporting_evidence=r.get("supporting_evidence", ""),
            confidence=float(r.get("confidence", 0.0)),
            provenance=r.get("provenance", "model"),
            model_inferred=bool(r.get("model_inferred", True)),
        ) for r in raw.get("relationships", [])]
        obj = cls(
            analysis_version=raw.get("analysis_version", SCHEMA_VERSION),
            document_ref=raw.get("document_ref", ""),
            source_page=int(raw.get("source_page", 0)),
            figure_id=raw.get("figure_id", ""),
            entities=entities, relationships=rels,
        )
        errs = obj.validate()
        if errs:
            raise ValueError("; ".join(errs))
        return obj


def muse_json_schema() -> dict:
    """JSON Schema sent as response_format.json_schema so Muse output parses first try."""
    num = {"type": "number", "minimum": 0, "maximum": 1000}
    return {
        "name": "AtlasVisualKnowledge",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "category": {"type": "string", "enum": sorted(ENTITY_CATEGORIES)},
                        "description": {"type": "string"},
                        "box": {"type": "array", "items": num, "minItems": 4, "maxItems": 4},
                        "source_evidence": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "uncertainty": {"type": "string"},
                    },
                    # box optional: text-sourced entities have no visual location
                    "required": ["id", "name", "category", "confidence"],
                    },
                },
                "relationships": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "source_id": {"type": "string"},
                            "target_id": {"type": "string"},
                            "rel_type": {"type": "string", "enum": sorted(RELATIONSHIP_TYPES)},
                            "explanation": {"type": "string"},
                            "supporting_evidence": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": ["source_id", "target_id", "rel_type", "confidence"],
                    },
                },
            },
            "required": ["entities", "relationships"],
        },
    }


def coerce_muse_payload(payload: dict[str, Any], document_ref: str = "",
                         source_page: int = 0, figure_id: str = "") -> VisualAnalysis:
    """Validate raw Muse JSON (0..1000 boxes) into a versioned VisualAnalysis."""
    entities: list[VisualEntity] = []
    for e in payload.get("entities", []):
        bbox = None
        if e.get("box"):
            bbox = BoundingBox.from_grid1000([float(v) for v in e["box"]])
        entities.append(VisualEntity(
            id=str(e["id"]), name=str(e["name"]),
            category=str(e.get("category", "other")),
            description=str(e.get("description", "")),
            bbox=bbox, source_evidence=str(e.get("source_evidence", "")),
            confidence=float(e.get("confidence", 0.0)),
            uncertainty=str(e.get("uncertainty", "")),
            model_inferred=True,
        ))
    rels = [VisualRelationship(
        source_id=str(r["source_id"]), target_id=str(r["target_id"]),
        rel_type=str(r["rel_type"]), explanation=str(r.get("explanation", "")),
        supporting_evidence=str(r.get("supporting_evidence", "")),
        confidence=float(r.get("confidence", 0.0)),
    ) for r in payload.get("relationships", [])]
    analysis = VisualAnalysis(document_ref=document_ref, source_page=source_page,
                              figure_id=figure_id, entities=entities, relationships=rels)
    errs = analysis.validate()
    if errs:
        raise ValueError("; ".join(errs))
    return analysis
