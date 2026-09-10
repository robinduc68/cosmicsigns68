<script setup lang="ts">
import { computed, useId } from 'vue'
import { cn } from '../utils/cn'

const props = withDefaults(
  defineProps<{
    label?: string
    hint?: string
    error?: string
    placeholder?: string
    rows?: number
    maxlength?: number
    disabled?: boolean
  }>(),
  { rows: 3 },
)

const model = defineModel<string | null>()
const generatedId = useId()
const fieldId = computed(() => `textarea-${generatedId}`)
const count = computed(() => (model.value ?? '').length)
</script>

<template>
  <CsFormField :label="label" :hint="hint" :error="error" :field-id="fieldId">
    <template #labelAction>
      <span v-if="maxlength" class="text-caption text-[var(--text-subtle)]">
        {{ count }}/{{ maxlength }}
      </span>
    </template>
    <textarea
      :id="fieldId"
      v-model="model"
      :rows="rows"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :disabled="disabled"
      :aria-invalid="error ? true : undefined"
      :class="
        cn(
          'w-full resize-y rounded-xl border bg-[var(--bg-elevated)] px-3.5 py-2.5 text-body text-[var(--text)]',
          'placeholder:text-[var(--text-subtle)] transition-[border-color,box-shadow] duration-200',
          'focus:outline-none focus:border-[var(--accent)] focus:ring-4 focus:ring-[var(--accent-ring)]/25',
          'disabled:cursor-not-allowed disabled:opacity-55',
          props.error ? 'border-[var(--danger)]' : 'border-[var(--border)]',
        )
      "
    />
  </CsFormField>
</template>
