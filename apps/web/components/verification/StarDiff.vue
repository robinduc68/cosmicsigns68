<script setup lang="ts">
import { Check, Minus, X } from 'lucide-vue-next'
import { STAR_LABELS, type StarComparison } from '~/composables/useVerification'

const props = defineProps<{ comparisons: StarComparison[] }>()

const mismatchCount = computed(
  () => props.comparisons.filter((c) => c.status === 'MISMATCH').length,
)
const unverifiedCount = computed(
  () => props.comparisons.filter((c) => c.status === 'UNVERIFIED').length,
)
</script>

<template>
  <section>
    <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
      <h3 class="font-display text-h3 text-[var(--text)]">So sánh 14 chính tinh</h3>
      <div class="flex gap-2">
        <CsBadge v-if="mismatchCount" variant="danger">{{ mismatchCount }} lệch</CsBadge>
        <CsBadge v-if="unverifiedCount" variant="neutral">
          {{ unverifiedCount }} chưa kiểm định
        </CsBadge>
      </div>
    </div>

    <div class="overflow-x-auto rounded-[var(--radius-card)] border border-[var(--border)]">
      <table class="w-full border-collapse text-small">
        <thead>
          <tr class="border-b border-[var(--border)] bg-[var(--bg-elevated)] text-left">
            <th class="px-3 py-2 font-medium text-[var(--text-muted)]">Sao</th>
            <th class="px-3 py-2 font-medium text-[var(--text-muted)]">Engine</th>
            <th class="px-3 py-2 font-medium text-[var(--text-muted)]">Kỳ vọng</th>
            <th class="px-3 py-2 font-medium text-[var(--text-muted)]">Kết luận</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in comparisons"
            :key="row.star"
            class="border-b border-[var(--border)] last:border-0"
            :class="row.status === 'MISMATCH' && 'bg-[var(--danger-soft)]'"
          >
            <td class="px-3 py-2 text-[var(--text)]">{{ STAR_LABELS[row.star] ?? row.star }}</td>
            <td class="px-3 py-2 text-[var(--text-muted)]">{{ row.engine ?? '—' }}</td>
            <td class="px-3 py-2">
              <span v-if="row.expected" class="text-[var(--text)]">{{ row.expected }}</span>
              <span v-else class="text-[var(--text-subtle)] italic">chưa nhập</span>
            </td>
            <td class="px-3 py-2">
              <span
                v-if="row.status === 'MATCH'"
                class="inline-flex items-center gap-1 text-[var(--success)]"
              >
                <Check class="size-3.5" aria-hidden="true" />Khớp
              </span>
              <span
                v-else-if="row.status === 'MISMATCH'"
                class="inline-flex items-center gap-1 font-medium text-[var(--danger)]"
              >
                <X class="size-3.5" aria-hidden="true" />Lệch
              </span>
              <span v-else class="inline-flex items-center gap-1 text-[var(--text-subtle)]">
                <Minus class="size-3.5" aria-hidden="true" />Chưa kiểm định
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
