<script setup lang="ts">
import { RotateCw, TriangleAlert } from 'lucide-vue-next'

withDefaults(
  defineProps<{
    title?: string
    description?: string
    retryLabel?: string
    /** Shown only in development so a real user never sees a stack trace. */
    debug?: string
  }>(),
  {
    title: 'Có lỗi xảy ra',
    description: 'Bạn thử lại sau vài giây nhé. Nếu vẫn chưa được, hãy tải lại trang.',
    retryLabel: 'Thử lại',
  },
)

const emit = defineEmits<{ retry: [] }>()
const isDev = import.meta.dev
</script>

<template>
  <div
    class="flex flex-col items-center rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--card)] px-6 py-12 text-center"
    role="alert"
  >
    <div
      class="mb-4 flex size-11 items-center justify-center rounded-full bg-[var(--danger-soft)] text-[var(--danger)]"
    >
      <TriangleAlert class="size-5" aria-hidden="true" />
    </div>
    <p class="font-display text-h3 text-[var(--text)]">{{ title }}</p>
    <p class="mt-2 max-w-sm text-small text-[var(--text-muted)]">{{ description }}</p>
    <CsButton variant="secondary" class="mt-6" @click="emit('retry')">
      <template #leading><RotateCw class="size-4" aria-hidden="true" /></template>
      {{ retryLabel }}
    </CsButton>
    <pre
      v-if="isDev && debug"
      class="mt-6 max-w-full overflow-x-auto rounded-lg bg-[var(--card-hover)] p-3 text-left text-caption text-[var(--text-subtle)]"
      >{{ debug }}</pre
    >
  </div>
</template>
