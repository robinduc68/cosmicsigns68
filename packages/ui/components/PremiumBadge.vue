<script setup lang="ts">
import { Sparkles } from 'lucide-vue-next'

withDefaults(defineProps<{ label?: string }>(), { label: 'Chuyên sâu' })
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full border border-[var(--color-gold-400)]/35 bg-[var(--color-gold-400)]/8 px-2.5 py-1 text-caption font-medium tracking-wide text-[var(--color-gold-400)]"
  >
    <Sparkles class="size-3" aria-hidden="true" />
    {{ label }}
  </span>
</template>
