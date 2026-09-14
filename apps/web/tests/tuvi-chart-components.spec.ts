import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import TuViChartCanvas from '../components/astrology/chart/TuViChartCanvas.vue'
import TuViReadingMode from '../components/astrology/chart/TuViReadingMode.vue'
import TuViStar from '../components/astrology/chart/TuViStar.vue'
import { mapChartDtoToViewModel } from '../composables/useTuViChartViewModel'
import { scenario } from '../fixtures/chart-renderer-scenarios'
import type { StarViewModel } from '../types/chart-view-model'

const modelFor = (id: string) => mapChartDtoToViewModel(structuredClone(scenario(id).chart))

describe('TuViChartCanvas', () => {
  it('renders twelve labelled palaces in their fixed grid slots', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model: modelFor('cross-check-2001') } })
    expect(wrapper.findAll('[data-palace]')).toHaveLength(12)
    const menh = wrapper.get('[data-palace="MENH"]')
    // The footer reads as two bare fragments ("ĐV 1", "Dưỡng") on its own, so the
    // palace label spells out what they are.
    expect(menh.attributes('aria-label')).toBe(
      'Cung Mệnh, Mậu Tuất, đại vận 3 – 12 tuổi, Tràng Sinh: Dưỡng',
    )
    // Tuất is row 3, column 4 of the địa bàn.
    expect(menh.attributes('style')).toContain('grid-row: 3')
    expect(menh.attributes('style')).toContain('grid-column: 4')
  })

  it('renders the centre panel with chart facts as real text', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model: modelFor('cross-check-2001') } })
    const centre = wrapper.get('.tuvi-center')
    expect(centre.text()).toContain('Lá Số Tử Vi')
    expect(centre.text()).toContain('Mộc Tam Cục')
    expect(centre.text()).toContain('Bạch Lạp Kim')
  })

  it('emphasises all fourteen major stars without inventing strengths', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model: modelFor('cross-check-2001') } })
    expect(wrapper.findAll('.tuvi-star--major')).toHaveLength(14)
    expect(wrapper.find('.tuvi-star__strength').exists()).toBe(false)
    expect(wrapper.get('[data-palace="MENH"]').text()).toContain('Thái Âm')
  })

  it('marks provisional stars for screen readers too', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model: modelFor('cross-check-2001') } })
    expect(wrapper.get('.tuvi-star .sr-only').text()).toContain('chưa được kiểm định')
  })

  it('draws Tuần, Triệt and four connection lines from engine data', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model: modelFor('cross-check-2001') } })
    expect(wrapper.get('[data-void="TUAN"]').text()).toBe('Tuần')
    expect(wrapper.get('[data-void="TRIET"]').text()).toBe('Triệt')
    expect(wrapper.findAll('line[data-connection]')).toHaveLength(4)
  })

  it('shows the provisional badge for unverified engine output', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model: modelFor('cross-check-2001') } })
    const badge = wrapper.get('[data-provisional-badge]')
    expect(badge.text()).toBe('ENGINE PROVISIONAL — NOT FOR CUSTOMER USE')
    // Inline !important so no stylesheet can hide it.
    expect(badge.attributes('style')).toContain('display: block !important')
  })

  it('drops the badge only for an authoritative, fully verified chart', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model: modelFor('authoritative-demo') } })
    expect(wrapper.find('[data-provisional-badge]').exists()).toBe(false)
  })

  it('renders a chart with no placed stars without claiming "Vô chính diệu"', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model: modelFor('cross-check-2001-frame') } })
    expect(wrapper.findAll('[data-palace]')).toHaveLength(12)
    expect(wrapper.findAll('.tuvi-star')).toHaveLength(0)
    expect(wrapper.find('.tuvi-palace__empty').exists()).toBe(false)
  })

  it('keeps long Vietnamese names whole instead of truncating them', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model: modelFor('long-names-demo') } })
    expect(wrapper.text()).toContain('Thiên Đức Quý Nhân Phúc Tinh (mẫu 6)')
    expect(wrapper.text()).not.toContain('…')
  })
})

describe('TuViReadingMode', () => {
  it('shows the summary first, then the twelve palaces in the order the engine sent', async () => {
    const model = modelFor('cross-check-2001')
    const wrapper = await mountSuspended(TuViReadingMode, { props: { model } })
    const children = wrapper.get('.tuvi-reading').element.children
    expect(children[0]!.classList.contains('tuvi-reading__summary')).toBe(true)
    const order = wrapper.findAll('[data-palace]').map((p) => p.attributes('data-palace'))
    expect(order).toEqual(model.palaces.map((p) => p.id))
  })

  it('moves Tuần and Triệt inside the palaces when there is no grid border', async () => {
    const wrapper = await mountSuspended(TuViReadingMode, { props: { model: modelFor('cross-check-2001') } })
    expect(wrapper.findAll('.tuvi-palace__voids .tuvi-void')).toHaveLength(4)
  })
})

describe('TuViStar', () => {
  const base: StarViewModel = {
    code: 'TEST', name: 'Sao thử', category: 'MAJOR', element: null, elementLabel: null,
    polarityPrefix: null, ariaLabel: 'Sao thử', strength: null, strengthAbbr: null,
    strengthVerification: null, provisional: false, isMajor: true, isTransformation: false,
    isAnnual: false, palaceBranch: null, displayPriority: 0,
    verificationStatus: 'PROVISIONAL', provenance: null,
  }

  it('uses neutral ink when the engine declared no element', async () => {
    const wrapper = await mountSuspended(TuViStar, { props: { star: base, major: true } })
    expect(wrapper.classes()).toContain('is-element-none')
  })

  it('shows a strength abbreviation with its full name when one exists', async () => {
    const wrapper = await mountSuspended(TuViStar, {
      props: { star: { ...base, element: 'HOA', strength: 'VUONG', strengthAbbr: 'V' } },
    })
    const abbr = wrapper.get('abbr')
    expect(abbr.text()).toBe('(V)')
    expect(abbr.attributes('title')).toBe('Vượng')
    expect(wrapper.classes()).toContain('is-element-hoa')
  })
})

describe('12-palace orientation on the grid (golden case Mệnh = Tuất)', () => {
  /**
   * Guards two things at once: the engine's Earthly Branch → palace assignment, and
   * the renderer's Earthly Branch → grid coordinate mapping. A mirrored chart passes
   * a naive check because Mệnh and Thiên Di stay put, so named cells are asserted.
   */
  const CELLS = [
    { branch: 'Thân', row: 1, col: 4, palace: 'Phu Thê' },
    { branch: 'Tý', row: 4, col: 3, palace: 'Phúc Đức' },
    { branch: 'Tuất', row: 3, col: 4, palace: 'Mệnh' },
    { branch: 'Thìn', row: 2, col: 1, palace: 'Thiên Di' },
    { branch: 'Dậu', row: 2, col: 4, palace: 'Huynh Đệ' },
    { branch: 'Ngọ', row: 1, col: 2, palace: 'Tài Bạch' },
  ]

  it.each(CELLS)('renders $palace at branch $branch in row $row column $col', async (cell) => {
    const model = modelFor('cross-check-2001')
    expect(model.palaces.find((p) => p.isMenh)?.branch).toBe('Tuất')

    const wrapper = await mountSuspended(TuViChartCanvas, { props: { model } })
    const palace = wrapper.get(`[data-branch="${cell.branch}"]`)
    expect(palace.get('.tuvi-palace__name').text()).toContain(cell.palace)
    expect(palace.attributes('style')).toContain(`grid-row: ${cell.row}`)
    expect(palace.attributes('style')).toContain(`grid-column: ${cell.col}`)
  })

  it('never puts a palace name at the mirrored branch', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, {
      props: { model: modelFor('cross-check-2001') },
    })
    // The exact failure of engine 0.1.0: Phúc Đức on Thân, Phu Thê on Tý.
    expect(wrapper.get('[data-branch="Thân"]').text()).not.toContain('Phúc Đức')
    expect(wrapper.get('[data-branch="Tý"]').text()).not.toContain('Phu Thê')
  })
})

describe('ngũ hành colouring of stars', () => {
  const base: StarViewModel = {
    code: 'TEST', name: 'Sao thử', category: 'MAJOR', element: null, elementLabel: null,
    polarityPrefix: null, ariaLabel: 'Sao thử', strength: null, strengthAbbr: null,
    strengthVerification: null, provisional: false, isMajor: true, isTransformation: false,
    isAnnual: false, palaceBranch: null, displayPriority: 0,
    verificationStatus: 'PROVISIONAL', provenance: null,
  }

  const CASES = [
    { element: 'KIM', cssClass: 'is-element-kim' },
    { element: 'MOC', cssClass: 'is-element-moc' },
    { element: 'THUY', cssClass: 'is-element-thuy' },
    { element: 'HOA', cssClass: 'is-element-hoa' },
    { element: 'THO', cssClass: 'is-element-tho' },
  ] as const

  it.each(CASES)('maps a $element star to its semantic class', async ({ element, cssClass }) => {
    const wrapper = await mountSuspended(TuViStar, { props: { star: { ...base, element } } })
    expect(wrapper.classes()).toContain(cssClass)
    // The element also survives as data, so export and tests never depend on colour alone.
    expect(wrapper.attributes('data-element')).toBe(element)
  })

  it('falls back to the neutral class, not to a guessed element', async () => {
    const wrapper = await mountSuspended(TuViStar, { props: { star: base } })
    expect(wrapper.classes()).toContain('is-element-none')
    expect(wrapper.attributes('data-element')).toBe('NONE')
    for (const { cssClass } of CASES) expect(wrapper.classes()).not.toContain(cssClass)
  })

  it('classes the whole label, not just the strength letter', async () => {
    const star = { ...base, element: 'HOA' as const, strength: 'HAM' as const, strengthAbbr: 'H' }
    const wrapper = await mountSuspended(TuViStar, { props: { star, major: true } })
    // A Hỏa star that is Hãm still reads as Hỏa: strength never overrides the element.
    expect(wrapper.classes()).toContain('is-element-hoa')
    expect(wrapper.get('abbr').classes()).not.toContain('is-element-hoa')
  })

  it('keeps the element class on an annual star and differentiates by typography', async () => {
    const star = { ...base, element: 'MOC' as const, category: 'ANNUAL' as const, isAnnual: true }
    const wrapper = await mountSuspended(TuViStar, { props: { star } })
    expect(wrapper.classes()).toContain('is-element-moc')
    expect(wrapper.classes()).toContain('is-annual')
  })

  it('renders the polarity prefix without letting it pick the colour', async () => {
    const yang = await mountSuspended(TuViStar, {
      props: { star: { ...base, element: 'THUY', polarityPrefix: '+' } },
    })
    const yin = await mountSuspended(TuViStar, {
      props: { star: { ...base, element: 'THUY', polarityPrefix: '−' } },
    })
    expect(yang.text()).toBe('+Sao thử')
    expect(yin.text()).toBe('−Sao thử')
    // Same element, opposite polarity, identical colour class.
    expect(yang.classes()).toEqual(yin.classes())
  })

  it('separates typography from colour across categories', async () => {
    const major = await mountSuspended(TuViStar, {
      props: { star: { ...base, element: 'KIM' }, major: true },
    })
    const minor = await mountSuspended(TuViStar, {
      props: { star: { ...base, element: 'KIM' }, major: false },
    })
    expect(major.classes()).toContain('tuvi-star--major')
    expect(minor.classes()).toContain('tuvi-star--minor')
    // Typography differs, colour does not.
    expect(major.classes()).toContain('is-element-kim')
    expect(minor.classes()).toContain('is-element-kim')
  })

  it('exposes the element to screen readers so colour is not the only carrier', async () => {
    const star = {
      ...base, element: 'THUY' as const, elementLabel: 'Thủy',
      strength: 'MIEU' as const, strengthAbbr: 'M', name: 'Thái Âm',
      ariaLabel: 'Thái Âm, hành Thủy, Miếu',
    }
    const wrapper = await mountSuspended(TuViStar, { props: { star } })
    expect(wrapper.attributes('aria-label')).toBe('Thái Âm, hành Thủy, Miếu')
    expect(wrapper.attributes('title')).toBe('Thái Âm, hành Thủy, Miếu')
  })
})

describe('element metadata through the real engine payload', () => {
  it('carries the engine-declared element and never invents one', () => {
    const model = modelFor('cross-check-2001')
    const stars = model.palaces.flatMap((p) => p.majorStars)
    expect(stars).toHaveLength(14)
    // 12 of 14 today; Tham Lang and Cự Môn are disputed and stay neutral.
    expect(stars.filter((s) => s.element !== null)).toHaveLength(12)
    expect(stars.filter((s) => s.element === null).map((s) => s.name).sort()).toEqual([
      'Cự Môn',
      'Tham Lang',
    ])
  })

  it('builds an accessible label from engine data alone', () => {
    const model = modelFor('cross-check-2001')
    const star = model.palaces.flatMap((p) => p.majorStars).find((s) => s.name === 'Thái Âm')
    expect(star?.ariaLabel).toBe('Thái Âm, hành Thủy')
    expect(star?.polarityPrefix).toBe('−')
  })

  it('shows all five colours on the palette fixture', async () => {
    const wrapper = await mountSuspended(TuViChartCanvas, {
      props: { model: modelFor('five-element-palette') },
    })
    const rendered = new Set(
      wrapper.findAll('[data-element]').map((el) => el.attributes('data-element')),
    )
    for (const element of ['KIM', 'MOC', 'THUY', 'HOA', 'THO']) {
      expect(rendered).toContain(element)
    }
    expect(rendered).toContain('NONE')
  })

  it('colours bản mệnh and cục in the centre, and nothing else', () => {
    const model = modelFor('cross-check-2001')
    const coloured = model.center.fields.filter((f) => f.element !== null)
    expect(coloured.map((f) => f.label)).toEqual(['Bản mệnh', 'Cục'])
  })
})
