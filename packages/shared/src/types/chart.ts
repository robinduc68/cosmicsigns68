/**
 * Mirror of the payload produced by `packages/astrology-engine`.
 * The engine is the source of truth — never widen these types on the client.
 */

export type Gender = 'MALE' | 'FEMALE'
export type CalendarType = 'SOLAR' | 'LUNAR'
export type EngineStage = 'FRAME' | 'PREVIEW' | 'FULL'
export type ElementCode = 'KIM' | 'MOC' | 'THUY' | 'HOA' | 'THO'
/**
 * What kind of star this is. Only `MAJOR` is produced today; the rest exist so
 * minor, annual and transformation stars arrive into a settled contract.
 */
export type StarCategory =
  | 'MAJOR'
  | 'SUPPORTING'
  | 'MALEFIC'
  | 'LITERARY'
  | 'ROMANCE'
  | 'WEALTH'
  | 'TRANSFORMATION'
  | 'ANNUAL'
  | 'OTHER'

/** How far a school-dependent value is trusted. Never inferred on the client. */
export type VerificationStatus = 'UNVERIFIED' | 'PROVISIONAL' | 'VERIFIED'
export type StarStrength = 'MIEU' | 'VUONG' | 'DAC' | 'BINH' | 'HAM'
/** Âm/dương of a star. Drives a `+`/`−` prefix only — never a colour. */
export type YinYangPolarity = 'YANG' | 'YIN'

export type PalaceCode =
  | 'MENH'
  | 'PHU_MAU'
  | 'PHUC_DUC'
  | 'DIEN_TRACH'
  | 'QUAN_LOC'
  | 'NO_BOC'
  | 'THIEN_DI'
  | 'TAT_ACH'
  | 'TAI_BACH'
  | 'TU_TUC'
  | 'PHU_THE'
  | 'HUYNH_DE'

/** Where a star's placement came from, and how far that rule is trusted. */
export interface StarProvenance {
  rule: string
  verification: VerificationStatus
  /** Open-question ids still blocking this rule, e.g. `['Q1', 'Q2']`. */
  blocked_by: string[]
  note: string
}

/**
 * One star, whatever its category — there is no separate major/minor/annual DTO.
 *
 * Fields marked *schema v1* are absent from charts persisted before the data
 * contract existed; `mapChartDtoToViewModel` resolves both shapes. Every
 * astrology value is nullable, and `null` means "not computed or not verified" —
 * it is never replaced by a placeholder downstream.
 */
export interface ChartStar {
  /** Absent on schema v1, which used `code`. */
  id?: string
  /** Absent on schema v1, which used `label`. */
  name?: string
  /** Absent on schema v1, which used `kind`. */
  category?: StarCategory
  /**
   * Ngũ hành of the star itself, declared by the engine. `null` where the schools
   * disagree; the renderer draws neutral ink and never infers one from the name.
   */
  element: ElementCode | null
  polarity: YinYangPolarity | null
  strength: StarStrength | null
  /** Set exactly when `strength` is set, so unknown is never read as verified. */
  strength_verification?: VerificationStatus | null
  /** Địa chi the star sits on — the star is self-describing in a flat list. */
  palace_branch?: string | null
  is_major?: boolean
  is_annual?: boolean
  is_transformation?: boolean
  /** Engine-supplied display order. The renderer sorts by this, never by name. */
  display_priority?: number
  verification_status?: VerificationStatus
  provenance?: StarProvenance | null
  provisional: boolean
  /** @deprecated schema v1 field. Use `id`. */
  code?: string
  /** @deprecated schema v1 field. Use `name`. */
  label?: string
  /** @deprecated schema v1 field. Use `category`. */
  kind?: 'MAJOR' | 'MINOR' | 'TRANSFORMATION'
}

/** Tuần or Triệt on a palace, with the rule that placed it. */
export interface ChartVoidMark {
  present: boolean
  verification: VerificationStatus | null
  source_rule: string | null
}

/**
 * Đại vận / Tràng Sinh / lưu niên for one palace.
 *
 * Đại vận and Tràng Sinh are computed; `annual_target` is not. Everything here is
 * `PROVISIONAL` — see `docs/astrology-conventions.md` §24–25.
 */
export interface ChartPalaceCycles {
  major_cycle_age_start: number | null
  major_cycle_age_end: number | null
  /** 1-based position in the đại vận walk; 1 is cung Mệnh. */
  major_cycle_index: number | null
  /**
   * `'FORWARD'` (thuận) or `'BACKWARD'` (nghịch). Describes the walk only — the
   * twelve palace names never reverse with it.
   */
  major_cycle_direction: 'FORWARD' | 'BACKWARD' | null
  major_cycle_target: number | null
  /** Lưu niên — still null, and out of scope. */
  annual_target: number | null
  /** One of the twelve Tràng Sinh stages. */
  trang_sinh_stage: string | null
}

/**
 * One of the twelve palaces.
 *
 * `branch` is *where* on the địa bàn this cell sits; `name` is *which palace* the
 * engine assigned there. They are different concepts and the client must never
 * derive one from the other.
 */
export interface ChartPalace {
  name: PalaceCode
  label: string
  branch: string
  branch_index: number
  stem: string
  stem_index: number
  element: ElementCode
  nap_am: string
  is_menh: boolean
  is_than: boolean
  has_tuan: boolean
  has_triet: boolean
  is_empty_main_star: boolean
  major_stars: ChartStar[]
  minor_stars: ChartStar[]
  transformations: ChartStar[]
  /** Absent on schema v1. Equal to `name`; present so a palace is addressable. */
  id?: PalaceCode
  /** Position of this palace name in the classical sequence from Mệnh (0-11). */
  palace_index?: number
  /** Lunar month this palace counts as. `null` — depends on đại vận numbering. */
  month_number?: number | null
  annual_stars?: ChartStar[]
  /** The same stars as the grouped lists above, flat and ungrouped. */
  stars?: ChartStar[]
  tuan?: ChartVoidMark
  triet?: ChartVoidMark
  cycles?: ChartPalaceCycles
  /** Palace facts that are neither stars nor cycles. Empty today. */
  metadata?: Record<string, unknown>
}

export interface ChartPillar {
  can: string
  chi: string
  can_index: number
  chi_index: number
  name: string
  is_yang: boolean
  nap_am: string
  element: ElementCode
}

/** Which convention profile produced a chart, and how far each rule is trusted. */
export interface ConventionRule {
  rule: string
  policy: string
  implemented: boolean
  verification: 'UNVERIFIED' | 'PROVISIONAL' | 'VERIFIED'
  /** `BLOCKED` when a rule is unimplemented and waiting on an open question. */
  status: string
  blocked_by: string[]
  note: string
}

/** Which engine and rulebook produced a chart, and when. */
export interface ChartIdentity {
  /** Assigned by whatever stores the chart; `null` straight out of the engine. */
  chart_id: string | null
  engine_version: string
  convention_profile: string
  convention_version: string
  /** False while any critical rule is still provisional or unresolved. */
  production_ready: boolean
  /** UTC ISO-8601 — when the calculation ran, not when the person was born. */
  generated_at: string
}

/**
 * Traditional fields a printed chart carries that this engine does not compute.
 * All four are `null` and stay `null` until each is implemented against a source.
 */
export interface ChartTraditionalMetadata {
  chu_menh: string | null
  chu_than: string | null
  lai_nhan_cung: string | null
  /** Cân lượng — cân xương tính số. */
  can_luong: string | null
  /** Năm xem. Meaningful only paired with `tuoi_xem`, so both stay null together. */
  nam_xem: number | null
  /** Tuổi xem. Blocked on Q11: tuổi ta and completed years differ by a year. */
  tuoi_xem: number | null
}

export interface ChartPayload {
  /** Absent on charts persisted before the data contract; those are version 1. */
  schema_version?: number
  identity?: ChartIdentity
  traditional?: ChartTraditionalMetadata
  engine: {
    stage: EngineStage
    version: string
    is_authoritative: boolean
    convention_profile: string
    convention_version: string
  }
  convention: {
    profile: string
    version: string
    rules: ConventionRule[]
  }
  timezone: {
    policy: string
    timezone_id: string | null
    utc_offset_hours: number
    source: string
    /** False when the offset came from the caller rather than the tz database. */
    resolved_from_database: boolean
  }
  date_resolution: {
    civil_solar: number[]
    placement_solar: number[]
    day_pillar_solar: number[]
    late_zi: boolean
    late_zi_policy: string
    /** False only under `PILLAR_ONLY_NEXT_DAY`, which is asymmetric by design. */
    internally_consistent: boolean
  }
  birth: {
    name: string
    gender: Gender
    calendar_type: CalendarType
    solar: { day: number; month: number; year: number; hour: number; minute: number }
    birth_place: string | null
    tz_offset: number
    hour_branch: string
    hour_branch_index: number
    /** Added in schema v2. Same value as `name`, under the contract's own name. */
    full_name?: string
    /** `"09:30"`. Local clock time as given, before any timezone resolution. */
    local_birth_time?: string
    timezone_id?: string | null
    /**
     * The offset actually used, resolved from the tz database at the birth instant.
     * Distinct from the zone id because Vietnam's offset has changed over time.
     */
    historical_utc_offset?: number
  }
  lunar_birth: {
    day: number
    month: number
    year: number
    is_leap_month: boolean
    year_pillar: string
  }
  pillars: { year: ChartPillar; month: ChartPillar; day: ChartPillar; hour: ChartPillar }
  yin_yang: {
    year_is_yang: boolean
    gender_is_male: boolean
    label: string
    is_thuan_ly: boolean
  }
  menh: {
    branch: string
    branch_index: number
    element: ElementCode
    element_label: string
    nap_am: string
    three_directions_four_positions: {
      self: number
      trine_left: number
      trine_right: number
      opposite: number
    }
  }
  than: { branch: string; branch_index: number; resides_in: PalaceCode; resides_in_label: string }
  cuc: {
    number: number
    element: ElementCode
    element_label: string
    label: string
    relation: string
    relation_label: string
  }
  palaces: ChartPalace[]
  major_cycles: unknown[]
  annual_cycles: unknown[]
  four_transformations: Record<string, unknown>
}

export interface ChartSummary {
  id: string
  subject_name: string
  relationship_label: string | null
  gender: Gender
  calendar_type: CalendarType
  birth_day: number
  birth_month: number
  birth_year: number
  birth_hour: number
  birth_minute: number
  birth_place: string | null
  engine_stage: EngineStage
  engine_version: string
  convention_profile: string | null
  convention_version: string | null
  created_at: string
}

/** Whether a stored chart predates the conventions or engine now in force. */
export interface RecalculationStatus {
  needed: boolean
  reason: string
}

export interface ChartDetail extends ChartSummary {
  note: string | null
  /**
   * Payload shape of `chart`. Computed by the API, not stored: rows written
   * before the data contract report 1 and keep their original fields.
   */
  chart_schema_version: number | null
  /** Never acted on automatically — a stored chart is not rewritten under its reader. */
  recalculation: RecalculationStatus | null
  timezone_name: string
  tz_offset: number
  chart: ChartPayload
}
