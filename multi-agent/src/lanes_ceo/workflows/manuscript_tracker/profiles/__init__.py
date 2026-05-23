"""Journal profile loading with schema validation and null-fallback for missing fields."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("lanes_ceo.manuscript_tracker.profiles")

_PROFILES_DIR = Path(__file__).parent

# Valid schema versions that this codebase supports
_SUPPORTED_SCHEMA_VERSIONS = {"1.0"}

# Known journal profile keys that ship with this package
_BUILTIN_PROFILES: dict[str, str] = {
    "nature": "nature.yaml",
    "science": "science.yaml",
    "ieee_jssc": "ieee_jssc.yaml",
    "ieee_tpe": "ieee_tpe.yaml",
}


@dataclass
class ArticleType:
    """Constraints for a specific article type within a journal."""

    max_pages: int | None = None
    max_words: int | None = None
    max_figures: int | None = None
    required_sections: list[str] = field(default_factory=list)


@dataclass
class JournalProfile:
    """Loaded journal profile with typed fields. Missing fields from YAML become None."""

    key: str
    schema_version: str = "1.0"
    journal_name: str = ""
    article_types: dict[str, ArticleType] = field(default_factory=dict)
    default_type: str = ""
    figure_dpi_min: int | None = None
    figure_colorspace: str | None = None  # "CMYK" or "RGB"
    figure_formats: list[str] = field(default_factory=list)
    figure_width_max_inches: float | None = None
    max_tables: int | None = None
    citation_style: str | None = None
    supplementary_required: bool = False
    supplementary_extensions: list[str] = field(default_factory=list)

    def get_article_type(self, article_type: str | None = None) -> ArticleType:
        """Resolve article type, falling back to default_type."""
        if article_type and article_type in self.article_types:
            return self.article_types[article_type]
        if self.default_type and self.default_type in self.article_types:
            return self.article_types[self.default_type]
        raise ValueError(
            f"No article type '{article_type or self.default_type}' found in profile '{self.key}'"
        )


class ProfileLoader:
    """Load and validate journal profiles from YAML files."""

    @classmethod
    def list_builtin(cls) -> list[str]:
        """Return list of available built-in profile keys."""
        return list(_BUILTIN_PROFILES.keys())

    @classmethod
    def load(cls, journal_key: str, profile_dir: Path | None = None) -> JournalProfile:
        """Load a journal profile by key (e.g. 'nature').

        Searches: built-in profiles first, then profile_dir if given.
        """
        profile_dir = profile_dir or _PROFILES_DIR

        # Resolve YAML file path
        yaml_file = cls._resolve_profile_file(journal_key, profile_dir)
        if yaml_file is None:
            raise FileNotFoundError(
                f"Profile '{journal_key}' not found. Available: {cls.list_builtin()}"
            )

        logger.info("Loading profile '%s' from %s", journal_key, yaml_file)
        raw = cls._read_yaml(yaml_file)
        cls._validate_schema_version(raw, journal_key)

        return cls._parse_profile(journal_key, raw)

    @classmethod
    def _resolve_profile_file(cls, key: str, profile_dir: Path) -> Path | None:
        """Resolve profile key to YAML file path."""
        # Try built-in first
        if key in _BUILTIN_PROFILES:
            return _PROFILES_DIR / _BUILTIN_PROFILES[key]
        # Try exact match in profile_dir
        exact_path = profile_dir / f"{key}.yaml"
        if exact_path.exists():
            return exact_path
        return None

    @classmethod
    def _read_yaml(cls, path: Path) -> dict[str, Any]:
        """Read and parse a YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @classmethod
    def _validate_schema_version(cls, raw: dict[str, Any], journal_key: str) -> None:
        """Check schema_version field is present and supported."""
        version = raw.get("schema_version", "")
        if not version:
            logger.warning(
                "Profile '%s' has no schema_version field; assuming 1.0", journal_key
            )
        elif version not in _SUPPORTED_SCHEMA_VERSIONS:
            logger.warning(
                "Profile '%s' schema_version '%s' is not in supported list %s; "
                "proceeding with best effort",
                journal_key, version, _SUPPORTED_SCHEMA_VERSIONS,
            )

    @classmethod
    def _parse_profile(cls, key: str, raw: dict[str, Any]) -> JournalProfile:
        """Parse raw YAML dict into JournalProfile with null-safe field access."""
        j = raw.get("journal", {})

        article_types_raw = j.get("article_types", {}) or {}
        article_types: dict[str, ArticleType] = {}
        for at_key, at_val in article_types_raw.items():
            article_types[at_key] = ArticleType(
                max_pages=at_val.get("max_pages"),
                max_words=at_val.get("max_words"),
                max_figures=at_val.get("max_figures"),
                required_sections=at_val.get("required_sections", []) or [],
            )

        return JournalProfile(
            key=key,
            schema_version=raw.get("schema_version", "1.0"),
            journal_name=j.get("name", key),
            article_types=article_types,
            default_type=j.get("default_type", ""),
            figure_dpi_min=j.get("figure_dpi_min"),
            figure_colorspace=j.get("figure_colorspace"),
            figure_formats=j.get("figure_formats", []) or [],
            figure_width_max_inches=j.get("figure_width_max_inches"),
            max_tables=j.get("max_tables"),
            citation_style=j.get("citation_style"),
            supplementary_required=j.get("supplementary_required", False),
            supplementary_extensions=j.get("supplementary_extensions", []) or [],
        )

    @classmethod
    def diff_profiles(cls, key_a: str, key_b: str) -> list[dict[str, Any]]:
        """Compare two profiles and return a list of differing fields.

        Returns list of dicts with keys: field, value_a, value_b, compatible
        (compatible=True when both acceptable, False when migration needed).
        """
        profile_a = cls.load(key_a)
        profile_b = cls.load(key_b)

        diffs: list[dict[str, Any]] = []

        # Compare scalar fields
        scalar_fields = [
            "figure_dpi_min", "figure_colorspace", "figure_width_max_inches",
            "max_tables", "citation_style", "supplementary_required",
        ]
        for field_name in scalar_fields:
            val_a = getattr(profile_a, field_name, None)
            val_b = getattr(profile_b, field_name, None)
            if val_a != val_b:
                diffs.append({
                    "field": field_name,
                    "value_a": val_a,
                    "value_b": val_b,
                    "compatible": cls._is_compatible(val_a, val_b),
                })

        # Compare list fields
        list_fields = ["figure_formats", "supplementary_extensions"]
        for field_name in list_fields:
            val_a = set(getattr(profile_a, field_name, []))
            val_b = set(getattr(profile_b, field_name, []))
            if val_a != val_b:
                diffs.append({
                    "field": field_name,
                    "value_a": sorted(val_a),
                    "value_b": sorted(val_b),
                    "compatible": val_a.issuperset(val_b) or val_b.issuperset(val_a),
                })

        # Compare article types
        at_keys_a = set(profile_a.article_types.keys())
        at_keys_b = set(profile_b.article_types.keys())
        if at_keys_a != at_keys_b:
            diffs.append({
                "field": "article_types (keys)",
                "value_a": sorted(at_keys_a),
                "value_b": sorted(at_keys_b),
                "compatible": False,
            })

        return diffs

    @staticmethod
    def _is_compatible(a: Any, b: Any) -> bool:
        """Heuristic for whether two different values are still compatible."""
        if a is None or b is None:
            return False
        if isinstance(a, bool) and isinstance(b, bool):
            return a == b
        # String comparison: colorspace RGB vs CMYK are incompatible
        if isinstance(a, str) and isinstance(b, str):
            return a.upper() == b.upper()
        return False
