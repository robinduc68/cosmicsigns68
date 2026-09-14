<script setup lang="ts">
import type { ChartViewModel } from '~/types/chart-view-model'
import TuViCenter from './TuViCenter.vue'
import TuViChartLegend from './TuViChartLegend.vue'
import TuViPalace from './TuViPalace.vue'
import TuViVoidMarker from './TuViVoidMarker.vue'

/**
 * The canonical 1400 × 1750 chart. It never reflows: palace positions are fixed
 * by the địa bàn, and every size is in canvas pixels. Screen, print and PNG
 * export all render this same element and scale it from outside.
 */
const props = withDefaults(
  defineProps<{
    model: ChartViewModel
    showPendingFields?: boolean
    /** Dev-only: chuyển tiếp bộ đếm sao xuống từng cung. */
    inspect?: boolean
  }>(),
  { showPendingFields: false, inspect: false },
)

const root = ref<HTMLElement | null>(null)
defineExpose({ root })

const subjectName = computed(
  () => props.model.center.fields.find((entry) => entry.label === 'Họ tên')?.value ?? '',
)
</script>

<template>
  <div
    ref="root"
    class="tuvi-theme tuvi-chart"
    role="figure"
    :aria-label="subjectName ? `Lá số Tử Vi của ${subjectName}` : 'Lá số Tử Vi'"
    :data-provisional="model.meta.provisional ? 'true' : 'false'"
  >
    <div class="tuvi-grid">
      <template v-for="(cell, slot) in model.cells" :key="slot">
        <TuViPalace
          v-if="cell"
          :palace="cell"
          :inspect="inspect"
          :style="{ gridRow: String(cell.row), gridColumn: String(cell.col) }"
        />
      </template>
      <TuViCenter
        :center="model.center"
        :connections="model.connections"
        :show-pending-fields="showPendingFields"
      />
      <TuViVoidMarker v-for="marker in model.voidMarkers" :key="marker.kind" :marker="marker" />
    </div>
    <TuViChartLegend :meta="model.meta" />
  </div>
</template>
