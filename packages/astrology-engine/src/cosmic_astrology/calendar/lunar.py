"""Solar ↔ Vietnamese lunar calendar conversion.

The algorithm follows the widely used astronomical method popularised by
Hồ Ngọc Đức: new moons and solar longitudes are computed from Meeus'
approximations, then the Vietnamese calendar rules are applied
(month 11 always contains the winter solstice; a leap month is inserted in a
13-month year at the first month that does not contain a principal term).

Everything is computed in the *civil* timezone of the birth place, because the
lunar day boundary follows local midnight. Vietnam is UTC+7 today, but births
before 1975 in the South (UTC+8 during some periods) are handled by passing an
explicit ``tz_offset``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "LunarDate",
    "jd_from_solar",
    "jd_to_solar",
    "lunar_to_solar",
    "solar_to_lunar",
]

PI = math.pi


@dataclass(frozen=True, slots=True)
class LunarDate:
    """A date on the Vietnamese lunar calendar."""

    day: int
    month: int
    year: int
    is_leap_month: bool

    def as_tuple(self) -> tuple[int, int, int, bool]:
        return (self.day, self.month, self.year, self.is_leap_month)


def jd_from_solar(day: int, month: int, year: int) -> int:
    """Julian day number of a Gregorian (or Julian, before 1582-10-15) date."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jd = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        jd = day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def jd_to_solar(jd: int) -> tuple[int, int, int]:
    """Inverse of :func:`jd_from_solar`; returns ``(day, month, year)``."""
    if jd > 2299160:  # After 1582-10-15
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (b * 146097) // 4
    else:
        b = 0
        c = jd + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = b * 100 + d - 4800 + m // 10
    return (day, month, year)


# Meeus, *Astronomical Algorithms* 2nd ed., table 49.A — periodic terms of the
# new moon, as ``(coefficient, multiplier of E, M', M, F, omega)``.
_NEW_MOON_TERMS: tuple[tuple[float, int, int, int, int, int], ...] = (
    (-0.40720, 0, 1, 0, 0, 0),
    (0.17241, 1, 0, 1, 0, 0),
    (0.01608, 0, 2, 0, 0, 0),
    (0.01039, 0, 0, 0, 2, 0),
    (0.00739, 1, 1, -1, 0, 0),
    (-0.00514, 1, 1, 1, 0, 0),
    (0.00208, 2, 0, 2, 0, 0),
    (-0.00111, 0, 1, 0, -2, 0),
    (-0.00057, 0, 1, 0, 2, 0),
    (0.00056, 1, 2, 1, 0, 0),
    (-0.00042, 0, 3, 0, 0, 0),
    (0.00042, 1, 0, 1, 2, 0),
    (0.00038, 1, 0, 1, -2, 0),
    (-0.00024, 1, 2, -1, 0, 0),
    (-0.00017, 0, 0, 0, 0, 1),
    (-0.00007, 0, 1, 2, 0, 0),
    (0.00004, 0, 2, 0, -2, 0),
    (0.00004, 0, 0, 3, 0, 0),
    (0.00003, 0, 1, 1, -2, 0),
    (0.00003, 0, 2, 0, 2, 0),
    (-0.00003, 0, 1, 1, 2, 0),
    (0.00003, 0, 1, -1, 2, 0),
    (-0.00002, 0, 1, -1, -2, 0),
    (-0.00002, 0, 3, 1, 0, 0),
    (0.00002, 0, 4, 0, 0, 0),
)

# Meeus 49 additional corrections: ``(coefficient, constant, k factor)`` in degrees.
_NEW_MOON_ADDITIONAL: tuple[tuple[float, float, float], ...] = (
    (0.000325, 299.77, 0.107408),
    (0.000165, 251.88, 0.016321),
    (0.000164, 251.83, 26.651886),
    (0.000126, 349.42, 36.412478),
    (0.000110, 84.66, 18.206239),
    (0.000062, 141.74, 53.303771),
    (0.000060, 207.14, 2.453732),
    (0.000056, 154.84, 7.306860),
    (0.000047, 34.52, 27.261239),
    (0.000042, 207.19, 0.121824),
    (0.000040, 291.34, 1.844379),
    (0.000037, 161.72, 24.198154),
    (0.000035, 239.56, 25.513099),
    (0.000023, 331.55, 3.592518),
)


def _delta_t_days(year: float) -> float:
    """TT − UT in days, using the Espenak & Meeus polynomial expressions.

    Only the 1900–2150 branches are implemented: the engine rejects birth years
    outside 1900–2100 anyway.
    """
    if year < 1920:
        t = year - 1900
        seconds = -2.79 + 1.494119 * t - 0.0598939 * t**2 + 0.0061966 * t**3 - 0.000197 * t**4
    elif year < 1941:
        t = year - 1920
        seconds = 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
    elif year < 1961:
        t = year - 1950
        seconds = 29.07 + 0.407 * t - t**2 / 233 + t**3 / 2547
    elif year < 1986:
        t = year - 1975
        seconds = 45.45 + 1.067 * t - t**2 / 260 - t**3 / 718
    elif year < 2005:
        t = year - 2000
        seconds = (
            63.86
            + 0.3345 * t
            - 0.060374 * t**2
            + 0.0017275 * t**3
            + 0.000651814 * t**4
            + 0.00002373599 * t**5
        )
    elif year < 2050:
        t = year - 2000
        seconds = 62.92 + 0.32217 * t + 0.005589 * t**2
    else:
        t = year - 1820
        seconds = -20 + 32 * (t / 100) ** 2 - 0.5628 * (2150 - year)
    return seconds / 86400.0


# Lunations between the 1900 epoch used by the Vietnamese calendar rules
# (2415021.076998695) and the k=0 new moon of Meeus' series (2000-01-06).
_MEEUS_K_OFFSET = 1237


def _new_moon_jd(k: int) -> float:
    """Julian day (UT) of the k-th new moon counted from the 1900 epoch.

    Accuracy is a few seconds, which matters: a lunar month starts on the local
    civil day of the new moon, so an error of an hour can shift mùng 1 — and
    with it the whole chart — by a full day.
    """
    dr = PI / 180
    k = k - _MEEUS_K_OFFSET
    t = k / 1236.85
    t2 = t * t
    t3 = t2 * t
    t4 = t3 * t
    jde = 2451550.09766 + 29.530588861 * k + 0.00015437 * t2 - 0.000000150 * t3 + 0.00000000073 * t4
    e = 1 - 0.002516 * t - 0.0000074 * t2
    m = 2.5534 + 29.10535670 * k - 0.0000014 * t2 - 0.00000011 * t3
    mp = 201.5643 + 385.81693528 * k + 0.0107582 * t2 + 0.00001238 * t3 - 0.000000058 * t4
    f = 160.7108 + 390.67050284 * k - 0.0016118 * t2 - 0.00000227 * t3 + 0.000000011 * t4
    omega = 124.7746 - 1.56375588 * k + 0.0020672 * t2 + 0.00000215 * t3

    correction = 0.0
    for coeff, e_power, mp_mul, m_mul, f_mul, omega_mul in _NEW_MOON_TERMS:
        angle = (mp_mul * mp + m_mul * m + f_mul * f + omega_mul * omega) * dr
        correction += coeff * (e**e_power) * math.sin(angle)
    for coeff, constant, k_factor in _NEW_MOON_ADDITIONAL:
        correction += coeff * math.sin((constant + k_factor * k) * dr)

    jde += correction
    year = 2000 + k / 12.3685
    return jde - _delta_t_days(year)


def _sun_longitude(jdn: float) -> float:
    """Apparent ecliptic longitude of the Sun (radians) at the given Julian day."""
    t = (jdn - 2451545.0) / 36525
    t2 = t * t
    dr = PI / 180
    m = 357.52910 + 35999.05030 * t - 0.0001559 * t2 - 0.00000048 * t * t2
    l0 = 280.46645 + 36000.76983 * t + 0.0003032 * t2
    dl = (1.914600 - 0.004817 * t - 0.000014 * t2) * math.sin(dr * m)
    dl += (0.019993 - 0.000101 * t) * math.sin(dr * 2 * m) + 0.000290 * math.sin(dr * 3 * m)
    lam = (l0 + dl) * dr
    # math.floor, not int(): before the year 2000 the raw longitude is a large
    # negative angle and truncation-toward-zero would normalise it incorrectly.
    return lam - PI * 2 * math.floor(lam / (PI * 2))


def _new_moon_day(k: int, tz_offset: float) -> int:
    """Local (timezone-adjusted) day of the k-th new moon."""
    return math.floor(_new_moon_jd(k) + 0.5 + tz_offset / 24)


def _sun_longitude_index(day_number: int, tz_offset: float) -> int:
    """Index 0..11 of the 30° solar sector at local midnight of ``day_number``."""
    return math.floor(_sun_longitude(day_number - 0.5 - tz_offset / 24) / PI * 6)


def _lunar_month_11(year: int, tz_offset: float) -> int:
    """Local day number of the first day of lunar month 11 of ``year``."""
    off = jd_from_solar(31, 12, year) - 2415021
    k = int(off / 29.530588853)
    nm = _new_moon_day(k, tz_offset)
    sun_long = _sun_longitude_index(nm, tz_offset)
    if sun_long >= 9:
        nm = _new_moon_day(k - 1, tz_offset)
    return nm


def _leap_month_offset(a11: int, tz_offset: float) -> int:
    """Number of months between month 11 and the leap month of that lunar year."""
    k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    last = 0
    i = 1
    arc = _sun_longitude_index(_new_moon_day(k + i, tz_offset), tz_offset)
    while True:
        last = arc
        i += 1
        arc = _sun_longitude_index(_new_moon_day(k + i, tz_offset), tz_offset)
        if arc == last or i >= 14:
            break
    return i - 1


def solar_to_lunar(day: int, month: int, year: int, tz_offset: float = 7.0) -> LunarDate:
    """Convert a solar (Gregorian) date to the Vietnamese lunar calendar."""
    day_number = jd_from_solar(day, month, year)
    k = int((day_number - 2415021.076998695) / 29.530588853)
    month_start = _new_moon_day(k + 1, tz_offset)
    if month_start > day_number:
        month_start = _new_moon_day(k, tz_offset)
    a11 = _lunar_month_11(year, tz_offset)
    b11 = a11
    if a11 >= month_start:
        lunar_year = year
        a11 = _lunar_month_11(year - 1, tz_offset)
    else:
        lunar_year = year + 1
        b11 = _lunar_month_11(year + 1, tz_offset)
    lunar_day = day_number - month_start + 1
    diff = (month_start - a11) // 29
    lunar_leap = False
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_month_diff = _leap_month_offset(a11, tz_offset)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = True
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return LunarDate(day=lunar_day, month=lunar_month, year=lunar_year, is_leap_month=lunar_leap)


def lunar_to_solar(
    day: int,
    month: int,
    year: int,
    is_leap_month: bool = False,
    tz_offset: float = 7.0,
) -> tuple[int, int, int]:
    """Convert a Vietnamese lunar date to a solar date ``(day, month, year)``."""
    if month < 11:
        a11 = _lunar_month_11(year - 1, tz_offset)
        b11 = _lunar_month_11(year, tz_offset)
    else:
        a11 = _lunar_month_11(year, tz_offset)
        b11 = _lunar_month_11(year + 1, tz_offset)
    k = int(0.5 + (a11 - 2415021.076998695) / 29.530588853)
    off = month - 11
    if off < 0:
        off += 12
    has_leap_month = b11 - a11 > 365
    if is_leap_month and not has_leap_month:
        raise ValueError(f"Năm âm lịch {year} không có tháng nhuận")
    if has_leap_month:
        leap_off = _leap_month_offset(a11, tz_offset)
        leap_month = leap_off - 2
        if leap_month < 0:
            leap_month += 12
        if is_leap_month and month != leap_month:
            raise ValueError(f"Năm âm lịch {year} không có tháng {month} nhuận")
        if is_leap_month or off >= leap_off:
            off += 1
    month_start = _new_moon_day(k + off, tz_offset)
    return jd_to_solar(month_start + day - 1)
