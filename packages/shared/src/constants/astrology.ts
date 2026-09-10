import type { ElementCode, PalaceCode, StarStrength } from '../types/chart'

/** Display order used by the chart grid, starting at Mệnh. */
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

/** The twelve two-hour periods, for the birth-hour picker. */
export const BIRTH_HOUR_OPTIONS = EARTHLY_BRANCHES.map((branch, index) => ({
  value: index === 0 ? 23 : index * 2 - 1,
  branch,
  label:
    index === 0
      ? 'Tý (23:00 – 00:59)'
      : `${branch} (${String(index * 2 - 1).padStart(2, '0')}:00 – ${String(index * 2).padStart(2, '0')}:59)`,
}))
