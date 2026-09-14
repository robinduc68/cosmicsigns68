import type {
  ChartIdentity,
  ChartPalaceCycles,
  ChartTraditionalMetadata,
  ElementCode,
  StarCategory,
  StarProvenance,
  StarStrength,
  Transformation,
  VerificationStatus,
} from '@cosmic/shared'

export type { StarCategory }

/**
 * Visual model of a Tử Vi chart.
 *
 * Everything in here was already decided by the astrology engine. The mapper that
 * builds it reshapes and labels engine output; it never places a star, chooses a
 * palace or supplies a value the engine did not send. A field the engine does not
 * produce yet is `null`, and the renderer leaves it out.
 */


export interface StarViewModel {
  code: string
  name: string
  category: StarCategory
  /** Declared by the engine. `null` renders as neutral text — never guessed from the name. */
  element: ElementCode | null
  /** `'Kim'`, `'Mộc'`… for tooltips and screen readers. `null` alongside `element`. */
  elementLabel: string | null
  /** `'+'` for dương, `'−'` for âm, `null` when the engine declared no polarity. */
  polarityPrefix: string | null
  /** "Thái Âm, hành Thủy, Miếu" — colour is never the only carrier of meaning. */
  ariaLabel: string
  /** `null` when the engine sent no strength; the abbreviation is then omitted. */
  strength: StarStrength | null
  strengthAbbr: string | null
  /** Set exactly when `strength` is; unknown is never presented as verified. */
  strengthVerification: VerificationStatus | null
  provisional: boolean
  isMajor: boolean
  isTransformation: boolean
  isAnnual: boolean
  /** Địa chi the engine placed this star on. `null` on schema v1 payloads. */
  palaceBranch: string | null
  /** Engine-supplied ordering; falls back to a local table for schema v1. */
  displayPriority: number
  verificationStatus: VerificationStatus
  provenance: StarProvenance | null
  /**
   * Tứ Hóa this star carries, ready to render. Empty for most stars; a list so a
   * star can hold more than one once đại vận and lưu niên hóa arrive.
   */
  transformations: StarTransformationViewModel[]
}

export interface StarTransformationViewModel {
  code: Transformation
  /** `"Lộc"` — what the marker shows. */
  label: string
  /** `"Hóa Lộc"` — what a screen reader and the tooltip say. */
  fullLabel: string
}

export interface PalaceViewModel {
  id: string
  name: string
  stem: string
  stemShort: string
  branch: string
  branchIndex: number
  /** 1-based slot in the fixed địa bàn grid. */
  row: number
  col: number
  element: ElementCode
  elementLabel: string
  napAm: string
  isMenh: boolean
  isThan: boolean
  hasTuan: boolean
  hasTriet: boolean
  isEmptyMainStar: boolean
  majorStars: StarViewModel[]
  minorStars: StarViewModel[]
  /** Position of this palace name in the classical sequence from Mệnh (0-11). */
  palaceIndex: number | null
  /** Đại vận / lưu niên / Tràng Sinh. Every field is `null` today. */
  cycles: ChartPalaceCycles | null
  /** Đại vận age span, e.g. `"6 – 15"`. `null` until đại vận is implemented. */
  majorCycleAge: string | null
  monthNumber: number | null
  lifeStage: string | null
  majorCycleRef: string | null
  annualRef: string | null
  ariaLabel: string
  /** Estimated content height in canvas pixels, for the development overflow guard. */
  estimatedHeight: number
}

export type VoidKind = 'TUAN' | 'TRIET'

export interface VoidMarkerViewModel {
  kind: VoidKind
  label: string
  branches: [number, number]
  /** Centre of the border the two palaces share, as a percentage of the canvas. */
  x: number
  y: number
  /** Direction of that shared border. */
  orientation: 'horizontal' | 'vertical'
}

export type ConnectionType = 'TRINE' | 'OPPOSITE'

export interface ConnectionViewModel {
  from: number
  to: number
  type: ConnectionType
  /** Endpoints inside the centre panel, 0–100 on each axis. */
  x1: number
  y1: number
  x2: number
  y2: number
}

export interface CenterFieldViewModel {
  label: string
  /**
   * `null` when the engine does not supply this field. The renderer omits the line;
   * it is never shown as `"—"`, `"Không rõ"` or a zero, which would read as data.
   */
  value: string | null
  secondary: string | null
  /** Set only on fields whose value *is* an element name (bản mệnh, cục). */
  element: ElementCode | null
  /**
   * True for a field the chart is expected to carry one day but does not yet.
   * Lets a development view list what is missing without inventing content for it.
   */
  pending: boolean
}

export interface ChartMetaViewModel {
  engineVersion: string
  conventionProfile: string | null
  conventionVersion: string | null
  stage: string
  isAuthoritative: boolean
  /** True whenever anything on the chart has not been verified. */
  provisional: boolean
  utcOffsetHours: number | null
}

export interface ChartViewModel {
  palaces: PalaceViewModel[]
  /** 16 grid slots in reading order; `null` marks the centre panel. */
  cells: (PalaceViewModel | null)[]
  center: { title: string; subtitle: string; fields: CenterFieldViewModel[] }
  voidMarkers: VoidMarkerViewModel[]
  connections: ConnectionViewModel[]
  meta: ChartMetaViewModel
  /** Which engine and rulebook produced this chart. `null` on schema v1. */
  identity: ChartIdentity | null
  /** Traditional fields the engine does not compute. All `null` today. */
  traditional: ChartTraditionalMetadata | null
  /** 1 for charts persisted before the data contract, 2 afterwards. */
  schemaVersion: number
  warnings: string[]
}

/** How the viewer presents a chart: the whole địa bàn, or one palace after another. */
export type ChartViewMode = 'overview' | 'reading'
