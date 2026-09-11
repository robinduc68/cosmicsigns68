<script setup lang="ts">
const config = useRuntimeConfig()

useHead({ title: 'Hiểu mình rõ hơn qua lá số Tử Vi' })

const description =
  'Cosmic Signs lập lá số Tử Vi bằng engine tính toán riêng, sau đó diễn giải theo từng ' +
  'khía cạnh: tính cách, sự nghiệp, tài chính, tình duyên và vận hạn.'

useSeoMeta({
  description,
  ogTitle: 'Cosmic Signs — Hiểu mình rõ hơn qua lá số Tử Vi',
  ogDescription: description,
  ogType: 'website',
  ogUrl: config.public.siteUrl,
  ogLocale: 'vi_VN',
  ogSiteName: 'Cosmic Signs',
  twitterCard: 'summary_large_image',
  twitterTitle: 'Cosmic Signs — Hiểu mình rõ hơn qua lá số Tử Vi',
  twitterDescription: description,
})

const { request } = useApi()
const { data: health } = await useAsyncData('health', () =>
  request<{ status: string; env: string }>('/health').catch(() => ({
    status: 'unreachable',
    env: '',
  })),
)
const backendUp = computed(() => health.value?.status === 'ok')
</script>

<template>
  <div>
    <HomeHero />
    <HomePerspectives />
    <HomeChartPreview />
    <HomeHowItWorks />
    <HomeWhyUs />
    <HomePricing />
    <HomeFaq />
    <HomeFinalCta />

    <!-- Chỉ hiện khi chạy dev: xác nhận web ↔ api ↔ database đã thông nhau. -->
    <CsContainer v-if="$devMode" class="pb-20">
      <CsCard>
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p class="text-small font-medium text-[var(--text)]">Tình trạng hệ thống (dev)</p>
            <p class="mt-1 text-caption text-[var(--text-subtle)]">
              Backend:
              <span :class="backendUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'">
                {{ backendUp ? `đang chạy (${health?.env})` : 'chưa kết nối được' }}
              </span>
            </p>
          </div>
          <CsButton to="/dev/design-system" variant="secondary" size="sm">
            Xem design system
          </CsButton>
        </div>
      </CsCard>
    </CsContainer>
  </div>
</template>
