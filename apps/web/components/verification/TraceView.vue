<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'
import type { TraceStep } from '~/composables/useVerification'

const props = defineProps<{ trace: TraceStep[] }>()

/** Grouped so a reviewer opens one star, not a wall of twenty steps. */
const grouped = computed(() => {
  const groups = new Map<string, TraceStep[]>()
  for (const step of props.trace) {
    const list = groups.get(step.rule) ?? []
    list.push(step)
    groups.set(step.rule, list)
  }
  return [...groups.entries()]
})

const RULE_LABELS: Record<string, string> = {
  timezone: 'Múi giờ',
  late_zi: 'Ranh giới ngày (giờ Tý)',
  menh_placement: 'An Mệnh',
  than_placement: 'An Thân',
  cuc: 'Tính Cục',
  tu_vi_placement: 'An Tử Vi',
  major_stars: 'An 14 chính tinh',
}
</script>

<template>
  <section>
    <h3 class="mb-3 font-display text-h3 text-[var(--text)]">Vì sao engine đặt ở đó?</h3>
    <div class="divide-y divide-[var(--border)] rounded-[var(--radius-card)] border border-[var(--border)]">
      <details v-for="[rule, steps] in grouped" :key="rule" class="group">
        <summary
          class="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3 text-small focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
        >
          <span class="flex flex-wrap items-center gap-2">
            <span class="font-medium text-[var(--text)]">{{ RULE_LABELS[rule] ?? rule }}</span>
            <CsBadge
              :variant="steps[0]!.verification === 'VERIFIED' ? 'success' : 'neutral'"
            >
              {{ steps[0]!.verification }}
            </CsBadge>
            <CsBadge v-if="steps[0]!.blocked_by.length" variant="gold">
              chờ {{ steps[0]!.blocked_by.join(', ') }}
            </CsBadge>
          </span>
          <ChevronDown
            class="size-4 shrink-0 text-[var(--text-subtle)] transition-transform group-open:rotate-180"
            aria-hidden="true"
          />
        </summary>
        <ul class="space-y-3 px-4 pb-4">
          <li v-for="(step, index) in steps" :key="index" class="text-caption">
            <p class="font-medium text-[var(--text)]">{{ step.result }}</p>
            <dl class="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-[var(--text-muted)]">
              <div v-for="(value, key) in step.inputs" :key="key" class="flex gap-1">
                <dt class="text-[var(--text-subtle)]">{{ key }}:</dt>
                <dd>{{ value }}</dd>
              </div>
            </dl>
            <p class="mt-1 text-[var(--text-subtle)]">rule: {{ step.rule }} · {{ step.policy }}</p>
            <p v-if="step.note" class="mt-1 text-[var(--text-subtle)]">{{ step.note }}</p>
          </li>
        </ul>
      </details>
    </div>
  </section>
</template>
