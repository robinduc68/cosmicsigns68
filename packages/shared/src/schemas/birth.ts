import { z } from 'zod'

/**
 * Birth input contract. The same rules run in the browser (instant feedback)
 * and again on the server (authority) — this file describes the browser half
 * and must stay in step with `apps/api/app/schemas/chart.py`.
 */

export const genderSchema = z.enum(['MALE', 'FEMALE'])
export const calendarTypeSchema = z.enum(['SOLAR', 'LUNAR'])

const currentYear = new Date().getFullYear()

export const birthFormSchema = z
  .object({
    subject_name: z
      .string()
      .trim()
      .min(2, 'Tên cần ít nhất 2 ký tự')
      .max(120, 'Tên quá dài (tối đa 120 ký tự)'),
    gender: genderSchema,
    relationship_label: z.string().trim().max(60, 'Nhãn quá dài').optional().nullable(),

    calendar_type: calendarTypeSchema,
    birth_day: z.number().int().min(1, 'Ngày không hợp lệ').max(31, 'Ngày không hợp lệ'),
    birth_month: z.number().int().min(1, 'Tháng không hợp lệ').max(12, 'Tháng không hợp lệ'),
    birth_year: z
      .number()
      .int()
      .min(1900, 'Năm sinh cần từ 1900 trở đi')
      .max(currentYear, `Năm sinh không thể sau ${currentYear}`),
    birth_hour: z.number().int().min(0).max(23),
    birth_minute: z.number().int().min(0).max(59),
    is_leap_month: z.boolean(),

    birth_place: z.string().trim().max(160, 'Nơi sinh quá dài').optional().nullable(),
    timezone_name: z.string().min(1).max(64),
    tz_offset: z.number().min(-12).max(14),
    note: z.string().trim().max(500, 'Ghi chú tối đa 500 ký tự').optional().nullable(),
  })
  .superRefine((value, ctx) => {
    if (value.is_leap_month && value.calendar_type !== 'LUNAR') {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['is_leap_month'],
        message: 'Chỉ ngày âm lịch mới có tháng nhuận',
      })
    }

    if (value.calendar_type === 'LUNAR') {
      if (value.birth_day > 30) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['birth_day'],
          message: 'Tháng âm lịch chỉ có tối đa 30 ngày',
        })
      }
      return
    }

    const date = new Date(value.birth_year, value.birth_month - 1, value.birth_day)
    const isRealDate =
      date.getFullYear() === value.birth_year &&
      date.getMonth() === value.birth_month - 1 &&
      date.getDate() === value.birth_day
    if (!isRealDate) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['birth_day'],
        message: 'Ngày này không có trong tháng bạn chọn',
      })
      return
    }
    if (date.getTime() > Date.now()) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['birth_year'],
        message: 'Ngày sinh không thể ở tương lai',
      })
    }
  })

export type BirthFormValues = z.infer<typeof birthFormSchema>

export const emptyBirthForm = (): BirthFormValues => ({
  subject_name: '',
  gender: 'MALE',
  relationship_label: null,
  calendar_type: 'SOLAR',
  birth_day: 1,
  birth_month: 1,
  birth_year: 1995,
  birth_hour: 12,
  birth_minute: 0,
  is_leap_month: false,
  birth_place: null,
  timezone_name: 'Asia/Ho_Chi_Minh',
  tz_offset: 7,
  note: null,
})
