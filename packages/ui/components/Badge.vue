<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../utils/cn'

const badge = cva(
  'inline-flex items-center gap-1.5 rounded-full border font-medium whitespace-nowrap',
  {
    variants: {
      variant: {
        neutral: 'border-[var(--border)] bg-[var(--card)] text-[var(--text-muted)]',
        accent: 'border-transparent bg-[var(--accent-soft)] text-[var(--accent)]',
        success: 'border-transparent bg-[var(--success-soft)] text-[var(--success)]',
        danger: 'border-transparent bg-[var(--danger-soft)] text-[var(--danger)]',
        outline: 'border-[var(--border-strong)] text-[var(--text)]',
        gold: 'border-[var(--color-gold-400)]/40 bg-[var(--color-gold-400)]/10 text-[var(--color-gold-400)]',
      },
      size: { sm: 'px-2 py-0.5 text-caption', md: 'px-2.5 py-1 text-caption' },
    },
    defaultVariants: { variant: 'neutral', size: 'sm' },
  },
)

type Variants = VariantProps<typeof badge>
const props = defineProps<{ variant?: Variants['variant']; size?: Variants['size'] }>()
const classes = computed(() => cn(badge({ variant: props.variant, size: props.size })))
</script>

<template>
  <span :class="classes"><slot /></span>
</template>
