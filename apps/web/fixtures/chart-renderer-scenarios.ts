import type {
  ChartPayload,
  ChartStar,
  ElementCode,
  StarCategory,
  StarStrength,
  YinYangPolarity,
} from '@cosmic/shared'
import { STAR_CATEGORY_PRIORITY } from '~/utils/tuvi-chart'
import atSuu1985 from './charts/at-suu-1985.preview.json'
import crossCheckFrame from './charts/cross-check-2001.frame.json'
import crossCheckPreview from './charts/cross-check-2001.preview.json'
import reference1992 from './charts/reference-1992.preview.json'

/**
 * Scenarios for the internal chart-renderer demo and its tests.
 *
 * `synthetic: false` scenarios are unmodified engine output. `synthetic: true`
 * ones exist only to stress the layout — dense palaces, long names, the
 * authoritative-badge state — and are built from a real chart with obviously fake
 * additions ("Sao mẫu", "(mẫu)"). They are not astrology and must never reach a
 * customer.
 */
export interface ChartRendererScenario {
  id: string
  label: string
  description: string
  synthetic: boolean
  chart: ChartPayload
}

// JSON imports infer literal string types; the engine payload shape is the contract.
const asChart = (json: unknown) => json as ChartPayload
const clone = (chart: ChartPayload): ChartPayload => structuredClone(chart)

function demoStar(
  id: string,
  name: string,
  element: ElementCode | null = null,
  polarity: YinYangPolarity | null = null,
  category: StarCategory = 'OTHER',
): ChartStar {
  return {
    id,
    name,
    category,
    element,
    polarity,
    strength: null,
    strength_verification: null,
    palace_branch: null,
    is_major: category === 'MAJOR',
    is_annual: category === 'ANNUAL',
    is_transformation: category === 'TRANSFORMATION',
    display_priority: STAR_CATEGORY_PRIORITY[category],
    verification_status: 'UNVERIFIED',
    provenance: null,
    provisional: true,
  }
}

/**
 * Strengths sprinkled onto real stars, so the `(M)` / `(V)` / `(Đ)` form can be
 * seen rendering next to the Ngũ Hành colour.
 *
 * The values are the fixture's own invention and carry `UNVERIFIED`. The real
 * table is 168 cells that must be copied from a chosen edition and is still empty
 * — see `docs/astrology-conventions.md` §19. Stars left untouched keep
 * `strength: null` and must render with no suffix at all.
 */
function withDemoStrengths(base: ChartPayload): ChartPayload {
  const chart = clone(base)
  const byStar: Record<string, StarStrength> = {
    THAI_AM: 'MIEU',
    THIEN_CO: 'DAC',
    PHA_QUAN: 'VUONG',
    LIEM_TRINH: 'HAM',
    VAN_XUONG: 'BINH',
  }
  // Every list has to be touched: the payload arrives as JSON, so `stars` and the
  // grouped lists are separate objects rather than views of one another — and the
  // mapper reads the grouped ones.
  for (const palace of chart.palaces) {
    const lists = [
      palace.stars ?? [],
      palace.major_stars,
      palace.minor_stars,
      palace.transformations,
      palace.annual_stars ?? [],
    ]
    for (const star of lists.flat()) {
      const value = byStar[star.id ?? '']
      if (value) {
        star.strength = value
        star.strength_verification = 'UNVERIFIED'
      }
    }
  }
  return chart
}

/**
 * One openly fake star per category, so the normalized star model can be seen
 * iterating and ordering consistently.
 *
 * Categories are assigned by this fixture, never by the engine — the engine places
 * only chính tinh today. `strength` stays `null` everywhere: the miếu/vượng table
 * is not implemented, and a fixture is not a licence to invent one.
 */
function withEveryStarCategory(base: ChartPayload): ChartPayload {
  const chart = clone(base)
  const menh = chart.palaces.find((palace) => palace.is_menh) ?? chart.palaces[0]
  if (!menh) throw new Error('Lá số nền không có cung nào')
  const categories: StarCategory[] = [
    'SUPPORTING',
    'MALEFIC',
    'LITERARY',
    'ROMANCE',
    'WEALTH',
    'OTHER',
  ]
  menh.minor_stars = categories.map((category) =>
    demoStar(`CAT_${category}`, `${category} mẫu`, null, null, category),
  )
  menh.transformations = [demoStar('CAT_HOA', 'Hóa mẫu', null, null, 'TRANSFORMATION')]
  menh.annual_stars = [demoStar('CAT_LUU', 'L.Lưu mẫu', null, null, 'ANNUAL')]
  return chart
}

/**
 * One star per ngũ hành in a single palace, so all five colours can be compared
 * side by side without hunting across the địa bàn.
 *
 * The names are openly fake ("mẫu"). The point is the colour system, not astrology:
 * these elements are assigned by this fixture, never by the engine, and a sixth
 * entry with `element: null` shows what an unverified star looks like.
 */
function withFiveElementPalette(base: ChartPayload): ChartPayload {
  const chart = clone(base)
  const palette: [string, ElementCode | null, YinYangPolarity | null, StarStrength | null][] = [
    ['Kim mẫu', 'KIM', 'YANG', 'MIEU'],
    ['Mộc mẫu', 'MOC', 'YIN', 'VUONG'],
    ['Thủy mẫu', 'THUY', 'YANG', 'DAC'],
    ['Hỏa mẫu', 'HOA', 'YIN', 'BINH'],
    ['Thổ mẫu', 'THO', 'YANG', 'HAM'],
    ['Chưa rõ hành (mẫu)', null, null, null],
  ]
  const menh = chart.palaces.find((palace) => palace.is_menh) ?? chart.palaces[0]
  if (!menh) throw new Error('Lá số nền không có cung nào')
  // The strengths below are the fixture's own invention, which is why each one
  // carries UNVERIFIED: the miếu/vượng table is not implemented, and the shape
  // "value + verification" is what stops a demo value being read as a real one.
  const withStrength = (star: ChartStar, strength: StarStrength | null): ChartStar => ({
    ...star,
    strength,
    strength_verification: strength ? 'UNVERIFIED' : null,
  })

  menh.minor_stars = palette.map(([label, element, polarity, strength], i) =>
    withStrength(demoStar(`PALETTE_${i}`, label, element, polarity), strength),
  )
  // A second copy as major stars, to show the typography split at the same colours.
  menh.major_stars = [
    ...menh.major_stars,
    ...palette.map(([label, element, polarity, strength], i) =>
      withStrength(demoStar(`PALETTE_MAJOR_${i}`, label, element, polarity, 'MAJOR'), strength),
    ),
  ]
  return chart
}

function withDemoMinorStars(
  base: ChartPayload,
  perPalace: number,
  label: (index: number) => string,
): ChartPayload {
  const chart = clone(base)
  chart.palaces.forEach((palace, p) => {
    palace.minor_stars = Array.from({ length: perPalace }, (_, i) =>
      demoStar(`DEMO_${p}_${i}`, label(i)),
    )
  })
  return chart
}

function asAuthoritativeDemo(base: ChartPayload): ChartPayload {
  const chart = clone(base)
  chart.engine = { ...chart.engine, stage: 'FULL', is_authoritative: true }
  for (const palace of chart.palaces) {
    for (const star of [...palace.major_stars, ...palace.minor_stars, ...palace.transformations]) {
      star.provisional = false
    }
  }
  return chart
}

const crossCheck = asChart(crossCheckPreview)

export const CHART_RENDERER_SCENARIOS: ChartRendererScenario[] = [
  {
    id: 'cross-check-2001',
    label: 'Lá số thật — Âm nữ 2001',
    description: 'Đầu ra engine 0.2.0. Có Tuần/Triệt, cung vô chính diệu, 14 chính tinh.',
    synthetic: false,
    chart: crossCheck,
  },
  {
    id: 'reference-1992',
    label: 'Lá số thật — Dương nam 1992',
    description: 'Đầu ra engine 0.2.0. Mệnh ở Dần, Tuần Tuất–Hợi, Triệt Dần–Mão.',
    synthetic: false,
    chart: asChart(reference1992),
  },
  {
    id: 'at-suu-1985',
    label: 'Lá số thật — Triệt nằm ngang hàng',
    description: 'Đầu ra engine 0.2.0. Triệt ở Ngọ–Mùi, vắt qua một viền dọc.',
    synthetic: false,
    chart: asChart(atSuu1985),
  },
  {
    id: 'cross-check-2001-frame',
    label: 'Lá số thật — chưa an sao',
    description: 'Stage FRAME: 12 cung không có sao nào. Không được in "Vô chính diệu".',
    synthetic: false,
    chart: asChart(crossCheckFrame),
  },
  {
    id: 'dense-demo',
    label: 'GIẢ — nhiều sao',
    // 18, not 20: every palace now carries a đại vận / Tràng Sinh footer, which
    // costs 30px of star space. "Gần sức chứa" has to track that.
    description: 'Thêm 18 "Sao mẫu" mỗi cung, gần sức chứa. Không phải tử vi.',
    synthetic: true,
    chart: withDemoMinorStars(crossCheck, 18, (i) => `Sao mẫu ${i + 1}`),
  },
  {
    id: 'overflow-demo',
    label: 'GIẢ — quá tải',
    description: 'Thêm 30 "Sao mẫu" mỗi cung để thử cảnh báo tràn. Không phải tử vi.',
    synthetic: true,
    chart: withDemoMinorStars(crossCheck, 30, (i) => `Sao mẫu ${i + 1}`),
  },
  {
    id: 'long-names-demo',
    label: 'GIẢ — tên dài',
    description: 'Tên sao tiếng Việt dài để thử xuống dòng. Không phải tử vi.',
    synthetic: true,
    chart: withDemoMinorStars(crossCheck, 6, (i) => `Thiên Đức Quý Nhân Phúc Tinh (mẫu ${i + 1})`),
  },
  {
    id: 'five-element-palette',
    label: 'GIẢ — bảng màu 5 hành',
    description:
      'Sáu sao mẫu trong cung Mệnh: Kim, Mộc, Thủy, Hỏa, Thổ và một sao chưa rõ hành. ' +
      'Dùng để đối chiếu màu; hành do fixture gán, không phải engine. Không phải tử vi.',
    synthetic: true,
    chart: withFiveElementPalette(crossCheck),
  },
  {
    id: 'star-categories-demo',
    label: 'GIẢ — đủ 9 loại sao',
    description:
      'Mỗi loại sao một ngôi mẫu trong cung Mệnh, để thấy model sao chuẩn hóa được ' +
      'duyệt và sắp thứ tự thống nhất. Loại do fixture gán, không phải engine. Không phải tử vi.',
    synthetic: true,
    chart: withEveryStarCategory(crossCheck),
  },
  {
    id: 'strength-demo',
    label: 'GIẢ — độ sáng sao',
    description:
      'Gán độ sáng M/V/Đ/B/H cho vài sao để xem dạng "THÁI ÂM (M)". Độ sáng do fixture ' +
      'gán, KHÔNG phải engine — bảng 168 ô còn rỗng. Không phải tử vi.',
    synthetic: true,
    chart: withDemoStrengths(crossCheck),
  },
  {
    id: 'authoritative-demo',
    label: 'GIẢ — engine đã kiểm định',
    description: 'Giả lập stage FULL, chỉ để thấy badge cảnh báo biến mất. Không phải tử vi.',
    synthetic: true,
    chart: asAuthoritativeDemo(asChart(reference1992)),
  },
]

export function scenario(id: string): ChartRendererScenario {
  const found = CHART_RENDERER_SCENARIOS.find((entry) => entry.id === id)
  if (!found) throw new Error(`Không có kịch bản '${id}'`)
  return found
}
