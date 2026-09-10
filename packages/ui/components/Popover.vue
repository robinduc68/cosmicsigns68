<script setup lang="ts">
import { PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'

withDefaults(defineProps<{ align?: 'start' | 'center' | 'end'; width?: string }>(), {
  align: 'center',
  width: 'w-72',
})
const open = defineModel<boolean>('open', { default: false })
</script>

<template>
  <PopoverRoot v-model:open="open">
    <PopoverTrigger as-child>
      <slot name="trigger" />
    </PopoverTrigger>
    <PopoverPortal>
      <PopoverContent
        :align="align"
        :side-offset="8"
        :class="[
          width,
          'z-50 rounded-xl border border-[var(--border)] bg-[var(--bg-elevated)] p-4 shadow-xl focus:outline-none',
        ]"
      >
        <slot />
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
