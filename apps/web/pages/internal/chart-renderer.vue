<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'
import TuViChart from '~/components/astrology/chart/TuViChart.vue'
import { renderChartPng } from '~/composables/useChartExport'
import { useTuViChartViewModel } from '~/composables/useTuViChartViewModel'
import { CHART_RENDERER_SCENARIOS } from '~/fixtures/chart-renderer-scenarios'
import type { ChartViewMode } from '~/types/chart-view-model'

/**
 * Internal renderer workbench — development only (route middleware 404s it in a
 * production build). Deterministic fixtures, so screenshots are comparable run
 * to run: `?scenario=<id>&mode=overview|reading`.
 */
definePageMeta({
  path: '/_internal/chart-renderer',
  middleware: 'dev-only',
})

useHead({ title: 'Renderer lá số (nội bộ)' })
useSeoMeta({ robots: 'noindex, nofollow, noarchive' })

const route = useRoute()
const router = useRouter()

const first = CHART_RENDERER_SCENARIOS[0]!
const scenarioId = computed({
  get: () => String(route.query.scenario ?? first.id),
  set: (id: string | number | null) => {
    void router.replace({ query: { ...route.query, scenario: String(id ?? first.id) } })
  },
})
const current = computed(
  () => CHART_RENDERER_SCENARIOS.find((entry) => entry.id === scenarioId.value) ?? first,
)
const model = useTuViChartViewModel(() => current.value.chart)
const initialMode = computed<ChartViewMode | undefined>(() => {
  const requested = route.query.mode
  return requested === 'overview' || requested === 'reading' ? requested : undefined
})
const options = CHART_RENDERER_SCENARIOS.map((entry) => ({ value: entry.id, label: entry.label }))

// Fixed, so exported file names in regression runs never depend on today's date.
const EXPORT_DATE = new Date(2026, 8, 11)

onMounted(() => {
  if (!import.meta.dev) return
  // Development hook for automated export checks. Not present in production builds.
  ;(window as unknown as Record<string, unknown>).__tuviRenderPng = async (scale = 2) => {
    const node = document.querySelector<HTMLElement>('#tuvi-offscreen-host .tuvi-chart')
    if (!node) throw new Error('Chưa có canvas để xuất ảnh')
    const blob = await renderChartPng(node, scale)
    return await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(String(reader.result))
      reader.onerror = () => reject(reader.error)
      reader.readAsDataURL(blob)
    })
  }
})
</script>

<template>
  <CsContainer class="py-10">
    <CsBadge variant="gold">Nội bộ · kiểm thử giao diện lá số</CsBadge>
    <h1 class="mt-3 font-display text-h2 text-[var(--text)]">Renderer lá số Tử Vi</h1>

    <div class="mt-6 grid gap-4 sm:grid-cols-[minmax(0,22rem)_1fr] sm:items-end">
      <CsSelect v-model="scenarioId" label="Kịch bản" :options="options" />
      <p class="text-small text-[var(--text-muted)]">{{ current.description }}</p>
    </div>

    <div
      v-if="current.synthetic"
      class="mt-4 flex items-start gap-2 rounded-lg border border-[var(--color-gold-400)]/40 p-3 text-small text-[var(--text)]"
      role="note"
    >
      <AlertTriangle
        class="mt-0.5 size-4 shrink-0 text-[var(--color-gold-400)]"
        aria-hidden="true"
      />
      Dữ liệu giả, chỉ để thử bố cục — không phải kết quả tử vi và không bao giờ được hiển thị
      cho khách.
    </div>

    <div class="mt-6">
      <TuViChart
        v-if="model"
        :key="`${current.id}-${initialMode ?? 'auto'}`"
        :model="model"
        file-slug="demo"
        :export-date="EXPORT_DATE"
        :initial-mode="initialMode"
      />
    </div>
  </CsContainer>
</template>
