<script setup lang="ts">
import { CHART_GRID_BRANCH_INDEXES, type ChartPayload } from '@cosmic/shared'

const props = defineProps<{ chart: ChartPayload }>()

const byBranch = computed(
  () => new Map(props.chart.palaces.map((palace) => [palace.branch_index, palace])),
)
</script>

<template>
  <div class="overflow-hidden rounded-[var(--radius-card)] border border-[var(--border)]">
    <div class="grid grid-cols-4 gap-px bg-[var(--border)]">
      <template v-for="(branchIndex, cell) in CHART_GRID_BRANCH_INDEXES" :key="cell">
        <ChartPalace
          v-if="branchIndex !== null && byBranch.get(branchIndex)"
          :palace="byBranch.get(branchIndex)!"
        />
        <!-- Ô giữa: chỉ ô đầu tiên render nội dung, ba ô còn lại giữ chỗ lưới. -->
        <div
          v-else-if="branchIndex === null && cell === 5"
          class="col-span-2 row-span-2 bg-[var(--bg-elevated)] p-4"
        >
          <slot name="center" />
        </div>
        <div v-else-if="branchIndex !== null" class="bg-[var(--card)]" />
      </template>
    </div>
  </div>
</template>
