<script setup lang="ts">
import {
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuPortal,
  DropdownMenuRoot,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from 'reka-ui'

export interface DropdownItem {
  key: string
  label: string
  danger?: boolean
  disabled?: boolean
  separatorBefore?: boolean
}

withDefaults(defineProps<{ items: DropdownItem[]; align?: 'start' | 'center' | 'end' }>(), {
  align: 'end',
})

const emit = defineEmits<{ select: [key: string] }>()
</script>

<template>
  <DropdownMenuRoot>
    <DropdownMenuTrigger as-child>
      <slot name="trigger" />
    </DropdownMenuTrigger>
    <DropdownMenuPortal>
      <DropdownMenuContent
        :align="align"
        :side-offset="6"
        class="z-50 min-w-48 rounded-xl border border-[var(--border)] bg-[var(--bg-elevated)] p-1.5 shadow-xl focus:outline-none"
      >
        <template v-for="item in items" :key="item.key">
          <DropdownMenuSeparator
            v-if="item.separatorBefore"
            class="my-1.5 h-px bg-[var(--border)]"
          />
          <DropdownMenuItem
            :disabled="item.disabled"
            class="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-small transition-colors outline-none select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-45 data-[highlighted]:bg-[var(--card-hover)]"
            :class="item.danger ? 'text-[var(--danger)]' : 'text-[var(--text)]'"
            @select="emit('select', item.key)"
          >
            {{ item.label }}
          </DropdownMenuItem>
        </template>
      </DropdownMenuContent>
    </DropdownMenuPortal>
  </DropdownMenuRoot>
</template>
