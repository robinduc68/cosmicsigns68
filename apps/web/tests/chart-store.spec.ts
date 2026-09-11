import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useChartStore } from '../stores/chart'

/**
 * The wizard's rules live in the store, not the step components — this is where
 * "you cannot skip ahead past an invalid step" is actually enforced.
 */
describe('useChartStore', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('blocks the first step until the name is valid', () => {
    const store = useChartStore()
    expect(store.next()).toBe(false)
    expect(store.step).toBe(0)
    expect(store.errors.subject_name).toBeTruthy()

    store.form.subject_name = 'Nguyễn Văn A'
    expect(store.next()).toBe(true)
    expect(store.step).toBe(1)
    expect(store.errors.subject_name).toBeUndefined()
  })

  it('only reports errors belonging to the current step', () => {
    const store = useChartStore()
    store.form.subject_name = 'Nguyễn Văn A'
    store.next()

    // A future birth year is a step-1 problem and must surface there.
    store.form.birth_year = new Date().getFullYear()
    store.form.birth_month = 12
    store.form.birth_day = 31
    expect(store.next()).toBe(false)
    expect(store.step).toBe(1)
    expect(store.errors.birth_year).toBeTruthy()
    expect(store.errors.subject_name).toBeUndefined()
  })

  it('rejects a day the chosen month does not have', () => {
    const store = useChartStore()
    store.form.subject_name = 'Nguyễn Văn A'
    store.next()
    store.form.birth_month = 2
    store.form.birth_day = 31
    expect(store.next()).toBe(false)
    expect(store.errors.birth_day).toContain('không có trong tháng')
  })

  it('lets the user jump back but never forward', () => {
    const store = useChartStore()
    store.form.subject_name = 'Nguyễn Văn A'
    store.next()
    expect(store.step).toBe(1)

    store.goTo(0)
    expect(store.step).toBe(0)

    // Skipping ahead without validating would let an invalid chart be submitted.
    store.goTo(2)
    expect(store.step).toBe(0)
  })

  it('sends the user back to the step that owns a stale error on submit', async () => {
    const store = useChartStore()
    store.form.subject_name = 'Nguyễn Văn A'
    store.next()
    store.next()
    expect(store.step).toBe(2)

    store.form.subject_name = 'A'
    expect(await store.submit()).toBeNull()
    expect(store.step).toBe(0)
    expect(store.errors.subject_name).toBeTruthy()
  })

  it('resets back to a blank form', () => {
    const store = useChartStore()
    store.form.subject_name = 'Nguyễn Văn A'
    store.next()
    store.reset()
    expect(store.step).toBe(0)
    expect(store.form.subject_name).toBe('')
  })
})
