<script setup lang="ts">
import { CheckCircle2, Info, X, XCircle } from 'lucide-vue-next'
import { useToast } from '../composables/useToast'

const { toasts, dismiss } = useToast()

const icons = { default: Info, success: CheckCircle2, error: XCircle }
</script>

<template>
  <div
    class="pointer-events-none fixed inset-x-0 bottom-0 z-[60] flex flex-col items-center gap-2 p-4 sm:inset-x-auto sm:right-0 sm:bottom-0 sm:items-end"
    role="region"
    aria-label="Thông báo"
  >
    <TransitionGroup
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="translate-y-2 opacity-0"
      leave-active-class="transition duration-200 ease-in"
      leave-to-class="translate-y-1 opacity-0"
    >
      <div
        v-for="item in toasts"
        :key="item.id"
        role="status"
        aria-live="polite"
        class="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-xl border border-[var(--border)] bg-[var(--bg-elevated)] p-3.5 shadow-xl"
      >
        <component
          :is="icons[item.variant]"
          class="mt-0.5 size-4 shrink-0"
          :class="{
            'text-[var(--success)]': item.variant === 'success',
            'text-[var(--danger)]': item.variant === 'error',
            'text-[var(--text-subtle)]': item.variant === 'default',
          }"
          aria-hidden="true"
        />
        <div class="min-w-0 flex-1">
          <p class="text-small font-medium text-[var(--text)]">{{ item.title }}</p>
          <p v-if="item.description" class="mt-0.5 text-caption text-[var(--text-muted)]">
            {{ item.description }}
          </p>
        </div>
        <button
          type="button"
          class="rounded p-1 text-[var(--text-subtle)] transition-colors hover:text-[var(--text)]"
          aria-label="Đóng thông báo"
          @click="dismiss(item.id)"
        >
          <X class="size-3.5" aria-hidden="true" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
