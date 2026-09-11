<script setup lang="ts">
import { Check, Loader2 } from 'lucide-vue-next'

/**
 * Các chặng dưới đây là *đúng* những gì engine làm, theo đúng thứ tự. API chỉ
 * trả về một lần ở cuối nên không thể bám theo tiến trình thật từng bước; vì
 * vậy phần reveal luôn đợi phản hồi thật, và không có chặng nào tự nhận là
 * "đã xong" khi lá số chưa về.
 */
const STAGES = [
  'Đang đổi sang âm lịch…',
  'Đang lập tứ trụ can chi…',
  'Đang an Mệnh và Thân…',
  'Đang tính Cục và dựng 12 cung…',
]

const props = defineProps<{ done: boolean }>()

const reached = ref(0)
let timer: ReturnType<typeof setInterval> | undefined

onMounted(() => {
  timer = setInterval(() => {
    // Chặng cuối chỉ được đánh dấu xong khi lá số đã thực sự về.
    if (reached.value < STAGES.length - 1) reached.value += 1
  }, 650)
})

onBeforeUnmount(() => clearInterval(timer))
watch(
  () => props.done,
  (finished) => {
    if (finished) {
      reached.value = STAGES.length
      clearInterval(timer)
    }
  },
)
</script>

<template>
  <div class="py-10" role="status" aria-live="polite">
    <ol class="mx-auto max-w-sm space-y-4">
      <li
        v-for="(stage, index) in STAGES"
        :key="stage"
        class="flex items-center gap-3 transition-opacity duration-300"
        :class="index <= reached ? 'opacity-100' : 'opacity-35'"
      >
        <span class="flex size-5 shrink-0 items-center justify-center">
          <Check v-if="index < reached" class="size-4 text-[var(--success)]" aria-hidden="true" />
          <Loader2
            v-else-if="index === reached"
            class="size-4 animate-spin text-[var(--accent)]"
            aria-hidden="true"
          />
          <span v-else class="size-1.5 rounded-full bg-[var(--border-strong)]" />
        </span>
        <span class="text-small text-[var(--text-muted)]">{{ stage }}</span>
      </li>
    </ol>
  </div>
</template>
