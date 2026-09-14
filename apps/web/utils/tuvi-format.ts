/**
 * Vietnamese display formatting for chart values — the only place that decides how
 * a chart value is spelled for a reader.
 *
 * These functions **combine and label**; they never compute astrology. Can chi in
 * particular is supplied by the engine as a structured stem and branch, and is
 * joined here rather than recalculated — a second implementation of the sexagenary
 * cycle in the browser is a second thing that can be wrong.
 *
 * Every formatter returns `null` for input it cannot render. `null` means the
 * caller should omit the line; it is never turned into `"—"`, `"Không rõ"` or a
 * zero, which would read as data.
 */

import type { CalendarType, ChartPillar, ElementCode, Gender } from '@cosmic/shared'
import { ELEMENT_LABELS } from '@cosmic/shared'

const GENDER_LABELS: Record<Gender, string> = { MALE: 'Nam', FEMALE: 'Nữ' }

const CALENDAR_LABELS: Record<CalendarType, string> = { SOLAR: 'Dương lịch', LUNAR: 'Âm lịch' }

/** `'YANG'`/`'YIN'` paired with a gender, as a chart prints it: "Âm Nữ". */
const POLARITY_LABELS = { YANG: 'Dương', YIN: 'Âm' } as const

function pad(value: number): string {
  return String(value).padStart(2, '0')
}

export function formatGender(gender: Gender | null | undefined): string | null {
  return gender ? (GENDER_LABELS[gender] ?? null) : null
}

export function formatCalendarType(calendar: CalendarType | null | undefined): string | null {
  return calendar ? (CALENDAR_LABELS[calendar] ?? null) : null
}

/**
 * "Âm Nữ" from the two parts.
 *
 * The engine already sends this as `yin_yang.label`, and callers should prefer
 * that. This exists for the case where only the parts are at hand, and it must
 * agree with the engine — a test pins the two together.
 */
export function formatYinYang(
  yearIsYang: boolean | null | undefined,
  gender: Gender | null | undefined,
): string | null {
  const genderLabel = formatGender(gender)
  if (yearIsYang === null || yearIsYang === undefined || !genderLabel) return null
  return `${POLARITY_LABELS[yearIsYang ? 'YANG' : 'YIN']} ${genderLabel}`
}

/** "Tân Tỵ" — joins the stem and branch the engine supplied. Never derived. */
export function formatPillar(pillar: Pick<ChartPillar, 'can' | 'chi'> | null | undefined) {
  if (!pillar?.can || !pillar?.chi) return null
  return `${pillar.can} ${pillar.chi}`
}

/** "04/03/2001". */
export function formatSolarDate(
  date: { day: number; month: number; year: number } | null | undefined,
): string | null {
  if (!date) return null
  return `${pad(date.day)}/${pad(date.month)}/${date.year}`
}

/**
 * "10/02 Tân Tỵ" — lunar day and month, then the year's pillar.
 *
 * A lunar year is named by its can chi rather than a number, so the pillar is the
 * year here. A leap month is marked, because the same month number twice in one
 * year is otherwise indistinguishable.
 */
export function formatLunarDate(
  lunar:
    | { day: number; month: number; is_leap_month: boolean; year_pillar: string }
    | null
    | undefined,
): string | null {
  if (!lunar) return null
  const leap = lunar.is_leap_month ? ' nhuận' : ''
  const year = lunar.year_pillar ? ` ${lunar.year_pillar}` : ''
  return `${pad(lunar.day)}/${pad(lunar.month)}${leap}${year}`
}

/** "09:30 (giờ Tỵ)". The branch is the engine's; only the wording is added here. */
export function formatBirthTime(
  hour: number | null | undefined,
  minute: number | null | undefined,
  hourBranch?: string | null,
): string | null {
  if (typeof hour !== 'number' || typeof minute !== 'number') return null
  const clock = `${pad(hour)}:${pad(minute)}`
  return hourBranch ? `${clock} (giờ ${hourBranch})` : clock
}

/**
 * "Mộc Tam Cục".
 *
 * The engine sends this ready-made as `cuc.label`; prefer that. Provided for the
 * parts-only case, and pinned to the engine's wording by a test.
 */
const CUC_NUMERALS: Record<number, string> = {
  2: 'Nhị',
  3: 'Tam',
  4: 'Tứ',
  5: 'Ngũ',
  6: 'Lục',
}

export function formatCuc(
  element: ElementCode | null | undefined,
  cucNumber: number | null | undefined,
): string | null {
  if (!element || typeof cucNumber !== 'number') return null
  const numeral = CUC_NUMERALS[cucNumber]
  if (!numeral) return null
  return `${ELEMENT_LABELS[element]} ${numeral} Cục`
}

/**
 * "Mệnh Kim khắc Cục Mộc".
 *
 * The engine decides *which* relationship holds (`cuc.relation`); this only spells
 * it out with both element names, which a bare "Mệnh khắc Cục" leaves the reader
 * to look up. No relationship is inferred here.
 */
/**
 * Word order matters: whichever side acts comes first, so "Cục sinh Mệnh" reads as
 * a sentence rather than as "Mệnh được Cục sinh Cục ...". Each entry says which
 * side is the subject and which verb joins them.
 */
const RELATIONS: Record<string, { subject: 'menh' | 'cuc'; verb: string }> = {
  TUONG_HOA: { subject: 'menh', verb: 'tương hòa với' },
  MENH_SINH_CUC: { subject: 'menh', verb: 'sinh' },
  MENH_KHAC_CUC: { subject: 'menh', verb: 'khắc' },
  CUC_SINH_MENH: { subject: 'cuc', verb: 'sinh' },
  CUC_KHAC_MENH: { subject: 'cuc', verb: 'khắc' },
}

export function formatMenhCucRelation(
  relation: string | null | undefined,
  menhElement: ElementCode | null | undefined,
  cucElement: ElementCode | null | undefined,
): string | null {
  if (!relation || !menhElement || !cucElement) return null
  const shape = RELATIONS[relation]
  if (!shape) return null
  const menh = `Mệnh ${ELEMENT_LABELS[menhElement]}`
  const cuc = `Cục ${ELEMENT_LABELS[cucElement]}`
  return shape.subject === 'menh'
    ? `${menh} ${shape.verb} ${cuc}`
    : `${cuc} ${shape.verb} ${menh}`
}

/** "cư Phu Thê" — where Thân resides. */
export function formatThanCu(palaceLabel: string | null | undefined): string | null {
  return palaceLabel ? `cư ${palaceLabel}` : null
}

/**
 * "Thuận" / "Nghịch" — which way the đại vận walk runs.
 *
 * Describes the **walk only**. The twelve palace names never reverse with it, and
 * nothing in the renderer may reorder them on the strength of this value.
 */
export function formatCycleDirection(
  direction: 'FORWARD' | 'BACKWARD' | null | undefined,
): string | null {
  if (direction === 'FORWARD') return 'Thuận'
  if (direction === 'BACKWARD') return 'Nghịch'
  return null
}

/** "6 – 15" for a đại vận age span, or "6 –" when only the start is known. */
export function formatAgeRange(
  start: number | null | undefined,
  end: number | null | undefined,
): string | null {
  if (typeof start !== 'number') return null
  return typeof end === 'number' ? `${start} – ${end}` : String(start)
}
