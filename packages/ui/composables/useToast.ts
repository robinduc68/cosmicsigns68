import { ref } from 'vue'

export type ToastVariant = 'default' | 'success' | 'error'

export interface Toast {
  id: number
  title: string
  description?: string
  variant: ToastVariant
  duration: number
}

const toasts = ref<Toast[]>([])
let nextId = 0

/**
 * Minimal toast queue. Deliberately not a store: toasts are transient UI state,
 * never server state, and any component may raise one.
 */
export function useToast() {
  function dismiss(id: number): void {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  function push(
    title: string,
    options: { description?: string; variant?: ToastVariant; duration?: number } = {},
  ): number {
    const id = ++nextId
    const toast: Toast = {
      id,
      title,
      description: options.description,
      variant: options.variant ?? 'default',
      duration: options.duration ?? 4000,
    }
    // Keep at most three on screen — beyond that they stop being readable.
    toasts.value = [...toasts.value.slice(-2), toast]
    if (import.meta.client && toast.duration > 0) {
      window.setTimeout(() => dismiss(id), toast.duration)
    }
    return id
  }

  return {
    toasts,
    dismiss,
    toast: push,
    success: (title: string, description?: string) => push(title, { description, variant: 'success' }),
    error: (title: string, description?: string) => push(title, { description, variant: 'error' }),
  }
}
