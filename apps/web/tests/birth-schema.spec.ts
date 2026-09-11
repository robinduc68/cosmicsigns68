import { describe, expect, it } from 'vitest'
import { birthFormSchema, emptyBirthForm } from '@cosmic/shared'

/** The browser half of the birth-input contract; the API validates again. */
describe('birthFormSchema', () => {
  const valid = { ...emptyBirthForm(), subject_name: 'Nguyễn Văn A', birth_day: 10, birth_month: 9 }

  it('accepts a complete solar birth', () => {
    expect(birthFormSchema.safeParse(valid).success).toBe(true)
  })

  it('rejects a day that does not exist in the chosen month', () => {
    const result = birthFormSchema.safeParse({ ...valid, birth_day: 31, birth_month: 2 })
    expect(result.success).toBe(false)
    expect(result.error?.issues[0]?.message).toContain('không có trong tháng')
  })

  it('rejects a birth date in the future', () => {
    const result = birthFormSchema.safeParse({ ...valid, birth_year: new Date().getFullYear() + 1 })
    expect(result.success).toBe(false)
  })

  it('rejects a leap month on the solar calendar', () => {
    const result = birthFormSchema.safeParse({ ...valid, is_leap_month: true })
    expect(result.success).toBe(false)
    expect(result.error?.issues[0]?.message).toContain('âm lịch')
  })

  it('allows 30 days but not 31 on the lunar calendar', () => {
    const lunar = { ...valid, calendar_type: 'LUNAR' as const }
    expect(birthFormSchema.safeParse({ ...lunar, birth_day: 30 }).success).toBe(true)
    expect(birthFormSchema.safeParse({ ...lunar, birth_day: 31 }).success).toBe(false)
  })

  it('requires a name of at least two characters', () => {
    expect(birthFormSchema.safeParse({ ...valid, subject_name: 'A' }).success).toBe(false)
  })
})
