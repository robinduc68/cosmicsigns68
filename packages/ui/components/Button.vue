<script setup lang="ts">
import { computed } from 'vue'
import { cva, type VariantProps } from 'class-variance-authority'
import { Loader2 } from 'lucide-vue-next'
import { cn } from '../utils/cn'

const button = cva(
  [
    'relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl',
    'font-medium transition-[background-color,border-color,color,box-shadow,transform] duration-200',
    'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]',
    'disabled:pointer-events-none disabled:opacity-45 active:translate-y-px',
  ],
  {
    variants: {
      variant: {
        primary:
          'bg-[var(--accent)] text-[var(--accent-contrast)] shadow-[0_1px_2px_rgba(0,0,0,0.16)] hover:bg-[var(--accent-hover)]',
        secondary:
          'bg-[var(--card)] text-[var(--text)] border border-[var(--border)] hover:bg-[var(--card-hover)] hover:border-[var(--border-strong)]',
        outline:
          'border border-[var(--border-strong)] text-[var(--text)] hover:bg-[var(--card-hover)]',
        ghost: 'text-[var(--text-muted)] hover:bg-[var(--card-hover)] hover:text-[var(--text)]',
        danger: 'bg-[var(--danger)] text-white hover:opacity-90',
        link: 'text-[var(--accent)] underline-offset-4 hover:underline px-0 h-auto',
      },
      size: {
        sm: 'h-9 px-3.5 text-small',
        md: 'h-11 px-5 text-small',
        lg: 'h-13 px-7 text-body',
      },
      block: { true: 'w-full', false: '' },
    },
    defaultVariants: { variant: 'primary', size: 'md', block: false },
  },
)

type ButtonVariants = VariantProps<typeof button>

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariants['variant']
    size?: ButtonVariants['size']
    block?: boolean
    loading?: boolean
    disabled?: boolean
    type?: 'button' | 'submit' | 'reset'
    to?: string
    href?: string
    ariaLabel?: string
  }>(),
  { type: 'button', loading: false, disabled: false, block: false },
)

const classes = computed(() =>
  cn(button({ variant: props.variant, size: props.size, block: props.block })),
)
const isDisabled = computed(() => props.disabled || props.loading)
</script>

<template>
  <NuxtLink
    v-if="to && !isDisabled"
    :to="to"
    :class="classes"
    :aria-label="ariaLabel"
    :aria-busy="loading || undefined"
  >
    <slot name="leading" />
    <slot />
    <slot name="trailing" />
  </NuxtLink>
  <a
    v-else-if="href && !isDisabled"
    :href="href"
    :class="classes"
    :aria-label="ariaLabel"
    rel="noopener"
  >
    <slot name="leading" />
    <slot />
    <slot name="trailing" />
  </a>
  <button
    v-else
    :type="type"
    :class="classes"
    :disabled="isDisabled"
    :aria-label="ariaLabel"
    :aria-busy="loading || undefined"
  >
    <Loader2 v-if="loading" class="size-4 animate-spin" aria-hidden="true" />
    <slot v-else name="leading" />
    <span :class="loading ? 'opacity-90' : undefined"><slot /></span>
    <slot name="trailing" />
  </button>
</template>
