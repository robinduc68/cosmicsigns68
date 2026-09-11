<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{ error: NuxtError }>()

const isNotFound = computed(() => props.error.statusCode === 404)

useHead({ title: isNotFound.value ? 'Không tìm thấy trang' : 'Có lỗi xảy ra' })
</script>

<template>
  <div class="flex min-h-dvh flex-col items-center justify-center px-5 text-center">
    <CsLogo class="mb-10 text-[var(--accent)]" />
    <p class="font-display text-h1 text-[var(--text)]">
      {{ isNotFound ? 'Không tìm thấy trang này' : 'Có lỗi xảy ra' }}
    </p>
    <p class="mt-3 max-w-md text-body text-[var(--text-muted)]">
      {{
        isNotFound
          ? 'Đường dẫn bạn mở không tồn tại hoặc đã được đổi. Bạn quay về trang chủ nhé.'
          : 'Mình chưa xử lý được yêu cầu này. Bạn thử lại sau vài giây giúp mình.'
      }}
    </p>
    <div class="mt-8 flex flex-wrap justify-center gap-3">
      <CsButton to="/">Về trang chủ</CsButton>
      <CsButton v-if="!isNotFound" variant="secondary" @click="clearError({ redirect: '/' })">
        Thử lại
      </CsButton>
    </div>
  </div>
</template>
