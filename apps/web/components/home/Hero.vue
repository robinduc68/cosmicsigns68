<script setup lang="ts">
import { ArrowRight } from 'lucide-vue-next'
</script>

<template>
  <section class="relative overflow-hidden">
    <!-- Nền sao: thuần CSS, không thư viện, không ảnh hưởng tới LCP. -->
    <div
      class="pointer-events-none absolute inset-0 -z-10 opacity-70"
      aria-hidden="true"
      style="
        background:
          radial-gradient(1px 1px at 12% 24%, var(--star-field) 50%, transparent 50%),
          radial-gradient(1px 1px at 68% 16%, var(--star-field) 50%, transparent 50%),
          radial-gradient(1.5px 1.5px at 84% 62%, var(--star-field) 50%, transparent 50%),
          radial-gradient(1px 1px at 32% 72%, var(--star-field) 50%, transparent 50%),
          radial-gradient(1px 1px at 52% 42%, var(--star-field) 50%, transparent 50%);
      "
    />
    <div
      class="pointer-events-none absolute -top-40 left-1/2 -z-10 h-96 w-[42rem] -translate-x-1/2 rounded-full opacity-25 blur-3xl"
      aria-hidden="true"
      style="background: radial-gradient(closest-side, var(--color-brand-500), transparent)"
    />

    <CsContainer class="py-20 sm:py-28">
      <div class="max-w-2xl">
        <CsBadge variant="accent" size="md">Tử Vi Đẩu Số</CsBadge>
        <h1
          class="text-balance-heading mt-6 font-display text-h1 text-[var(--text)] sm:text-display"
        >
          Lá số không quyết định cuộc đời bạn.
          <span class="text-[var(--text-muted)]">
            Nhưng nó có thể giúp bạn hiểu mình rõ hơn.
          </span>
        </h1>
        <p class="mt-6 max-w-xl text-body text-[var(--text-muted)]">
          Cosmic Signs tính lá số bằng engine riêng, tất định và có kiểm thử. Phần diễn giải đi
          theo đúng những gì đã tính được — không phán chung chung.
        </p>
        <div class="mt-9 flex flex-wrap gap-3">
          <CsButton to="/lap-la-so" size="lg">
            Lập lá số miễn phí
            <template #trailing><ArrowRight class="size-4" aria-hidden="true" /></template>
          </CsButton>
          <CsButton to="/#cach-luan-giai" size="lg" variant="secondary">
            Khám phá cách Cosmic Signs luận giải
          </CsButton>
        </div>
        <p class="mt-5 text-caption text-[var(--text-subtle)]">
          Không cần tài khoản. Không quảng cáo. Lá số của bạn xoá được bất cứ lúc nào.
        </p>
      </div>
    </CsContainer>
  </section>
</template>
