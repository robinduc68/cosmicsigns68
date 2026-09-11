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
 * Every star the engine can place, plus the four Tứ Hóa it will place later.
 *
 * "Tử Vi" is deliberately absent: it names both a star and the whole discipline,
 * so it appears legitimately in titles and file headers ("Lá Số Tử Vi"). The star
 * sense is covered by the id scan below, where `TU_VI` has no innocent reading.
 */
const STAR_NAMES = [
  'Thiên Cơ', 'Thái Dương', 'Vũ Khúc', 'Thiên Đồng', 'Liêm Trinh',
  'Thiên Phủ', 'Thái Âm', 'Tham Lang', 'Cự Môn', 'Thiên Tướng', 'Thiên Lương',
  'Thất Sát', 'Phá Quân',
  'Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ',
]

const STAR_IDS = [
  'TU_VI', 'THIEN_CO', 'THAI_DUONG', 'VU_KHUC', 'THIEN_DONG', 'LIEM_TRINH',
  'THIEN_PHU', 'THAI_AM', 'THAM_LANG', 'CU_MON', 'THIEN_TUONG', 'THIEN_LUONG',
  'THAT_SAT', 'PHA_QUAN',
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

  it('builds the element class from the element alone', () => {
    const utils = SOURCES.find((s) => s.path.endsWith('utils/tuvi-chart.ts'))!.text
    // One expression, one input: the element. No lookup table keyed by anything else.
    expect(utils).toContain("return `is-element-${(element ?? 'none').toLowerCase()}`")
  })
})
