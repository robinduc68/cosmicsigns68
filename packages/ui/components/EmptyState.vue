<script setup lang="ts">
defineProps<{ title: string; description?: string }>()
</script>

<template>
  <div
    class="flex flex-col items-center rounded-[var(--radius-card)] border border-dashed border-[var(--border)] px-6 py-14 text-center"
  >
    <div
      v-if="$slots.icon"
      class="mb-4 flex size-11 items-center justify-center rounded-full bg-[var(--card)] text-[var(--text-subtle)]"
    >
      <slot name="icon" />
    </div>
    <p class="font-display text-h3 text-[var(--text)]">{{ title }}</p>
    <p v-if="description" class="mt-2 max-w-sm text-small text-[var(--text-muted)]">
      {{ description }}
    </p>
    <div v-if="$slots.action" class="mt-6"><slot name="action" /></div>
  </div>
</template>
