import { describe, expect, it } from 'vitest'
import { EARTHLY_BRANCHES, type ChartPayload } from '@cosmic/shared'
import { mapChartDtoToViewModel } from '../composables/useTuViChartViewModel'
import { scenario } from '../fixtures/chart-renderer-scenarios'
import { centerAnchor, elementColor } from '../utils/tuvi-chart'

const real = () => structuredClone(scenario('cross-check-2001').chart)
const branchNames = (indexes: number[]) => indexes.map((i) => EARTHLY_BRANCHES[i]).sort()

describe('mapChartDtoToViewModel', () => {
  it('places twelve palaces on the fixed địa bàn and leaves the four centre slots empty', () => {
    const vm = mapChartDtoToViewModel(real())
    expect(vm.palaces).toHaveLength(12)
    expect(vm.cells).toHaveLength(16)
    const centre = vm.cells.flatMap((cell, slot) => (cell ? [] : [slot]))
    expect(centre).toEqual([5, 6, 9, 10])
    expect(vm.cells.filter((cell) => cell !== null).map((cell) => cell!.branch)).toEqual([
      'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Thìn', 'Dậu', 'Mão', 'Tuất', 'Dần', 'Sửu', 'Tý', 'Hợi',
    ])
  })

  it('keeps palace names exactly as the engine sent them', () => {
    const chart = real()
    const vm = mapChartDtoToViewModel(chart)
    const mapped = Object.fromEntries(vm.palaces.map((p) => [p.branch, p.name]))
    const engine = Object.fromEntries(chart.palaces.map((p) => [p.branch, p.label]))
    expect(mapped).toEqual(engine)
  })

  it('does not move a single star', () => {
    const chart = real()
    const vm = mapChartDtoToViewModel(chart)
    const mapped = vm.palaces.flatMap((p) => p.majorStars.map((s) => `${s.code}@${p.branch}`))
    const engine = chart.palaces.flatMap((p) => p.major_stars.map((s) => `${s.code}@${p.branch}`))
    expect(mapped.sort()).toEqual(engine.sort())
  })

  it('omits strength when the engine sent none, and shows it once the engine does', () => {
    const plain = mapChartDtoToViewModel(real()).palaces.flatMap((p) => p.majorStars)
    expect(plain).toHaveLength(14)
    expect(plain.every((s) => s.strength === null && s.strengthAbbr === null)).toBe(true)

    const chart = real()
    chart.palaces[0]!.major_stars[0]!.strength = 'MIEU'
    const star = mapChartDtoToViewModel(chart).palaces[0]!.majorStars[0]!
    expect(star.strengthAbbr).toBe('M')
  })

  it('never guesses a star element from its name, but uses one the engine declares', () => {
    const plain = mapChartDtoToViewModel(real()).palaces.flatMap((p) => p.majorStars)
    expect(plain.every((s) => s.element === null)).toBe(true)

    const chart = real()
    Object.assign(chart.palaces[0]!.major_stars[0]!, { element: 'THUY' })
    expect(mapChartDtoToViewModel(chart).palaces[0]!.majorStars[0]!.element).toBe('THUY')

    const bogus = real()
    Object.assign(bogus.palaces[0]!.major_stars[0]!, { element: 'NOT_AN_ELEMENT' })
    expect(mapChartDtoToViewModel(bogus).palaces[0]!.majorStars[0]!.element).toBeNull()
  })

  it('puts Tuần and Triệt on the border their two palaces share', () => {
    const vm = mapChartDtoToViewModel(real())
    const tuan = vm.voidMarkers.find((m) => m.kind === 'TUAN')!
    const triet = vm.voidMarkers.find((m) => m.kind === 'TRIET')!
    // Thân sits top-right with Dậu below it; Tỵ top-left with Thìn below.
    expect(branchNames(tuan.branches)).toEqual(['Dậu', 'Thân'])
    expect(tuan).toMatchObject({ orientation: 'horizontal', x: 87.5, y: 25 })
    expect(branchNames(triet.branches)).toEqual(['Thìn', 'Tỵ'])
    expect(triet).toMatchObject({ orientation: 'horizontal', x: 12.5, y: 25 })
  })

  it('handles a border shared side by side as well', () => {
    const vm = mapChartDtoToViewModel(structuredClone(scenario('at-suu-1985').chart))
    const triet = vm.voidMarkers.find((m) => m.kind === 'TRIET')!
    expect(branchNames(triet.branches)).toEqual(['Mùi', 'Ngọ'])
    // Low in the top row, so the label does not cut through the star area.
    expect(triet).toMatchObject({ orientation: 'vertical', x: 50, y: 22 })
  })

  it('warns instead of guessing when the Tuần flags do not make a pair', () => {
    const chart = real()
    chart.palaces.forEach((p) => (p.has_tuan = false))
    chart.palaces[0]!.has_tuan = true
    const vm = mapChartDtoToViewModel(chart)
    expect(vm.voidMarkers.some((m) => m.kind === 'TUAN')).toBe(false)
    expect(vm.warnings.join(' ')).toContain('Tuần')
  })

  it('draws only the tam phương tứ chính the engine supplied', () => {
    const chart = real()
    const d = chart.menh.three_directions_four_positions
    const vm = mapChartDtoToViewModel(chart)
    expect(vm.connections).toHaveLength(4)
    expect(new Set(vm.connections.flatMap((c) => [c.from, c.to]))).toEqual(
      new Set([d.self, d.trine_left, d.trine_right, d.opposite]),
    )
    const opposite = vm.connections.filter((c) => c.type === 'OPPOSITE')
    expect(opposite).toEqual([expect.objectContaining({ from: d.self, to: d.opposite })])
  })

  it('lists only centre fields that exist and invents none', () => {
    const chart = real()
    chart.birth.name = ''
    const labels = mapChartDtoToViewModel(chart).center.fields.map((f) => f.label)
    expect(labels).not.toContain('Họ tên')
    for (const notProduced of ['Chủ mệnh', 'Chủ thân', 'Năm xem', 'Cân lượng']) {
      expect(labels).not.toContain(notProduced)
    }
    expect(labels).toContain('Cục')
  })

  it('does not print "Vô chính diệu" on a chart whose stars were never placed', () => {
    const vm = mapChartDtoToViewModel(structuredClone(scenario('cross-check-2001-frame').chart))
    expect(vm.palaces.every((p) => p.majorStars.length === 0)).toBe(true)
    expect(vm.palaces.some((p) => p.isEmptyMainStar)).toBe(false)

    const placed = mapChartDtoToViewModel(real())
    expect(placed.palaces.filter((p) => p.isEmptyMainStar).map((p) => p.branch).sort()).toEqual(
      ['Thân', 'Tỵ'],
    )
  })

  it('reads engine and convention metadata and flags unverified data', () => {
    const meta = mapChartDtoToViewModel(real()).meta
    expect(meta.provisional).toBe(true)
    expect(meta.engineVersion).toBe('0.2.0-frame')
    expect(meta.conventionProfile).toBe('COSMIC_SIGNS_STANDARD_V1')
    expect(meta.utcOffsetHours).toBe(7)
    expect(mapChartDtoToViewModel(scenario('authoritative-demo').chart).meta.provisional).toBe(false)
  })

  it('tolerates charts stored before the convention layer existed', () => {
    const chart = real() as unknown as Record<string, unknown>
    delete chart.timezone
    delete chart.convention
    const engine = chart.engine as Record<string, unknown>
    delete engine.convention_profile
    delete engine.convention_version
    const meta = mapChartDtoToViewModel(chart as unknown as ChartPayload).meta
    expect(meta.conventionProfile).toBeNull()
    expect(meta.utcOffsetHours).toBeNull()
  })

  it('warns in development when a palace would overflow, and not before', () => {
    expect(mapChartDtoToViewModel(scenario('dense-demo').chart).warnings).toEqual([])
    const overflow = mapChartDtoToViewModel(scenario('overflow-demo').chart).warnings
    expect(overflow.some((w) => w.includes('vượt sức chứa'))).toBe(true)
  })

  it('orders by display category but keeps the engine order inside a category', () => {
    const chart = real()
    const palace = chart.palaces[0]!
    palace.minor_stars = [
      { code: 'B', label: 'Sao mẫu B', kind: 'MINOR', strength: null, provisional: true },
      { code: 'A', label: 'Sao mẫu A', kind: 'MINOR', strength: null, provisional: true },
    ]
    palace.transformations = [
      { code: 'T', label: 'Hóa mẫu', kind: 'TRANSFORMATION', strength: null, provisional: true },
    ]
    const codes = mapChartDtoToViewModel(chart).palaces[0]!.minorStars.map((s) => s.code)
    expect(codes).toEqual(['T', 'B', 'A'])
  })
})

describe('chart geometry and colour', () => {
  it('derives centre anchors from the grid', () => {
    expect(centerAnchor(5)).toEqual({ x: 0, y: 0 }) // Tỵ, top-left corner
    expect(centerAnchor(6)).toEqual({ x: 25, y: 0 }) // Ngọ, top edge
    expect(centerAnchor(3)).toEqual({ x: 0, y: 75 }) // Mão, left edge
    expect(centerAnchor(11)).toEqual({ x: 100, y: 100 }) // Hợi, bottom-right corner
  })

  it('maps elements through one colour table and falls back to neutral ink', () => {
    expect(elementColor('HOA')).toBe('var(--chart-hoa)')
    expect(elementColor(null)).toBe('var(--chart-text)')
  })
})
