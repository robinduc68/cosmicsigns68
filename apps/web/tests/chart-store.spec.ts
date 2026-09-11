import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useChartStore } from '../stores/chart'

/** The one-page form's rules live in the store, so they are tested here. */
describe('useChartStore', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('requires a name before anything else', () => {
    const store = useChartStore()
    expect(store.validate()).toBe(false)
    expect(store.errors.subject_name).toBeTruthy()
  })

  it('accepts a complete birth and clears errors', () => {
    const store = useChartStore()
    store.validate()
    store.form.subject_name = 'Nguyễn Văn A'
    expect(store.validate()).toBe(true)
    expect(store.errors).toEqual({})
  })

  it('rejects a day the chosen month does not have', () => {
    const store = useChartStore()
    store.form.subject_name = 'Nguyễn Văn A'
    store.form.birth_month = 2
    store.form.birth_day = 31
    expect(store.validate()).toBe(false)
    expect(store.errors.birth_day).toContain('không có trong tháng')
  })

  it('rejects a birth in the future', () => {
    const store = useChartStore()
    store.form.subject_name = 'Nguyễn Văn A'
    store.form.birth_year = new Date().getFullYear() + 1
    expect(store.validate()).toBe(false)
  })

  it('rejects a leap month on the solar calendar', () => {
    const store = useChartStore()
    store.form.subject_name = 'Nguyễn Văn A'
    store.form.is_leap_month = true
    expect(store.validate()).toBe(false)
    expect(store.errors.is_leap_month).toBeTruthy()
  })

  it('does not reach the API when the form is invalid', async () => {
    const store = useChartStore()
    expect(await store.submit()).toBeNull()
    expect(store.submitting).toBe(false)
    expect(store.submitError).toBeNull()
  })

  it('resets back to a blank form', () => {
    const store = useChartStore()
    store.form.subject_name = 'Nguyễn Văn A'
    store.validate()
    store.reset()
    expect(store.form.subject_name).toBe('')
    expect(store.errors).toEqual({})
  })
})
