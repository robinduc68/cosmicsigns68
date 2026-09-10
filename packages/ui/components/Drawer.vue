<script setup lang="ts">
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from 'reka-ui'
import { X } from 'lucide-vue-next'

/** A side/bottom sheet. On phones it slides up from the bottom edge. */
withDefaults(defineProps<{ title: string; description?: string; side?: 'right' | 'bottom' }>(), {
  side: 'right',
})

const open = defineModel<boolean>('open', { default: false })
</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-50 bg-black/55 backdrop-blur-[2px]" />
      <DialogContent
        :class="[
          'fixed z-50 flex flex-col border-[var(--border)] bg-[var(--bg-elevated)] focus:outline-none',
          side === 'right'
            ? 'inset-y-0 right-0 w-full max-w-sm border-l'
            : 'inset-x-0 bottom-0 max-h-[85vh] rounded-t-2xl border-t',
        ]"
      >
        <div class="flex items-start justify-between gap-4 border-b border-[var(--border)] p-5">
          <div>
            <DialogTitle class="font-display text-h3 text-[var(--text)]">{{ title }}</DialogTitle>
            <DialogDescription v-if="description" class="mt-1 text-small text-[var(--text-muted)]">
              {{ description }}
            </DialogDescription>
          </div>
          <DialogClose
            class="-mt-1 -mr-1 rounded-lg p-2 text-[var(--text-subtle)] transition-colors hover:bg-[var(--card-hover)] hover:text-[var(--text)]"
            aria-label="Đóng"
          >
            <X class="size-4" aria-hidden="true" />
          </DialogClose>
        </div>
        <div class="flex-1 overflow-y-auto p-5"><slot /></div>
        <div v-if="$slots.footer" class="border-t border-[var(--border)] p-5"><slot name="footer" /></div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
