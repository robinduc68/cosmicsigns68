import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import TuViCenter from '../components/astrology/chart/TuViCenter.vue'
import { mapChartDtoToViewModel } from '../composables/useTuViChartViewModel'
import { scenario } from '../fixtures/chart-renderer-scenarios'
import {
  formatAgeRange,
  formatBirthTime,
  formatCuc,
  formatGender,
  formatLunarDate,
  formatMenhCucRelation,
  formatPillar,
  formatSolarDate,
  formatThanCu,
  formatYinYang,
} from '../utils/tuvi-format'

const real = () => structuredClone(scenario('cross-check-2001').chart)
const vm = () => mapChartDtoToViewModel(real())
const field = (label: string) => vm().center.fields.find((f) => f.label === label)

describe('Vietnamese formatters', () => {
  it('labels gender and yin-yang the way a chart prints them', () => {
    expect(formatGender('FEMALE')).toBe('Nữ')
    expect(formatGender('MALE')).toBe('Nam')
    expect(formatYinYang(false, 'FEMALE')).toBe('Âm Nữ')
    expect(formatYinYang(true, 'MALE')).toBe('Dương Nam')
  })

  it('joins a pillar from the stem and branch the engine supplied', () => {
    expect(formatPillar({ can: 'Tân', chi: 'Tỵ' })).toBe('Tân Tỵ')
  })

  it('formats solar and lunar dates distinctly', () => {
    expect(formatSolarDate({ day: 4, month: 3, year: 2001 })).toBe('04/03/2001')
    expect(
      formatLunarDate({ day: 10, month: 2, is_leap_month: false, year_pillar: 'Tân Tỵ' }),
    ).toBe('10/02 Tân Tỵ')
  })

  it('marks a leap month, which is otherwise indistinguishable', () => {
    expect(
      formatLunarDate({ day: 10, month: 2, is_leap_month: true, year_pillar: 'Tân Tỵ' }),
    ).toBe('10/02 nhuận Tân Tỵ')
  })

  it('formats the birth time with its hour branch', () => {
    expect(formatBirthTime(9, 30, 'Tỵ')).toBe('09:30 (giờ Tỵ)')
    expect(formatBirthTime(9, 30)).toBe('09:30')
    expect(formatBirthTime(0, 5, 'Tý')).toBe('00:05 (giờ Tý)')
  })

  it('builds the cục name from its element and number', () => {
    expect(formatCuc('MOC', 3)).toBe('Mộc Tam Cục')
    expect(formatCuc('KIM', 4)).toBe('Kim Tứ Cục')
    expect(formatCuc('THUY', 2)).toBe('Thủy Nhị Cục')
  })

  it('spells the Mệnh–Cục relationship out with both elements', () => {
    expect(formatMenhCucRelation('MENH_KHAC_CUC', 'KIM', 'MOC')).toBe('Mệnh Kim khắc Cục Mộc')
    expect(formatMenhCucRelation('TUONG_HOA', 'THO', 'THO')).toBe('Mệnh Thổ tương hòa với Cục Thổ')
    // Whichever side acts comes first, so the line reads as a sentence.
    expect(formatMenhCucRelation('CUC_SINH_MENH', 'HOA', 'MOC')).toBe('Cục Mộc sinh Mệnh Hỏa')
    expect(formatMenhCucRelation('CUC_KHAC_MENH', 'KIM', 'HOA')).toBe('Cục Hỏa khắc Mệnh Kim')
    expect(formatMenhCucRelation('MENH_SINH_CUC', 'KIM', 'THUY')).toBe('Mệnh Kim sinh Cục Thủy')
  })

  it('formats thân cư and an age range', () => {
    expect(formatThanCu('Phu Thê')).toBe('cư Phu Thê')
    expect(formatAgeRange(6, 15)).toBe('6 – 15')
    expect(formatAgeRange(6, null)).toBe('6')
  })

  it('returns null for anything it cannot render, never a placeholder', () => {
    expect(formatGender(null)).toBeNull()
    expect(formatPillar(null)).toBeNull()
    expect(formatPillar({ can: '', chi: 'Tỵ' })).toBeNull()
    expect(formatSolarDate(null)).toBeNull()
    expect(formatLunarDate(undefined)).toBeNull()
    expect(formatBirthTime(null, 30)).toBeNull()
    expect(formatCuc('MOC', null)).toBeNull()
    // An unknown cục number is not guessed into a numeral.
    expect(formatCuc('MOC', 99)).toBeNull()
    expect(formatMenhCucRelation('KHONG_BIET', 'KIM', 'MOC')).toBeNull()
    expect(formatThanCu(null)).toBeNull()
    expect(formatAgeRange(null, 15)).toBeNull()
  })
})

describe('formatters agree with the engine', () => {
  /**
   * The engine sends `yin_yang.label`, `cuc.label` and `pillar.name` ready-made,
   * and the formatters can build the same strings from the parts. Two spellings of
   * one value is exactly how a chart ends up contradicting itself, so they are
   * pinned together here.
   */
  it('produces the same yin-yang label the engine sent', () => {
    const chart = real()
    expect(formatYinYang(chart.yin_yang.year_is_yang, chart.birth.gender)).toBe(
      chart.yin_yang.label,
    )
  })

  it('produces the same cục label the engine sent', () => {
    const chart = real()
    expect(formatCuc(chart.cuc.element, chart.cuc.number)).toBe(chart.cuc.label)
  })

  it('produces the same pillar names the engine sent', () => {
    const { pillars } = real()
    for (const pillar of [pillars.year, pillars.month, pillars.day, pillars.hour]) {
      expect(formatPillar(pillar)).toBe(pillar.name)
    }
  })
})

describe('centre mapping', () => {
  it('carries every traditional field the engine supports', () => {
    const expected: Record<string, string> = {
      'Họ tên': 'Nguyễn Thị Minh Anh',
      'Giới tính': 'Nữ',
      'Ngày dương': '04/03/2001',
      'Ngày âm': '10/02 Tân Tỵ',
      'Giờ sinh': '09:30 (giờ Tỵ)',
      'Can Chi năm': 'Tân Tỵ',
      'Can Chi tháng': 'Tân Mão',
      'Can Chi ngày': 'Bính Dần',
      'Can Chi giờ': 'Quý Tỵ',
      'Âm dương': 'Âm Nữ',
      'Bản mệnh': 'Bạch Lạp Kim',
      Cục: 'Mộc Tam Cục',
      'Mệnh – Cục': 'Mệnh Kim khắc Cục Mộc',
      Mệnh: 'Tuất',
      Thân: 'Thân',
    }
    for (const [label, value] of Object.entries(expected)) {
      expect(field(label)?.value, label).toBe(value)
    }
  })

  it('colours bản mệnh and cục only', () => {
    const coloured = vm().center.fields.filter((f) => f.element !== null)
    expect(coloured.map((f) => f.label)).toEqual(['Bản mệnh', 'Cục'])
  })

  it('shows where Thân resides as a secondary note', () => {
    expect(field('Thân')?.secondary).toBe('cư Phu Thê')
  })

  it('marks every unsupported field pending with no value', () => {
    const pending = vm().center.fields.filter((f) => f.pending)
    expect(pending.map((f) => f.label)).toEqual([
      'Cân lượng',
      'Chủ Mệnh',
      'Chủ Thân',
      'Lai nhân cung',
      'Năm xem',
      'Tuổi xem',
    ])
    expect(pending.every((f) => f.value === null)).toBe(true)
  })
})

describe('null omission in the renderer', () => {
  it('omits every unavailable line on a customer chart', async () => {
    const wrapper = await mountSuspended(TuViCenter, {
      props: { center: vm().center, connections: [] },
    })
    const text = wrapper.text()
    for (const label of ['Cân lượng', 'Chủ Mệnh', 'Chủ Thân', 'Lai nhân cung', 'Năm xem']) {
      expect(text).not.toContain(label)
    }
    expect(wrapper.findAll('[data-pending]')).toHaveLength(0)
    // And nothing stands in for them.
    for (const placeholder of ['N/A', 'Không rõ', 'Chưa rõ', '--']) {
      expect(text).not.toContain(placeholder)
    }
  })

  it('still shows every supported line', async () => {
    const wrapper = await mountSuspended(TuViCenter, {
      props: { center: vm().center, connections: [] },
    })
    const text = wrapper.text()
    for (const label of ['Họ tên', 'Giới tính', 'Ngày dương', 'Ngày âm', 'Can Chi năm', 'Cục']) {
      expect(text).toContain(label)
    }
  })

  it('lists the gaps when a development view asks for them', async () => {
    const wrapper = await mountSuspended(TuViCenter, {
      props: { center: vm().center, connections: [], showPendingFields: true },
    })
    expect(wrapper.findAll('[data-pending]')).toHaveLength(6)
    expect(wrapper.text()).toContain('Chủ Mệnh')
    // It names the gap; it does not fill it.
    expect(wrapper.text()).toContain('chưa có dữ liệu')
  })
})

describe('palace stem, branch and name', () => {
  it('gives every palace its own stem, branch and palace name', () => {
    const palaces = vm().palaces
    expect(palaces).toHaveLength(12)
    expect(new Set(palaces.map((p) => p.branch)).size).toBe(12)
    expect(new Set(palaces.map((p) => p.name)).size).toBe(12)
    for (const palace of palaces) {
      expect(palace.stem, palace.branch).toBeTruthy()
      expect(palace.napAm, palace.branch).toBeTruthy()
      expect(['KIM', 'MOC', 'THUY', 'HOA', 'THO']).toContain(palace.element)
    }
  })

  it('takes stem and branch from the engine, unchanged', () => {
    const chart = real()
    const mapped = new Map(vm().palaces.map((p) => [p.branchIndex, p]))
    for (const palace of chart.palaces) {
      const view = mapped.get(palace.branch_index)!
      expect(view.stem).toBe(palace.stem)
      expect(view.branch).toBe(palace.branch)
      expect(view.name).toBe(palace.label)
      expect(view.element).toBe(palace.element)
      expect(view.napAm).toBe(palace.nap_am)
    }
  })

  it('carries đại vận and Tràng Sinh from the engine, and leaves lưu niên null', () => {
    const palaces = vm().palaces
    // Every palace gets one đại vận and one stage; lưu niên is not implemented.
    expect(new Set(palaces.map((p) => p.lifeStage)).size).toBe(12)
    expect(new Set(palaces.map((p) => p.majorCycleRef)).size).toBe(12)
    for (const palace of palaces) {
      expect(palace.majorCycleAge).toMatch(/^\d+ – \d+$/)
      expect(palace.annualRef).toBeNull()
      expect(palace.monthNumber).toBeNull()
    }
    const menh = palaces.find((p) => p.isMenh)!
    expect(menh.majorCycleRef).toBe('ĐV 1')
  })

  it('renders lưu niên once the engine does supply it', () => {
    // Proves the wiring is live rather than permanently reading a dead key.
    const chart = real()
    const palace = chart.palaces[0]!
    palace.cycles = {
      major_cycle_age_start: 6,
      major_cycle_age_end: 15,
      major_cycle_index: 3,
      major_cycle_direction: 'FORWARD',
      major_cycle_target: null,
      annual_target: 7,
      trang_sinh_stage: 'Đế Vượng',
    }
    const view = mapChartDtoToViewModel(chart).palaces.find(
      (p) => p.branchIndex === palace.branch_index,
    )!
    expect(view.majorCycleAge).toBe('6 – 15')
    expect(view.lifeStage).toBe('Đế Vượng')
    expect(view.majorCycleRef).toBe('ĐV 3')
    expect(view.annualRef).toBe('LN 7')
  })
})
