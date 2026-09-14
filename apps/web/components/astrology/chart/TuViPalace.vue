<script setup lang="ts">
import type { PalaceViewModel } from '~/types/chart-view-model'
import { ELEMENT_COLOR_MAP } from '~/utils/tuvi-chart'
import TuViStar from './TuViStar.vue'

const props = withDefaults(
  defineProps<{
    palace: PalaceViewModel
    /**
     * Tuần/Triệt drawn inside the palace. Used only where the grid is gone (reading
     * mode); on the canvas they sit on the shared border instead.
     */
    inlineVoids?: string[]
  }>(),
  { inlineVoids: () => [] },
)

const hasFooter = computed(
  () => !!(props.palace.majorCycleRef || props.palace.lifeStage || props.palace.annualRef),
)

/** The đại vận number behind the "ĐV n" label, for the tooltip wording. */
const cycleNumber = computed(() => props.palace.cycles?.major_cycle_index ?? null)

const root = ref<HTMLElement | null>(null)
const overflowing = ref(false)

onMounted(async () => {
  if (!import.meta.dev || !root.value) return
  // Measure after web fonts settle; fallback metrics would give a false reading.
  await document.fonts?.ready
  const el = root.value
  // Canvas palaces have a fixed height; reading-mode cards grow and never trip this.
  if (el.scrollHeight > el.clientHeight + 1) {
    overflowing.value = true
    console.warn(
      `[TuViPalace] Cung ${props.palace.name} tràn ${el.scrollHeight - el.clientHeight}px — ` +
        'một phần nội dung đang bị che.',
    )
  }
})
</script>

<template>
  <section
    ref="root"
    :data-overflow="overflowing ? 'true' : undefined"
    class="tuvi-palace"
    :class="{ 'is-menh': palace.isMenh, 'is-than': palace.isThan }"
    :aria-label="palace.ariaLabel"
    :data-branch="palace.branch"
    :data-palace="palace.id"
  >
    <header>
      <div class="tuvi-palace__header">
        <span class="tuvi-palace__stembranch" :title="`${palace.stem} ${palace.branch}`">
          {{ palace.stemShort }}.{{ palace.branch }}
        </span>
        <h3 class="tuvi-palace__name">
          {{ palace.name
          }}<span v-if="palace.isThan" class="tuvi-palace__than">&lt;Thân&gt;</span>
        </h3>
        <span
          class="tuvi-palace__age"
          :title="palace.majorCycleAge ? `Đại vận ${palace.majorCycleAge} tuổi` : undefined"
        >
          <template v-if="palace.majorCycleAge !== null">{{ palace.majorCycleAge }}</template>
        </span>
      </div>
      <div class="tuvi-palace__sub">
        <span
          class="tuvi-palace__element"
          :style="{ color: ELEMENT_COLOR_MAP[palace.element].color }"
          :title="`Nạp âm ${palace.napAm}`"
        >
          {{ palace.napAm }}
        </span>
        <span v-if="palace.monthNumber !== null">Th.{{ palace.monthNumber }}</span>
      </div>
      <div v-if="inlineVoids.length" class="tuvi-palace__voids">
        <span v-for="label in inlineVoids" :key="label" class="tuvi-void" role="note">
          {{ label }}
        </span>
      </div>
    </header>

    <ul v-if="palace.majorStars.length" class="tuvi-palace__majors">
      <li v-for="star in palace.majorStars" :key="star.code">
        <TuViStar :star="star" major />
      </li>
    </ul>
    <p v-else-if="palace.isEmptyMainStar" class="tuvi-palace__empty">Vô chính diệu</p>

    <ul v-if="palace.minorStars.length" class="tuvi-palace__minors">
      <li v-for="star in palace.minorStars" :key="star.code">
        <TuViStar :star="star" />
      </li>
    </ul>

    <!-- Three fixed grid slots so the middle label stays centred; an empty slot is a
         spacer, not a missing value. Each carries its own title because "ĐV 1" and
         "Dưỡng" are meaningless read out on their own. -->
    <footer v-if="hasFooter" class="tuvi-palace__footer">
      <span :title="palace.majorCycleRef ? `Đại vận thứ ${cycleNumber}` : undefined">{{
        palace.majorCycleRef ?? ''
      }}</span>
      <span :title="palace.lifeStage ? `Vòng Tràng Sinh: ${palace.lifeStage}` : undefined">{{
        palace.lifeStage ?? ''
      }}</span>
      <span :title="palace.annualRef ? `Lưu niên: ${palace.annualRef}` : undefined">{{
        palace.annualRef ?? ''
      }}</span>
    </footer>
  </section>
</template>
