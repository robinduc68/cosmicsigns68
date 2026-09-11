import { CHART_GRID_BRANCH_INDEXES, EARTHLY_BRANCHES } from '@cosmic/shared'

/**
 * Client for the internal verification workbench.
 *
 * Deliberately has no helper that copies engine output into expected values —
 * the omission is the safeguard. A reviewer types what the source says.
 */

export type ReviewState = 'PENDING' | 'IN_REVIEW' | 'VERIFIED' | 'DISAGREEMENT' | 'BLOCKED'
export type ComparisonStatus = 'MATCH' | 'MISMATCH' | 'UNVERIFIED'

export interface StarComparison {
  star: string
  engine: string | null
  expected: string | null
  status: ComparisonStatus
}

export interface FixtureSummary {
  id: string
  purpose: string
  birth_date: string
  birth_time: string
  calendar: string
  gender: string
  timezone: string | null
  utc_offset: number | null
  lunar_date: string | null
  menh: string | null
  cuc: string | null
  state: ReviewState
  blockers: string[]
  mismatches: string[]
  reviewer: string | null
  source: { id: string; title: string; source_type: string } | null
  blocked_reason: string | null
  is_anchor: boolean
}

export interface TraceStep {
  rule: string
  result: string
  inputs: Record<string, unknown>
  policy: string
  verification: string
  blocked_by: string[]
  note: string
}

export interface PalaceComparison {
  name: string
  label: string
  branch: string
  is_menh: boolean
  is_than: boolean
  has_tuan: boolean
  has_triet: boolean
  engine_stars: string[]
  expected_stars: string[] | null
  matches: boolean | null
}

export interface FixtureReview {
  state: ReviewState
  expected_tu_vi: string | null
  expected_stars: Record<string, string> | null
  expected_tuan: string[] | null
  expected_triet: string[] | null
  independently_confirmed: boolean
  reviewer: string | null
  reviewed_at: string | null
  source_id: string | null
  page: string | null
  notes: string
}

export interface FixtureDetail {
  id: string
  purpose: string
  input: Record<string, string | number | boolean | null>
  timezone_context: Record<string, unknown> | null
  derived_frame: Record<string, unknown> | null
  engine_candidate_stars: Record<string, string> | null
  review: FixtureReview
  state: { state: ReviewState; blockers: string[]; mismatches: string[] }
  comparisons: StarComparison[]
  palaces: PalaceComparison[]
  trace: TraceStep[]
  source: Record<string, unknown> | null
  blocked_reason: string | null
  late_zi_demonstration: Record<string, Record<string, unknown>> | null
  anchor_tu_vi: string | null
  anchor_basis: string | null
}

export interface VerificationSource {
  id: string
  title: string
  source_type: string
  author: string | null
  edition: string | null
  publication_year: number | null
  publisher: string | null
  school: string | null
  notes: string
  is_citable: boolean
}

export const MAJOR_STAR_CODES = [
  'TU_VI', 'THIEN_CO', 'THAI_DUONG', 'VU_KHUC', 'THIEN_DONG', 'LIEM_TRINH',
  'THIEN_PHU', 'THAI_AM', 'THAM_LANG', 'CU_MON', 'THIEN_TUONG', 'THIEN_LUONG',
  'THAT_SAT', 'PHA_QUAN',
] as const

export const STAR_LABELS: Record<string, string> = {
  TU_VI: 'Tử Vi',
  THIEN_CO: 'Thiên Cơ',
  THAI_DUONG: 'Thái Dương',
  VU_KHUC: 'Vũ Khúc',
  THIEN_DONG: 'Thiên Đồng',
  LIEM_TRINH: 'Liêm Trinh',
  THIEN_PHU: 'Thiên Phủ',
  THAI_AM: 'Thái Âm',
  THAM_LANG: 'Tham Lang',
  CU_MON: 'Cự Môn',
  THIEN_TUONG: 'Thiên Tướng',
  THIEN_LUONG: 'Thiên Lương',
  THAT_SAT: 'Thất Sát',
  PHA_QUAN: 'Phá Quân',
}

/** Branch options for the reviewer's dropdowns, in địa bàn reading order. */
export const BRANCH_OPTIONS = CHART_GRID_BRANCH_INDEXES.filter(
  (index): index is number => index !== null,
).map((index) => ({ value: EARTHLY_BRANCHES[index]!, label: EARTHLY_BRANCHES[index]! }))

const BASE = '/api/v1/_internal/verification'

export function useVerification() {
  const { request } = useApi()

  return {
    listFixtures: () =>
      request<FixtureSummary[]>(`${BASE}/fixtures`),
    fixtureDetail: (id: string) => request<FixtureDetail>(`${BASE}/fixtures/${id}`),
    saveReview: (id: string, body: Partial<FixtureReview>) =>
      request<{ state: FixtureDetail['state']; review: FixtureReview }>(
        `${BASE}/fixtures/${id}/review`,
        { method: 'PUT', body },
      ),
    progress: () =>
      request<{
        profile: string
        version: string
        fixtures: Record<string, number>
        rules: { rule: string; status: string; blocked_by: string[]; policy: string }[]
        production_ready: boolean
        failures: string[]
        primary_source: VerificationSource | null
        open_discrepancies: Record<string, unknown>[]
      }>(`${BASE}/progress`),
    sources: () =>
      request<{ sources: { sources: VerificationSource[] }; source_types: string[] }>(
        `${BASE}/sources`,
      ),
    recordDiscrepancy: (body: Record<string, unknown>) =>
      request<Record<string, unknown>>(`${BASE}/discrepancies`, { method: 'POST', body }),
  }
}
