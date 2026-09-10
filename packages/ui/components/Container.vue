<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '../utils/cn'

const props = withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg'; as?: string }>(), {
  size: 'lg',
  as: 'div',
})

const classes = computed(() =>
  cn(
    'mx-auto w-full px-5 sm:px-6 lg:px-8',
    props.size === 'sm' && 'max-w-3xl',
    props.size === 'md' && 'max-w-5xl',
    props.size === 'lg' && 'max-w-6xl',
  ),
)
</script>

<template>
  <component :is="as" :class="classes"><slot /></component>
</template>
