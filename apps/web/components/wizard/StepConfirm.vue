<script setup lang="ts">
import { BIRTH_HOUR_OPTIONS, type BirthFormValues } from '@cosmic/shared'

const form = defineModel<BirthFormValues>({ required: true })
defineProps<{ errors: Partial<Record<keyof BirthFormValues, string>> }>()
const emit = defineEmits<{ edit: [step: number] }>()


const rows = computed(() => {
  const f = form.value
  const calendar = f.calendar_type === 'LUNAR' ? 'âm lịch' : 'dương lịch'
  const leap = f.is_leap_month ? ' nhuận' : ''
  return [
    { label: 'Tên', value: f.subject_name, step: 0 },
    { label: 'Giới tính', value: f.gender === 'MALE' ? 'Nam' : 'Nữ', step: 0 },
    ...(f.relationship_label
      ? [{ label: 'Quan hệ', value: f.relationship_label, step: 0 }]
      : []),
    {
      label: 'Ngày sinh',
      value: `${f.birth_day}/${f.birth_month}${leap}/${f.birth_year} (${calendar})`,
      step: 1,
    },
    {
      label: 'Giờ sinh',
      value: BIRTH_HOUR_OPTIONS.find((o) => o.value === f.birth_hour)?.label ?? String(f.birth_hour),
      step: 1,
    },
    ...(f.birth_place ? [{ label: 'Nơi sinh', value: f.birth_place, step: 1 }] : []),
  ]
})
</script>

<template>
  <div class="space-y-6">
    <CsCard>
      <dl class="divide-y divide-[var(--border)]">
        <div v-for="row in rows" :key="row.label" class="flex items-baseline gap-4 py-3 first:pt-0">
          <dt class="w-28 shrink-0 text-caption text-[var(--text-subtle)]">{{ row.label }}</dt>
          <dd class="flex-1 text-small text-[var(--text)]">{{ row.value }}</dd>
          <button
            type="button"
            class="rounded text-caption text-[var(--accent)] underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
            @click="emit('edit', row.step)"
          >
            Sửa
          </button>
        </div>
      </dl>
    </CsCard>

    <CsTextarea
      v-model="form.note"
      label="Ghi chú"
      placeholder="Điều bạn đang muốn hiểu rõ hơn…"
      :maxlength="500"
      :error="errors.note"
      hint="Không bắt buộc, chỉ bạn nhìn thấy."
    />

    <p class="text-caption text-[var(--text-subtle)]">
      Kiểm tra kỹ ngày và giờ giúp mình nhé — sai một canh giờ là lá số khác hẳn.
    </p>
  </div>
</template>
