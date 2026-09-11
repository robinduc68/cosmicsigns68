import { describe, expect, it } from 'vitest'
import type { ChartPayload, ChartStar } from '@cosmic/shared'
import { mapChartDtoToViewModel } from '../composables/useTuViChartViewModel'
import { scenario } from '../fixtures/chart-renderer-scenarios'

/**
 * The frontend half of the chart data contract.
 *
 * The mapper is allowed to relabel, order and group. It is not allowed to supply
 * a value the engine did not send — so most of this file is about what comes out
 * `null` rather than what comes out populated.
 */

const real = () => structuredClone(scenario('cross-check-2001').chart)

describe('mapper preserves engine values', () => {
  it('carries element, polarity and strength through untouched', () => {
    const chart = real()
    const source = new Map(
      chart.palaces.flatMap((p) => p.major_stars.map((s) => [s.id!, s] as const)),
    )
    const mapped = mapChartDtoToViewModel(chart).palaces.flatMap((p) => p.majorStars)

    expect(mapped).toHaveLength(14)
    for (const star of mapped) {
      const origin = source.get(star.code)
      expect(origin, star.code).toBeDefined()
      expect(star.element).toBe(origin!.element)
      expect(star.strength).toBe(origin!.strength)
      expect(star.palaceBranch).toBe(origin!.palace_branch)
      // Polarity reaches the view model as a prefix, never as a colour.
      expect(star.polarityPrefix).toBe(
        origin!.polarity === 'YANG' ? '+' : origin!.polarity === 'YIN' ? '−' : null,
      )
    }
  })

  it('preserves every field the renderer is allowed to read', () => {
    // The five the data contract promises to carry end to end.
    const star = mapChartDtoToViewModel(real())
      .palaces.flatMap((p) => p.majorStars)
      .find((s) => s.code === 'THAI_AM')!
    expect(star.element).toBe('THUY')
    expect(star.polarityPrefix).toBe('−')
    expect(star.category).toBe('MAJOR')
    expect(star.strength).toBeNull()
    expect(star.verificationStatus).toBe('PROVISIONAL')
  })

  it('keeps the catalogued name rather than the raw id', () => {
    const star = mapChartDtoToViewModel(real())
      .palaces.flatMap((p) => p.majorStars)
      .find((s) => s.code === 'THIEN_DONG')!
    expect(star.name).toBe('Thiên Đồng')
  })

  it('keeps verification metadata instead of flattening it to a boolean', () => {
    const star = mapChartDtoToViewModel(real()).palaces.flatMap((p) => p.majorStars)[0]!
    expect(star.verificationStatus).toBe('PROVISIONAL')
    expect(star.provenance?.rule).toBe('major_stars/TWO_CHAINS_CLASSICAL')
    expect(star.provenance?.blocked_by).toEqual(['Q1', 'Q2', 'Q3'])
  })

  it('uses the ordering the engine supplied', () => {
    const chart = real()
    const menh = chart.palaces.find((p) => p.is_menh)!
    // Engine order reversed; a mapper that re-sorted by name or code would show it.
    menh.major_stars = [...menh.major_stars].reverse()
    const mapped = mapChartDtoToViewModel(chart).palaces.find((p) => p.isMenh)!
    expect(mapped.majorStars.map((s) => s.code)).toEqual(menh.major_stars.map((s) => s.id))
    expect(mapped.majorStars.every((s) => s.displayPriority === 0)).toBe(true)
  })

  it('passes chart identity and traditional metadata straight through', () => {
    const vm = mapChartDtoToViewModel(real())
    expect(vm.schemaVersion).toBe(2)
    expect(vm.identity?.chart_id).toBeNull()
    expect(vm.identity?.production_ready).toBe(false)
    expect(vm.traditional).toEqual({
      chu_menh: null,
      chu_than: null,
      lai_nhan_cung: null,
      can_luong: null,
      nam_xem: null,
      tuoi_xem: null,
    })
  })
})

describe('mapper invents nothing', () => {
  it('leaves every unimplemented field null', () => {
    const vm = mapChartDtoToViewModel(real())
    for (const palace of vm.palaces) {
      // Đại vận and Tràng Sinh are implemented; month number and lưu niên are not.
      expect(palace.monthNumber).toBeNull()
      expect(palace.annualRef).toBeNull()
      expect(palace.cycles?.annual_target ?? null).toBeNull()
      for (const star of [...palace.majorStars, ...palace.minorStars]) {
        expect(star.strength).toBeNull()
        expect(star.strengthAbbr).toBeNull()
        expect(star.strengthVerification).toBeNull()
      }
    }
  })

  it('does not substitute a placeholder string for a missing value', () => {
    const vm = mapChartDtoToViewModel(real())
    const banned = ['Unknown', 'N/A', 'NA', 'None', 'null', 'TBD', '-', '?']
    const texts = vm.palaces.flatMap((p) => [
      p.name,
      p.napAm,
      ...[...p.majorStars, ...p.minorStars].flatMap((s) => [s.name, s.elementLabel ?? '']),
    ])
    for (const text of texts) expect(banned).not.toContain(text.trim())
  })

  it('reads an unrecognised verification level as UNVERIFIED, not as verified', () => {
    const chart = real()
    const star = chart.palaces.flatMap((p) => p.major_stars)[0]!
    Object.assign(star, { verification_status: 'TOTALLY_FINE', provenance: null })
    const mapped = mapChartDtoToViewModel(chart).palaces.flatMap((p) => p.majorStars)
    expect(mapped.find((s) => s.code === star.id)!.verificationStatus).toBe('UNVERIFIED')
  })

  it('drops a half-populated provenance rather than showing part of it', () => {
    const chart = real()
    const star = chart.palaces.flatMap((p) => p.major_stars)[0]!
    Object.assign(star, { provenance: { rule: 'major_stars/X' } })
    const mapped = mapChartDtoToViewModel(chart).palaces.flatMap((p) => p.majorStars)
    expect(mapped.find((s) => s.code === star.id)!.provenance).toBeNull()
  })
})

describe('charts persisted under schema v1 still map', () => {
  /** A star exactly as the 11 stored development charts spell it. */
  const legacyStar = (code: string, label: string): ChartStar =>
    ({
      code,
      label,
      kind: 'MAJOR',
      strength: null,
      provisional: true,
      element: 'THUY',
      polarity: 'YIN',
    }) as unknown as ChartStar

  const legacyChart = (): ChartPayload => {
    const chart = real()
    delete (chart as { schema_version?: number }).schema_version
    delete (chart as { identity?: unknown }).identity
    delete (chart as { traditional?: unknown }).traditional
    for (const palace of chart.palaces) {
      palace.major_stars = palace.major_stars.map((s) => legacyStar(s.id!, s.name!))
      delete palace.stars
      delete palace.annual_stars
      delete palace.tuan
      delete palace.triet
      delete palace.cycles
      delete palace.palace_index
      delete palace.id
    }
    return chart
  }

  it('reads the v1 spelling of id, name and category', () => {
    const vm = mapChartDtoToViewModel(legacyChart())
    const stars = vm.palaces.flatMap((p) => p.majorStars)
    expect(stars).toHaveLength(14)
    expect(stars.every((s) => s.code.length > 0 && s.name.length > 0)).toBe(true)
    expect(stars.every((s) => s.category === 'MAJOR' && s.isMajor)).toBe(true)
  })

  it('reports version 1 rather than pretending the new fields exist', () => {
    const vm = mapChartDtoToViewModel(legacyChart())
    expect(vm.schemaVersion).toBe(1)
    expect(vm.identity).toBeNull()
    expect(vm.traditional).toBeNull()
    expect(vm.palaces.every((p) => p.palaceIndex === null && p.cycles === null)).toBe(true)
  })

  it('still draws Tuần and Triệt from the v1 booleans', () => {
    const vm = mapChartDtoToViewModel(legacyChart())
    expect(vm.voidMarkers.map((m) => m.kind).sort()).toEqual(['TRIET', 'TUAN'])
  })

  it('falls back to the local ordering when the engine sent no priority', () => {
    const vm = mapChartDtoToViewModel(legacyChart())
    expect(vm.palaces.flatMap((p) => p.majorStars).every((s) => s.displayPriority === 0)).toBe(
      true,
    )
  })
})

describe('palace name and earthly branch stay separate concepts', () => {
  it('never derives one from the other', () => {
    const vm = mapChartDtoToViewModel(real())
    expect(vm.palaces).toHaveLength(12)
    for (const palace of vm.palaces) {
      expect(palace.branch.length).toBeGreaterThan(0)
      expect(palace.name.length).toBeGreaterThan(0)
    }
    // Twelve distinct branches and twelve distinct palace names, independently.
    expect(new Set(vm.palaces.map((p) => p.branch)).size).toBe(12)
    expect(new Set(vm.palaces.map((p) => p.name)).size).toBe(12)
  })
})

describe('the normalized star model iterates uniformly', () => {
  it('renders every category through one code path', () => {
    const vm = mapChartDtoToViewModel(structuredClone(scenario('star-categories-demo').chart))
    const menh = vm.palaces.find((p) => p.isMenh)!
    const categories = new Set([...menh.majorStars, ...menh.minorStars].map((s) => s.category))
    for (const expected of [
      'MAJOR',
      'SUPPORTING',
      'MALEFIC',
      'LITERARY',
      'ROMANCE',
      'WEALTH',
      'TRANSFORMATION',
      'ANNUAL',
      'OTHER',
    ]) {
      expect(categories).toContain(expected)
    }
  })

  it('orders the phụ tinh group by the engine priority', () => {
    const vm = mapChartDtoToViewModel(structuredClone(scenario('star-categories-demo').chart))
    const menh = vm.palaces.find((p) => p.isMenh)!
    const priorities = menh.minorStars.map((s) => s.displayPriority)
    expect(priorities).toEqual([...priorities].sort((a, b) => a - b))
    // Lưu stars sort last without being hidden or faded out.
    expect(menh.minorStars.at(-1)!.isAnnual).toBe(true)
  })
})
