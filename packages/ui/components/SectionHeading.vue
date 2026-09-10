<script setup lang="ts">
withDefaults(
  defineProps<{
    eyebrow?: string
    title: string
    description?: string
    align?: 'left' | 'center'
    as?: 'h2' | 'h3'
  }>(),
  { align: 'left', as: 'h2' },
)
</script>

<template>
  <div :class="['max-w-2xl', align === 'center' && 'mx-auto text-center']">
    <p
      v-if="eyebrow"
      class="mb-3 text-caption font-medium tracking-[0.14em] text-[var(--accent)] uppercase"
    >
      {{ eyebrow }}
    </p>
    <component
      :is="as"
      class="text-balance-heading font-display text-h2 text-[var(--text)] sm:text-h1"
    >
      {{ title }}
    </component>
    <p v-if="description" class="mt-4 text-body text-[var(--text-muted)]">{{ description }}</p>
    <slot />
  </div>
</template>
