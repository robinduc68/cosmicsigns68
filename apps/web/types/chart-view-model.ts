import type { ElementCode, StarStrength } from '@cosmic/shared'

/**
 * Visual model of a Tử Vi chart.
 *
 * Everything in here was already decided by the astrology engine. The mapper that
 * builds it reshapes and labels engine output; it never places a star, chooses a
 * palace or supplies a value the engine did not send. A field the engine does not
 * produce yet is `null`, and the renderer leaves it out.
 */

export type StarCategory =
  | 'MAJOR'
  | 'TRANSFORMATION'
  | 'SUPPORTING'
  | 'MALEFIC'
  | 'MINOR'
  | 'ANNUAL'

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
  provisional: boolean
  isTransformation: boolean
  isAnnual: boolean
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
  /** Not produced by the engine yet — rendered only once present. */
  majorCycleAge: number | null
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
  value: string
  secondary: string | null
  /** Set only on fields whose value *is* an element name (bản mệnh, cục). */
  element: ElementCode | null
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
  warnings: string[]
}

/** How the viewer presents a chart: the whole địa bàn, or one palace after another. */
export type ChartViewMode = 'overview' | 'reading'
