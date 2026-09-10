<script setup lang="ts">
import { computed, useId } from 'vue'
import { Check } from 'lucide-vue-next'

defineProps<{ label?: string; description?: string; disabled?: boolean }>()
const model = defineModel<boolean>({ default: false })
const generatedId = useId()
const fieldId = computed(() => `checkbox-${generatedId}`)
</script>

<template>
  <label
    :for="fieldId"
    class="group flex cursor-pointer items-start gap-3"
    :class="disabled && 'cursor-not-allowed opacity-55'"
  >
    <span class="relative mt-0.5 flex size-5 shrink-0 items-center justify-center">
      <input
        :id="fieldId"
        v-model="model"
        type="checkbox"
        :disabled="disabled"
        class="peer size-5 appearance-none rounded-md border border-[var(--border-strong)] bg-[var(--bg-elevated)] transition-colors checked:border-[var(--accent)] checked:bg-[var(--accent)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
      />
      <Check
        class="pointer-events-none absolute size-3.5 text-[var(--accent-contrast)] opacity-0 peer-checked:opacity-100"
        aria-hidden="true"
      />
    </span>
    <span v-if="label || description || $slots.default" class="text-small">
      <span class="block text-[var(--text)]"><slot>{{ label }}</slot></span>
      <span v-if="description" class="mt-0.5 block text-caption text-[var(--text-muted)]">
        {{ description }}
      </span>
    </span>
  </label>
</template>
