<script setup lang="ts">
import { useId } from 'vue'

export interface RadioOption {
  value: string
  label: string
  description?: string
}

withDefaults(
  defineProps<{
    label?: string
    hint?: string
    error?: string
    options: RadioOption[]
    columns?: 1 | 2 | 3
  }>(),
  { columns: 2 },
)

const model = defineModel<string | null>()
const name = `radio-${useId()}`
</script>

<template>
  <fieldset>
    <legend v-if="label" class="mb-2 text-small font-medium text-[var(--text)]">
      {{ label }}
    </legend>
    <div
      class="grid gap-2.5"
      :class="[
        columns === 1 && 'grid-cols-1',
        columns === 2 && 'grid-cols-2',
        columns === 3 && 'grid-cols-2 sm:grid-cols-3',
      ]"
    >
      <label
        v-for="option in options"
        :key="option.value"
        class="relative flex cursor-pointer flex-col gap-0.5 rounded-xl border px-4 py-3 transition-[border-color,background-color] duration-200 focus-within:ring-4 focus-within:ring-[var(--accent-ring)]/25"
        :class="
          model === option.value
            ? 'border-[var(--accent)] bg-[var(--accent-soft)]'
            : 'border-[var(--border)] bg-[var(--bg-elevated)] hover:border-[var(--border-strong)]'
        "
      >
        <input
          v-model="model"
          type="radio"
          :name="name"
          :value="option.value"
          class="sr-only"
          :aria-describedby="option.description ? `${name}-${option.value}-desc` : undefined"
        />
        <span
          class="text-small font-medium"
          :class="model === option.value ? 'text-[var(--accent)]' : 'text-[var(--text)]'"
        >
          {{ option.label }}
        </span>
        <span
          v-if="option.description"
          :id="`${name}-${option.value}-desc`"
          class="text-caption text-[var(--text-muted)]"
        >
          {{ option.description }}
        </span>
      </label>
    </div>
    <p v-if="error" class="mt-1.5 text-caption text-[var(--danger)]">{{ error }}</p>
    <p v-else-if="hint" class="mt-1.5 text-caption text-[var(--text-subtle)]">{{ hint }}</p>
  </fieldset>
</template>
