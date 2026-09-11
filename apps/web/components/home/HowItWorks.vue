<script setup lang="ts">
import { Calculator, FileText, PencilLine, Sparkles } from 'lucide-vue-next'

const STEPS = [
  {
    icon: PencilLine,
    title: 'Bạn nhập ngày giờ sinh',
    body: 'Dương lịch hoặc âm lịch đều được, kể cả tháng nhuận. Chỉ cần bốn thông tin: tên, giới tính, ngày sinh và giờ sinh.',
  },
  {
    icon: Calculator,
    title: 'Engine tính lá số',
    body: 'Đổi lịch theo thuật toán thiên văn, lập tứ trụ, an Mệnh – Thân, tính Cục rồi dựng đủ 12 cung. Không có AI ở bước này.',
  },
  {
    icon: FileText,
    title: 'Rule engine rút ra dấu hiệu',
    body: 'Từ chart JSON, hệ luật rút ra các dấu hiệu kèm dẫn chứng — cung nào, sao nào, quan hệ nào.',
  },
  {
    icon: Sparkles,
    title: 'AI viết lời, không tính toán',
    body: 'AI chỉ nhận dấu hiệu đã có và diễn đạt thành lời. Nó không được tự suy ra vị trí sao hay Mệnh, Cục.',
  },
]
</script>

<template>
  <section id="cach-hoat-dong" class="scroll-mt-20 border-y border-[var(--border)] py-20 sm:py-24">
    <CsContainer>
      <CsSectionHeading
        eyebrow="Cách hoạt động"
        title="Tính toán và diễn giải là hai việc tách rời"
        description="Phần lớn ứng dụng tử vi dùng AI để làm cả hai, nên sai lá số ngay từ đầu. Ở đây pipeline đi một chiều và mỗi lớp chỉ làm đúng việc của nó."
      />
      <ol class="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <li v-for="(step, index) in STEPS" :key="step.title">
          <CsCard class="h-full">
            <div class="flex items-center gap-3">
              <span
                class="inline-flex size-9 shrink-0 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]"
              >
                <component :is="step.icon" class="size-4" aria-hidden="true" />
              </span>
              <span class="text-caption font-medium text-[var(--text-subtle)]">
                Bước {{ index + 1 }}
              </span>
            </div>
            <p class="mt-4 font-display text-h3 text-[var(--text)]">{{ step.title }}</p>
            <p class="mt-2 text-small text-[var(--text-muted)]">{{ step.body }}</p>
          </CsCard>
        </li>
      </ol>
    </CsContainer>
  </section>
</template>
