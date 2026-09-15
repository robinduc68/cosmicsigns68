import { computed, toValue, type MaybeRefOrGetter } from 'vue'
import {
  CHART_GRID_BRANCH_INDEXES,
  ELEMENT_LABELS,
  type ChartPalace,
  type ChartPayload,
  type ChartStar,
  type AnnualChart,
  type AnnualStar,
  type ElementCode,
  type Transformation,
  type YinYangPolarity,
} from '@cosmic/shared'
import type {
  StarProvenance,
  VerificationStatus,
} from '@cosmic/shared'
import type {
  CenterFieldViewModel,
  ChartViewModel,
  ConnectionType,
  ConnectionViewModel,
  PalaceViewModel,
  StarCategory,
  StarTransformationViewModel,
  StarViewModel,
  VoidKind,
  VoidMarkerViewModel,
} from '~/types/chart-view-model'
import {
  formatAgeRange,
  formatCycleDirection,
  formatBirthTime,
  formatCalendarType,
  formatGender,
  formatLunarDate,
  formatMenhCucRelation,
  formatPillar,
  formatSolarDate,
  formatAmDuongLy,
  formatThanCu,
  formatThanMenh,
} from '~/utils/tuvi-format'
import {
  PALACE_METRICS,
  STAR_CATEGORY_PRIORITY,
  ELEMENT_COLOR_MAP,
  STRENGTH_ABBREVIATIONS,
  STRENGTH_LABELS,
  TRANSFORMATION_FULL_LABELS,
  TRANSFORMATION_LABELS,
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

/** Schema v1 `kind` values, mapped onto the categories that replaced them. */
const LEGACY_KIND_TO_CATEGORY: Record<string, StarCategory> = {
  MAJOR: 'MAJOR',
  TRANSFORMATION: 'TRANSFORMATION',
  MINOR: 'OTHER',
}

function categoryOf(star: ChartStar, fallback: StarCategory): StarCategory {
  const declared = optionalString(star, 'category')
  if (declared && STAR_CATEGORIES.has(declared)) return declared as StarCategory
  const legacy = optionalString(star, 'kind')
  return (legacy && LEGACY_KIND_TO_CATEGORY[legacy]) || fallback
}

function verificationOf(value: unknown): VerificationStatus | null {
  return value === 'UNVERIFIED' || value === 'PROVISIONAL' || value === 'VERIFIED' ? value : null
}

/**
 * Provenance as the engine sent it, or `null`.
 *
 * Read defensively rather than cast: this is the field a reviewer trusts to tell
 * a provisional placement from a verified one, so a malformed one must read as
 * "no provenance" and not as a half-populated object.
 */
function provenanceOf(star: ChartStar): StarProvenance | null {
  const raw = field(star, 'provenance')
  if (!raw || typeof raw !== 'object') return null
  const rule = optionalString(raw, 'rule')
  const verification = verificationOf(field(raw, 'verification'))
  if (!rule || !verification) return null
  const blockedBy = field(raw, 'blocked_by')
  return {
    rule,
    verification,
    blocked_by: Array.isArray(blockedBy) ? blockedBy.filter((x) => typeof x === 'string') : [],
    note: optionalString(raw, 'note') ?? '',
  }
}

const POLARITY_PREFIX: Record<YinYangPolarity, string> = { YANG: '+', YIN: '−' }

function polarityOf(star: ChartStar): YinYangPolarity | null {
  const declared = optionalString(star, 'polarity')
  return declared === 'YANG' || declared === 'YIN' ? declared : null
}

const TRANSFORMATION_CODES: ReadonlySet<string> = new Set(Object.keys(TRANSFORMATION_LABELS))

/** Tứ Hóa as the engine sent it. Anything unrecognised is dropped, never guessed. */
function transformationsOf(star: ChartStar): StarTransformationViewModel[] {
  const raw = field(star, 'transformations')
  if (!Array.isArray(raw)) return []
  // Độ sáng của từng hóa đến từ một bảng riêng của engine, khoá theo hóa. Chỗ nào
  // engine không có ô, hóa hiện không hậu tố — renderer không suy ra giá trị nào.
  const strengths = field(star, 'transformation_strengths')
  const byCode = typeof strengths === 'object' && strengths !== null ? strengths : {}
  return raw
    .filter((code): code is Transformation => typeof code === 'string' && TRANSFORMATION_CODES.has(code))
    .map((code) => {
      const value = (byCode as Record<string, unknown>)[code]
      const strength =
        typeof value === 'string' && value in STRENGTH_ABBREVIATIONS
          ? (value as keyof typeof STRENGTH_ABBREVIATIONS)
          : null
      return {
        code,
        label: TRANSFORMATION_LABELS[code],
        fullLabel: TRANSFORMATION_FULL_LABELS[code],
        strengthAbbr: strength ? STRENGTH_ABBREVIATIONS[strength] : null,
        strengthLabel: strength ? STRENGTH_LABELS[strength] : null,
      }
    })
}

/** Một lưu tinh, đưa về đúng model sao chung — renderer không cần biết nó khác. */
function mapAnnualStar(star: AnnualStar): StarViewModel {
  const element = isElementCode(star.element) ? star.element : null
  const elementLabel = element ? ELEMENT_COLOR_MAP[element].label : null
  return {
    code: star.id,
    name: star.name,
    category: 'ANNUAL',
    element,
    elementLabel,
    polarityPrefix: null,
    ariaLabel: [star.name, elementLabel && `hành ${elementLabel}`].filter(Boolean).join(', '),
    strength: null,
    strengthAbbr: null,
    strengthVerification: null,
    // Lưu tinh đi kèm lá số PROVISIONAL nên cũng chưa kiểm định, nhưng nó không
    // mang dấu * nào — cảnh báo nằm ở banner chung.
    provisional: true,
    isMajor: false,
    isTransformation: false,
    isAnnual: true,
    palaceBranch: star.palace_branch,
    displayPriority: star.display_priority,
    verificationStatus: 'PROVISIONAL',
    provenance: null,
    transformations: [],
    annualTransformations: [],
  }
}

function mapStar(
  star: ChartStar,
  fallback: StarCategory,
  annualByStarId?: Map<string, StarTransformationViewModel[]>,
): StarViewModel {
  const category = categoryOf(star, fallback)
  const raw = field(star, 'element')
  const element = isElementCode(raw) ? raw : null
  const polarity = polarityOf(star)
  const elementLabel = element ? ELEMENT_COLOR_MAP[element].label : null
  const strengthLabel = star.strength ? STRENGTH_LABELS[star.strength] : null
  const provenance = provenanceOf(star)
  const transformations = transformationsOf(star)
  // `id`/`name` are the contract; `code`/`label` are the schema v1 spelling of the
  // same values. Neither is derived from the other.
  const id = optionalString(star, 'id') ?? optionalString(star, 'code') ?? ''
  const name = optionalString(star, 'name') ?? optionalString(star, 'label') ?? ''
  return {
    code: id,
    name,
    category,
    palaceBranch: optionalString(star, 'palace_branch'),
    displayPriority: optionalNumber(star, 'display_priority') ?? STAR_CATEGORY_PRIORITY[category],
    // Trust comes from the engine. A chart that sent none is UNVERIFIED, which is
    // the safe reading — never the flattering one.
    verificationStatus:
      verificationOf(field(star, 'verification_status')) ??
      provenance?.verification ??
      'UNVERIFIED',
    provenance,
    strengthVerification: star.strength
      ? (verificationOf(field(star, 'strength_verification')) ?? 'UNVERIFIED')
      : null,
    isMajor: category === 'MAJOR',
    element,
    elementLabel,
    polarityPrefix: polarity ? POLARITY_PREFIX[polarity] : null,
    // Spelled out because colour alone must not carry the element.
    ariaLabel: [
      name,
      ...transformations.map((t) => t.fullLabel),
      ...(annualByStarId?.get(id) ?? []).map((t) => `lưu niên ${t.fullLabel}`),
      elementLabel && `hành ${elementLabel}`,
      strengthLabel,
    ]
      .filter(Boolean)
      .join(', '),
    strength: star.strength,
    strengthAbbr: star.strength ? STRENGTH_ABBREVIATIONS[star.strength] : null,
    provisional: star.provisional,
    isTransformation: category === 'TRANSFORMATION',
    transformations,
    annualTransformations: annualByStarId?.get(id) ?? [],
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
      'vẽ bằng mực trung tính. Xem cosmic_astrology/stars/catalog.py.',
  )
}

/** Stable by category priority; the engine's own order survives within a category. */
function byDisplayPriority(stars: StarViewModel[]): StarViewModel[] {
  return stars
    .map((star, index) => ({ star, index }))
    // Engine-supplied priority; ties keep the engine's own order.
    .sort((a, b) => a.star.displayPriority - b.star.displayPriority || a.index - b.index)
    .map(({ star }) => star)
}

/** Dữ liệu lưu niên đã sắp sẵn theo địa chi, để `mapPalace` không phải lọc lại. */
interface AnnualIndex {
  starsByBranch: Map<number, StarViewModel[]>
  palaceRefByBranch: Map<number, string>
  transformationsByStarId: Map<string, StarTransformationViewModel[]>
}

function indexAnnual(annual: AnnualChart | null): AnnualIndex | null {
  if (!annual) return null
  const starsByBranch = new Map<number, StarViewModel[]>()
  for (const star of annual.stars) {
    const list = starsByBranch.get(star.palace_branch_index) ?? []
    list.push(mapAnnualStar(star))
    starsByBranch.set(star.palace_branch_index, list)
  }
  const transformationsByStarId = new Map<string, StarTransformationViewModel[]>()
  for (const entry of annual.transformations) {
    const code = entry.transformation
    if (!TRANSFORMATION_CODES.has(code)) continue
    const list = transformationsByStarId.get(entry.star_id) ?? []
    list.push({
      code,
      label: `L.${TRANSFORMATION_LABELS[code]}`,
      fullLabel: `Lưu ${TRANSFORMATION_FULL_LABELS[code]}`,
      // Chưa có ô bằng chứng nào cho độ sáng của hóa lưu niên. Mượn giá trị của hóa
      // bản mệnh cùng tên sẽ là bịa: đó là hai trạng thái khác nhau trên hai lớp khác nhau.
      strengthAbbr: null,
      strengthLabel: null,
    })
    transformationsByStarId.set(entry.star_id, list)
  }
  return {
    starsByBranch,
    palaceRefByBranch: new Map(
      annual.palaces.map((p) => [p.branch_index, `LN.${p.short_label}`]),
    ),
    transformationsByStarId,
  }
}

function mapPalace(
  palace: ChartPalace,
  starsPlaced: boolean,
  annual: AnnualIndex | null,
): PalaceViewModel {
  const { row, col } = gridPosition(palace.branch_index)
  const byStar = annual?.transformationsByStarId
  const majorStars = byDisplayPriority(palace.major_stars.map((s) => mapStar(s, 'MAJOR', byStar)))
  const minorStars = byDisplayPriority([
    ...palace.transformations.map((s) => mapStar(s, 'TRANSFORMATION', byStar)),
    ...palace.minor_stars.map((s) => mapStar(s, 'OTHER', byStar)),
    // Schema v2 only; grouped with the phụ tinh for layout, category preserved.
    ...(palace.annual_stars ?? []).map((s) => mapStar(s, 'ANNUAL', byStar)),
    // Lưu tinh của năm xem. Chúng là instance RIÊNG — không sao bản mệnh nào bị
    // sửa, nên bỏ năm xem đi là lá số trở về đúng như cũ.
    ...(annual?.starsByBranch.get(palace.branch_index) ?? []),
  ])
  // A FRAME-stage chart places no stars, yet the engine still flags every palace
  // as empty. "Vô chính diệu" is a statement about the chart, so it is only shown
  // once the engine has actually placed the major stars.
  const isEmptyMainStar = starsPlaced && palace.is_empty_main_star
  // Read from `cycles`, which is where schema v2 puts them. The keys these lines
  // used to read (`life_stage`, `major_cycle_palace`) are emitted by no version of
  // the engine, so they would have stayed null even once đại vận is implemented.
  const cycles = palace.cycles ?? null
  const lifeStage = cycles?.trang_sinh_stage ?? null
  const majorCycleRef =
    typeof cycles?.major_cycle_index === 'number' ? `ĐV ${cycles.major_cycle_index}` : null
  // Ô phải của footer: cung lưu niên trên địa chi này. `cycles.annual_target` là
  // một khái niệm khác (đang xem lưu niên nào) và vẫn chưa cài.
  const annualRef = annual?.palaceRefByBranch.get(palace.branch_index) ?? null
  // Hai dạng của cùng một con số, không phải hai con số. Lá số in ghi **một** trị
  // ở góc cung — tuổi khởi đại vận; khoảng đầy đủ đi vào tooltip thay vì chiếm chỗ
  // trên một ô đã chật. Cả hai đều đọc thẳng từ engine, không tính lại gì.
  const majorCycleAgeStart = optionalNumber(cycles ?? {}, 'major_cycle_age_start')
  const majorCycleAge = formatAgeRange(
    cycles?.major_cycle_age_start ?? null,
    cycles?.major_cycle_age_end ?? null,
  )

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
    palaceIndex: optionalNumber(palace, 'palace_index'),
    cycles,
    majorCycleAge,
    majorCycleAgeStart,
    annualPalaceRef: annual?.palaceRefByBranch.get(palace.branch_index) ?? null,
    monthNumber: optionalNumber(palace, 'month_number'),
    lifeStage,
    majorCycleRef,
    annualRef,
    // Spelled out because the footer reads as two bare fragments otherwise.
    ariaLabel: [
      `Cung ${palace.label}`,
      `${palace.stem} ${palace.branch}`,
      majorCycleAge && `đại vận ${majorCycleAge} tuổi`,
      lifeStage && `Tràng Sinh: ${lifeStage}`,
    ]
      .filter(Boolean)
      .join(', '),
    estimatedHeight: estimatePalaceHeight({
      majors: majorStars.length,
      emptyLine: isEmptyMainStar && majorStars.length === 0,
      minors: minorStars.length,
      footer: Boolean(lifeStage || majorCycleRef || annualRef),
      // Mỗi dòng Tứ Hóa chiếm chỗ riêng dưới ngôi sao mang nó. Bỏ sót chúng khỏi
      // phép ước lượng là cách cảnh báo tràn báo thiếu đúng ở cung đông nhất.
      hoaLines: [...majorStars, ...minorStars].reduce(
        (total, star) => total + star.transformations.length + star.annualTransformations.length,
        0,
      ),
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
      kinds: [kind],
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
      kinds: [kind],
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

/**
 * Gộp những dấu rơi vào cùng một đường biên thành một nhãn "Tuần - Triệt".
 *
 * Vị trí vẫn do engine quyết; chỗ này chỉ nhận ra hai dấu đang chồng lên nhau. Không
 * ghép chuỗi cứng ở tầng vẽ: nhãn dựng từ chính các dấu có mặt, nên biên nào chỉ có
 * một dấu thì vẫn chỉ hiện một chữ.
 */
function mergeCoincidentVoids(markers: VoidMarkerViewModel[]): VoidMarkerViewModel[] {
  const byBorder = new Map<string, VoidMarkerViewModel>()
  for (const marker of markers) {
    const border = `${marker.x}:${marker.y}:${marker.orientation}`
    const existing = byBorder.get(border)
    if (!existing) {
      byBorder.set(border, marker)
      continue
    }
    byBorder.set(border, {
      ...existing,
      kinds: [...existing.kinds, ...marker.kinds],
      label: `${existing.label} - ${marker.label}`,
    })
  }
  return [...byBorder.values()]
}

function link(from: number, to: number, type: ConnectionType): ConnectionViewModel {
  const start = centerAnchor(from)
  const end = centerAnchor(to)
  return { from, to, type, x1: start.x, y1: start.y, x2: end.x, y2: end.y }
}

/** Narrow an engine element string; anything unexpected loses its colour, not the value. */
function elementOf(value: unknown): ElementCode | null {
  return isElementCode(value) ? value : null
}

/**
 * "26 tuổi ta · 25 tuổi tròn" — cả hai, vì quy ước chưa chọn cách nào.
 *
 * Q11 chưa được trả lời, nên engine đưa ra hai con số và giao diện nói rõ cả hai
 * thay vì chọn hộ một cái rồi trình bày như thể đó là câu trả lời.
 */
function formatViewingAge(annual: AnnualChart | null): string | null {
  if (!annual || annual.age_tuoi_ta === null || annual.age_completed === null) return null
  return `${annual.age_tuoi_ta} tuổi ta · ${annual.age_completed} tuổi tròn`
}

/**
 * Direction of the đại vận walk, read off any palace that carries it.
 *
 * The engine stamps the same value on all twelve, so the first one that has it is
 * the answer; a chart that carries none (schema v1, or đại vận not computed) gives
 * `null` and the line is dropped.
 */
function majorCycleDirection(chart: ChartPayload): 'FORWARD' | 'BACKWARD' | null {
  for (const palace of chart.palaces) {
    const value = palace.cycles?.major_cycle_direction
    if (value === 'FORWARD' || value === 'BACKWARD') return value
  }
  return null
}

/**
 * The traditional block a printed chart carries in its centre.
 *
 * Every value here is either supplied by the engine or formatted from engine
 * values by `utils/tuvi-format`. Nothing is computed: can chi is joined, not
 * derived, and a field the engine does not produce is `pending` with a `null`
 * value so the renderer can leave the line out entirely.
 */
function centerFields(
  chart: ChartPayload,
  annual: AnnualChart | null = null,
): CenterFieldViewModel[] {
  const { birth, lunar_birth: lunar, pillars } = chart
  const traditional = chart.traditional ?? null

  const f = (
    label: string,
    value: string | null,
    secondary: string | null = null,
    element: ElementCode | null = null,
  ): CenterFieldViewModel => ({ label, value, secondary, element, pending: false })

  /** A field the chart should carry one day. Never given a stand-in value. */
  const pending = (label: string, value: string | null = null): CenterFieldViewModel => ({
    label,
    value,
    secondary: null,
    element: null,
    pending: value === null,
  })

  return [
    f('Họ tên', birth.name),
    f('Giới tính', formatGender(birth.gender)),
    f('Ngày dương', formatSolarDate(birth.solar), formatCalendarType(birth.calendar_type)),
    f('Ngày âm', formatLunarDate(lunar)),
    f('Giờ sinh', formatBirthTime(birth.solar.hour, birth.solar.minute, birth.hour_branch)),
    // Can chi comes structured from the engine; the formatter only joins the pair.
    f('Can Chi năm', formatPillar(pillars.year)),
    f('Can Chi tháng', formatPillar(pillars.month)),
    f('Can Chi ngày', formatPillar(pillars.day)),
    f('Can Chi giờ', formatPillar(pillars.hour)),
    // The engine already spells this out; the formatter exists for parts-only callers.
    f('Âm dương', chart.yin_yang.label),
    f('Bản mệnh', chart.menh.nap_am, null, elementOf(chart.menh.element)),
    f('Cục', chart.cuc.label, null, elementOf(chart.cuc.element)),
    f(
      'Mệnh – Cục',
      formatMenhCucRelation(
        optionalString(chart.cuc, 'relation'),
        elementOf(chart.menh.element),
        elementOf(chart.cuc.element),
      ) ?? chart.cuc.relation_label,
    ),
    f('Mệnh', chart.menh.branch),
    f('Thân', chart.than.branch, formatThanCu(chart.than.resides_in_label)),
    // Engine-calculated and, until now, visible nowhere: the đại vận walk runs one
    // way or the other and a reader cannot tell which from the palace footers alone.
    f('Chiều đại vận', formatCycleDirection(majorCycleDirection(chart))),
    // Not implemented anywhere in the engine — listed so the gap is visible in a
    // development view, and omitted entirely on a customer chart.
    pending('Cân lượng', traditional?.can_luong ?? null),
    pending('Chủ Mệnh', traditional?.chu_menh ?? null),
    pending('Chủ Thân', traditional?.chu_than ?? null),
    pending('Lai nhân cung', traditional?.lai_nhan_cung ?? null),
    // Năm xem đến từ khối lưu niên, không phải từ traditional metadata (vốn là
    // chỗ dành cho giá trị engine chưa tính).
    pending('Năm xem', annual ? `${annual.viewing_year} — ${annual.year_pillar}` : null),
    pending('Tuổi', formatViewingAge(annual)),
    // Ba dòng tóm tắt kiểu lá số in. Cả ba **đọc lại từ giá trị engine đã tính**,
    // không dòng nào so sánh lại gì: âm dương thuận/nghịch là ``is_thuan_ly``,
    // Mệnh–Cục là ``cuc.relation``, Thân–Mệnh là ``than.resides_in``. Tính lại ở
    // đây là mở đường cho frontend và engine bất đồng ý kiến về cùng một lá số.
    f('', formatAmDuongLy(chart.yin_yang.is_thuan_ly)),
    f('', chart.cuc.relation_label ?? null),
    f('', formatThanMenh(optionalString(chart.than, 'resides_in'), chart.than.resides_in_label)),
  ].map((entry) => (entry.value?.trim() ? entry : { ...entry, value: null }))
}

export function mapChartDtoToViewModel(
  chart: ChartPayload,
  annualChart: AnnualChart | null = null,
): ChartViewModel {
  const warnings: string[] = []
  const starsPlaced = chart.palaces.some((palace) => palace.major_stars.length > 0)
  const annual = indexAnnual(annualChart)
  const palaces = chart.palaces.map((palace) => mapPalace(palace, starsPlaced, annual))
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

  const voidMarkers = mergeCoincidentVoids(
    [
      voidMarker('TUAN', 'Tuần', palaces, warnings),
      voidMarker('TRIET', 'Triệt', palaces, warnings),
    ].filter((marker): marker is VoidMarkerViewModel => marker !== null),
  )

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
    center: {
      title: 'Lá Số Tử Vi',
      subtitle: 'Cosmic Signs',
      fields: centerFields(chart, annualChart),
    },
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
    identity: chart.identity ?? null,
    traditional: chart.traditional ?? null,
    // Absent means the chart predates the data contract, which is version 1 — a
    // fact about the stored payload, not a default for a field someone forgot.
    schemaVersion: optionalNumber(chart, 'schema_version') ?? 1,
    annual: annualChart
      ? {
          viewingYear: annualChart.viewing_year,
          label: `${annualChart.viewing_year} — ${annualChart.year_pillar}`,
          ageTuoiTa: annualChart.age_tuoi_ta,
          ageCompleted: annualChart.age_completed,
          ageConvention: annualChart.age_convention,
          starCount: annualChart.stars.length,
        }
      : null,
    warnings,
  }
}

/**
 * Memoised view model for a chart that may still be loading.
 *
 * The annual source is separate and optional: a chart renders perfectly well with
 * no viewing year, and supplying one adds data without touching the natal chart.
 */
export function useTuViChartViewModel(
  source: MaybeRefOrGetter<ChartPayload | null | undefined>,
  annualSource?: MaybeRefOrGetter<AnnualChart | null | undefined>,
) {
  return computed(() => {
    const chart = toValue(source)
    if (!chart) return null
    return mapChartDtoToViewModel(chart, (annualSource ? toValue(annualSource) : null) ?? null)
  })
}
