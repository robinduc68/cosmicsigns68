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
    expect(menh.attributes('aria-label')).toBe('Cung Mệnh, Mậu Tuất')
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
    code: 'TEST', name: 'Sao thử', category: 'MAJOR', element: null, strength: null,
    strengthAbbr: null, provisional: false, isTransformation: false, isAnnual: false,
  }

  it('uses neutral ink when the engine declared no element', async () => {
    const wrapper = await mountSuspended(TuViStar, { props: { star: base, major: true } })
    expect(wrapper.attributes('style')).toContain('var(--chart-text)')
  })

  it('shows a strength abbreviation with its full name when one exists', async () => {
    const wrapper = await mountSuspended(TuViStar, {
      props: { star: { ...base, element: 'HOA', strength: 'VUONG', strengthAbbr: 'V' } },
    })
    const abbr = wrapper.get('abbr')
    expect(abbr.text()).toBe('(V)')
    expect(abbr.attributes('title')).toBe('Vượng')
    expect(wrapper.attributes('style')).toContain('var(--chart-hoa)')
  })
})
