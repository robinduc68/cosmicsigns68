<script setup lang="ts">
import {
  BookOpen,
  Download,
  LayoutGrid,
  Maximize,
  Printer,
  Scan,
  ZoomIn,
  ZoomOut,
} from 'lucide-vue-next'
import type { ChartViewMode } from '~/types/chart-view-model'

defineProps<{ mode: ChartViewMode; exporting: boolean; printing: boolean }>()
const emit = defineEmits<{
  'update:mode': [mode: ChartViewMode]
  zoomIn: []
  zoomOut: []
  fit: []
  fullscreen: []
  exportPng: []
  print: []
}>()

const MODES: { value: ChartViewMode; label: string; icon: typeof LayoutGrid }[] = [
  { value: 'overview', label: 'Toàn lá số', icon: LayoutGrid },
  { value: 'reading', label: 'Đọc từng cung', icon: BookOpen },
]
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-2" role="toolbar" aria-label="Công cụ lá số">
    <div class="inline-flex rounded-xl border border-[var(--border)] p-0.5" role="group" aria-label="Chế độ xem">
      <button
        v-for="option in MODES"
        :key="option.value"
        type="button"
        class="inline-flex h-9 items-center gap-1.5 rounded-lg px-3 text-small transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
        :class="
          mode === option.value
            ? 'bg-[var(--accent-soft)] text-[var(--accent)]'
            : 'text-[var(--text-muted)] hover:text-[var(--text)]'
        "
        :aria-pressed="mode === option.value"
        @click="emit('update:mode', option.value)"
      >
        <component :is="option.icon" class="size-4" aria-hidden="true" />
        {{ option.label }}
      </button>
    </div>

    <div class="flex flex-wrap items-center gap-1.5">
      <template v-if="mode === 'overview'">
        <CsIconButton label="Thu nhỏ" @click="emit('zoomOut')">
          <ZoomOut class="size-4" aria-hidden="true" />
        </CsIconButton>
        <CsIconButton label="Phóng to" @click="emit('zoomIn')">
          <ZoomIn class="size-4" aria-hidden="true" />
        </CsIconButton>
        <CsIconButton label="Vừa màn hình" @click="emit('fit')">
          <Scan class="size-4" aria-hidden="true" />
        </CsIconButton>
        <CsIconButton label="Toàn màn hình" @click="emit('fullscreen')">
          <Maximize class="size-4" aria-hidden="true" />
        </CsIconButton>
      </template>
      <CsButton variant="secondary" size="sm" :loading="printing" @click="emit('print')">
        <template #leading><Printer class="size-4" aria-hidden="true" /></template>
        In / PDF
      </CsButton>
      <CsButton size="sm" :loading="exporting" @click="emit('exportPng')">
        <template #leading><Download class="size-4" aria-hidden="true" /></template>
        Tải PNG
      </CsButton>
    </div>
  </div>
</template>
