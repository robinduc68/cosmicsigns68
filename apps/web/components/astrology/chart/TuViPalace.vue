<script setup lang="ts">
import type { PalaceViewModel } from '~/types/chart-view-model'
import { ELEMENT_COLOR_MAP, elementClass } from '~/utils/tuvi-chart'
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

/** The đại vận number behind the "ĐV n" label, for the tooltip wording. */
const cycleNumber = computed(() => props.palace.cycles?.major_cycle_index ?? null)

/**
 * Ô footer — chỉ những giá trị engine thật sự cấp.
 *
 * Mỗi ô mang ``title`` riêng vì "ĐV 1" và "Dưỡng" đọc lên một mình thì vô nghĩa.
 */
const footerCells = computed(() => {
  const cells: { key: string; text: string; title: string }[] = []
  if (props.palace.majorCycleRef) {
    cells.push({
      key: 'dv',
      text: props.palace.majorCycleRef,
      title: `Đại vận thứ ${cycleNumber.value}${
        props.palace.majorCycleAge ? ` — ${props.palace.majorCycleAge} tuổi` : ''
      }`,
    })
  }
  if (props.palace.lifeStage) {
    cells.push({
      key: 'ts',
      text: props.palace.lifeStage,
      title: `Vòng Tràng Sinh: ${props.palace.lifeStage}`,
    })
  }
  if (props.palace.monthNumber !== null) {
    cells.push({
      key: 'thang',
      text: `Tháng ${props.palace.monthNumber}`,
      title: `Nguyệt lệnh: tháng ${props.palace.monthNumber}`,
    })
  }
  if (props.palace.annualRef) {
    cells.push({
      key: 'ln',
      text: props.palace.annualRef,
      title: `Lưu niên: ${props.palace.annualRef}`,
    })
  }
  return cells
})

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
        <!-- Một trị, như lá số in. Khoảng đầy đủ nằm ở tooltip: ô này đã chật, và
             "93 – 102" đẩy tên cung xuống dòng trên màn hẹp. -->
        <span
          class="tuvi-palace__age"
          :title="palace.majorCycleAge ? `Đại vận ${palace.majorCycleAge} tuổi` : undefined"
        >
          <template v-if="palace.majorCycleAgeStart !== null">{{
            palace.majorCycleAgeStart
          }}</template>
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

    <!--
      Tứ Hóa: **một khối, sau toàn bộ chính tinh**.

      Trước đây mỗi dòng hóa nằm trong chính ngôi sao mang nó. Ở một cung có hai chính
      tinh mà sao thứ nhất mang hóa, dòng hóa chen vào GIỮA hai chính tinh — khối chính
      tinh vỡ, và mắt đọc thành hai cụm rời. Dòng hóa mang màu ngũ hành của sao mang nó
      và nói tên sao ấy trong tooltip, nên tách ra không mất thông tin nào.
    -->
    <ul v-if="palace.transformationLines.length" class="tuvi-palace__hoa">
      <li
        v-for="(hoa, index) in palace.transformationLines"
        :key="`${hoa.code}-${index}`"
        class="tuvi-hoa-line"
        :class="[elementClass(hoa.carrierElement), { 'is-annual-hoa': hoa.isAnnual }]"
        :data-transformation="hoa.code"
        :title="`${hoa.fullLabel} — của ${hoa.carrierName}`"
      >
        {{ hoa.fullLabel
        }}<abbr v-if="hoa.strengthAbbr" class="tuvi-star__strength" :title="hoa.strengthLabel ?? undefined"
          >({{ hoa.strengthAbbr }})</abbr
        >
      </li>
    </ul>

    <!--
      Hai cột của bản in truyền thống: cát/trợ bên trái, sát/bại bên phải.

      Mỗi cột là một danh sách RIÊNG, không phải một lưới hai cột chảy tràn hàng. Lưới
      tràn hàng xếp sao theo thứ tự dữ liệu, nên cát và sát nằm lẫn lộn — người đọc mất
      đúng cái mà bản in dựng ra để thấy: thế cân bằng của cung.

      Cột do engine quyết (``traditional_column``). Renderer không suy từ tên sao, từ
      loại, và tuyệt đối không từ màu — màu là ngũ hành, cát/hung là chuyện khác.
    -->
    <div v-if="palace.leftColumn.length || palace.rightColumn.length" class="tuvi-palace__stars">
      <ul class="tuvi-palace__column" data-column="left">
        <li v-for="star in palace.leftColumn" :key="star.code">
          <TuViStar :star="star" />
        </li>
      </ul>
      <ul class="tuvi-palace__column" data-column="right">
        <li v-for="star in palace.rightColumn" :key="star.code">
          <TuViStar :star="star" />
        </li>
      </ul>
    </div>

    <!--
      Footer: mỗi ô là **một giá trị engine thật sự cấp**. Ô nào không có dữ liệu thì
      không được dựng ra — một ô trống đọc như dữ liệu bị mất, còn chỗ dành sẵn thì
      đẩy hai ô kia lệch khỏi trục.

      ``Tháng n`` đã có chỗ ở đây. Engine chưa cấp ``month_number`` nên nó không hiện;
      khi nào cấp thì dòng này tự có, không phải dựng lại bố cục.
    -->
    <footer v-if="footerCells.length" class="tuvi-palace__footer">
      <span v-for="cell in footerCells" :key="cell.key" :title="cell.title">{{ cell.text }}</span>
    </footer>
  </section>
</template>
