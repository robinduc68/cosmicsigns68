<script setup lang="ts">
import type { BirthFormValues } from '@cosmic/shared'

const form = defineModel<BirthFormValues>({ required: true })
defineProps<{ errors: Partial<Record<keyof BirthFormValues, string>> }>()

const GENDER_OPTIONS = [
  { value: 'MALE', label: 'Nam' },
  { value: 'FEMALE', label: 'Nữ' },
]

/**
 * Giới tính là dữ liệu tính toán, không phải nhân khẩu học: Tử Vi dùng nó cùng
 * âm dương của năm sinh để quyết định chiều thuận / nghịch của đại vận.
 */
</script>

<template>
  <div class="space-y-6">
    <CsInput
      v-model="form.subject_name"
      label="Lá số này của ai?"
      placeholder="Nguyễn Văn A"
      autocomplete="name"
      :maxlength="120"
      :error="errors.subject_name"
      required
      hint="Tên chỉ dùng để bạn nhận ra lá số khi xem lại."
    />

    <CsRadioGroup
      v-model="form.gender"
      label="Giới tính"
      :options="GENDER_OPTIONS"
      :error="errors.gender"
      hint="Cùng với âm dương của năm sinh, giới tính quyết định chiều đi của đại vận."
    />

    <CsInput
      v-model="form.relationship_label"
      label="Nhãn quan hệ"
      placeholder="Mẹ, bạn thân, người yêu…"
      :maxlength="60"
      :error="errors.relationship_label"
      hint="Không bắt buộc. Hữu ích khi bạn lập lá số cho nhiều người."
    />
  </div>
</template>
