"""Manifest creation, query, and validation.

Manages experiment manifests: YAML records that link simulation inputs,
extracted metrics, and generated figures for reproducibility.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..schemas import (
    MANIFEST_SCHEMA_VERSION,
    PIPE_VERSION,
    Manifest,
    ManifestInputFile,
    MetricsDict,
    SimDataFrame,
    SimMeta,
)

logger = logging.getLogger("lanes_ceo.manifest")


class ExperimentManager:
    """Create, query, and validate experiment manifests.

    Each experiment gets a unique experiment_id and a YAML manifest
    recording all inputs, metrics, and outputs.
    """

    def __init__(self, output_base: str | Path = "./experiments") -> None:
        self.output_base = Path(output_base)
        self.output_base.mkdir(parents=True, exist_ok=True)

    def create_manifest(
        self,
        dataframe: SimDataFrame,
        metrics: MetricsDict,
        figures: list[str | Path] = None,
        data_outputs: list[str | Path] = None,
        parameters: dict[str, Any] = None,
        input_files: list[str | Path] = None,
    ) -> Manifest:
        """Create a new experiment manifest.

        Args:
            dataframe: The parsed SimDataFrame (provides input_hash and meta).
            metrics: Extracted MetricsDict.
            figures: List of generated figure file paths.
            data_outputs: List of generated data file paths (CSV, JSON, etc.).
            parameters: Design parameters dict (vin, vout, fsw, etc.).
            input_files: List of input file paths used in this run.

        Returns:
            Manifest object ready for serialization.
        """
        experiment_id = f"exp-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).astimezone().isoformat()

        # Compute input file hashes
        input_file_records: list[dict[str, str]] = []
        if input_files:
            for fpath in input_files:
                p = Path(fpath)
                if p.exists():
                    sha = self._sha256_file(p)
                    input_file_records.append({"path": str(p), "sha256": sha})
                else:
                    input_file_records.append({"path": str(p), "sha256": "UNKNOWN"})

        # Build simulation block
        sim_block: dict[str, Any] = {
            "tool": dataframe.meta.tool or "unknown",
            "type": dataframe.meta.sim_type or "unknown",
            "input_files": input_file_records,
        }

        # Parameters: merge explicit params with those from meta
        params = dict(dataframe.meta.parameters)
        if parameters:
            params.update(parameters)

        # Metrics
        metrics_dict = metrics.summary

        # Outputs
        outputs: dict[str, list[str]] = {
            "figures": [str(p) for p in (figures or [])],
            "data": [str(p) for p in (data_outputs or [])],
        }

        manifest = Manifest(
            schema_version=MANIFEST_SCHEMA_VERSION,
            experiment_id=experiment_id,
            timestamp=timestamp,
            simulation=sim_block,
            parameters=params,
            metrics=metrics_dict,
            outputs=outputs,
            pipeline_version=PIPE_VERSION,
            input_hash=dataframe.input_hash,
        )

        return manifest

    def save_manifest(self, manifest: Manifest, experiment_dir: str | Path | None = None) -> Path:
        """Save a manifest to its experiment directory.

        Args:
            manifest: The Manifest to save.
            experiment_dir: Optional specific directory. If None, uses output_base/experiment_id/.

        Returns:
            Path to the written manifest YAML file.
        """
        if experiment_dir is None:
            exp_dir = self.output_base / manifest.experiment_id
        else:
            exp_dir = Path(experiment_dir)

        exp_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = exp_dir / "manifest.yaml"

        manifest.to_yaml(manifest_path)
        logger.info("Manifest saved to %s", manifest_path)

        return manifest_path

    def load_manifest(self, path: str | Path) -> Manifest:
        """Load a manifest from a YAML file.

        Args:
            path: Path to manifest.yaml.

        Returns:
            Manifest object.
        """
        return Manifest.from_yaml(Path(path))

    def query_manifests(
        self,
        base_dir: str | Path | None = None,
        **filters: Any,
    ) -> list[Manifest]:
        """Scan a directory for manifests and filter by criteria.

        Args:
            base_dir: Directory to scan for manifest.yaml files.
            **filters: Key=value pairs to match against manifest fields.

        Returns:
            List of matching Manifest objects.
        """
        base = Path(base_dir) if base_dir else self.output_base
        manifests: list[Manifest] = []

        for yaml_path in base.rglob("manifest.yaml"):
            try:
                m = self.load_manifest(yaml_path)
                if self._match_filters(m, filters):
                    manifests.append(m)
            except Exception as exc:
                logger.debug("Skipping invalid manifest %s: %s", yaml_path, exc)

        return manifests

    def diff_manifests(self, m1: Manifest, m2: Manifest) -> dict[str, Any]:
        """Compare two manifests and return a diff dict.

        Args:
            m1, m2: Two Manifest objects to compare.

        Returns:
            Dict with keys: parameters_diff, metrics_diff, outputs_diff.
        """
        diff: dict[str, Any] = {
            "parameters_diff": self._dict_diff(m1.parameters, m2.parameters),
            "metrics_diff": self._dict_diff(m1.metrics, m2.metrics),
            "outputs_diff": {},
        }

        # Compare figure/output file counts
        if m1.outputs and m2.outputs:
            for key in set(m1.outputs.keys()) | set(m2.outputs.keys()):
                v1 = m1.outputs.get(key, [])
                v2 = m2.outputs.get(key, [])
                if v1 != v2:
                    diff["outputs_diff"][key] = {
                        "manifest1_count": len(v1),
                        "manifest2_count": len(v2),
                    }

        return diff

    # ── helpers ──

    @staticmethod
    def _sha256_file(path: Path) -> str:
        """Compute SHA-256 of a file. Returns 'UNKNOWN' on any read error."""
        try:
            hasher = hashlib.sha256()
            with open(path, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except OSError as exc:
            logger.warning("Cannot hash %s: %s", path, exc)
            return "UNKNOWN"

    @staticmethod
    def _match_filters(manifest: Manifest, filters: dict[str, Any]) -> bool:
        """Check if a manifest matches all given filters."""
        for key, value in filters.items():
            # Search in parameters first, then metrics, then top-level attrs
            found = False
            if key in manifest.parameters and manifest.parameters[key] == value:
                found = True
            elif key in manifest.metrics and manifest.metrics[key] == value:
                found = True
            elif hasattr(manifest, key) and getattr(manifest, key) == value:
                found = True
            if not found:
                return False
        return True

    @staticmethod
    def _dict_diff(d1: dict, d2: dict) -> dict[str, Any]:
        """Compute key-level diff between two dicts."""
        diff: dict[str, Any] = {}
        all_keys = set(d1.keys()) | set(d2.keys())
        for k in all_keys:
            v1 = d1.get(k)
            v2 = d2.get(k)
            if v1 != v2:
                diff[k] = {"old": v1, "new": v2}
        return diff
