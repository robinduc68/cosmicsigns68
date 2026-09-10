<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '../utils/cn'

const props = withDefaults(
  defineProps<{
    /** `interactive` adds hover affordance — only use it when the whole card is clickable. */
    interactive?: boolean
    padded?: boolean
    as?: string
    to?: string
  }>(),
  { interactive: false, padded: true, as: 'div' },
)

const classes = computed(() =>
  cn(
    'rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--card)]',
    props.padded && 'p-5 sm:p-6',
    props.interactive &&
      'transition-[border-color,background-color,transform] duration-200 hover:border-[var(--border-strong)] hover:bg-[var(--card-hover)] focus-within:border-[var(--border-strong)]',
  ),
)
</script>

<template>
  <NuxtLink v-if="to" :to="to" :class="classes"><slot /></NuxtLink>
  <component :is="as" v-else :class="classes"><slot /></component>
</template>
