"""Hợp đồng dữ liệu của lá số.

Bộ test này không kiểm một luật tử vi nào. Nó kiểm **hình dạng** của payload và
một quy tắc duy nhất xuyên suốt dự án: *dữ liệu tử vi chưa biết thì phải là
``null``* — không "Unknown", không "N/A", không sao giữ chỗ, không độ sáng đoán.

Xem `docs/chart-data-contract.md`.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.chart.model import CHART_SCHEMA_VERSION, StarCategory
from cosmic_astrology.chart.types import (
    PALACE_ORDER,
    CalendarType,
    EngineStage,
    Gender,
    PalaceName,
    Star,
)
from cosmic_astrology.conventions.policies import VerificationStatus

#: Every key a star must carry. A star that grows a field without this list
#: growing too would reach the frontend as an undeclared surprise.
STAR_KEYS = {
    "id",
    "name",
    "category",
    "element",
    "polarity",
    "strength",
    "strength_verification",
    "palace_branch",
    "is_major",
    "is_annual",
    "is_transformation",
    "has_transformation",
    "transformations",
    "display_priority",
    "verification_status",
    "provenance",
    "provisional",
}

PALACE_KEYS = {
    "id",
    "name",
    "label",
    "branch",
    "branch_index",
    "stem",
    "stem_index",
    "element",
    "nap_am",
    "is_menh",
    "is_than",
    "has_tuan",
    "has_triet",
    "is_empty_main_star",
    "palace_index",
    "month_number",
    "major_stars",
    "minor_stars",
    "transformations",
    "annual_stars",
    "stars",
    "tuan",
    "triet",
    "cycles",
    "metadata",
}


def _birth() -> BirthInput:
    return BirthInput(
        name="Hợp đồng dữ liệu",
        gender=Gender.FEMALE,
        calendar_type=CalendarType.SOLAR,
        day=4,
        month=3,
        year=2001,
        hour=9,
        minute=30,
        timezone_id="Asia/Ho_Chi_Minh",
    )


@pytest.fixture
def payload() -> dict[str, Any]:
    chart = build_chart(
        _birth(), stage=EngineStage.PREVIEW, generated_at="2026-01-01T00:00:00+00:00"
    )
    # Through JSON, because that is how every consumer actually receives it.
    return json.loads(json.dumps(chart.to_dict(), ensure_ascii=False))


def test_the_payload_declares_its_schema_version(payload: dict[str, Any]) -> None:
    """Without this a reader has to probe for fields to guess the shape."""
    assert payload["schema_version"] == CHART_SCHEMA_VERSION


def test_identity_says_which_engine_and_rulebook_produced_the_chart(
    payload: dict[str, Any],
) -> None:
    identity = payload["identity"]
    assert identity["engine_version"]
    assert identity["convention_profile"]
    assert identity["convention_version"]
    assert identity["generated_at"] == "2026-01-01T00:00:00+00:00"
    # The engine does not name its own charts; persistence does.
    assert identity["chart_id"] is None
    # Taken from the profile's own gate, not asserted by hand.
    assert identity["production_ready"] is False


def test_all_twelve_palaces_exist_on_distinct_branches(payload: dict[str, Any]) -> None:
    palaces = payload["palaces"]
    assert len(palaces) == 12
    assert len({p["branch_index"] for p in palaces}) == 12
    assert len({p["name"] for p in palaces}) == 12


def test_every_palace_carries_both_a_branch_and_a_palace_name(payload: dict[str, Any]) -> None:
    """Địa chi là *chỗ*, tên cung là *cung nào* — hai khái niệm, không suy ra nhau."""
    for palace in payload["palaces"]:
        assert palace["branch"], palace
        assert palace["name"] in {p.value for p in PalaceName}
        assert palace["id"] == palace["name"]
        assert palace["palace_index"] == PALACE_ORDER.index(PalaceName(palace["name"]))


def test_palace_index_follows_the_palace_name_not_the_branch(payload: dict[str, Any]) -> None:
    """Nếu palace_index suy từ địa chi thì nó sẽ trùng branch_index — không được."""
    pairs = {(p["palace_index"], p["branch_index"]) for p in payload["palaces"]}
    assert any(pi != bi for pi, bi in pairs)


def test_every_palace_has_the_full_key_set(payload: dict[str, Any]) -> None:
    for palace in payload["palaces"]:
        assert set(palace) == PALACE_KEYS, sorted(set(palace) ^ PALACE_KEYS)


def test_every_star_uses_the_one_normalised_model(payload: dict[str, Any]) -> None:
    stars = [s for p in payload["palaces"] for s in p["stars"]]
    assert stars, "lá số PREVIEW phải có sao"
    for star in stars:
        assert set(star) == STAR_KEYS, sorted(set(star) ^ STAR_KEYS)
        assert star["category"] in {c.value for c in StarCategory}


def test_the_flat_star_list_is_exactly_the_grouped_lists(payload: dict[str, Any]) -> None:
    """Một tập sao, hai cách trình bày — không được lệch nhau."""
    for palace in payload["palaces"]:
        grouped = [
            *palace["major_stars"],
            *palace["minor_stars"],
            *palace["transformations"],
            *palace["annual_stars"],
        ]
        assert sorted(s["id"] for s in grouped) == sorted(s["id"] for s in palace["stars"])


def test_a_star_names_the_branch_it_sits_on(payload: dict[str, Any]) -> None:
    """Danh sách sao phẳng phải tự mô tả được, không cần cung bọc ngoài."""
    for palace in payload["palaces"]:
        for star in palace["stars"]:
            assert star["palace_branch"] == palace["branch"]


def test_unimplemented_astrology_values_are_null_not_placeholders(
    payload: dict[str, Any],
) -> None:
    """Quy tắc trung tâm: chưa cài thì ``null``, không phải "N/A" hay giá trị giả."""
    traditional = payload["traditional"]
    assert set(traditional) == {
        "chu_menh",
        "chu_than",
        "lai_nhan_cung",
        "can_luong",
        "nam_xem",
        "tuoi_xem",
    }
    assert all(value is None for value in traditional.values())

    for palace in payload["palaces"]:
        assert palace["month_number"] is None
        cycles = palace["cycles"]
        assert set(cycles) == {
            "major_cycle_age_start",
            "major_cycle_age_end",
            "major_cycle_index",
            "major_cycle_direction",
            "major_cycle_target",
            "annual_target",
            "trang_sinh_stage",
        }
        # Đại vận và Tràng Sinh đã cài; lưu niên thì chưa và phải để trống.
        assert cycles["annual_target"] is None
        assert cycles["major_cycle_target"] is None
        assert palace["metadata"] == {}

    # Lưu niên và Tứ Hóa chưa cài: rỗng, không phải dữ liệu bịa. `major_cycles` ở
    # gốc payload vẫn rỗng — đại vận nằm trên từng cung, chỗ nó thuộc về.
    assert payload["major_cycles"] == []
    assert payload["annual_cycles"] == []
    assert payload["four_transformations"] == {}


def test_no_string_field_smuggles_in_a_placeholder(payload: dict[str, Any]) -> None:
    """Chặn đúng những chuỗi hay được dùng thay cho ``null``."""
    banned = {"unknown", "n/a", "na", "none", "null", "tbd", "?", "-", "chưa rõ", "không rõ"}
    # `convention.rules` carries policy *names*, where NONE is a real choice
    # ("không hiệu chỉnh giờ sinh") rather than a stand-in for a missing value.
    skipped = {"chart.convention", "chart.trace"}

    def walk(node: object, path: str) -> None:
        if path in skipped:
            return
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")
        elif isinstance(node, str):
            assert node.strip().lower() not in banned, f"{path} = {node!r}"

    walk(payload, "chart")
    # The guard has to actually reach the astrology data, not just the skips.
    assert payload["palaces"] and payload["birth"]


def test_null_survives_json_serialisation(payload: dict[str, Any]) -> None:
    """``None`` phải qua JSON thành ``null``, không thành chuỗi "None"."""
    raw = json.dumps(payload, ensure_ascii=False)
    assert '"strength": null' in raw
    assert '"chu_menh": null' in raw
    assert '"None"' not in raw


def test_strength_is_absent_and_says_so_honestly(payload: dict[str, Any]) -> None:
    """Bảng miếu/vượng chưa cài, nên mọi độ sáng phải trống — cả hai nửa."""
    for palace in payload["palaces"]:
        for star in palace["stars"]:
            assert star["strength"] is None
            assert star["strength_verification"] is None


def test_a_strength_without_its_verification_is_rejected() -> None:
    """Có giá trị mà không có mức tin cậy là cách "chưa biết" bị đọc thành "đã kiểm"."""
    from cosmic_astrology.chart.types import StarStrength

    with pytest.raises(ValueError, match="cùng có hoặc cùng thiếu"):
        Star(
            id="X",
            name="Sao X",
            category=StarCategory.MAJOR,
            strength=StarStrength.MIEU,
        )


def test_verification_metadata_survives_serialisation(payload: dict[str, Any]) -> None:
    """Mức tin cậy phải đi cùng dữ liệu, nếu không nó sẽ bị đọc là sự thật."""
    for palace in payload["palaces"]:
        for star in palace["stars"]:
            assert star["verification_status"] in {v.value for v in VerificationStatus}
            provenance = star["provenance"]
            assert provenance is not None, star["name"]
            # Provenance phải chỉ đúng LUẬT đã đặt sao đó, không phải một luật chung.
            rule, _, policy = provenance["rule"].partition("/")
            assert rule in {r["rule"] for r in payload["convention"]["rules"]}
            assert policy, star["name"]
            assert provenance["verification"] == star["verification_status"]
            # Chặn bởi câu hỏi mở nào phải nói ra, không được ẩn trong code.
            assert provenance["blocked_by"], star["name"]

    for palace in payload["palaces"]:
        for mark in (palace["tuan"], palace["triet"]):
            assert set(mark) == {"present", "verification", "source_rule"}
            assert isinstance(mark["present"], bool)
            assert mark["verification"] in {v.value for v in VerificationStatus}


def test_a_star_never_claims_more_trust_than_the_rule_that_placed_it(
    payload: dict[str, Any],
) -> None:
    rules = {r["rule"]: r for r in payload["convention"]["rules"]}
    major = rules["major_stars"]["verification"]
    for palace in payload["palaces"]:
        for star in palace["major_stars"]:
            assert star["verification_status"] == major


def test_birth_information_reports_the_offset_actually_used(payload: dict[str, Any]) -> None:
    birth = payload["birth"]
    assert birth["full_name"] == birth["name"]
    assert birth["local_birth_time"] == "09:30"
    assert birth["timezone_id"] == "Asia/Ho_Chi_Minh"
    # The resolved offset, not the one a caller asked for.
    assert birth["historical_utc_offset"] == payload["timezone"]["utc_offset_hours"]


def test_schema_version_1_keys_are_still_emitted(payload: dict[str, Any]) -> None:
    """Renderer và 11 lá số đã lưu vẫn đọc những khóa này, nên không được bỏ."""
    for key in ("engine", "convention", "birth", "lunar_birth", "pillars", "yin_yang"):
        assert key in payload
    for key in ("branch", "name", "label", "has_tuan", "has_triet", "major_stars"):
        assert key in payload["palaces"][0]


def test_frame_stage_produces_the_same_shape_with_no_stars() -> None:
    """Hình dạng payload không được phụ thuộc vào việc đã an sao hay chưa."""
    frame = build_chart(_birth(), stage=EngineStage.FRAME).to_dict()
    assert frame["schema_version"] == CHART_SCHEMA_VERSION
    for palace in frame["palaces"]:  # type: ignore[index]
        assert set(palace) == PALACE_KEYS
        assert palace["stars"] == []
