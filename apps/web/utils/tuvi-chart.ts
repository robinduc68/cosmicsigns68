import { CHART_GRID_BRANCH_INDEXES, type ElementCode, type StarStrength } from '@cosmic/shared'
import type { StarCategory } from '~/types/chart-view-model'

/**
 * Presentation constants for the Tử Vi chart renderer.
 *
 * Nothing here is astrology. Colours, ordering and geometry decide where text
 * lands on the page; which star sits in which palace is the engine's business.
 */

/** Canonical 4:5 canvas. Export and print render at this size, then scale. */
export const CANONICAL_CHART_WIDTH = 1400
export const CANONICAL_CHART_HEIGHT = 1750

/** The single place ngũ hành colours are named. Values live in the chart stylesheet. */
export const ELEMENT_COLOR_MAP: Record<ElementCode, { label: string; color: string }> = {
  KIM: { label: 'Kim', color: 'var(--chart-kim)' },
  MOC: { label: 'Mộc', color: 'var(--chart-moc)' },
  THUY: { label: 'Thủy', color: 'var(--chart-thuy)' },
  HOA: { label: 'Hỏa', color: 'var(--chart-hoa)' },
  THO: { label: 'Thổ', color: 'var(--chart-tho)' },
}

export const ELEMENT_ORDER: ElementCode[] = ['KIM', 'MOC', 'THUY', 'HOA', 'THO']

/** Neutral text when the engine declared no element. */
export function elementColor(element: ElementCode | null): string {
  return element ? ELEMENT_COLOR_MAP[element].color : 'var(--chart-text)'
}

/**
 * Semantic class for a ngũ hành. The only input is the element the engine
 * declared — there is no path from a star's name to a colour, by construction.
 */
export function elementClass(element: ElementCode | null): string {
  return `is-element-${(element ?? 'none').toLowerCase()}`
}

export const STRENGTH_LEGEND: { key: StarStrength; abbr: string; label: string }[] = [
  { key: 'MIEU', abbr: 'M', label: 'Miếu' },
  { key: 'VUONG', abbr: 'V', label: 'Vượng' },
  { key: 'DAC', abbr: 'Đ', label: 'Đắc' },
  { key: 'BINH', abbr: 'B', label: 'Bình hòa' },
  { key: 'HAM', abbr: 'H', label: 'Hãm' },
]

export const STRENGTH_ABBREVIATIONS = Object.fromEntries(
  STRENGTH_LEGEND.map((entry) => [entry.key, entry.abbr]),
) as Record<StarStrength, string>

export const STRENGTH_LABELS = Object.fromEntries(
  STRENGTH_LEGEND.map((entry) => [entry.key, entry.label]),
) as Record<StarStrength, string>

/**
 * Fallback rendering order, used only for schema v1 charts that carry no
 * engine-supplied `display_priority`. It moves text on the page and nothing else —
 * no astrological weight is implied, and the engine's own order is kept within
 * each category. Must mirror `_CATEGORY_PRIORITY` in the engine's `chart/model.py`.
 */
export const STAR_CATEGORY_PRIORITY: Record<StarCategory, number> = {
  MAJOR: 0,
  TRANSFORMATION: 1,
  SUPPORTING: 2,
  MALEFIC: 3,
  LITERARY: 4,
  ROMANCE: 5,
  WEALTH: 6,
  OTHER: 7,
  ANNUAL: 8,
}

/**
 * Palace metrics in canvas pixels, for the development overflow guard. Keep in
 * step with tuvi-chart.css. The palace also measures its real rendered height in
 * development, so drift here can produce a false alarm but never a silent clip.
 */
export const PALACE_METRICS = {
  /** 395 px row − 22 px top − 16 px bottom padding. */
  contentHeight: 357,
  header: 46,
  blockGap: 12,
  majorRow: 30,
  minorRow: 21,
  emptyLine: 34,
  footer: 30,
} as const

export function estimatePalaceHeight(content: {
  majors: number
  emptyLine: boolean
  minors: number
  footer: boolean
}): number {
  const m = PALACE_METRICS
  let height = m.header
  if (content.majors > 0) height += m.blockGap + content.majors * m.majorRow
  else if (content.emptyLine) height += m.emptyLine
  if (content.minors > 0) height += m.blockGap + Math.ceil(content.minors / 2) * m.minorRow
  if (content.footer) height += m.footer
  return height
}

/** 1-based grid slot of a palace, read from the shared địa bàn layout. */
export function gridPosition(branchIndex: number): { row: number; col: number } {
  const slot = CHART_GRID_BRANCH_INDEXES.indexOf(branchIndex)
  if (slot < 0) throw new Error(`Địa chi không hợp lệ: ${branchIndex}`)
  return { row: Math.floor(slot / 4) + 1, col: (slot % 4) + 1 }
}

/**
 * Where a palace's inner edge meets the centre panel, 0–100 on each axis.
 *
 * Derived from the grid rather than tabulated: corner palaces meet the panel at
 * its corners, edge palaces at the middle of their stretch of border.
 */
export function centerAnchor(branchIndex: number): { x: number; y: number } {
  const { row, col } = gridPosition(branchIndex)
  const clampToPanel = (value: number) => Math.min(75, Math.max(25, value))
  return {
    x: (clampToPanel((col - 0.5) * 25) - 25) * 2,
    y: (clampToPanel((row - 0.5) * 25) - 25) * 2,
  }
}
