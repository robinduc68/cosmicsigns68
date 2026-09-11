import type { ElementCode, PalaceCode, StarStrength } from '../types/chart'

/** Reading order of the palaces, starting at Mệnh. Not the grid layout. */
export const PALACE_ORDER: PalaceCode[] = [
  'MENH',
  'PHU_MAU',
  'PHUC_DUC',
  'DIEN_TRACH',
  'QUAN_LOC',
  'NO_BOC',
  'THIEN_DI',
  'TAT_ACH',
  'TAI_BACH',
  'TU_TUC',
  'PHU_THE',
  'HUYNH_DE',
]

export const PALACE_LABELS: Record<PalaceCode, string> = {
  MENH: 'Mệnh',
  PHU_MAU: 'Phụ Mẫu',
  PHUC_DUC: 'Phúc Đức',
  DIEN_TRACH: 'Điền Trạch',
  QUAN_LOC: 'Quan Lộc',
  NO_BOC: 'Nô Bộc',
  THIEN_DI: 'Thiên Di',
  TAT_ACH: 'Tật Ách',
  TAI_BACH: 'Tài Bạch',
  TU_TUC: 'Tử Tức',
  PHU_THE: 'Phu Thê',
  HUYNH_DE: 'Huynh Đệ',
}

export const ELEMENT_LABELS: Record<ElementCode, string> = {
  KIM: 'Kim',
  MOC: 'Mộc',
  THUY: 'Thủy',
  HOA: 'Hỏa',
  THO: 'Thổ',
}

export const STRENGTH_LABELS: Record<StarStrength, string> = {
  MIEU: 'Miếu',
  VUONG: 'Vượng',
  DAC: 'Đắc',
  BINH: 'Bình',
  HAM: 'Hãm',
}

/** Địa chi in canonical order — index matches the engine's `branch_index`. */
export const EARTHLY_BRANCHES = [
  'Tý',
  'Sửu',
  'Dần',
  'Mão',
  'Thìn',
  'Tỵ',
  'Ngọ',
  'Mùi',
  'Thân',
  'Dậu',
  'Tuất',
  'Hợi',
] as const

/**
 * Địa bàn layout: which địa chi owns each cell of the 4×4 chart grid, read left
 * to right, top to bottom. `null` marks the four centre cells, which carry the
 * chart summary rather than a palace.
 *
 *   Tỵ   Ngọ  Mùi  Thân
 *   Thìn  ·    ·   Dậu
 *   Mão   ·    ·   Tuất
 *   Dần  Sửu  Tý   Hợi
 *
 * Fixed for every chart: a palace's cell is decided by its địa chi, never by its
 * position in the palace array. Lives here, not in the web app, so the layout is
 * stated once and the frontend keeps rendering chart JSON rather than encoding
 * Tử Vi rules of its own.
 */
export const CHART_GRID_BRANCH_INDEXES: readonly (number | null)[] = [
  5, 6, 7, 8,
  4, null, null, 9,
  3, null, null, 10,
  2, 1, 0, 11,
]

/** The twelve two-hour periods, for the birth-hour picker. */
export const BIRTH_HOUR_OPTIONS = EARTHLY_BRANCHES.map((branch, index) => ({
  value: index === 0 ? 23 : index * 2 - 1,
  branch,
  label:
    index === 0
      ? 'Tý (23:00 – 00:59)'
      : `${branch} (${String(index * 2 - 1).padStart(2, '0')}:00 – ${String(index * 2).padStart(2, '0')}:59)`,
}))
