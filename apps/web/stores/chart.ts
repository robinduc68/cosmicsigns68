import { defineStore } from 'pinia'
import {
  ApiError,
  birthFormSchema,
  emptyBirthForm,
  type BirthFormValues,
  type ChartDetail,
} from '@cosmic/shared'

/** Labels of the wizard steps, in order. The store owns the step count so the
 *  page never has to repeat it. */
export const WIZARD_STEPS = ['Thông tin', 'Ngày giờ sinh', 'Xác nhận'] as const

const LAST_STEP = WIZARD_STEPS.length - 1

/** Fields collected by each wizard step, used to scope validation. */
const STEP_FIELDS: Record<number, (keyof BirthFormValues)[]> = {
  0: ['subject_name', 'gender', 'relationship_label'],
  1: [
    'calendar_type',
    'birth_day',
    'birth_month',
    'birth_year',
    'birth_hour',
    'birth_minute',
    'is_leap_month',
    'birth_place',
  ],
  2: ['note'],
}

export const useChartStore = defineStore('chart', () => {
  const form = ref<BirthFormValues>(emptyBirthForm())
  const step = ref(0)
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

  watch(form, () => {
    idempotencyKey.value = newKey()
  }, { deep: true })

  /** Validates the whole form, then keeps only the messages for `fields`. */
  function validateFields(fields: (keyof BirthFormValues)[]): boolean {
    const result = birthFormSchema.safeParse(form.value)
    const scoped: Partial<Record<keyof BirthFormValues, string>> = {}

    if (!result.success) {
      for (const issue of result.error.issues) {
        const field = issue.path[0] as keyof BirthFormValues | undefined
        if (field && fields.includes(field) && !scoped[field]) {
          scoped[field] = issue.message
        }
      }
    }
    errors.value = scoped
    return Object.keys(scoped).length === 0
  }

  function validateStep(index: number): boolean {
    return validateFields(STEP_FIELDS[index] ?? [])
  }

  function next(): boolean {
    if (!validateStep(step.value)) return false
    step.value = Math.min(step.value + 1, LAST_STEP)
    return true
  }

  const isLastStep = computed(() => step.value === LAST_STEP)

  function back(): void {
    errors.value = {}
    step.value = Math.max(step.value - 1, 0)
  }

  function goTo(index: number): void {
    // Jumping ahead is only allowed through `next`, which validates.
    if (index < step.value) {
      errors.value = {}
      step.value = index
    }
  }

  function reset(): void {
    form.value = emptyBirthForm()
    step.value = 0
    errors.value = {}
    submitError.value = null
  }

  async function submit(): Promise<ChartDetail | null> {
    const parsed = birthFormSchema.safeParse(form.value)
    if (!parsed.success) {
      // Something an earlier step should have caught — send the user back to it.
      const field = parsed.error.issues[0]?.path[0] as keyof BirthFormValues | undefined
      const owningStep = Object.entries(STEP_FIELDS).find(
        ([, fields]) => field && fields.includes(field),
      )
      step.value = owningStep ? Number(owningStep[0]) : 0
      validateStep(step.value)
      return null
    }

    submitting.value = true
    submitError.value = null
    try {
      const { request } = useApi()
      return await request<ChartDetail>('/api/v1/charts', {
        method: 'POST',
        body: parsed.data,
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

  return {
    form,
    step,
    isLastStep,
    errors,
    submitting,
    submitError,
    validateStep,
    next,
    back,
    goTo,
    reset,
    submit,
  }
})
