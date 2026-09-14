import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import { describe, expect, it } from 'vitest'

/**
 * A star's appearance must be decided by its ngũ hành, never by its name.
 *
 * This is the one rule a future edit is most likely to break, because "just make
 * Hóa Kỵ red" is a one-line change that looks harmless. So rather than test a
 * behaviour, this scans the renderer's own source: if a star name appears anywhere
 * in the code that draws the chart, the rule has already been broken.
 */

const ROOT = join(import.meta.dirname, '..')

/**
 * Every star the engine can place.
 *
 * "Tử Vi" is deliberately absent: it names both a star and the whole discipline,
 * so it appears legitimately in titles and file headers ("Lá Số Tử Vi"). The star
 * sense is covered by the id scan below, where `TU_VI` has no innocent reading.
 *
 * Hóa Lộc / Quyền / Khoa / Kỵ are absent for a different reason: they are not
 * stars. They are states a placed star carries, so a label table keyed by the
 * transformation enum is correct rather than a violation — the test below pins
 * that it really is keyed by the enum and not by any star name.
 */
const STAR_NAMES = [
  'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh',
  'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương',
  'Thất Sát', 'Phá Quân',
  'Văn Xương', 'Văn Khúc', 'Tả Phù', 'Hữu Bật', 'Thiên Khôi', 'Thiên Việt',
  'Lộc Tồn', 'Kình Dương', 'Đà La', 'Đào Hoa', 'Hồng Loan', 'Thiên Mã',
]

const STAR_IDS = [
  'TU_VI', 'THIEN_CO', 'THAI_DUONG', 'VU_KHUC', 'THIEN_DONG', 'LIEM_TRINH',
  'THIEN_PHU', 'THAI_AM', 'THAM_LANG', 'CU_MON', 'THIEN_TUONG', 'THIEN_LUONG',
  'THAT_SAT', 'PHA_QUAN',
  'VAN_XUONG', 'VAN_KHUC', 'TA_PHU', 'HUU_BAT', 'THIEN_KHOI', 'THIEN_VIET',
  'LOC_TON', 'KINH_DUONG', 'DA_LA', 'DAO_HOA', 'HONG_LOAN', 'THIEN_HY', 'THIEN_MA',
]

/** Source that actually draws the chart. Tests and fixtures name stars freely. */
const SCANNED = [
  'components/astrology/chart',
  'composables/useTuViChartViewModel.ts',
  'utils/tuvi-chart.ts',
  'utils/tuvi-format.ts',
]

function filesUnder(path: string): string[] {
  const absolute = join(ROOT, path)
  if (!statSync(absolute).isDirectory()) return [absolute]
  return readdirSync(absolute)
    .map((entry) => join(absolute, entry))
    .filter((entry) => statSync(entry).isFile())
}

const SOURCES = SCANNED.flatMap(filesUnder).map((file) => ({
  path: relative(ROOT, file),
  text: readFileSync(file, 'utf8'),
}))

describe('the renderer never keys off a star name', () => {
  it('scans the files that actually draw the chart', () => {
    // A guard that silently scans nothing would pass forever.
    expect(SOURCES.length).toBeGreaterThan(8)
    expect(SOURCES.some((s) => s.path.endsWith('TuViStar.vue'))).toBe(true)
    expect(SOURCES.some((s) => s.path.endsWith('tuvi-chart.css'))).toBe(true)
  })

  it.each(STAR_NAMES)('does not mention %s anywhere in renderer source', (name) => {
    const offenders = SOURCES.filter((s) => s.text.includes(name)).map((s) => s.path)
    expect(offenders).toEqual([])
  })

  it.each(STAR_IDS)('does not branch on the star id %s either', (id) => {
    const offenders = SOURCES.filter((s) => s.text.includes(id)).map((s) => s.path)
    expect(offenders).toEqual([])
  })

  it('declares exactly one colour rule per ngũ hành and nothing else', () => {
    const css = SOURCES.find((s) => s.path.endsWith('tuvi-chart.css'))!.text
    const starColourRules = [...css.matchAll(/\.tuvi-star\.is-element-(\w+)\s*\{/g)].map(
      (m) => m[1],
    )
    expect(starColourRules.sort()).toEqual(['hoa', 'kim', 'moc', 'none', 'tho', 'thuy'])
  })

  it('keys the Tứ Hóa labels by the transformation, never by a star name', () => {
    const utils = SOURCES.find((s) => s.path.endsWith('utils/tuvi-chart.ts'))!.text
    // The table is Record<Transformation, string>; its keys are the four enum
    // values. A star name appearing as a key would be the violation.
    for (const key of ['HOA_LOC', 'HOA_QUYEN', 'HOA_KHOA', 'HOA_KY']) {
      expect(utils).toContain(key)
    }
    expect(utils).toContain('Record<Transformation, string>')
  })

  it('builds the element class from the element alone', () => {
    const utils = SOURCES.find((s) => s.path.endsWith('utils/tuvi-chart.ts'))!.text
    // One expression, one input: the element. No lookup table keyed by anything else.
    expect(utils).toContain("return `is-element-${(element ?? 'none').toLowerCase()}`")
  })
})
