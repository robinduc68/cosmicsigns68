<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '../utils/cn'

const props = withDefaults(
  defineProps<{ class?: string; rounded?: 'sm' | 'md' | 'full'; lines?: number }>(),
  { rounded: 'md', lines: 1 },
)

const base = computed(() =>
  cn(
    'animate-pulse bg-[var(--card-hover)]',
    props.rounded === 'sm' && 'rounded',
    props.rounded === 'md' && 'rounded-lg',
    props.rounded === 'full' && 'rounded-full',
    props.class,
  ),
)
</script>

<template>
  <div v-if="lines <= 1" :class="base" aria-hidden="true" />
  <div v-else class="space-y-2" aria-hidden="true">
    <div
      v-for="line in lines"
      :key="line"
      :class="[base, line === lines && 'w-3/5']"
      class="h-3.5"
    />
  </div>
</template>
