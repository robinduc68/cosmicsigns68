<script setup lang="ts">
import { computed, useId } from 'vue'
import { ChevronDown } from 'lucide-vue-next'
import { cn } from '../utils/cn'

export interface SelectOption {
  value: string | number
  label: string
  disabled?: boolean
}

/**
 * A styled native `<select>`. On phones this hands the user the OS picker,
 * which beats any custom listbox for reach, speed and accessibility.
 */
const props = defineProps<{
  label?: string
  hint?: string
  error?: string
  options: SelectOption[]
  placeholder?: string
  required?: boolean
  disabled?: boolean
}>()

const model = defineModel<string | number | null>()
const generatedId = useId()
const fieldId = computed(() => `select-${generatedId}`)
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
      <select
        :id="fieldId"
        v-model="model"
        :required="required"
        :disabled="disabled"
        :aria-invalid="error ? true : undefined"
        :class="
          cn(
            'w-full appearance-none rounded-xl border bg-[var(--bg-elevated)] py-2.5 pr-10 pl-3.5',
            'text-body text-[var(--text)] transition-[border-color,box-shadow] duration-200',
            'focus:outline-none focus:border-[var(--accent)] focus:ring-4 focus:ring-[var(--accent-ring)]/25',
            'disabled:cursor-not-allowed disabled:opacity-55',
            props.error ? 'border-[var(--danger)]' : 'border-[var(--border)]',
            model === null || model === '' ? 'text-[var(--text-subtle)]' : '',
          )
        "
      >
        <option v-if="placeholder" :value="null" disabled>{{ placeholder }}</option>
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>
      <ChevronDown
        class="pointer-events-none absolute top-1/2 right-3.5 size-4 -translate-y-1/2 text-[var(--text-subtle)]"
        aria-hidden="true"
      />
    </div>
  </CsFormField>
</template>
