import { defineStore } from 'pinia'
import {
  ApiError,
  birthFormSchema,
  emptyBirthForm,
  type BirthFormValues,
  type ChartDetail,
} from '@cosmic/shared'

/**
 * State of the one-page "Lập lá số" form. Validation lives here rather than in
 * the page so it can be tested without rendering anything.
 */
export const useChartStore = defineStore('chart', () => {
  const form = ref<BirthFormValues>(emptyBirthForm())
  const errors = ref<Partial<Record<keyof BirthFormValues, string>>>({})
  const submitting = ref(false)
  const submitError = ref<string | null>(null)

  /**
   * Regenerated whenever the payload changes so a retry of the *same* birth
   * cannot create a duplicate chart, while an edited one legitimately can.
   */
  const idempotencyKey = ref(newKey())

  function newKey(): string {
    if (import.meta.client && 'randomUUID' in crypto) return crypto.randomUUID()
    return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`
  }

  watch(
    form,
    () => {
      idempotencyKey.value = newKey()
    },
    { deep: true },
  )

  /** Validates the whole form and keeps the first message for each field. */
  function validate(): boolean {
    const result = birthFormSchema.safeParse(form.value)
    const next: Partial<Record<keyof BirthFormValues, string>> = {}
    if (!result.success) {
      for (const issue of result.error.issues) {
        const field = issue.path[0] as keyof BirthFormValues | undefined
        if (field && !next[field]) next[field] = issue.message
      }
    }
    errors.value = next
    return result.success
  }

  function reset(): void {
    form.value = emptyBirthForm()
    errors.value = {}
    submitError.value = null
  }

  async function submit(): Promise<ChartDetail | null> {
    if (!validate()) return null

    submitting.value = true
    submitError.value = null
    try {
      const { request } = useApi()
      return await request<ChartDetail>('/api/v1/charts', {
        method: 'POST',
        body: birthFormSchema.parse(form.value),
        headers: { 'Idempotency-Key': idempotencyKey.value },
      })
    } catch (caught: unknown) {
      if (caught instanceof ApiError) {
        const fieldErrors = caught.fieldErrors
        if (Object.keys(fieldErrors).length > 0) {
          errors.value = fieldErrors as Partial<Record<keyof BirthFormValues, string>>
        }
        submitError.value = caught.message
      } else {
        submitError.value = 'Không lập được lá số. Bạn thử lại giúp mình nhé.'
      }
      return null
    } finally {
      submitting.value = false
    }
  }

  return { form, errors, submitting, submitError, validate, reset, submit }
})
