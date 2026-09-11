/** `$devMode` lets templates hide development-only affordances. */
export default defineNuxtPlugin(() => ({
  provide: { devMode: import.meta.dev },
}))
