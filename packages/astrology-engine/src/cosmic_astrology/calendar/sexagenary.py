"""Can Chi (sexagenary cycle) computation and Ngũ hành nạp âm."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from cosmic_astrology.calendar.lunar import LunarDate, jd_from_solar, solar_to_lunar

__all__ = [
    "CAN",
    "CHI",
    "Element",
    "Pillar",
    "SexagenaryPillars",
    "hour_branch_index",
    "nap_am_element",
    "pillars_for_birth",
    "sexagenary_index",
]

CAN: tuple[str, ...] = (
    "Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý",
)  # fmt: skip

CHI: tuple[str, ...] = (
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
)  # fmt: skip


class Element(StrEnum):
    """Ngũ hành."""

    KIM = "KIM"
    MOC = "MOC"
    THUY = "THUY"
    HOA = "HOA"
    THO = "THO"


# 30 nạp âm groups, each covering two consecutive pillars of the 60-year cycle.
_NAP_AM: tuple[tuple[str, Element], ...] = (
    ("Hải Trung Kim", Element.KIM),
    ("Lư Trung Hỏa", Element.HOA),
    ("Đại Lâm Mộc", Element.MOC),
    ("Lộ Bàng Thổ", Element.THO),
    ("Kiếm Phong Kim", Element.KIM),
    ("Sơn Đầu Hỏa", Element.HOA),
    ("Giản Hạ Thủy", Element.THUY),
    ("Thành Đầu Thổ", Element.THO),
    ("Bạch Lạp Kim", Element.KIM),
    ("Dương Liễu Mộc", Element.MOC),
    ("Tuyền Trung Thủy", Element.THUY),
    ("Ốc Thượng Thổ", Element.THO),
    ("Tích Lịch Hỏa", Element.HOA),
    ("Tùng Bách Mộc", Element.MOC),
    ("Trường Lưu Thủy", Element.THUY),
    ("Sa Trung Kim", Element.KIM),
    ("Sơn Hạ Hỏa", Element.HOA),
    ("Bình Địa Mộc", Element.MOC),
    ("Bích Thượng Thổ", Element.THO),
    ("Kim Bạch Kim", Element.KIM),
    ("Phú Đăng Hỏa", Element.HOA),
    ("Thiên Hà Thủy", Element.THUY),
    ("Đại Trạch Thổ", Element.THO),
    ("Thoa Xuyến Kim", Element.KIM),
    ("Tang Đố Mộc", Element.MOC),
    ("Đại Khê Thủy", Element.THUY),
    ("Sa Trung Thổ", Element.THO),
    ("Thiên Thượng Hỏa", Element.HOA),
    ("Thạch Lựu Mộc", Element.MOC),
    ("Đại Hải Thủy", Element.THUY),
)


@dataclass(frozen=True, slots=True)
class Pillar:
    """One can–chi pair."""

    can_index: int
    chi_index: int

    @property
    def can(self) -> str:
        return CAN[self.can_index]

    @property
    def chi(self) -> str:
        return CHI[self.chi_index]

    @property
    def name(self) -> str:
        return f"{self.can} {self.chi}"

    @property
    def is_yang(self) -> bool:
        """Dương can (Giáp, Bính, Mậu, Canh, Nhâm) have an even index."""
        return self.can_index % 2 == 0

    def to_dict(self) -> dict[str, object]:
        nap_am_name, element = nap_am_element(self.can_index, self.chi_index)
        return {
            "can": self.can,
            "chi": self.chi,
            "can_index": self.can_index,
            "chi_index": self.chi_index,
            "name": self.name,
            "is_yang": self.is_yang,
            "nap_am": nap_am_name,
            "element": element.value,
        }


@dataclass(frozen=True, slots=True)
class SexagenaryPillars:
    """Tứ trụ — the four pillars of a birth moment."""

    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar

    def to_dict(self) -> dict[str, object]:
        return {
            "year": self.year.to_dict(),
            "month": self.month.to_dict(),
            "day": self.day.to_dict(),
            "hour": self.hour.to_dict(),
        }


def sexagenary_index(can_index: int, chi_index: int) -> int:
    """Position (0..59) of a can–chi pair inside the 60-pillar cycle."""
    for i in range(60):
        if i % 10 == can_index and i % 12 == chi_index:
            return i
    raise ValueError(f"Cặp can chi không hợp lệ: {can_index}/{chi_index}")


def nap_am_element(can_index: int, chi_index: int) -> tuple[str, Element]:
    """Nạp âm name and its ngũ hành for a can–chi pair."""
    return _NAP_AM[sexagenary_index(can_index, chi_index) // 2]


def hour_branch_index(hour: int) -> int:
    """Địa chi of a birth hour. 23:00–00:59 is giờ Tý (index 0)."""
    if not 0 <= hour <= 23:
        raise ValueError("Giờ sinh phải nằm trong khoảng 0–23")
    return ((hour + 1) // 2) % 12


def year_pillar(lunar_year: int) -> Pillar:
    return Pillar(can_index=(lunar_year + 6) % 10, chi_index=(lunar_year + 8) % 12)


def month_pillar(lunar_year: int, lunar_month: int) -> Pillar:
    """Ngũ hổ độn: lunar month 1 is always a Dần month."""
    year_can = (lunar_year + 6) % 10
    return Pillar(
        can_index=(year_can * 2 + 1 + lunar_month) % 10,
        chi_index=(lunar_month + 1) % 12,
    )


def day_pillar(solar_day: int, solar_month: int, solar_year: int) -> Pillar:
    jd = jd_from_solar(solar_day, solar_month, solar_year)
    return Pillar(can_index=(jd + 9) % 10, chi_index=(jd + 1) % 12)


def hour_pillar(day_can_index: int, hour: int) -> Pillar:
    """Ngũ thử độn: the can of giờ Tý is derived from the can of the day."""
    chi_index = hour_branch_index(hour)
    return Pillar(can_index=(day_can_index % 5 * 2 + chi_index) % 10, chi_index=chi_index)


def pillars_for_birth(
    solar_day: int,
    solar_month: int,
    solar_year: int,
    hour: int,
    lunar: LunarDate | None = None,
    tz_offset: float = 7.0,
) -> SexagenaryPillars:
    """Four pillars for a birth moment given as a *solar* date plus local hour.

    A birth between 23:00 and 23:59 belongs to giờ Tý of the *following* day for
    the day pillar, which is why the day pillar is shifted before it is derived.
    """
    lunar_date = lunar or solar_to_lunar(solar_day, solar_month, solar_year, tz_offset)
    jd = jd_from_solar(solar_day, solar_month, solar_year)
    day_jd = jd + 1 if hour == 23 else jd
    day = Pillar(can_index=(day_jd + 9) % 10, chi_index=(day_jd + 1) % 12)
    return SexagenaryPillars(
        year=year_pillar(lunar_date.year),
        month=month_pillar(lunar_date.year, lunar_date.month),
        day=day,
        hour=hour_pillar(day.can_index, hour),
    )
