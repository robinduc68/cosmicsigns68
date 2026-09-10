<script setup lang="ts">
import { computed, useId } from 'vue'
import { cn } from '../utils/cn'

const props = withDefaults(
  defineProps<{
    label?: string
    hint?: string
    error?: string
    type?: string
    placeholder?: string
    required?: boolean
    disabled?: boolean
    inputmode?: 'text' | 'numeric' | 'tel' | 'email' | 'decimal'
    autocomplete?: string
    maxlength?: number
    min?: number | string
    max?: number | string
  }>(),
  { type: 'text' },
)

const model = defineModel<string | number | null>()
const generatedId = useId()
const fieldId = computed(() => `input-${generatedId}`)

const classes = computed(() =>
  cn(
    'w-full rounded-xl border bg-[var(--bg-elevated)] px-3.5 py-2.5 text-body text-[var(--text)]',
    'placeholder:text-[var(--text-subtle)] transition-[border-color,box-shadow] duration-200',
    'focus:outline-none focus:border-[var(--accent)] focus:ring-4 focus:ring-[var(--accent-ring)]/25',
    'disabled:cursor-not-allowed disabled:opacity-55',
    props.error ? 'border-[var(--danger)]' : 'border-[var(--border)]',
  ),
)
</script>

<template>
  <CsFormField
    :label="label"
    :hint="hint"
    :error="error"
    :required="required"
    :field-id="fieldId"
  >
    <div class="relative">
      <div
        v-if="$slots.leading"
        class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-[var(--text-subtle)]"
      >
        <slot name="leading" />
      </div>
      <input
        :id="fieldId"
        v-model="model"
        :type="type"
        :class="[classes, $slots.leading && 'pl-10', $slots.trailing && 'pr-10']"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :inputmode="inputmode"
        :autocomplete="autocomplete"
        :maxlength="maxlength"
        :min="min"
        :max="max"
        :aria-invalid="error ? true : undefined"
        :aria-describedby="error ? `${fieldId}-error` : hint ? `${fieldId}-hint` : undefined"
      />
      <div v-if="$slots.trailing" class="absolute inset-y-0 right-3 flex items-center">
        <slot name="trailing" />
      </div>
    </div>
  </CsFormField>
</template>
