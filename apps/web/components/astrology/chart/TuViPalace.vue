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
    /** Dev-only: hiện bộ đếm sao trên cung. Không có tác dụng ở bản production. */
    inspect?: boolean
  }>(),
  { inlineVoids: () => [], inspect: false },
)

const hasFooter = computed(
  () => !!(props.palace.majorCycleRef || props.palace.lifeStage || props.palace.annualRef),
)

/** The đại vận number behind the "ĐV n" label, for the tooltip wording. */
const cycleNumber = computed(() => props.palace.cycles?.major_cycle_index ?? null)

const root = ref<HTMLElement | null>(null)
const overflowing = ref(false)

/**
 * Bộ đếm kiểm tra, chỉ có ở chế độ dev.
 *
 * Hai số đầu đọc từ view model, số thứ ba **đếm trong DOM**. Đó là chủ ý: nếu
 * ``Rendered`` lặp lại ``Natal + Annual`` thì nó chẳng chứng minh được gì. Đếm thật
 * trong DOM mới bắt được cả bộ lọc âm thầm ở renderer lẫn sao bị CSS nuốt mất.
 */
const natalCount = computed(
  () =>
    props.palace.majorStars.filter((star) => !star.isAnnual).length +
    props.palace.minorStars.filter((star) => !star.isAnnual).length,
)
const annualCount = computed(
  () =>
    props.palace.majorStars.filter((star) => star.isAnnual).length +
    props.palace.minorStars.filter((star) => star.isAnnual).length,
)
const renderedCount = ref(0)

async function measureRendered(): Promise<void> {
  if (!import.meta.dev) return
  await nextTick()
  renderedCount.value = root.value?.querySelectorAll('.tuvi-star').length ?? 0
}

watch(
  () => [props.inspect, props.palace] as const,
  () => void measureRendered(),
  { immediate: true },
)

const isDev = import.meta.dev

onMounted(async () => {
  if (!import.meta.dev || !root.value) return
  // Measure after web fonts settle; fallback metrics would give a false reading.
  await document.fonts?.ready
  const el = root.value
  // Canvas palaces have a fixed height; reading-mode cards grow and never trip this.
  await measureRendered()
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

    <!-- Bộ đếm dev. ``isDev`` được gấp thành hằng ``false`` lúc build, nên đây là
         nhánh chết ở production. Phần đánh dấu vẫn nằm trong bundle — nhánh chết
         trong hàm render không bị gom bỏ — nhưng không có đường nào chạy tới nó. -->
    <p
      v-if="isDev && inspect"
      class="tuvi-palace__inspect"
      :data-mismatch="renderedCount !== natalCount + annualCount ? 'true' : undefined"
      data-palace-inspect
    >
      Natal: {{ natalCount }} · Annual: {{ annualCount }} · Rendered: {{ renderedCount }}
    </p>

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
