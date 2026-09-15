<script setup lang="ts">
import type { ChartViewModel, PalaceViewModel } from '~/types/chart-view-model'
import TuViChartLegend from './TuViChartLegend.vue'
import TuViPalace from './TuViPalace.vue'

/**
 * Palace-by-palace layout for narrow screens, where the full grid would shrink to
 * unreadable text. Palaces follow the order the engine sent them in.
 */
const props = defineProps<{ model: ChartViewModel }>()

/**
 * Cùng một phép lọc như bản canvas: trường nào engine chưa tính thì **bỏ hẳn dòng**,
 * không dựng ra rồi để trống.
 *
 * Trước đây chế độ đọc dựng thẳng ``model.center.fields``, nên "Cân lượng" hiện thành
 * một nhãn với ô giá trị rỗng — đúng cái "giá trị giữ chỗ" mà hợp đồng dữ liệu cấm.
 * Một nhãn trống đọc như dữ liệu bị mất, chứ không đọc như dữ liệu chưa có.
 */
const fields = computed(() => props.model.center.fields.filter((entry) => entry.value !== null))

// With no grid there is no shared border to sit on, so Tuần/Triệt move inside.
function inlineVoids(palace: PalaceViewModel): string[] {
  return props.model.voidMarkers
    .filter((marker) => marker.branches.includes(palace.branchIndex))
    .map((marker) => marker.label)
}
</script>

<template>
  <div class="tuvi-theme tuvi-reading">
    <section class="tuvi-reading__summary" aria-label="Thông tin lá số">
      <p class="tuvi-center__brand">{{ model.center.subtitle }}</p>
      <h2 class="tuvi-center__title">{{ model.center.title }}</h2>
      <dl class="tuvi-center__fields">
        <template v-for="(entry, index) in fields" :key="entry.label || `tt-${index}`">
          <dd v-if="!entry.label" class="tuvi-center__summary">{{ entry.value }}</dd>
          <template v-else>
            <dt>{{ entry.label }}</dt>
            <dd>
              <span>{{ entry.value }}</span>
              <span v-if="entry.secondary" class="tuvi-center__secondary">{{
                entry.secondary
              }}</span>
            </dd>
          </template>
        </template>
      </dl>
    </section>

    <ol class="tuvi-reading__palaces" aria-label="12 cung">
      <li v-for="palace in model.palaces" :key="palace.id" class="tuvi-reading__card">
        <TuViPalace :palace="palace" :inline-voids="inlineVoids(palace)" />
      </li>
    </ol>

    <TuViChartLegend :meta="model.meta" compact />
  </div>
</template>
