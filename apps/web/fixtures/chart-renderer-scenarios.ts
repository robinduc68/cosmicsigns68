import type { ChartPayload, ChartStar } from '@cosmic/shared'
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

function demoStar(code: string, label: string): ChartStar {
  return { code, label, kind: 'MINOR', strength: null, provisional: true }
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
    description: 'Thêm 20 "Sao mẫu" mỗi cung, gần sức chứa. Không phải tử vi.',
    synthetic: true,
    chart: withDemoMinorStars(crossCheck, 20, (i) => `Sao mẫu ${i + 1}`),
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
