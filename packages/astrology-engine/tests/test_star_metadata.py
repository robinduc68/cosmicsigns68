"""Ngũ hành của sao — metadata, không phải suy diễn từ tên.

Trọng tâm của bộ test này là **tính trung thực**: mỗi sao hoặc có ngũ hành ghi
nhận được, hoặc để trống hẳn. Không có trạng thái thứ ba nào kiểu "đoán tạm cho
đủ màu", và metadata tuyệt đối không được dịch chuyển vị trí an sao.
"""

from __future__ import annotations

import pytest

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.calendar.sexagenary import Element
from cosmic_astrology.chart.builder import _THIEN_PHU_CHAIN, _TU_VI_CHAIN
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender, StarKind
from cosmic_astrology.conventions import COSMIC_SIGNS_STANDARD_V1
from cosmic_astrology.conventions.policies import RuleId, VerificationStatus
from cosmic_astrology.stars import (
    STAR_METADATA,
    Polarity,
    StarMetadata,
    element_coverage,
    metadata_for,
)

PLACED_CODES = tuple(code for code, _, _ in (*_TU_VI_CHAIN, *_THIEN_PHU_CHAIN))


def _chart() -> dict[str, object]:
    return build_chart(
        BirthInput(
            name="star-metadata",
            gender=Gender.FEMALE,
            calendar_type=CalendarType.SOLAR,
            day=4,
            month=3,
            year=2001,
            hour=9,
            minute=30,
            timezone_id="Asia/Ho_Chi_Minh",
        ),
        stage=EngineStage.PREVIEW,
    ).to_dict()


def test_the_catalogue_covers_exactly_the_stars_the_engine_places() -> None:
    """A star the engine places but the catalogue forgot would silently lose colour."""
    assert sorted(STAR_METADATA) == sorted(PLACED_CODES)
    assert len(PLACED_CODES) == 14


def test_labels_agree_with_the_placement_tables() -> None:
    placed_labels = {code: label for code, label, _ in (*_TU_VI_CHAIN, *_THIEN_PHU_CHAIN)}
    assert {c: m.label for c, m in STAR_METADATA.items()} == placed_labels


@pytest.mark.parametrize("meta", sorted(STAR_METADATA.values(), key=lambda m: m.code))
def test_element_and_polarity_are_recorded_together(meta: StarMetadata) -> None:
    """The sources state them in one phrase, so half an answer is not an answer."""
    assert (meta.element is None) == (meta.polarity is None), meta.label


def test_a_half_recorded_entry_is_rejected_at_construction() -> None:
    """Ngũ hành có mà âm/dương không, hay ngược lại, là dấu hiệu đã điền nửa vời."""
    with pytest.raises(ValueError, match="cùng có hoặc cùng thiếu"):
        StarMetadata("X", "Sao X", Element.KIM, None, "ghi chú")


def test_an_entry_without_a_reason_is_rejected() -> None:
    with pytest.raises(ValueError, match="phải ghi lý do"):
        StarMetadata("X", "Sao X", Element.KIM, Polarity.YANG, "   ")


def test_a_blank_element_without_alternatives_is_rejected() -> None:
    """Để trống phải kèm lý do cụ thể, không được là một ô trống lặng lẽ."""
    with pytest.raises(ValueError, match="mâu thuẫn"):
        StarMetadata("X", "Sao X", None, None, "chưa rõ", ("chỉ một cách đọc",))


@pytest.mark.parametrize("meta", sorted(STAR_METADATA.values(), key=lambda m: m.code))
def test_every_entry_explains_itself(meta: StarMetadata) -> None:
    assert meta.note.strip(), f"{meta.label} không ghi lý do"


def test_stars_without_an_element_record_the_competing_readings() -> None:
    """Trống không được phép là im lặng: phải nói rõ các trường phái ghi gì."""
    blank = [m for m in STAR_METADATA.values() if not m.has_element]
    assert [m.label for m in blank] == ["Tham Lang", "Cự Môn"]
    for meta in blank:
        assert len(meta.alternatives) >= 2, f"{meta.label} thiếu danh sách cách đọc khác"
        assert "CHƯA GHI NHẬN" in meta.note


def test_coverage_is_counted_from_the_table_not_hardcoded() -> None:
    coverage = element_coverage()
    entries = tuple(STAR_METADATA.values())
    assert coverage.total == len(entries)
    assert coverage.with_element == sum(1 for m in entries if m.has_element)
    assert coverage.missing == tuple(m.label for m in entries if not m.has_element)
    assert coverage.percentage == round(coverage.with_element / coverage.total * 100, 1)


def test_all_five_elements_are_represented() -> None:
    """Nếu thiếu một hành thì bảng màu không bao giờ được kiểm bằng mắt đầy đủ."""
    used = {m.element for m in STAR_METADATA.values() if m.element}
    assert used == set(Element)


def test_metadata_for_returns_none_for_an_uncatalogued_star() -> None:
    """Phụ tinh sẽ xuất hiện trước khi được ghi nhận hành — đó là câu trả lời hợp lệ."""
    assert metadata_for("KHONG_CO_SAO_NAY") is None


def test_the_rule_is_declared_provisional_and_blocked() -> None:
    """Chưa chốt nguồn chuẩn thì không sao nào được coi là đã kiểm định."""
    binding = COSMIC_SIGNS_STANDARD_V1.binding(RuleId.STAR_ELEMENTS)
    assert binding.implemented is True
    assert binding.verification is VerificationStatus.PROVISIONAL
    assert binding.verification is not VerificationStatus.VERIFIED
    assert set(binding.blocked_by) >= {"Q1", "Q2", "Q3"}
    assert binding.source.is_complete is False


def test_the_chart_dto_carries_element_and_polarity() -> None:
    stars = [s for p in _chart()["palaces"] for s in p["major_stars"]]  # type: ignore[index]
    assert len(stars) == 14
    for star in stars:
        meta = metadata_for(star["code"])
        assert meta is not None
        assert star["element"] == (meta.element.value if meta.element else None)
        assert star["polarity"] == (meta.polarity.value if meta.polarity else None)


def test_the_dto_never_invents_an_element() -> None:
    """Đúng 12 sao có màu, 2 sao không — số này phải khớp bảng, không được nhiều hơn."""
    stars = [s for p in _chart()["palaces"] for s in p["major_stars"]]  # type: ignore[index]
    coloured = [s["label"] for s in stars if s["element"]]
    assert len(coloured) == element_coverage().with_element
    assert sorted(s["label"] for s in stars if not s["element"]) == ["Cự Môn", "Tham Lang"]


def test_polarity_uses_only_the_two_declared_values() -> None:
    stars = [s for p in _chart()["palaces"] for s in p["major_stars"]]  # type: ignore[index]
    values = {s["polarity"] for s in stars} - {None}
    assert values <= {p.value for p in Polarity}


def test_attaching_metadata_did_not_move_any_star() -> None:
    """Bất biến bảo vệ §23: metadata chỉ đi kèm sao, không quyết định sao nằm đâu.

    Vị trí kỳ vọng suy từ chính hai chuỗi an sao (Tử Vi nghịch, Thiên Phủ thuận) —
    độc lập với bảng ngũ hành, nên nếu metadata có ảnh hưởng thì test này vỡ.
    """
    chart = _chart()
    placed = {
        s["code"]: p["branch_index"]
        for p in chart["palaces"]  # type: ignore[index]
        for s in p["major_stars"]
    }
    tu_vi = placed["TU_VI"]
    thien_phu = placed["THIEN_PHU"]
    assert thien_phu == (4 - tu_vi) % 12
    for code, _, offset in _TU_VI_CHAIN:
        assert placed[code] == (tu_vi + offset) % 12
    for code, _, offset in _THIEN_PHU_CHAIN:
        assert placed[code] == (thien_phu + offset) % 12


def test_every_placed_star_is_a_major_star_of_known_kind() -> None:
    for palace in _chart()["palaces"]:  # type: ignore[index]
        for star in palace["major_stars"]:
            assert star["kind"] == StarKind.MAJOR.value
