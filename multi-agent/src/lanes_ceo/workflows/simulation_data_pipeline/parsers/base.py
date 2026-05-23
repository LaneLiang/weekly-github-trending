"""Abstract base class for all simulation data parsers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..schemas import SimDataFrame


class RawParseError(Exception):
    """Raised when a raw simulation file cannot be parsed."""

    def __init__(self, message: str, path: str = "", byte_offset: int | None = None) -> None:
        full = message
        if path:
            full = f"{path}: {full}"
        if byte_offset is not None:
            full = f"{full} (byte {byte_offset})"
        super().__init__(full)
        self.path = path
        self.byte_offset = byte_offset


class UnsupportedSPICEVariant(RawParseError):
    """Raised when the SPICE raw file uses an unsupported format variant."""


class BaseParser:
    """Abstract base class for all simulation data parsers.

    Subclasses must implement ``parse(path) -> SimDataFrame``.
    """

    SUPPORTED_EXTENSIONS: set[str] = set()
    """File extensions this parser can handle (e.g., {'.raw', '.sw0'})."""

    PARSER_NAME: str = "base"
    """Human-readable parser name for logging and error messages."""

    def can_handle(self, path: Path) -> bool:
        """Check if this parser can handle the given file."""
        return path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def parse(self, path: Path, **kwargs: Any) -> SimDataFrame:
        """Parse a simulation file into a SimDataFrame.

        Args:
            path: Path to the simulation data file.
            **kwargs: Parser-specific options.

        Returns:
            SimDataFrame with the parsed waveform data.

        Raises:
            RawParseError: If parsing fails.
        """
        raise NotImplementedError
