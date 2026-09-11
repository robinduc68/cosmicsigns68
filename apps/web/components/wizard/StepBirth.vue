<script setup lang="ts">
import { BIRTH_HOUR_OPTIONS, type BirthFormValues } from '@cosmic/shared'

const form = defineModel<BirthFormValues>({ required: true })
defineProps<{ errors: Partial<Record<keyof BirthFormValues, string>> }>()

const CALENDAR_OPTIONS = [
  { value: 'SOLAR', label: 'Dương lịch', description: 'Ngày trên giấy khai sinh' },
  { value: 'LUNAR', label: 'Âm lịch', description: 'Ngày ta, có thể rơi vào tháng nhuận' },
]

const currentYear = new Date().getFullYear()
const range = (from: number, to: number) =>
  Array.from({ length: to - from + 1 }, (_, i) => from + i)

const isLunar = computed(() => form.value.calendar_type === 'LUNAR')

const dayOptions = computed(() =>
  range(1, isLunar.value ? 30 : 31).map((d) => ({ value: d, label: String(d) })),
)
const monthOptions = range(1, 12).map((m) => ({ value: m, label: `Tháng ${m}` }))
const yearOptions = range(1900, currentYear)
  .reverse()
  .map((y) => ({ value: y, label: String(y) }))
// Tử Vi an Mệnh theo canh giờ, nên người dùng chọn thẳng canh thay vì gõ giờ
// phút rồi để frontend tự quy đổi — quy đổi là việc của engine.
const hourOptions = BIRTH_HOUR_OPTIONS.map((option) => ({
  value: option.value,
  label: option.label,
}))

// Rời khỏi âm lịch thì tháng nhuận không còn nghĩa; và ngày 31 không tồn tại
// trên lịch âm, nên kéo về 30 thay vì để người dùng gặp lỗi validate.
watch(isLunar, (lunar) => {
  if (!lunar) form.value.is_leap_month = false
  else if (form.value.birth_day > 30) form.value.birth_day = 30
})
</script>

<template>
  <div class="space-y-6">
    <CsRadioGroup
      v-model="form.calendar_type"
      label="Ngày sinh bạn nhập theo lịch nào?"
      :options="CALENDAR_OPTIONS"
      :error="errors.calendar_type"
    />

    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
      <CsSelect
        v-model="form.birth_day"
        label="Ngày"
        :options="dayOptions"
        :error="errors.birth_day"
        required
      />
      <CsSelect
        v-model="form.birth_month"
        label="Tháng"
        :options="monthOptions"
        :error="errors.birth_month"
        required
      />
      <CsSelect
        v-model="form.birth_year"
        label="Năm"
        :options="yearOptions"
        :error="errors.birth_year"
        class="col-span-2 sm:col-span-1"
        required
      />
    </div>

    <CsCheckbox
      v-if="isLunar"
      v-model="form.is_leap_month"
      label="Sinh vào tháng nhuận"
      description="Chỉ tích khi bạn chắc chắn — tháng nhuận cho ra lá số khác hẳn."
    />

    <CsSelect
      v-model="form.birth_hour"
      label="Giờ sinh"
      :options="hourOptions"
      :error="errors.birth_hour"
      required
      hint="Mỗi canh giờ kéo dài hai tiếng, nên lệch vài phút không đổi lá số. Nhưng nếu bạn không chắc mình sinh vào canh nào thì nên hỏi lại người nhà trước."
    />

    <CsInput
      v-model="form.birth_place"
      label="Nơi sinh"
      placeholder="Hà Nội"
      :maxlength="160"
      :error="errors.birth_place"
      hint="Không bắt buộc. Hiện chỉ để ghi nhớ, chưa dùng để đổi múi giờ."
    />
  </div>
</template>
