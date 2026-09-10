<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../utils/cn'

const iconButton = cva(
  [
    'inline-flex items-center justify-center rounded-lg transition-colors duration-200',
    'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]',
    'disabled:pointer-events-none disabled:opacity-45',
  ],
  {
    variants: {
      variant: {
        ghost: 'text-[var(--text-muted)] hover:bg-[var(--card-hover)] hover:text-[var(--text)]',
        outline:
          'border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)] hover:border-[var(--border-strong)]',
        solid: 'bg-[var(--accent)] text-[var(--accent-contrast)] hover:bg-[var(--accent-hover)]',
      },
      size: { sm: 'size-8', md: 'size-10', lg: 'size-11' },
    },
    defaultVariants: { variant: 'ghost', size: 'md' },
  },
)

type Variants = VariantProps<typeof iconButton>

const props = defineProps<{
  variant?: Variants['variant']
  size?: Variants['size']
  label: string
  disabled?: boolean
  to?: string
}>()

const classes = computed(() => cn(iconButton({ variant: props.variant, size: props.size })))
</script>

<template>
  <NuxtLink v-if="to" :to="to" :class="classes" :aria-label="label"><slot /></NuxtLink>
  <button v-else type="button" :class="classes" :aria-label="label" :disabled="disabled">
    <slot />
  </button>
</template>
