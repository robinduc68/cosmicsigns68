<script setup lang="ts">
import { elementColor } from '~/utils/tuvi-chart'
import type { ChartViewModel, ConnectionViewModel } from '~/types/chart-view-model'
import TuViChartConnections from './TuViChartConnections.vue'

const props = withDefaults(
  defineProps<{
    center: ChartViewModel['center']
    connections: ConnectionViewModel[]
    /**
     * Internal development views only. Lists the fields the chart does not carry
     * yet, so a gap is visible while building. A customer chart omits those lines
     * entirely rather than showing a dash or a zero in their place.
     */
    showPendingFields?: boolean
  }>(),
  { showPendingFields: false },
)

const fields = computed(() =>
  props.center.fields.filter((entry) => entry.value !== null || props.showPendingFields),
)

/**
 * Cảnh báo tràn cho khối giữa, chỉ ở dev.
 *
 * Khối giữa có ``overflow: hidden`` như mỗi cung, nên nó cắt **âm thầm** — và nó đã
 * cắt thật: dòng "Thân Mệnh đồng cung" biến mất mà không có dấu hiệu nào. Một họ tên
 * dài xuống dòng là đủ để tái diễn. Mỗi cung đã tự đo chiều cao của mình từ lâu; chỗ
 * này thiếu, nên thêm vào.
 */
const root = ref<HTMLElement | null>(null)
const content = ref<HTMLElement | null>(null)

onMounted(async () => {
  if (!import.meta.dev || !root.value || !content.value) return
  await document.fonts?.ready
  const overflow = content.value.scrollHeight - root.value.clientHeight
  if (overflow > 0) {
    console.warn(`[TuViCenter] Khối giữa tràn ${overflow}px — một phần thông tin đang bị che.`)
  }
})

// Twelve ticks for the twelve palaces — geometry for the watermark, nothing more.
// Rounded: Math.sin/cos can differ in the last digit between the server (Node) and
// the browser, which surfaces as an SVG attribute hydration mismatch.
const round = (value: number) => Math.round(value * 1000) / 1000
const TICKS = Array.from({ length: 12 }, (_, i) => {
  const angle = (i * Math.PI) / 6
  return {
    x1: round(100 + 72 * Math.cos(angle)),
    y1: round(100 + 72 * Math.sin(angle)),
    x2: round(100 + 90 * Math.cos(angle)),
    y2: round(100 + 90 * Math.sin(angle)),
  }
})
</script>

<template>
  <section ref="root" class="tuvi-center" aria-label="Thông tin lá số">
    <TuViChartConnections :connections="connections" />

    <div class="tuvi-center__seal" aria-hidden="true">
      <svg viewBox="0 0 200 200" width="74%" height="74%">
        <circle cx="100" cy="100" r="94" fill="none" stroke="currentColor" stroke-width="1.4" />
        <circle cx="100" cy="100" r="70" fill="none" stroke="currentColor" stroke-width="0.9" />
        <line
          v-for="(tick, index) in TICKS"
          :key="index"
          :x1="tick.x1"
          :y1="tick.y1"
          :x2="tick.x2"
          :y2="tick.y2"
          stroke="currentColor"
          stroke-width="1"
        />
        <path
          d="M100 30 A70 70 0 0 1 100 170 A35 35 0 0 1 100 100 A35 35 0 0 0 100 30 Z"
          fill="currentColor"
        />
        <circle cx="100" cy="65" r="7" fill="currentColor" />
        <circle cx="100" cy="135" r="7" fill="none" stroke="currentColor" stroke-width="2" />
      </svg>
    </div>

    <div ref="content" class="tuvi-center__content">
      <p class="tuvi-center__brand">{{ center.subtitle }}</p>
      <h2 class="tuvi-center__title">{{ center.title }}</h2>
      <div class="tuvi-center__rule" aria-hidden="true" />
      <dl class="tuvi-center__fields">
        <template v-for="(entry, index) in fields" :key="entry.label || `tt-${index}`">
          <!-- Dòng tóm tắt không có nhãn: nó là một mệnh đề, không phải một cặp
               nhãn–giá trị. Cho nó chiếm cả hai cột thay vì để một ô <dt> trống,
               vì một ô trống đọc như dữ liệu bị thiếu. -->
          <dd v-if="!entry.label" class="tuvi-center__summary">{{ entry.value }}</dd>
          <template v-else>
          <dt>{{ entry.label }}</dt>
          <dd>
            <!-- Only a value that *is* an element name takes its colour. -->
            <span
              v-if="entry.value !== null"
              :style="entry.element ? { color: elementColor(entry.element) } : undefined"
              >{{ entry.value }}</span
            >
            <!-- Development only: names the gap instead of filling it. -->
            <span v-else class="tuvi-center__pending" data-pending>chưa có dữ liệu</span>
            <span v-if="entry.secondary" class="tuvi-center__secondary">{{ entry.secondary }}</span>
          </dd>
          </template>
        </template>
      </dl>
    </div>
  </section>
</template>
