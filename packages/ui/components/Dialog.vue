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

withDefaults(defineProps<{ title: string; description?: string; size?: 'sm' | 'md' | 'lg' }>(), {
  size: 'md',
})

const open = defineModel<boolean>('open', { default: false })
</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogPortal>
      <DialogOverlay
        class="fixed inset-0 z-50 bg-black/55 backdrop-blur-[2px] data-[state=open]:animate-[fade-up_0.2s_ease-out]"
      />
      <DialogContent
        :class="[
          'fixed top-1/2 left-1/2 z-50 w-[calc(100vw-2rem)] -translate-x-1/2 -translate-y-1/2',
          'rounded-2xl border border-[var(--border)] bg-[var(--bg-elevated)] p-6 shadow-2xl',
          'focus:outline-none data-[state=open]:animate-[fade-up_0.24s_var(--ease-out-soft)]',
          size === 'sm' && 'max-w-sm',
          size === 'md' && 'max-w-md',
          size === 'lg' && 'max-w-2xl',
        ]"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <DialogTitle class="font-display text-h3 text-[var(--text)]">{{ title }}</DialogTitle>
            <DialogDescription v-if="description" class="mt-1.5 text-small text-[var(--text-muted)]">
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
        <div class="mt-5"><slot /></div>
        <div v-if="$slots.footer" class="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <slot name="footer" />
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
