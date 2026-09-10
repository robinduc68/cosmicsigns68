/**
 * Mirror of the payload produced by `packages/astrology-engine`.
 * The engine is the source of truth — never widen these types on the client.
 */

export type Gender = 'MALE' | 'FEMALE'
export type CalendarType = 'SOLAR' | 'LUNAR'
export type EngineStage = 'FRAME' | 'PREVIEW' | 'FULL'
export type ElementCode = 'KIM' | 'MOC' | 'THUY' | 'HOA' | 'THO'
export type StarKind = 'MAJOR' | 'MINOR' | 'TRANSFORMATION'
export type StarStrength = 'MIEU' | 'VUONG' | 'DAC' | 'BINH' | 'HAM'

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

export interface ChartStar {
  code: string
  label: string
  kind: StarKind
  strength: StarStrength | null
  provisional: boolean
}

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

export interface ChartPayload {
  engine: { stage: EngineStage; version: string; is_authoritative: boolean }
  birth: {
    name: string
    gender: Gender
    calendar_type: CalendarType
    solar: { day: number; month: number; year: number; hour: number; minute: number }
    birth_place: string | null
    tz_offset: number
    hour_branch: string
    hour_branch_index: number
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
  created_at: string
}

export interface ChartDetail extends ChartSummary {
  note: string | null
  timezone_name: string
  tz_offset: number
  chart: ChartPayload
}
