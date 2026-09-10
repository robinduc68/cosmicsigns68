import { createResolver } from '@nuxt/kit'

const { resolve } = createResolver(import.meta.url)

/**
 * @cosmic/ui — the Cosmic Signs design system, shipped as a Nuxt layer.
 *
 * Consuming apps only need `extends: ['@cosmic/ui']`; every component is then
 * auto-imported with the `Cs` prefix (CsButton, CsCard, …).
 */
export default defineNuxtConfig({
  components: [{ path: resolve('./components'), prefix: 'Cs', pathPrefix: false }],
  imports: {
    dirs: [resolve('./composables')],
  },
  css: [resolve('./assets/css/tokens.css')],
})
