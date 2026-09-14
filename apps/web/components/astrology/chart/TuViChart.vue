<script setup lang="ts">
import type { PanzoomObject } from '@panzoom/panzoom'
import { useChartExport } from '~/composables/useChartExport'
import type { ChartViewMode, ChartViewModel } from '~/types/chart-view-model'
import { CANONICAL_CHART_HEIGHT, CANONICAL_CHART_WIDTH } from '~/utils/tuvi-chart'
import TuViChartCanvas from './TuViChartCanvas.vue'
import TuViChartToolbar from './TuViChartToolbar.vue'
import TuViReadingMode from './TuViReadingMode.vue'
import './tuvi-chart.css'

/**
 * Tử Vi chart viewer: toolbar, pan/zoom overview, palace-by-palace reading mode,
 * PNG export and print. It displays the view model it is given and nothing else —
 * no astrology is decided here.
 */
const props = withDefaults(
  defineProps<{
    model: ChartViewModel
    fileSlug?: string
    /** Fixed date for reproducible export file names; defaults to today. */
    exportDate?: Date
    /** Force the starting mode; otherwise narrow screens start in reading mode. */
    initialMode?: ChartViewMode
    /**
     * Internal development views only: list centre fields the chart does not carry
     * yet. Applied to the on-screen canvas alone — the off-screen canvas is what
     * PNG export and print render, and those must never carry a development note.
     */
    showPendingFields?: boolean
  }>(),
  {
    fileSlug: 'la-so',
    exportDate: undefined,
    initialMode: undefined,
    showPendingFields: false,
  },
)

const mode = ref<ChartViewMode>(props.initialMode ?? 'overview')

/**
 * Chế độ soi lá số, chỉ có ở dev: mỗi cung hiện ``Natal · Annual · Rendered``.
 *
 * Có mặt vì đợt việc này bắt đầu bằng câu hỏi "lá số thưa vì tính thiếu hay vì vẽ
 * thiếu?", và câu đó đã phải trả lời bằng cách đo DOM qua giao thức debug của trình
 * duyệt. Lần sau nhìn là thấy.
 */
const inspecting = ref(false)
const viewport = ref<HTMLElement | null>(null)
const stage = ref<HTMLElement | null>(null)
const offscreen = ref<InstanceType<typeof TuViChartCanvas> | null>(null)
const ready = ref(false)
const hostMounted = ref(false)
const printing = ref(false)
const isDev = import.meta.dev

const { exporting, exportPng } = useChartExport()
const { error: toastError } = useToast()

let panzoom: PanzoomObject | null = null
let panzoomLoading: Promise<void> | null = null
let fitScale = 1
let resizeObserver: ResizeObserver | null = null

function measureFit(): number {
  const el = viewport.value
  if (!el || el.clientWidth === 0) return 0
  const byWidth = el.clientWidth / CANONICAL_CHART_WIDTH
  const byHeight =
    document.fullscreenElement === el ? el.clientHeight / CANONICAL_CHART_HEIGHT : Infinity
  return Math.min(1, byWidth, byHeight)
}

function onWheel(event: WheelEvent) {
  // Plain scrolling keeps scrolling the page; only pinch / ctrl + wheel zooms.
  if (!panzoom || !(event.ctrlKey || event.metaKey)) return
  event.preventDefault()
  panzoom.zoomWithWheel(event)
}

async function createPanzoom(el: HTMLElement, fit: number) {
  const { default: Panzoom } = await import('@panzoom/panzoom')
  panzoom = Panzoom(el, {
    origin: '0 0',
    canvas: true,
    startScale: fit,
    minScale: fit * 0.75,
    maxScale: 4,
    step: 0.25,
    panOnlyWhenZoomed: true,
    cursor: 'grab',
  })
  viewport.value?.addEventListener('wheel', onWheel, { passive: false })
}

async function fitToViewport(force = false) {
  const el = stage.value
  const fit = measureFit()
  if (!el || fit <= 0) return

  const wasAtFit = panzoom !== null && Math.abs(panzoom.getScale() - fitScale) < 1e-3
  fitScale = fit
  if (!panzoom) {
    // Size the chart right away. Pan/zoom is a lazily loaded chunk; waiting for it
    // left a blank box on a cold route, which is what a first-time visitor sees.
    el.style.transform = `scale(${fit})`
    ready.value = true
    panzoomLoading ??= createPanzoom(el, fit)
    await panzoomLoading
  } else {
    panzoom.setOptions({ startScale: fit, minScale: fit * 0.75 })
    // Keep a reader's own zoom on resize; only re-fit when they were at fit already.
    if (force || wasAtFit) panzoom.reset({ animate: false })
  }
  ready.value = true
}

const zoomIn = () => panzoom?.zoomIn()
const zoomOut = () => panzoom?.zoomOut()
const fit = () => void fitToViewport(true)

async function toggleFullscreen() {
  const el = viewport.value
  if (!el) return
  try {
    if (document.fullscreenElement) await document.exitFullscreen()
    else await el.requestFullscreen()
  } catch {
    toastError('Trình duyệt chưa cho mở toàn màn hình')
  }
}

function onFullscreenChange() {
  void nextTick(() => fitToViewport(true))
}

async function onExportPng() {
  const node = offscreen.value?.root
  if (!node) return
  const result = await exportPng(node, { fileSlug: props.fileSlug, date: props.exportDate })
  if (!result) toastError('Chưa tạo được ảnh lá số', 'Bạn thử lại sau vài giây nhé.')
}

async function onPrint() {
  printing.value = true
  try {
    await document.fonts?.ready
    // Prints the always-mounted off-screen canvas; see the print rules in tuvi-chart.css.
    window.print()
  } finally {
    printing.value = false
  }
}

onMounted(async () => {
  hostMounted.value = true
  if (!props.initialMode && window.matchMedia('(max-width: 767px)').matches) {
    // 1400 px squeezed into a phone is ~5 px text. Start where it can be read.
    mode.value = 'reading'
  }
  resizeObserver = new ResizeObserver(() => {
    if (mode.value === 'overview') void fitToViewport()
  })
  if (viewport.value) resizeObserver.observe(viewport.value)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  if (mode.value === 'overview') {
    await nextTick()
    await fitToViewport(true)
  }
  if (isDev && props.model.warnings.length) console.warn('[TuViChart]', props.model.warnings)
})

watch(mode, async (next) => {
  if (next !== 'overview') return
  await nextTick()
  await fitToViewport(true)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  viewport.value?.removeEventListener('wheel', onWheel)
  panzoom?.destroy()
  panzoom = null
})

defineExpose({ mode, exportPng: onExportPng, print: onPrint })
</script>

<template>
  <div class="tuvi-viewer">
    <TuViChartToolbar
      v-model:mode="mode"
      class="mb-3"
      :exporting="exporting"
      :printing="printing"
      @zoom-in="zoomIn"
      @zoom-out="zoomOut"
      @fit="fit"
      @fullscreen="toggleFullscreen"
      @export-png="onExportPng"
      @print="onPrint"
    >
      <template v-if="isDev" #dev>
        <button
          type="button"
          class="inline-flex h-9 items-center rounded-lg border border-[var(--border)] px-3 text-small"
          :class="inspecting ? 'bg-[var(--accent)]/15 text-[var(--accent)]' : ''"
          :aria-pressed="inspecting"
          data-dev-inspect-toggle
          @click="inspecting = !inspecting"
        >
          Soi cung
        </button>
      </template>
    </TuViChartToolbar>

    <ul
      v-if="isDev && model.warnings.length"
      class="mb-3 space-y-1 rounded-lg border border-[var(--color-gold-400)]/40 p-3 text-caption text-[var(--text)]"
      data-dev-warnings
    >
      <li v-for="warning in model.warnings" :key="warning">Dev: {{ warning }}</li>
    </ul>

    <div
      v-show="mode === 'overview'"
      ref="viewport"
      class="tuvi-viewport"
      data-view="overview"
    >
      <p v-if="!ready" class="tuvi-viewport__placeholder" role="status">Đang dựng lá số…</p>
      <div ref="stage" class="tuvi-stage" :class="{ 'is-ready': ready }">
        <TuViChartCanvas
          :model="model"
          :show-pending-fields="showPendingFields"
          :inspect="inspecting"
        />
      </div>
    </div>

    <TuViReadingMode v-if="mode === 'reading'" :model="model" data-view="reading" />

    <!-- Always mounted on the client, off screen: the exporter captures it flat, and
         print (button or Ctrl+P) shows it without depending on the current view. -->
    <Teleport to="body">
      <div v-if="hostMounted" id="tuvi-offscreen-host" aria-hidden="true" inert>
        <TuViChartCanvas ref="offscreen" :model="model" />
      </div>
    </Teleport>
  </div>
</template>
