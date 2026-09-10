<script setup lang="ts">
import { AlertCircle } from 'lucide-vue-next'

defineProps<{
  label?: string
  hint?: string
  error?: string
  required?: boolean
  fieldId?: string
}>()
</script>

<template>
  <div class="w-full">
    <div v-if="label" class="mb-1.5 flex items-baseline justify-between gap-3">
      <label :for="fieldId" class="text-small font-medium text-[var(--text)]">
        {{ label }}
        <span v-if="required" class="text-[var(--danger)]" aria-hidden="true">*</span>
      </label>
      <slot name="labelAction" />
    </div>
    <slot />
    <p
      v-if="error"
      :id="fieldId ? `${fieldId}-error` : undefined"
      class="mt-1.5 flex items-start gap-1.5 text-caption text-[var(--danger)]"
    >
      <AlertCircle class="mt-px size-3.5 shrink-0" aria-hidden="true" />
      <span>{{ error }}</span>
    </p>
    <p
      v-else-if="hint"
      :id="fieldId ? `${fieldId}-hint` : undefined"
      class="mt-1.5 text-caption text-[var(--text-subtle)]"
    >
      {{ hint }}
    </p>
  </div>
</template>
