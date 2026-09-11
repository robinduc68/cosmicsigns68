<script setup lang="ts">
import type { ChartPalace } from '@cosmic/shared'

defineProps<{ palace: ChartPalace }>()
</script>

<template>
  <div
    :data-branch="palace.branch"
    class="flex min-h-32 flex-col gap-1.5 bg-[var(--card)] p-2 transition-colors sm:min-h-40 sm:p-3"
    :class="palace.is_menh && 'bg-[var(--accent-soft)]'"
  >
    <div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1">
      <span class="font-display text-small font-semibold text-[var(--text)]">
        {{ palace.label }}
      </span>
      <CsBadge v-if="palace.is_than" variant="gold">Thân</CsBadge>
    </div>

    <div class="flex flex-wrap gap-1">
      <CsBadge v-if="palace.has_tuan" variant="outline">Tuần</CsBadge>
      <CsBadge v-if="palace.has_triet" variant="outline">Triệt</CsBadge>
    </div>

    <!-- Chính tinh trước, rồi phụ tinh và tứ hoá — đúng thứ tự người ta đọc. -->
    <ul v-if="palace.major_stars.length" class="space-y-0.5">
      <li v-for="star in palace.major_stars" :key="star.code" class="text-caption">
        <span class="font-medium text-[var(--accent)]">{{ star.label }}</span>
        <span v-if="star.strength" class="text-[var(--text-subtle)]">
          {{ ' ' }}{{ star.strength }}
        </span>
        <span v-if="star.provisional" class="text-[var(--text-subtle)]">
          <span aria-hidden="true">*</span>
          <span class="sr-only">— vị trí chưa được kiểm định</span>
        </span>
      </li>
    </ul>
    <p v-else-if="palace.is_empty_main_star" class="text-caption text-[var(--text-subtle)]">
      Vô chính diệu
    </p>

    <ul v-if="palace.minor_stars.length" class="flex flex-wrap gap-x-1.5 text-caption">
      <li v-for="star in palace.minor_stars" :key="star.code" class="text-[var(--text-muted)]">
        {{ star.label }}
      </li>
    </ul>

    <div class="mt-auto pt-1 text-caption text-[var(--text-subtle)]">
      <p>{{ palace.stem }} {{ palace.branch }}</p>
      <p>{{ palace.nap_am }}</p>
    </div>
  </div>
</template>
