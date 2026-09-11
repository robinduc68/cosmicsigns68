"""Resolving the UTC offset of a birth moment.

Vietnam did not sit on UTC+7 for the whole of the last century. According to the
IANA database the South ran on UTC+8 from 1960 until mid-1975, and there were
several earlier changes. A hard-coded ``+7`` is therefore wrong by a full hour
for a large cohort of living adults — and an hour is enough to cross a canh giờ
boundary or a midnight, which moves cung Mệnh and the whole chart.

This module is deliberately *only* about what the clock on the wall read. Where
the sun actually was is a separate question, handled by
``BirthTimeCorrectionPolicy`` — see ``docs/astrology-conventions.md`` §2.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from cosmic_astrology.conventions.policies import TimezonePolicy

__all__ = ["TimezoneResolution", "resolve_timezone", "tzdata_version"]


def tzdata_version() -> str:
    """Version of the timezone database in use, for the chart's audit trail.

    The bundled ``tzdata`` package is preferred over whatever the host OS ships
    so that two machines cannot silently disagree about 1968.
    """
    try:
        import tzdata

        return f"tzdata {tzdata.__version__}"
    except (ImportError, AttributeError):  # pragma: no cover - depends on install
        return "system tzdb (phiên bản không xác định)"


@dataclass(frozen=True, slots=True)
class TimezoneResolution:
    """How the engine decided what UTC offset applied at the birth moment."""

    policy: TimezonePolicy
    utc_offset_hours: float
    timezone_id: str | None
    source: str
    #: True when the offset came from the tz database rather than the caller.
    resolved_from_database: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "policy": self.policy.value,
            "timezone_id": self.timezone_id,
            "utc_offset_hours": self.utc_offset_hours,
            "source": self.source,
            "resolved_from_database": self.resolved_from_database,
        }


def resolve_timezone(
    *,
    policy: TimezonePolicy,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    timezone_id: str | None,
    fallback_offset: float,
) -> TimezoneResolution:
    """Resolve the offset that applied at a local civil date and time.

    With ``IANA_HISTORICAL`` and a ``timezone_id``, the offset comes from the tz
    database at that instant. Without a ``timezone_id`` the caller's explicit
    offset is used and the result says so, so a chart never claims a database
    lookup it did not perform.
    """
    if policy is TimezonePolicy.IANA_HISTORICAL and timezone_id:
        try:
            zone = ZoneInfo(timezone_id)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Không tìm thấy múi giờ IANA: {timezone_id}") from exc

        # Ambiguous/imaginary local times (DST transitions) resolve to the
        # standard-time reading; Vietnam has no DST in the supported range, and
        # guessing differently would be a silent astrology decision.
        local = datetime(year, month, day, hour, minute, tzinfo=zone)
        offset = local.utcoffset()
        if offset is None:  # pragma: no cover - ZoneInfo always supplies one
            raise ValueError(f"Múi giờ {timezone_id} không trả về offset")
        return TimezoneResolution(
            policy=policy,
            utc_offset_hours=offset.total_seconds() / 3600.0,
            timezone_id=timezone_id,
            source=f"IANA {timezone_id} · {tzdata_version()}",
            resolved_from_database=True,
        )

    return TimezoneResolution(
        policy=TimezonePolicy.FIXED_OFFSET,
        utc_offset_hours=fallback_offset,
        timezone_id=timezone_id,
        source="Offset do người gọi cung cấp",
        resolved_from_database=False,
    )
