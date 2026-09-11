import { afterEach, describe, expect, it } from 'vitest'
import { nextTick } from 'vue'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import TuViChart from '../components/astrology/chart/TuViChart.vue'
import { chartExportFileName, slugifyVietnamese } from '../composables/useChartExport'
import { mapChartDtoToViewModel } from '../composables/useTuViChartViewModel'
import { scenario } from '../fixtures/chart-renderer-scenarios'
import type { ChartViewMode, ChartViewModel } from '../types/chart-view-model'

const modelFor = (id = 'cross-check-2001') =>
  mapChartDtoToViewModel(structuredClone(scenario(id).chart))

type Mounted = Awaited<ReturnType<typeof mountSuspended>>
const mounted: Mounted[] = []
async function mountViewer(props: { model: ChartViewModel; initialMode?: ChartViewMode }) {
  const wrapper = await mountSuspended(TuViChart, { props })
  mounted.push(wrapper)
  return wrapper
}

afterEach(() => {
  // The off-screen host is teleported to <body>; unmount so tests do not see each other's.
  while (mounted.length) mounted.pop()!.unmount()
})

describe('TuViChart viewer', () => {
  it('offers both view modes plus zoom, export and print', async () => {
    const wrapper = await mountViewer({ model: modelFor(), initialMode: 'overview' })
    const toolbar = wrapper.get('[role="toolbar"]')
    for (const text of ['Toàn lá số', 'Đọc từng cung', 'Tải PNG', 'In / PDF']) {
      expect(toolbar.text()).toContain(text)
    }
    for (const label of ['Phóng to', 'Thu nhỏ', 'Vừa màn hình', 'Toàn màn hình']) {
      expect(toolbar.find(`[aria-label="${label}"]`).exists()).toBe(true)
    }
  })

  it('switches to reading mode but keeps the canonical canvas mounted', async () => {
    const wrapper = await mountViewer({ model: modelFor(), initialMode: 'overview' })
    const reading = wrapper
      .findAll('button[aria-pressed]')
      .find((button) => button.text().includes('Đọc từng cung'))!
    await reading.trigger('click')

    expect(wrapper.find('.tuvi-reading').exists()).toBe(true)
    const overview = wrapper.get('[data-view="overview"]').element as HTMLElement
    expect(overview.style.display).toBe('none')
  })

  it('mounts an off-screen canonical canvas for export and print, hidden from assistive tech', async () => {
    await mountViewer({ model: modelFor(), initialMode: 'overview' })
    const host = document.getElementById('tuvi-offscreen-host')
    expect(host).not.toBeNull()
    expect(host!.getAttribute('aria-hidden')).toBe('true')
    expect(host!.hasAttribute('inert')).toBe(true)
    expect(host!.querySelectorAll('[data-palace]')).toHaveLength(12)
    // Export view: canvas only — no toolbar, no dev warnings inside the image.
    expect(host!.querySelector('[role="toolbar"]')).toBeNull()
    expect(host!.querySelector('[data-dev-warnings]')).toBeNull()
  })

  it('starts narrow screens in reading mode instead of shrinking the chart', async () => {
    const original = window.matchMedia
    window.matchMedia = ((query: string) => ({
      matches: query.includes('max-width'),
      media: query,
      onchange: null,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      dispatchEvent: () => false,
    })) as typeof window.matchMedia
    try {
      const wrapper = await mountViewer({ model: modelFor() })
      await nextTick()
      expect(wrapper.find('.tuvi-reading').exists()).toBe(true)
    } finally {
      window.matchMedia = original
    }
  })

  it('never lets development warnings leak into a chart canvas', async () => {
    const model = modelFor('overflow-demo')
    expect(model.warnings.length).toBeGreaterThan(0)
    const wrapper = await mountViewer({ model, initialMode: 'overview' })
    // The list only renders under import.meta.dev, which is off in tests. What must
    // hold in every environment is that it is never part of a canvas that gets exported.
    const list = wrapper.find('[data-dev-warnings]')
    if (list.exists()) expect(list.element.closest('.tuvi-chart')).toBeNull()
    expect(document.querySelector('.tuvi-chart [data-dev-warnings]')).toBeNull()
  })
})

describe('chart export file names', () => {
  it('drops Vietnamese diacritics, including đ', () => {
    expect(slugifyVietnamese('Nguyễn Thị Minh Anh')).toBe('nguyen-thi-minh-anh')
    expect(slugifyVietnamese('Đặng Đức Độ')).toBe('dang-duc-do')
    expect(slugifyVietnamese('   ')).toBe('la-so')
  })

  it('builds la-so-tu-vi-{slug}-{yyyy-mm-dd}.png', () => {
    expect(chartExportFileName('Nguyễn Thị Minh Anh', new Date(2026, 8, 11))).toBe(
      'la-so-tu-vi-nguyen-thi-minh-anh-2026-09-11.png',
    )
  })
})
