# DEVELOPMENT FIXTURES — not astrology truth

Every `*.json` here is **unmodified output of the Cosmic Signs engine**, captured to
give the renderer and its tests a stable payload to work against. Regenerate them —
never hand-edit them:

```bash
apps/api/.venv/bin/python packages/astrology-engine/scripts/dump_web_fixtures.py
```

`generated_at` is pinned so the files are byte-stable; a regeneration that changes
nothing produces no diff, which is what makes a real contract change visible.

## These are not expected astrology values

The engine's placements are `PROVISIONAL`: the 14 chính tinh, Cục, palace order and
palace stems have not been signed off against a chosen source (Q1/Q2/Q3 in
`docs/astrology-conventions.md`). **Do not** treat any value in these files as
correct astrology, and do not derive expected values for a new test from them — that
is exactly how the mirrored-palace bug survived its own test suite.

Values that are genuinely verified against a definition live in
`packages/astrology-engine/tests/fixtures/` instead, where the expectation is
derived from the rule rather than from the engine.

## Which file shows what

| File | Stage | Shows |
| --- | --- | --- |
| `cross-check-2001.preview.json` | PREVIEW | The complete schema v2 payload: 14 chính tinh, Tuần/Triệt, a vô-chính-diệu palace |
| `cross-check-2001.frame.json` | FRAME | A chart with no stars placed at all |
| `reference-1992.preview.json` | PREVIEW | Mệnh at Dần; Tuần and Triệt on separate rows |
| `at-suu-1985.preview.json` | PREVIEW | Triệt spanning a horizontal border |

Nullable-but-unimplemented fields (`traditional.*`, `cycles.*`, `month_number`,
every `strength`) are `null` in all four, and that is correct — see
`docs/chart-data-contract.md`.
