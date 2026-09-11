<script setup lang="ts">
import { INSIGHT_CATEGORIES } from '@cosmic/shared'
</script>

<template>
  <section id="cach-luan-giai" class="scroll-mt-20 py-20 sm:py-24">
    <CsContainer>
      <CsSectionHeading
        eyebrow="Một lá số – nhiều góc nhìn"
        title="Tám khía cạnh, đọc riêng từng phần"
        description="Mỗi phần đều bám vào cung, sao và tam phương tứ chính tương ứng trong lá số của bạn."
      />
      <div class="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <CsCard v-for="category in INSIGHT_CATEGORIES" :key="category.key" interactive>
          <p class="font-display text-h3 text-[var(--text)]">{{ category.title }}</p>
          <p class="mt-2 text-small text-[var(--text-muted)]">{{ category.description }}</p>
        </CsCard>
      </div>
    </CsContainer>
  </section>
</template>
