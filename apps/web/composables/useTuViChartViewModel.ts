import { computed, toValue, type MaybeRefOrGetter } from 'vue'
import {
  CHART_GRID_BRANCH_INDEXES,
  ELEMENT_LABELS,
  type ChartPalace,
  type ChartPayload,
  type ChartStar,
  type ElementCode,
  type YinYangPolarity,
} from '@cosmic/shared'
import type {
  CenterFieldViewModel,
  ChartViewModel,
  ConnectionType,
  ConnectionViewModel,
  PalaceViewModel,
  StarCategory,
  StarViewModel,
  VoidKind,
  VoidMarkerViewModel,
} from '~/types/chart-view-model'
import {
  PALACE_METRICS,
  STAR_CATEGORY_PRIORITY,
  ELEMENT_COLOR_MAP,
  STRENGTH_ABBREVIATIONS,
  STRENGTH_LABELS,
  centerAnchor,
  estimatePalaceHeight,
  gridPosition,
} from '~/utils/tuvi-chart'

/**
 * Chart DTO → view model.
 *
 * Reshapes and labels engine output. It must never decide astrology: no star is
 * placed, no palace chosen and no missing value filled in here. Fields the engine
 * may add later (star element, strength, major-cycle age, …) are read defensively
 * so they appear once present, without widening the shared DTO contract today.
 */

/** How far above the row's bottom border a side-by-side Tuần/Triệt label sits, in %. */
const VERTICAL_VOID_INSET = 3

const ELEMENT_CODES: ReadonlySet<string> = new Set(['KIM', 'MOC', 'THUY', 'HOA', 'THO'])
const STAR_CATEGORIES: ReadonlySet<string> = new Set(Object.keys(STAR_CATEGORY_PRIORITY))

function isElementCode(value: unknown): value is ElementCode {
  return typeof value === 'string' && ELEMENT_CODES.has(value)
}

function field(source: object, key: string): unknown {
  return (source as Record<string, unknown>)[key]
}

function optionalNumber(source: object, key: string): number | null {
  const value = field(source, key)
  return typeof value === 'number' && Number.isFinite(value) ? value : null
}

function optionalString(source: object, key: string): string | null {
  const value = field(source, key)
  return typeof value === 'string' && value.trim() ? value : null
}

function categoryOf(star: ChartStar, fallback: StarCategory): StarCategory {
  const declared = optionalString(star, 'category')
  return declared && STAR_CATEGORIES.has(declared) ? (declared as StarCategory) : fallback
}

const POLARITY_PREFIX: Record<YinYangPolarity, string> = { YANG: '+', YIN: '−' }

function polarityOf(star: ChartStar): YinYangPolarity | null {
  const declared = optionalString(star, 'polarity')
  return declared === 'YANG' || declared === 'YIN' ? declared : null
}

function mapStar(star: ChartStar, fallback: StarCategory): StarViewModel {
  const category = categoryOf(star, fallback)
  const raw = field(star, 'element')
  const element = isElementCode(raw) ? raw : null
  const polarity = polarityOf(star)
  const elementLabel = element ? ELEMENT_COLOR_MAP[element].label : null
  const strengthLabel = star.strength ? STRENGTH_LABELS[star.strength] : null
  return {
    code: star.code,
    name: star.label,
    category,
    element,
    elementLabel,
    polarityPrefix: polarity ? POLARITY_PREFIX[polarity] : null,
    // Spelled out because colour alone must not carry the element.
    ariaLabel: [star.label, elementLabel && `hành ${elementLabel}`, strengthLabel]
      .filter(Boolean)
      .join(', '),
    strength: star.strength,
    strengthAbbr: star.strength ? STRENGTH_ABBREVIATIONS[star.strength] : null,
    provisional: star.provisional,
    isTransformation: category === 'TRANSFORMATION',
    isAnnual: category === 'ANNUAL',
  }
}

/**
 * Stars the engine sent without a ngũ hành, for the dev console only.
 *
 * A missing element is real astrology data that nobody has verified, not a bug to
 * paper over. Reporting it keeps the gap visible without putting a guess on the
 * chart — and it never reaches a customer-facing or exported chart, because it
 * goes to the console under `import.meta.dev` and not into the DOM.
 */
function reportMissingElements(palaces: PalaceViewModel[]): void {
  if (!import.meta.dev) return
  // Keyed by name, which is what the message prints: one line per star, however
  // many palaces or categories it turns up in.
  const missing = new Set<string>()
  for (const palace of palaces) {
    for (const star of [...palace.majorStars, ...palace.minorStars]) {
      if (!star.element) missing.add(star.name)
    }
  }
  if (missing.size === 0) return
  console.warn(
    `[TuVi Renderer] Thiếu metadata ngũ hành: ${[...missing].sort().join(', ')} — ` +
      'vẽ bằng mực trung tính. Xem cosmic_astrology/stars/metadata.py.',
  )
}

/** Stable by category priority; the engine's own order survives within a category. */
function byDisplayPriority(stars: StarViewModel[]): StarViewModel[] {
  return stars
    .map((star, index) => ({ star, index }))
    .sort(
      (a, b) =>
        STAR_CATEGORY_PRIORITY[a.star.category] - STAR_CATEGORY_PRIORITY[b.star.category] ||
        a.index - b.index,
    )
    .map(({ star }) => star)
}

function mapPalace(palace: ChartPalace, starsPlaced: boolean): PalaceViewModel {
  const { row, col } = gridPosition(palace.branch_index)
  const majorStars = byDisplayPriority(palace.major_stars.map((s) => mapStar(s, 'MAJOR')))
  const minorStars = byDisplayPriority([
    ...palace.transformations.map((s) => mapStar(s, 'TRANSFORMATION')),
    ...palace.minor_stars.map((s) => mapStar(s, 'MINOR')),
  ])
  // A FRAME-stage chart places no stars, yet the engine still flags every palace
  // as empty. "Vô chính diệu" is a statement about the chart, so it is only shown
  // once the engine has actually placed the major stars.
  const isEmptyMainStar = starsPlaced && palace.is_empty_main_star
  const lifeStage = optionalString(palace, 'life_stage')
  const majorCycleRef = optionalString(palace, 'major_cycle_palace')
  const annualRef = optionalString(palace, 'annual_palace')

  return {
    id: palace.name,
    name: palace.label,
    stem: palace.stem,
    stemShort: palace.stem.charAt(0),
    branch: palace.branch,
    branchIndex: palace.branch_index,
    row,
    col,
    element: palace.element,
    elementLabel: ELEMENT_LABELS[palace.element],
    napAm: palace.nap_am,
    isMenh: palace.is_menh,
    isThan: palace.is_than,
    hasTuan: palace.has_tuan,
    hasTriet: palace.has_triet,
    isEmptyMainStar,
    majorStars,
    minorStars,
    majorCycleAge: optionalNumber(palace, 'major_cycle_age'),
    monthNumber: optionalNumber(palace, 'month_number'),
    lifeStage,
    majorCycleRef,
    annualRef,
    ariaLabel: `Cung ${palace.label}, ${palace.stem} ${palace.branch}`,
    estimatedHeight: estimatePalaceHeight({
      majors: majorStars.length,
      emptyLine: isEmptyMainStar && majorStars.length === 0,
      minors: minorStars.length,
      footer: Boolean(lifeStage || majorCycleRef || annualRef),
    }),
  }
}

function voidMarker(
  kind: VoidKind,
  label: string,
  palaces: PalaceViewModel[],
  warnings: string[],
): VoidMarkerViewModel | null {
  const flagged = palaces.filter((p) => (kind === 'TUAN' ? p.hasTuan : p.hasTriet))
  if (flagged.length === 0) return null

  const [a, b] = flagged
  if (flagged.length !== 2 || !a || !b) {
    warnings.push(`${label}: engine đánh dấu ${flagged.length} cung, cần đúng 2.`)
    return null
  }
  if (a.row === b.row && Math.abs(a.col - b.col) === 1) {
    return {
      kind,
      label,
      branches: [a.branchIndex, b.branchIndex],
      x: (Math.max(a.col, b.col) - 1) * 25,
      // Low in the row: a side-by-side border runs straight through the star area,
      // and the bottom of a palace is the part most often empty.
      y: a.row * 25 - VERTICAL_VOID_INSET,
      orientation: 'vertical',
    }
  }
  if (a.col === b.col && Math.abs(a.row - b.row) === 1) {
    return {
      kind,
      label,
      branches: [a.branchIndex, b.branchIndex],
      x: (a.col - 0.5) * 25,
      y: (Math.max(a.row, b.row) - 1) * 25,
      orientation: 'horizontal',
    }
  }
  warnings.push(`${label}: hai cung ${a.branch} và ${b.branch} không kề nhau trên lưới.`)
  return null
}

function link(from: number, to: number, type: ConnectionType): ConnectionViewModel {
  const start = centerAnchor(from)
  const end = centerAnchor(to)
  return { from, to, type, x1: start.x, y1: start.y, x2: end.x, y2: end.y }
}

const pad = (value: number) => String(value).padStart(2, '0')

/** Narrow an engine element string; anything unexpected loses its colour, not the value. */
function elementOf(value: unknown): ElementCode | null {
  return isElementCode(value) ? value : null
}

function centerFields(chart: ChartPayload): CenterFieldViewModel[] {
  const { birth, lunar_birth: lunar, pillars } = chart
  const leap = lunar.is_leap_month ? ' nhuận' : ''
  const year =
    birth.solar.year === lunar.year
      ? String(birth.solar.year)
      : `${birth.solar.year} (âm ${lunar.year})`

  // `element` is set only where the value itself names an element, so the centre
  // gains two coloured values rather than becoming rainbow text.
  const f = (
    label: string,
    value: string,
    secondary: string | null = null,
    element: ElementCode | null = null,
  ): CenterFieldViewModel => ({ label, value, secondary, element })

  const fields: CenterFieldViewModel[] = [
    f('Họ tên', birth.name),
    f('Năm', year, pillars.year.name),
    f('Tháng', `${birth.solar.month} (${lunar.month}${leap})`, pillars.month.name),
    f('Ngày', `${birth.solar.day} (${lunar.day})`, pillars.day.name),
    f('Giờ', `${birth.solar.hour} giờ ${pad(birth.solar.minute)} phút`, pillars.hour.name),
    f('Âm dương', chart.yin_yang.label),
    f('Bản mệnh', chart.menh.nap_am, null, elementOf(chart.menh.element)),
    f('Cục', chart.cuc.label, null, elementOf(chart.cuc.element)),
    f('Mệnh – Cục', chart.cuc.relation_label),
    f('Mệnh', chart.menh.branch),
    f(
      'Thân',
      chart.than.branch,
      chart.than.resides_in_label ? `cư ${chart.than.resides_in_label}` : null,
    ),
  ]
  return fields.filter((entry) => entry.value.trim() !== '')
}

export function mapChartDtoToViewModel(chart: ChartPayload): ChartViewModel {
  const warnings: string[] = []
  const starsPlaced = chart.palaces.some((palace) => palace.major_stars.length > 0)
  const palaces = chart.palaces.map((palace) => mapPalace(palace, starsPlaced))
  const byBranch = new Map(palaces.map((p) => [p.branchIndex, p]))
  reportMissingElements(palaces)

  if (palaces.length !== 12 || byBranch.size !== 12) {
    warnings.push(`Engine gửi ${palaces.length} cung, cần đủ 12 cung khác địa chi.`)
  }
  for (const palace of palaces) {
    if (palace.estimatedHeight > PALACE_METRICS.contentHeight) {
      warnings.push(
        `Cung ${palace.name}: ước tính cao ${palace.estimatedHeight}px, ` +
          `vượt sức chứa ${PALACE_METRICS.contentHeight}px.`,
      )
    }
  }

  const voidMarkers = [
    voidMarker('TUAN', 'Tuần', palaces, warnings),
    voidMarker('TRIET', 'Triệt', palaces, warnings),
  ].filter((marker): marker is VoidMarkerViewModel => marker !== null)

  // Tam phương tứ chính comes from the engine; the renderer only draws it.
  const directions = chart.menh.three_directions_four_positions
  const connections = directions
    ? [
        link(directions.self, directions.trine_left, 'TRINE'),
        link(directions.self, directions.trine_right, 'TRINE'),
        link(directions.trine_left, directions.trine_right, 'TRINE'),
        link(directions.self, directions.opposite, 'OPPOSITE'),
      ]
    : []

  // Charts stored before the convention layer existed lack these blocks.
  const engine = chart.engine
  const timezone = field(chart, 'timezone')
  const utcOffset =
    timezone && typeof timezone === 'object' ? optionalNumber(timezone, 'utc_offset_hours') : null
  const anyProvisionalStar = palaces.some((p) =>
    [...p.majorStars, ...p.minorStars].some((star) => star.provisional),
  )

  return {
    palaces,
    cells: CHART_GRID_BRANCH_INDEXES.map((index) =>
      index === null ? null : (byBranch.get(index) ?? null),
    ),
    center: { title: 'Lá Số Tử Vi', subtitle: 'Cosmic Signs', fields: centerFields(chart) },
    voidMarkers,
    connections,
    meta: {
      engineVersion: engine.version,
      conventionProfile: optionalString(engine, 'convention_profile'),
      conventionVersion: optionalString(engine, 'convention_version'),
      stage: engine.stage,
      isAuthoritative: engine.is_authoritative === true,
      provisional: engine.is_authoritative !== true || anyProvisionalStar,
      utcOffsetHours: utcOffset,
    },
    warnings,
  }
}

/** Memoised view model for a chart that may still be loading. */
export function useTuViChartViewModel(source: MaybeRefOrGetter<ChartPayload | null | undefined>) {
  return computed(() => {
    const chart = toValue(source)
    return chart ? mapChartDtoToViewModel(chart) : null
  })
}
