<script setup lang="ts">
import { BadgeCheck, Bot, Lock, ScanSearch, Smartphone } from 'lucide-vue-next'

/** Bám sát mục 1.2 của business.md — đây là những điểm sản phẩm thật sự khác. */
const REASONS = [
  {
    icon: BadgeCheck,
    title: 'Cùng input luôn ra cùng lá số',
    body: 'Engine tất định, không random, có bộ test đối chiếu ngày Tết chính thống 2000–2026 và các tháng nhuận.',
  },
  {
    icon: Bot,
    title: 'AI không được tự bịa lá số',
    body: 'Mọi luận điểm phải trỏ về được một dữ kiện có thật trong chart JSON. Không có dữ kiện thì không viết.',
  },
  {
    icon: ScanSearch,
    title: 'Luận giải có cơ chế',
    body: 'Dấu hiệu → cơ chế → biểu hiện thực tế. Không nước đôi kiểu "có thể thế này mà cũng có thể thế kia".',
  },
  {
    icon: Smartphone,
    title: 'Đọc được trên điện thoại',
    body: 'Giao diện tối giản, không quảng cáo chen ngang, có cả nền sáng và nền tối.',
  },
  {
    icon: Lock,
    title: 'Dữ liệu là của bạn',
    body: 'Ngày sinh là thông tin cá nhân. Lá số có địa chỉ không đoán được và bạn xoá được thật sự.',
  },
]
</script>

<template>
  <section class="py-20 sm:py-24">
    <CsContainer>
      <CsSectionHeading
        eyebrow="Vì sao là Cosmic Signs"
        title="Năm điều chúng mình không thỏa hiệp"
      />
      <div class="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <CsCard v-for="reason in REASONS" :key="reason.title" class="h-full">
          <component :is="reason.icon" class="size-5 text-[var(--accent)]" aria-hidden="true" />
          <p class="mt-4 font-display text-h3 text-[var(--text)]">{{ reason.title }}</p>
          <p class="mt-2 text-small text-[var(--text-muted)]">{{ reason.body }}</p>
        </CsCard>
      </div>
    </CsContainer>
  </section>
</template>
