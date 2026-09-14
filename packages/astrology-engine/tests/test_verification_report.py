"""The verification report must be derived, never asserted by hand."""

from __future__ import annotations

import json
from pathlib import Path

from cosmic_astrology.conventions import COSMIC_SIGNS_STANDARD_V1, RuleId, VerificationStatus
from cosmic_astrology.review import load_store
from cosmic_astrology.verification import DEFAULT_FIXTURE, build_report, render_report

PROFILE = COSMIC_SIGNS_STANDARD_V1


def test_the_report_covers_every_rule_in_the_profile() -> None:
    assert len(build_report().rules) == len(RuleId)


def test_fixture_counts_come_from_the_review_store_not_from_a_constant() -> None:
    data = json.loads(Path(DEFAULT_FIXTURE).read_text(encoding="utf-8"))
    summary = load_store().summary()
    stats = build_report().fixtures

    assert stats.total == summary["TOTAL"] == len(data["cases"])
    assert stats.verified == summary["VERIFIED"]
    assert stats.in_review == summary["IN_REVIEW"]
    assert stats.pending == summary["PENDING"]
    assert stats.disagreement == summary["DISAGREEMENT"]
    assert stats.blocked == summary["BLOCKED"]
    # The buckets are exhaustive: every case is counted exactly once.
    counted = (
        stats.verified + stats.in_review + stats.pending + stats.disagreement + stats.blocked
    )
    assert counted == stats.total


def test_the_report_reflects_rule_status_changes() -> None:
    """Change a binding, and the report has to follow — no hard-coded rows."""
    before = dict((label, status) for label, status, _ in build_report().rules)
    assert before["Late Zi hour"] == "UNVERIFIED"

    variant = PROFILE.with_rule(RuleId.LATE_ZI, policy="CIVIL_DAY")
    after = dict((label, status) for label, status, _ in build_report(variant).rules)
    assert after["Late Zi hour"] == "UNVERIFIED"  # policy chosen, still unverified

    verified = variant.with_rule(RuleId.LATE_ZI, verification=VerificationStatus.VERIFIED)
    final = dict((label, status) for label, status, _ in build_report(verified).rules)
    assert final["Late Zi hour"] == "VERIFIED"


def test_the_report_says_the_engine_is_not_production_ready_and_why() -> None:
    report = build_report()
    assert report.production_ready is False
    assert report.failures

    rendered = render_report(report)
    assert "COSMIC_SIGNS_NAM_PHAI_V1" in rendered
    assert "BLOCKED" in rendered
    assert "PROVISIONAL" in rendered
    assert "Sẵn sàng cho production: KHÔNG" in rendered


def test_a_missing_fixture_file_is_reported_not_silently_zeroed() -> None:
    stats = build_report(fixture_path=Path("/nonexistent/matrix.json")).fixtures
    assert stats.total == 0
    assert "KHÔNG TÌM THẤY" in stats.source_of_truth
