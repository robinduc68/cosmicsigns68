<script setup lang="ts">
withDefaults(defineProps<{ compact?: boolean; size?: 'sm' | 'md' }>(), {
  compact: false,
  size: 'md',
})
</script>

<template>
  <span class="inline-flex items-center gap-2.5" aria-label="Cosmic Signs">
    <!-- A minimal astrology wheel: an orbit, an axis and a single fixed star. -->
    <svg
      :class="size === 'sm' ? 'size-6' : 'size-7'"
      viewBox="0 0 28 28"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="14" cy="14" r="10.25" stroke="currentColor" stroke-opacity="0.28" />
      <circle cx="14" cy="14" r="5.5" stroke="currentColor" stroke-opacity="0.16" />
      <path
        d="M14 3.75v20.5M3.75 14h20.5"
        stroke="currentColor"
        stroke-opacity="0.12"
        stroke-linecap="round"
      />
      <path
        d="m19.4 7.1.72 1.9 1.9.72-1.9.72-.72 1.9-.72-1.9-1.9-.72 1.9-.72.72-1.9Z"
        fill="currentColor"
      />
      <circle cx="14" cy="14" r="1.6" fill="currentColor" />
    </svg>
    <span
      v-if="!compact"
      class="font-display text-[0.95rem] font-semibold tracking-[0.16em] uppercase"
    >
      Cosmic Signs
    </span>
  </span>
</template>
