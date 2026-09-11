<script setup lang="ts">
import { Check } from 'lucide-vue-next'

defineProps<{ steps: string[]; current: number }>()
const emit = defineEmits<{ goTo: [index: number] }>()
</script>

<template>
  <ol class="flex items-center gap-2" aria-label="Tiến độ lập lá số">
    <li
      v-for="(label, index) in steps"
      :key="label"
      class="flex min-w-0 flex-1"
      :aria-current="index === current ? 'step' : undefined"
    >
      <!-- Bước đã qua thì quay lại được; bước chưa tới thì nút tắt, để trạng
           thái "chưa mở" được nói ra thay vì chỉ trông mờ đi. -->
      <button
        type="button"
        class="flex min-w-0 flex-1 flex-col gap-1.5 rounded text-left disabled:cursor-default focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
        :disabled="index >= current"
        @click="emit('goTo', index)"
      >
        <span
          class="h-1 w-full rounded-full transition-colors duration-300"
          :class="index <= current ? 'bg-[var(--accent)]' : 'bg-[var(--border)]'"
        />
        <span
          class="flex items-center gap-1.5 truncate text-caption"
          :class="index <= current ? 'text-[var(--text)]' : 'text-[var(--text-subtle)]'"
        >
          <Check v-if="index < current" class="size-3 shrink-0" aria-hidden="true" />
          {{ label }}
        </span>
      </button>
    </li>
  </ol>
</template>
