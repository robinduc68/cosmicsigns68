import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',
  devtools: { enabled: true },

  // The design system ships as a layer: components arrive auto-imported as Cs*.
  extends: ['@cosmic/ui'],

  modules: ['@nuxt/fonts', '@nuxtjs/color-mode', '@pinia/nuxt', '@vueuse/nuxt'],

  vite: {
    plugins: [tailwindcss()],
  },

  colorMode: {
    preference: 'dark',
    fallback: 'dark',
    classSuffix: '',
  },

  fonts: {
    families: [
      { name: 'Be Vietnam Pro', provider: 'google', weights: [400, 500, 600] },
      { name: 'Manrope', provider: 'google', weights: [500, 600, 700] },
    ],
  },

  runtimeConfig: {
    // Server-side calls inside Docker go straight to the api container.
    apiBaseInternal: process.env.NUXT_API_BASE_INTERNAL || '',
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8100',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3100',
    },
  },

  app: {
    head: {
      htmlAttrs: { lang: 'vi' },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },

  typescript: { strict: true, typeCheck: false },
})
