<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'
import { DISCLAIMER_TEXT } from '@cosmic/shared'

const FOOTER_LINKS = [
  { to: '/', label: 'Trang chủ' },
  { to: '/lap-la-so', label: 'Lập lá số' },
]

const colorMode = useColorMode()
const year = new Date().getFullYear()

function toggleTheme() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <div class="flex min-h-dvh flex-col bg-[var(--bg)]">
    <header
      class="sticky top-0 z-40 border-b border-[var(--border)] bg-[var(--bg)]/85 backdrop-blur-md"
    >
      <CsContainer class="flex h-16 items-center justify-between gap-4">
        <NuxtLink
          to="/"
          class="rounded text-[var(--text)] transition-colors hover:text-[var(--accent)]"
        >
          <CsLogo />
        </NuxtLink>

        <div class="flex items-center gap-1.5">
          <CsIconButton :label="colorMode.value === 'dark' ? 'Chuyển sang giao diện sáng' : 'Chuyển sang giao diện tối'" @click="toggleTheme">
            <ClientOnly>
              <Moon v-if="colorMode.value === 'dark'" class="size-4" aria-hidden="true" />
              <Sun v-else class="size-4" aria-hidden="true" />
              <template #fallback><span class="size-4" /></template>
            </ClientOnly>
          </CsIconButton>
          <CsButton to="/lap-la-so" size="sm">Lập lá số</CsButton>
        </div>
      </CsContainer>
    </header>

    <main class="flex-1"><slot /></main>

    <footer class="mt-24 border-t border-[var(--border)] py-10">
      <CsContainer class="flex flex-col gap-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <CsLogo class="text-[var(--text-muted)]" />
          <!-- py-1 giữ vùng chạm >= 24px theo WCAG 2.2 AA; chữ small không thôi
               chỉ cao 22px, hụt trên điện thoại. -->
          <nav class="flex flex-wrap gap-x-5 gap-y-1 text-small text-[var(--text-muted)]">
            <NuxtLink
              v-for="link in FOOTER_LINKS"
              :key="link.to"
              :to="link.to"
              class="rounded py-1 transition-colors hover:text-[var(--text)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
            >
              {{ link.label }}
            </NuxtLink>
          </nav>
        </div>
        <p class="max-w-2xl text-caption text-[var(--text-subtle)]">{{ DISCLAIMER_TEXT }}</p>
        <p class="text-caption text-[var(--text-subtle)]">© {{ year }} Cosmic Signs</p>
      </CsContainer>
    </footer>
  </div>
</template>
