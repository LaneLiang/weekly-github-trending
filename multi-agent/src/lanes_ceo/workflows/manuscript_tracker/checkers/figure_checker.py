"""FigureChecker — verify figure DPI, colorspace, dimensions, and format compliance."""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
from pathlib import Path

from lanes_ceo.workflows.manuscript_tracker.checkers.base import BaseChecker, CheckItem, CheckResult
from lanes_ceo.workflows.manuscript_tracker.config import DEFAULT_CONFIG

logger = logging.getLogger("lanes_ceo.manuscript_tracker.figure")


class FigureChecker(BaseChecker):
    """Check figure files for DPI, colorspace, format, and size compliance.

    Uses ImageMagick (magick identify) with 30s timeout per image.
    Falls back to Pillow (PIL) if ImageMagick is unavailable.
    """

    name = "figure"

    # Valid raster formats (vector formats like .eps/.pdf bypass pixel checks)
    RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif"}

    def __init__(self, dpi_min: int | None = None, colorspace: str | None = None):
        self._dpi_min = dpi_min
        self._colorspace = colorspace

    def check(self, project: "LaTeXProject", profile: "JournalProfile") -> CheckResult:  # noqa: F821
        config = DEFAULT_CONFIG
        figure_files = project.figure_files

        dpi_min = self._dpi_min or profile.figure_dpi_min or config.figure_dpi_min
        required_colorspace = self._colorspace or profile.figure_colorspace
        width_max = profile.figure_width_max_inches or config.figure_width_max_inches
        allowed_formats = profile.figure_formats or []

        if not figure_files:
            return self._skip("项目中未发现图片文件")

        items: list[CheckItem] = []
        issues_found = 0

        # Detect best tool: ImageMagick > Pillow
        magick_cmd = self._detect_magick()
        has_pillow = self._check_pillow()

        if not magick_cmd and not has_pillow:
            return self._skip("ImageMagick 和 Pillow 均不可用，无法检查图片属性")

        for fig_path in figure_files:
            rel_path = fig_path.relative_to(project.project_dir) if project.project_dir in fig_path.parents else fig_path

            # Check format
            suffix = fig_path.suffix.lower()
            if suffix == ".jpeg":
                suffix = ".jpg"
            if allowed_formats and suffix not in allowed_formats:
                items.append(CheckItem(
                    code="FIG_FORMAT",
                    description=f"图片格式不符合要求: {rel_path} ({suffix}, 期刊接受: {allowed_formats})",
                    status="fail",
                    detail=f"当前格式: {suffix}, 允许格式: {allowed_formats}",
                    fix_suggestion=f"将 {suffix.upper()} 转换为期刊允许的格式",
                ))
                issues_found += 1

            # For vector formats (.eps, .pdf), skip raster checks
            if suffix in (".eps", ".pdf"):
                continue

            # For raster formats, check DPI and colorspace
            if suffix in self.RASTER_EXTENSIONS:
                if magick_cmd:
                    info = self._identify_magick(fig_path, magick_cmd, config.figure_timeout_seconds)
                else:
                    info = self._identify_pillow(fig_path)

                if info is None:
                    items.append(CheckItem(
                        code="FIG_READ_ERROR",
                        description=f"无法读取图片信息: {rel_path}",
                        status="warn",
                        detail="文件可能损坏或格式不支持",
                        fix_suggestion="确认图片文件完整且格式有效",
                    ))
                    continue

                # DPI check
                dpi = info.get("dpi", 0)
                if dpi > 0 and dpi < dpi_min:
                    items.append(CheckItem(
                        code="FIG_DPI",
                        description=f"图片 DPI 不足: {rel_path} ({dpi} dpi < {dpi_min})",
                        status="fail",
                        detail=f"当前: {dpi} dpi, 要求: >= {dpi_min} dpi",
                        fix_suggestion=f"重新导出图片，设置分辨率 >= {dpi_min} dpi",
                    ))
                    issues_found += 1

                # Colorspace check
                cs = info.get("colorspace", "").upper()
                if required_colorspace and cs and cs != required_colorspace:
                    items.append(CheckItem(
                        code="FIG_COLORSPACE",
                        description=f"图片色彩空间不符合要求: {rel_path} ({cs}, 期刊要求: {required_colorspace})",
                        status="fail",
                        detail=f"当前: {cs}, 要求: {required_colorspace}",
                        fix_suggestion=f"用 ImageMagick: magick convert {rel_path} -colorspace {required_colorspace} output.{suffix}",
                    ))
                    issues_found += 1

                # Width check
                width_inches = info.get("width_inches", 0)
                if width_inches > 0 and width_max and width_inches > width_max:
                    items.append(CheckItem(
                        code="FIG_WIDTH",
                        description=f"图片宽度超过限制: {rel_path} ({width_inches:.2f}\" > {width_max}\")",
                        status="warn",
                        detail=f"当前: {width_inches:.2f}\", 上限: {width_max}\"",
                        fix_suggestion=f"将图片宽度缩放到 {width_max}\" 以内",
                    ))

        if not items:
            items.append(CheckItem(
                code="FIG_ALL_PASS",
                description=f"所有图片检查通过 ({len(figure_files)} 张)",
                status="pass",
            ))

        if issues_found > 0:
            return self._fail(
                items=items,
                summary=f"图片检查发现问题: {issues_found} 项不达标",
            )

        return self._pass(
            items=items,
            summary=f"图片检查通过 ({len(figure_files)} 张)",
        )

    # ── tool detection ──

    def _detect_magick(self) -> str | None:
        """Return ImageMagick identify command: 'magick' (v7) or 'identify' (v6)."""
        if shutil.which("magick"):
            return "magick"
        if shutil.which("identify"):
            return "identify"
        return None

    def _check_pillow(self) -> bool:
        """Check if Pillow is importable."""
        try:
            import PIL.Image  # noqa: F401
            return True
        except ImportError:
            return False

    # ── ImageMagick identification ──

    def _identify_magick(self, path: Path, magick_cmd: str,
                         timeout: int = 30) -> dict | None:
        """Run identify -verbose and parse key fields."""
        if magick_cmd == "magick":
            cmd = ["magick", "identify", "-verbose", str(path)]
        else:
            cmd = ["identify", "-verbose", str(path)]
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            logger.warning("ImageMagick identify timed out for %s", path.name)
            return None
        except FileNotFoundError:
            return None

        if proc.returncode != 0:
            logger.warning("ImageMagick failed for %s: %s", path.name, proc.stderr[:200])
            # Try fallback to simple identify (without -verbose)
            try:
                if magick_cmd == "magick":
                    fb_cmd = ["magick", "identify", str(path)]
                else:
                    fb_cmd = ["identify", str(path)]
                proc = subprocess.run(
                    fb_cmd, capture_output=True, text=True, timeout=timeout,
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    return self._parse_simple_identify(proc.stdout, magick_cmd, path, timeout)
            except Exception:
                logger.debug("ImageMagick identify failed for %s, skipping DPI check", path)
            return None

        return self._parse_verbose_identify(proc.stdout)

    def _parse_verbose_identify(self, output: str) -> dict:
        """Parse 'magick identify -verbose' output."""
        info: dict = {"dpi": 0, "colorspace": "", "width_inches": 0}
        lines = output.split("\n")

        for i, line in enumerate(lines):
            ls = line.strip()

            if "Resolution:" in ls:
                # "Resolution: 300x300" or "300x300 DPI"
                parts = ls.split(":")
                if len(parts) >= 2:
                    res_str = parts[1].strip()
                    # "300x300"
                    nums = res_str.replace("DPCM", "").replace("PixelsPerCentimeter", "").strip()
                    m = re.match(r'(\d+(?:\.\d+)?)', nums)
                    if m:
                        dpi_val = float(m.group(1))
                        # Only check current line for DPCM units, not entire output
                        if "PixelsPerCentimeter" in ls or "DPCM" in ls:
                            dpi_val = dpi_val * 2.54
                        info["dpi"] = int(round(dpi_val))

            if "Colorspace:" in ls:
                cs = ls.split(":", 1)[1].strip()
                # Normalize common names
                cs_normalized = cs.upper()
                if cs_normalized in ("SRGB", "RGBA"):
                    cs_normalized = "RGB"
                info["colorspace"] = cs_normalized

            if "Geometry:" in ls:
                # "Geometry: 1920x1080+0+0"
                parts = ls.split(":")[1].strip()
                geo_match = re.match(r'(\d+)x(\d+)', parts)
                if geo_match:
                    w_px = int(geo_match.group(1))
                    if info["dpi"] > 0:
                        info["width_inches"] = round(w_px / info["dpi"], 2)

            if "Print size:" in ls:
                # "Print size: 6.4x3.6"
                parts = ls.split(":", 1)[1].strip()
                size_match = re.match(r'([\d.]+)x', parts)
                if size_match:
                    info["width_inches"] = float(size_match.group(1))

        return info

    def _parse_simple_identify(self, line: str, magick_cmd: str,
                               path: Path, timeout: int) -> dict | None:
        """Fallback: parse basic identify line and get DPI separately."""
        info: dict = {"dpi": 0, "colorspace": "", "width_inches": 0}

        # Try to get DPI separately
        try:
            if magick_cmd == "magick":
                dpi_cmd = ["magick", "identify", "-format", "%x x %y", str(path)]
            else:
                dpi_cmd = ["identify", "-format", "%x x %y", str(path)]
            proc = subprocess.run(
                dpi_cmd, capture_output=True, text=True, timeout=timeout,
            )
            if proc.returncode == 0:
                dpi_str = proc.stdout.strip()
                m = re.match(r'(\d+(?:\.\d+)?)', dpi_str)
                if m:
                    info["dpi"] = int(round(float(m.group(1))))
        except Exception:
            logger.debug("DPI regex extraction failed, keeping defaults")

        return info

    # ── Pillow fallback ──

    def _identify_pillow(self, path: Path) -> dict | None:
        """Use Pillow to get image info as fallback."""
        try:
            from PIL import Image

            img = Image.open(path)
            info: dict = {"dpi": 0, "colorspace": "", "width_inches": 0}

            # DPI
            dpi = img.info.get("dpi", None)
            if dpi:
                if isinstance(dpi, (tuple, list)):
                    info["dpi"] = int(round(dpi[0]))
                else:
                    info["dpi"] = int(round(dpi))

            # Colorspace / mode
            mode = img.mode.upper()
            if "RGB" in mode:
                info["colorspace"] = "RGB"
            elif "CMYK" in mode:
                info["colorspace"] = "CMYK"
            elif "L" in mode:
                info["colorspace"] = "GRAY"
            elif "RGBA" in mode:
                info["colorspace"] = "RGB"
            else:
                info["colorspace"] = mode

            # Width in inches
            if info["dpi"] > 0:
                info["width_inches"] = round(img.width / info["dpi"], 2)

            img.close()
            return info
        except Exception as exc:
            logger.warning("Pillow failed for %s: %s", path.name, exc)
            return None

