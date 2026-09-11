/**
 * Guards development-only routes such as the design system showcase.
 * They must never be reachable from a production build.
 */
export default defineNuxtRouteMiddleware(() => {
  if (!import.meta.dev) {
    throw createError({ statusCode: 404, statusMessage: 'Not Found', fatal: true })
  }
})
