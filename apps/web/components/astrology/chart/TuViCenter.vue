<script setup lang="ts">
import { elementColor } from '~/utils/tuvi-chart'
import type { ChartViewModel, ConnectionViewModel } from '~/types/chart-view-model'
import TuViChartConnections from './TuViChartConnections.vue'

defineProps<{ center: ChartViewModel['center']; connections: ConnectionViewModel[] }>()

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
  <section class="tuvi-center" aria-label="Thông tin lá số">
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

    <div class="tuvi-center__content">
      <p class="tuvi-center__brand">{{ center.subtitle }}</p>
      <h2 class="tuvi-center__title">{{ center.title }}</h2>
      <div class="tuvi-center__rule" aria-hidden="true" />
      <dl class="tuvi-center__fields">
        <template v-for="entry in center.fields" :key="entry.label">
          <dt>{{ entry.label }}</dt>
          <dd>
            <!-- Only a value that *is* an element name takes its colour. -->
            <span :style="entry.element ? { color: elementColor(entry.element) } : undefined">{{
              entry.value
            }}</span>
            <span v-if="entry.secondary" class="tuvi-center__secondary">{{ entry.secondary }}</span>
          </dd>
        </template>
      </dl>
    </div>
  </section>
</template>
