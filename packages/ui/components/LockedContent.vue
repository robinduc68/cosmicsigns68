<script setup lang="ts">
import { Lock } from 'lucide-vue-next'

/**
 * Premium gate. Shows a real slice of the content — never a full blur — then
 * explains what the paid part actually contains and on what it is based.
 */
withDefaults(
  defineProps<{
    title: string
    /** The visible teaser. Around 15–20% of the section. */
    preview?: string
    basis?: string
    ctaLabel?: string
    ctaTo?: string
    /** For a gate whose purchase flow does not exist yet: no dead buttons. */
    ctaDisabled?: boolean
  }>(),
  { ctaLabel: 'Mở luận giải', ctaDisabled: false },
)
</script>

<template>
  <div
    class="overflow-hidden rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--card)]"
  >
    <div v-if="preview || $slots.preview" class="relative px-5 pt-5 sm:px-6 sm:pt-6">
      <div class="text-body text-[var(--text-muted)]">
        <slot name="preview">{{ preview }}</slot>
      </div>
      <div
        class="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-b from-transparent to-[var(--card)]"
      />
    </div>

    <div class="border-t border-[var(--border)] px-5 py-5 sm:px-6">
      <div class="flex flex-wrap items-center gap-2">
        <span
          class="inline-flex size-7 items-center justify-center rounded-full bg-[var(--color-gold-400)]/10 text-[var(--color-gold-400)]"
        >
          <Lock class="size-3.5" aria-hidden="true" />
        </span>
        <p class="font-display text-h3 text-[var(--text)]">{{ title }}</p>
      </div>
      <p v-if="basis" class="mt-2.5 text-small text-[var(--text-muted)]">{{ basis }}</p>
      <CsButton v-if="ctaTo && !ctaDisabled" :to="ctaTo" class="mt-4" size="sm">
        {{ ctaLabel }}
      </CsButton>
      <CsButton v-else class="mt-4" size="sm" :disabled="ctaDisabled">
        <slot name="cta">{{ ctaLabel }}</slot>
      </CsButton>
    </div>
  </div>
</template>
