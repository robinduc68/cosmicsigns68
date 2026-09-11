"""Regenerate the renderer fixtures in ``apps/web/fixtures/charts``.

The renderer's real-chart fixtures are unmodified engine output, so they go stale
the moment the DTO grows a field. Writing them by hand is how a fixture quietly
stops matching the engine it claims to come from; this script is the only way they
should ever be produced.

    apps/api/.venv/bin/python packages/astrology-engine/scripts/dump_web_fixtures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages/astrology-engine/src"))

from cosmic_astrology import BirthInput, build_chart  # noqa: E402
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender  # noqa: E402

OUT = ROOT / "apps/web/fixtures/charts"

#: Pinned so regenerating produces byte-identical files. A wall-clock timestamp
#: would make every run dirty the working tree and hide real contract changes in
#: the diff.
GENERATED_AT = "2026-09-11T00:00:00+00:00"

#: ``(filename, birth, stage)``. Keep the birth data identical when regenerating —
#: the scenario descriptions and tests refer to these exact charts.
CASES: tuple[tuple[str, BirthInput, EngineStage], ...] = (
    (
        "cross-check-2001.preview.json",
        BirthInput(
            name="Nguyễn Thị Minh Anh",
            gender=Gender.FEMALE,
            calendar_type=CalendarType.SOLAR,
            day=4,
            month=3,
            year=2001,
            hour=9,
            minute=30,
            timezone_id="Asia/Ho_Chi_Minh",
        ),
        EngineStage.PREVIEW,
    ),
    (
        "cross-check-2001.frame.json",
        BirthInput(
            name="Nguyễn Thị Minh Anh",
            gender=Gender.FEMALE,
            calendar_type=CalendarType.SOLAR,
            day=4,
            month=3,
            year=2001,
            hour=9,
            minute=30,
            timezone_id="Asia/Ho_Chi_Minh",
        ),
        EngineStage.FRAME,
    ),
    (
        "reference-1992.preview.json",
        BirthInput(
            name="Trần Văn Bảo",
            gender=Gender.MALE,
            calendar_type=CalendarType.SOLAR,
            day=10,
            month=9,
            year=1992,
            hour=14,
            minute=0,
            timezone_id="Asia/Ho_Chi_Minh",
        ),
        EngineStage.PREVIEW,
    ),
    (
        "at-suu-1985.preview.json",
        BirthInput(
            name="Lê Hoàng Phúc",
            gender=Gender.MALE,
            calendar_type=CalendarType.SOLAR,
            day=15,
            month=6,
            year=1985,
            hour=8,
            minute=0,
            timezone_id="Asia/Ho_Chi_Minh",
        ),
        EngineStage.PREVIEW,
    ),
)


def main() -> int:
    for filename, birth, stage in CASES:
        payload = build_chart(birth, stage=stage, generated_at=GENERATED_AT).to_dict()
        target = OUT / filename
        target.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        stars = [s for p in payload["palaces"] for s in p["major_stars"]]  # type: ignore[index]
        coloured = sum(1 for s in stars if s["element"])
        print(
            f"{filename}: schema v{payload['schema_version']}, "
            f"{len(stars)} chính tinh, {coloured} có ngũ hành"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
