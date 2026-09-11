<script setup lang="ts">
import { ArrowRight } from 'lucide-vue-next'
</script>

<template>
  <section class="pb-24">
    <CsContainer>
      <div
        class="relative overflow-hidden rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--card)] px-6 py-16 text-center sm:px-12"
      >
        <div
          class="pointer-events-none absolute -top-24 left-1/2 h-64 w-[32rem] -translate-x-1/2 rounded-full opacity-20 blur-3xl"
          aria-hidden="true"
          style="background: radial-gradient(closest-side, var(--color-brand-500), transparent)"
        />
        <h2 class="text-balance-heading font-display text-h2 text-[var(--text)] sm:text-h1">
          Mất hai phút để biết lá số mình trông như thế nào
        </h2>
        <p class="mx-auto mt-4 max-w-xl text-body text-[var(--text-muted)]">
          Không cần đăng ký, không cần thẻ. Nhập ngày giờ sinh là xem được ngay.
        </p>
        <CsButton to="/lap-la-so" size="lg" class="mt-8">
          Lập lá số miễn phí
          <template #trailing><ArrowRight class="size-4" aria-hidden="true" /></template>
        </CsButton>
      </div>
    </CsContainer>
  </section>
</template>
