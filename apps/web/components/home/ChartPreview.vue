<script setup lang="ts">
import {
  CHART_GRID_BRANCH_INDEXES,
  EARTHLY_BRANCHES,
  PALACE_LABELS,
  PALACE_ORDER,
} from '@cosmic/shared'

/**
 * Khung địa bàn — phần *cố định* của mọi lá số: 12 địa chi luôn nằm đúng các ô
 * này. Vị trí Mệnh, Thân và các sao thì phụ thuộc ngày giờ sinh nên không hiển
 * thị ở đây; bịa ra một lá số mẫu là vi phạm nguyên tắc "không fake dữ liệu".
 */
const gridBranches = CHART_GRID_BRANCH_INDEXES.map((index) =>
  index === null ? null : EARTHLY_BRANCHES[index],
)
</script>

<template>
  <section class="py-20 sm:py-24">
    <CsContainer>
      <div class="grid items-center gap-12 lg:grid-cols-2">
        <div>
          <CsSectionHeading
            eyebrow="Lá số của bạn"
            title="Đầy đủ 12 cung, ngay từ bản miễn phí"
            description="Bạn xem được toàn bộ khung lá số: địa chi, thiên can, nạp âm, Mệnh, Thân, Cục, Tuần và Triệt. Phần bị khoá chỉ là bài luận giải chuyên sâu."
          />
          <ul class="mt-8 flex flex-wrap gap-2">
            <li
              v-for="palace in PALACE_ORDER"
              :key="palace"
              class="rounded-full border border-[var(--border)] px-3 py-1 text-caption text-[var(--text-muted)]"
            >
              {{ PALACE_LABELS[palace] }}
            </li>
          </ul>
        </div>

        <CsCard :padded="false" class="overflow-hidden">
          <div class="grid grid-cols-4 gap-px bg-[var(--border)]">
            <div
              v-for="(branch, index) in gridBranches"
              :key="index"
              class="aspect-square bg-[var(--card)] p-2 sm:p-3"
              :class="!branch && 'bg-[var(--bg-elevated)]'"
            >
              <template v-if="branch">
                <span class="font-display text-small text-[var(--text)]">{{ branch }}</span>
                <div class="mt-2 space-y-1.5" aria-hidden="true">
                  <CsSkeleton class="h-1.5 w-3/4" rounded="full" />
                  <CsSkeleton class="h-1.5 w-1/2" rounded="full" />
                </div>
              </template>
            </div>
          </div>
          <p
            class="border-t border-[var(--border)] bg-[var(--card)] px-4 py-3 text-caption text-[var(--text-subtle)]"
          >
            Khung địa bàn 12 địa chi. Mệnh, Thân và các sao được an theo đúng ngày giờ sinh của
            bạn, nên chỉ xuất hiện trên lá số thật.
          </p>
        </CsCard>
      </div>
    </CsContainer>
  </section>
</template>
