<script setup lang="ts">
import { CHART_GRID_BRANCH_INDEXES, EARTHLY_BRANCHES } from '@cosmic/shared'
import { STAR_LABELS, type PalaceComparison } from '~/composables/useVerification'

const props = defineProps<{ palaces: PalaceComparison[] }>()

const byBranch = computed(() => new Map(props.palaces.map((p) => [p.branch, p])))

/** Same địa bàn layout as the customer-facing chart, so an expert reads it fast. */
const cells = computed(() =>
  CHART_GRID_BRANCH_INDEXES.map((index) =>
    index === null ? null : byBranch.value.get(EARTHLY_BRANCHES[index]!) ?? null,
  ),
)

const hasExpected = computed(() => props.palaces.some((p) => p.expected_stars !== null))
const label = (code: string) => STAR_LABELS[code] ?? code
</script>

<template>
  <section>
    <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
      <h3 class="font-display text-h3 text-[var(--text)]">Đối chiếu theo 12 cung</h3>
      <CsBadge v-if="!hasExpected" variant="neutral">Chưa có giá trị kỳ vọng</CsBadge>
    </div>

    <div
      class="grid grid-cols-2 gap-px overflow-hidden rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--border)] sm:grid-cols-4"
    >
      <template v-for="(palace, cell) in cells" :key="cell">
        <div
          v-if="palace"
          class="min-h-36 bg-[var(--card)] p-2.5"
          :class="palace.matches === false && 'bg-[var(--danger-soft)]'"
        >
          <div class="flex flex-wrap items-baseline gap-x-1.5 gap-y-1">
            <span class="font-display text-small font-semibold text-[var(--text)]">
              {{ palace.label }}
            </span>
            <span class="text-caption text-[var(--text-subtle)]">{{ palace.branch }}</span>
            <CsBadge v-if="palace.is_than" variant="gold">Thân</CsBadge>
          </div>
          <div class="mt-1 flex flex-wrap gap-1">
            <CsBadge v-if="palace.has_tuan" variant="outline">Tuần</CsBadge>
            <CsBadge v-if="palace.has_triet" variant="outline">Triệt</CsBadge>
          </div>

          <dl class="mt-2 space-y-1.5 text-caption">
            <div>
              <dt class="text-[var(--text-subtle)]">Engine</dt>
              <dd class="text-[var(--accent)]">
                <span v-if="palace.engine_stars.length">
                  {{ palace.engine_stars.map(label).join(', ') }}
                </span>
                <span v-else class="text-[var(--text-subtle)]">vô chính diệu</span>
              </dd>
            </div>
            <div v-if="palace.expected_stars !== null">
              <dt class="text-[var(--text-subtle)]">Kỳ vọng</dt>
              <dd class="text-[var(--text)]">
                <span v-if="palace.expected_stars.length">
                  {{ palace.expected_stars.map(label).join(', ') }}
                </span>
                <span v-else class="text-[var(--text-subtle)]">vô chính diệu</span>
              </dd>
            </div>
          </dl>

          <p
            v-if="palace.matches !== null"
            class="mt-2 text-caption font-medium"
            :class="palace.matches ? 'text-[var(--success)]' : 'text-[var(--danger)]'"
          >
            {{ palace.matches ? '✓ Khớp' : '✗ Lệch' }}
          </p>
        </div>
        <div v-else class="hidden bg-[var(--bg-elevated)] sm:block" />
      </template>
    </div>
  </section>
</template>
