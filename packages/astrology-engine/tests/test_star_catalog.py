"""Catalog sao — định danh và thuộc tính của sao, tách khỏi chỗ sao được an.

Trọng tâm là **tính trung thực**: mỗi sao hoặc có ngũ hành ghi nhận được, hoặc để
trống hẳn. Không có trạng thái thứ ba kiểu "đoán tạm cho đủ màu", và metadata
tuyệt đối không được dịch chuyển vị trí an sao.
"""

from __future__ import annotations

import logging

import pytest

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.calendar.sexagenary import Element
from cosmic_astrology.chart.builder import _THIEN_PHU_CHAIN, _TU_VI_CHAIN
from cosmic_astrology.chart.model import StarCategory, display_priority_for
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender
from cosmic_astrology.conventions import COSMIC_SIGNS_STANDARD_V1
from cosmic_astrology.conventions.policies import RuleId, VerificationStatus
from cosmic_astrology.conventions.provenance import SourceReference
from cosmic_astrology.stars import (
    STAR_CATALOG,
    BlankReason,
    Polarity,
    StarDefinition,
    canonical_form,
    definition_for,
    metadata_coverage,
)
from cosmic_astrology.stars.report import render_report

#: Every star id any placement rule can emit today.
PLACED_IDS = tuple(star_id for star_id, _ in (*_TU_VI_CHAIN, *_THIEN_PHU_CHAIN))

MAJOR = StarCategory.MAJOR


def _chart(stage: EngineStage = EngineStage.PREVIEW) -> dict:
    return build_chart(
        BirthInput(
            name="star-catalog",
            gender=Gender.FEMALE,
            calendar_type=CalendarType.SOLAR,
            day=4,
            month=3,
            year=2001,
            hour=9,
            minute=30,
            timezone_id="Asia/Ho_Chi_Minh",
        ),
        stage=stage,
    ).to_dict()


def _placed_stars() -> list[dict]:
    return [s for p in _chart()["palaces"] for s in p["stars"]]


# --------------------------------------------------------------- catalog shape


def test_every_star_the_engine_can_place_exists_in_the_catalog() -> None:
    """Một sao được an mà catalog không biết sẽ mất tên và mất màu, âm thầm."""
    missing = [star_id for star_id in PLACED_IDS if definition_for(star_id) is None]
    assert missing == [], f"thiếu mục trong catalog: {missing}"
    assert len(PLACED_IDS) == 14

    # Phụ tinh nhóm 1 cũng phải có mặt, nếu không sẽ render bằng mã sao trơ.
    placed = {s["id"] for s in _placed_stars()}
    uncatalogued = [sid for sid in placed if definition_for(sid) is None]
    assert uncatalogued == [], f"thiếu mục trong catalog: {uncatalogued}"
    assert len(placed) == 88


def test_the_catalog_holds_all_fourteen_major_stars() -> None:
    expected = {
        "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh",
        "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương",
        "Thất Sát", "Phá Quân",
    }  # fmt: skip
    majors = [d for d in STAR_CATALOG.values() if d.category is MAJOR]
    assert {d.vietnamese_name for d in majors} == expected
    assert len(majors) == 14


def test_placement_rules_carry_ids_only_not_star_names() -> None:
    """Tên sao nằm ở catalog; luật an sao mang tên nữa là hai nguồn sự thật."""
    for entry in (*_TU_VI_CHAIN, *_THIEN_PHU_CHAIN):
        assert len(entry) == 2, entry
        star_id, offset = entry
        assert isinstance(star_id, str) and star_id.isupper()
        assert isinstance(offset, int)


def test_ids_are_unique_and_match_their_key() -> None:
    assert len({d.id for d in STAR_CATALOG.values()}) == len(STAR_CATALOG)
    for key, definition in STAR_CATALOG.items():
        assert key == definition.id


def test_names_are_unique() -> None:
    names = [d.vietnamese_name for d in STAR_CATALOG.values()]
    assert len(set(names)) == len(names)


@pytest.mark.parametrize("definition", sorted(STAR_CATALOG.values(), key=lambda d: d.id))
def test_canonical_name_is_the_diacritic_free_form(definition: StarDefinition) -> None:
    assert definition.canonical_name == canonical_form(definition.vietnamese_name)
    assert definition.canonical_name.isascii(), definition.canonical_name


def test_canonical_form_handles_the_letters_vietnamese_actually_uses() -> None:
    assert canonical_form("Thiên Đồng") == "Thien Dong"
    assert canonical_form("Tử Vi") == "Tu Vi"
    assert canonical_form("Phá Quân") == "Pha Quan"


def test_display_priority_comes_from_the_category() -> None:
    for definition in STAR_CATALOG.values():
        assert definition.display_priority == display_priority_for(definition.category)


# ----------------------------------------------------------- honesty invariants


@pytest.mark.parametrize("definition", sorted(STAR_CATALOG.values(), key=lambda d: d.id))
def test_element_and_polarity_are_recorded_together(definition: StarDefinition) -> None:
    """Sách ghi chúng trong cùng một câu, nên nửa câu không phải câu trả lời."""
    assert definition.has_element == definition.has_polarity, definition.vietnamese_name


@pytest.mark.parametrize("definition", sorted(STAR_CATALOG.values(), key=lambda d: d.id))
def test_every_entry_explains_itself(definition: StarDefinition) -> None:
    assert definition.note.strip(), f"{definition.vietnamese_name} không ghi lý do"


def test_stars_without_an_element_record_the_competing_readings() -> None:
    """Trống không được phép là im lặng: phải nói rõ các trường phái ghi gì."""
    disputed = [d for d in STAR_CATALOG.values() if d.blank_reason is BlankReason.DISPUTED]
    assert sorted(d.vietnamese_name for d in disputed) == [
        "Cự Môn",
        "Hữu Bật",
        "Tham Lang",
        "Đào Hoa",
    ]
    for definition in disputed:
        assert len(definition.alternatives) >= 2
        assert "CHƯA GHI NHẬN" in definition.note
        assert definition.verification_status is VerificationStatus.UNVERIFIED


def test_a_blank_element_always_says_why_it_is_blank() -> None:
    """Tranh chấp và chưa tra cứu là hai việc khác nhau: một bên phải CHỌN, một
    bên phải TÌM. Gộp lại là đánh mất thông tin về việc cần làm tiếp."""
    for definition in STAR_CATALOG.values():
        if definition.has_element:
            assert definition.blank_reason is None, definition.vietnamese_name
        else:
            assert definition.blank_reason is not None, definition.vietnamese_name


def test_nothing_is_verified_while_no_reference_edition_is_selected() -> None:
    """sources.json chưa chốt nguồn chuẩn, nên không mục nào được nhận VERIFIED."""
    for definition in STAR_CATALOG.values():
        assert definition.verification_status is not VerificationStatus.VERIFIED
        assert definition.provenance.has_citation is False
        assert definition.provenance.is_complete is False
        assert definition.provenance.note


def test_a_half_recorded_entry_is_rejected_at_construction() -> None:
    with pytest.raises(ValueError, match="cùng có hoặc cùng thiếu"):
        StarDefinition(
            id="X",
            canonical_name="Sao X",
            vietnamese_name="Sao X",
            category=MAJOR,
            element=Element.KIM,
            polarity=None,
            verification_status=VerificationStatus.PROVISIONAL,
            provenance=SourceReference(note="thử"),
            note="ghi chú",
        )


def test_an_entry_without_a_reason_is_rejected() -> None:
    with pytest.raises(ValueError, match="phải ghi lý do"):
        StarDefinition(
            id="X",
            canonical_name="Sao X",
            vietnamese_name="Sao X",
            category=MAJOR,
            element=Element.KIM,
            polarity=Polarity.YANG,
            verification_status=VerificationStatus.PROVISIONAL,
            provenance=SourceReference(note="thử"),
            note="   ",
        )


def test_a_blank_element_without_a_reason_is_rejected() -> None:
    with pytest.raises(ValueError, match="phải nói RÕ vì sao"):
        StarDefinition(
            id="X",
            canonical_name="Sao X",
            vietnamese_name="Sao X",
            category=MAJOR,
            element=None,
            polarity=None,
            verification_status=VerificationStatus.UNVERIFIED,
            provenance=SourceReference(note="thử"),
            note="chưa rõ",
        )


def test_claiming_a_dispute_without_listing_the_readings_is_rejected() -> None:
    with pytest.raises(ValueError, match="mâu thuẫn"):
        StarDefinition(
            id="X",
            canonical_name="Sao X",
            vietnamese_name="Sao X",
            category=MAJOR,
            element=None,
            polarity=None,
            verification_status=VerificationStatus.UNVERIFIED,
            provenance=SourceReference(note="thử"),
            note="chưa rõ",
            alternatives=("chỉ một cách đọc",),
            blank_reason=BlankReason.DISPUTED,
        )


def test_a_star_without_an_element_cannot_claim_to_be_provisional() -> None:
    """Không có giá trị thì không có gì để 'tạm tin' cả."""
    with pytest.raises(ValueError, match="không thể là PROVISIONAL"):
        StarDefinition(
            id="X",
            canonical_name="Sao X",
            vietnamese_name="Sao X",
            category=MAJOR,
            element=None,
            polarity=None,
            verification_status=VerificationStatus.PROVISIONAL,
            provenance=SourceReference(note="thử"),
            note="chưa rõ",
            alternatives=("cách đọc A", "cách đọc B"),
            blank_reason=BlankReason.DISPUTED,
        )


def test_verified_requires_a_complete_citation() -> None:
    """Không ai được nâng lên VERIFIED chỉ bằng cách sửa file này."""
    with pytest.raises(ValueError, match="chỉ được VERIFIED"):
        StarDefinition(
            id="X",
            canonical_name="Sao X",
            vietnamese_name="Sao X",
            category=MAJOR,
            element=Element.KIM,
            polarity=Polarity.YANG,
            verification_status=VerificationStatus.VERIFIED,
            provenance=SourceReference(note="chưa có trích dẫn"),
            note="ghi chú",
        )


def test_a_verified_entry_is_accepted_once_it_is_actually_sourced() -> None:
    """Cổng chặn phải mở được — nếu không thì nó chỉ là cấm cửa, không phải quy trình."""
    definition = StarDefinition(
        id="X",
        canonical_name="Sao X",
        vietnamese_name="Sao X",
        category=MAJOR,
        element=Element.KIM,
        polarity=Polarity.YANG,
        verification_status=VerificationStatus.VERIFIED,
        provenance=SourceReference(
            title="Tử Vi Đẩu Số Toàn Thư",
            year=1995,
            page="12",
            verified_by="người thẩm định",
            verified_at="2026-09-11",
        ),
        note="ghi chú",
    )
    assert definition.verification_status is VerificationStatus.VERIFIED


# ------------------------------------------------------------------- coverage


def test_coverage_is_counted_from_the_catalog_not_hardcoded() -> None:
    coverage = metadata_coverage()
    assert coverage.total == len(STAR_CATALOG)
    major = coverage.by_category(MAJOR)
    entries = [d for d in STAR_CATALOG.values() if d.category is MAJOR]
    assert major.total == len(entries)
    assert major.with_element == sum(1 for d in entries if d.has_element)
    assert major.with_polarity == sum(1 for d in entries if d.has_polarity)
    assert major.element_percentage == round(major.with_element / major.total * 100, 1)


def test_every_category_has_a_row_even_at_zero() -> None:
    """0/0 là một sự thật đáng thấy, không phải một hàng nên giấu đi."""
    coverage = metadata_coverage()
    assert {row.category for row in coverage.categories} == set(StarCategory)
    # Chưa có sao nào thuộc các loại này — vẫn phải có hàng trong báo cáo.
    for category in (StarCategory.TRANSFORMATION, StarCategory.ANNUAL):
        assert coverage.by_category(category).total == 0


def test_all_five_elements_are_represented() -> None:
    used = {d.element for d in STAR_CATALOG.values() if d.element}
    assert used == set(Element)


def test_the_report_prints_the_counts_it_computed() -> None:
    """Báo cáo và dữ liệu phải là một; con số gõ tay sẽ trôi khỏi bảng."""
    major = metadata_coverage().by_category(MAJOR)
    text = render_report()
    assert f"{major.with_element}/{major.total}" in text
    assert f"Tổng số sao trong catalog: {len(STAR_CATALOG)}" in text
    for name in major.missing_element:
        assert name in text
    # Khoảng trống nguồn phải nêu rõ, không được lặng lẽ bỏ qua.
    assert "Chưa có trích dẫn" in text


def test_definition_for_returns_none_for_an_uncatalogued_star() -> None:
    assert definition_for("KHONG_CO_SAO_NAY") is None


# ------------------------------------------------------- metadata reaches DTO


def test_the_chart_dto_carries_catalogued_metadata() -> None:
    stars = _placed_stars()
    # 14 chính tinh + 13 phụ tinh nhóm 1 + 24 phụ tinh nhóm 2 (Nam phái).
    assert len(stars) == 88
    for star in stars:
        definition = definition_for(star["id"])
        assert definition is not None
        assert star["name"] == definition.vietnamese_name
        assert star["category"] == definition.category.value
        assert star["element"] == (definition.element.value if definition.element else None)
        assert star["polarity"] == (definition.polarity.value if definition.polarity else None)
        assert star["display_priority"] == definition.display_priority


def test_the_dto_never_invents_an_element() -> None:
    """Sao chưa tra được ngũ hành thì ra null — không có giá trị nào được đoán."""
    stars = _placed_stars()
    blank = {s["name"] for s in stars if not s["element"]}
    catalogued_blank = {d.vietnamese_name for d in STAR_CATALOG.values() if not d.has_element}
    assert blank <= catalogued_blank
    assert {"Tham Lang", "Cự Môn", "Hữu Bật", "Đào Hoa"} <= blank


def test_missing_element_stays_null_all_the_way_through() -> None:
    for star in _placed_stars():
        if star["id"] in {"THAM_LANG", "CU_MON"}:
            assert star["element"] is None
            assert star["polarity"] is None


def test_polarity_uses_only_the_two_declared_values() -> None:
    values = {s["polarity"] for s in _placed_stars()} - {None}
    assert values <= {p.value for p in Polarity}


def test_star_placement_trust_is_separate_from_metadata_trust() -> None:
    """Hai câu hỏi khác nhau: 'sao nằm đúng chỗ chưa' và 'sao này là hành gì'."""
    binding = COSMIC_SIGNS_STANDARD_V1.binding(RuleId.MAJOR_STARS)
    for star in _placed_stars():
        # Vị trí: lấy từ luật an sao.
        assert star["verification_status"] == binding.verification.value
        # Metadata: lấy từ catalog, và hai sao chưa ghi nhận thì UNVERIFIED.
        definition = definition_for(star["id"])
        assert definition is not None
        if star["id"] in {"THAM_LANG", "CU_MON"}:
            assert definition.verification_status is VerificationStatus.UNVERIFIED


# --------------------------------------------------------- placement untouched


def test_attaching_metadata_did_not_move_any_star() -> None:
    """Bất biến bảo vệ §9: catalog chỉ đi kèm sao, không quyết định sao nằm đâu."""
    chart = _chart()
    placed = {
        s["id"]: p["branch_index"] for p in chart["palaces"] for s in p["major_stars"]
    }
    tu_vi = placed["TU_VI"]
    thien_phu = placed["THIEN_PHU"]
    assert thien_phu == (4 - tu_vi) % 12
    for star_id, offset in _TU_VI_CHAIN:
        assert placed[star_id] == (tu_vi + offset) % 12
    for star_id, offset in _THIEN_PHU_CHAIN:
        assert placed[star_id] == (thien_phu + offset) % 12


def test_every_placed_star_has_a_known_category() -> None:
    known = {c.value for c in StarCategory}
    for star in _placed_stars():
        assert star["category"] in known
        assert star["is_major"] is (star["category"] == MAJOR.value)


def test_frame_stage_places_no_stars_at_all() -> None:
    assert [s for p in _chart(EngineStage.FRAME)["palaces"] for s in p["stars"]] == []


# --------------------------------------------------- uncatalogued star handling


def test_an_uncatalogued_star_is_reported_but_does_not_take_the_chart_down(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Thiếu metadata là lỗi lập trình, không phải vấn đề của người dùng.

    Mất cả lá số chỉ vì một sao chưa được ghi vào catalog thì tệ hơn là vẽ nó trơn.
    Nhưng im lặng thì càng tệ, nên nó phải được log — và tuyệt đối không được gán
    một ngũ hành bịa để trông cho đủ.
    """
    from cosmic_astrology.chart.builder import _placed_star

    with caplog.at_level(logging.WARNING):
        star = _placed_star("SAO_CHUA_CO_TRONG_CATALOG", "Tý", profile=COSMIC_SIGNS_STANDARD_V1)

    assert star.id == "SAO_CHUA_CO_TRONG_CATALOG"
    assert star.name == "SAO_CHUA_CO_TRONG_CATALOG", "không có tên thì dùng id, không bịa tên"
    assert star.element is None
    assert star.polarity is None
    assert star.category is StarCategory.OTHER
    assert star.palace_branch == "Tý"
    assert "catalog" in caplog.text.lower()


def test_a_catalogued_star_logs_nothing(caplog: pytest.LogCaptureFixture) -> None:
    """Cảnh báo phải hiếm, nếu không sẽ không ai đọc nó nữa."""
    from cosmic_astrology.chart.builder import _placed_star

    with caplog.at_level(logging.WARNING):
        _placed_star("TU_VI", "Tý", profile=COSMIC_SIGNS_STANDARD_V1)
    assert caplog.text == ""
