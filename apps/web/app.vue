<script setup lang="ts">
const config = useRuntimeConfig()

useHead({
  titleTemplate: (title?: string) => (title ? `${title} · Cosmic Signs` : 'Cosmic Signs'),
  link: [{ rel: 'canonical', href: config.public.siteUrl }],
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <CsToaster />
</template>
