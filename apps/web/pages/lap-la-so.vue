<script setup lang="ts">
import { Sparkles } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'

useHead({ title: 'Lập lá số' })
useSeoMeta({
  description:
    'Nhập họ tên, ngày giờ sinh và giới tính — Cosmic Signs lập lá số Tử Vi đầy đủ 12 cung ' +
    'ngay lập tức. Miễn phí, không cần tài khoản.',
})

const store = useChartStore()
const { form, errors, submitting, submitError } = storeToRefs(store)
const { error: toastError } = useToast()

const range = (from: number, to: number) =>
  Array.from({ length: to - from + 1 }, (_, i) => from + i)

const isLunar = computed(() => form.value.calendar_type === 'LUNAR')
const dayOptions = computed(() =>
  range(1, isLunar.value ? 30 : 31).map((d) => ({ value: d, label: String(d) })),
)
const monthOptions = range(1, 12).map((m) => ({ value: m, label: `Tháng ${m}` }))
const hourOptions = range(0, 23).map((h) => ({ value: h, label: `${h} giờ` }))
const minuteOptions = range(0, 59).map((m) => ({ value: m, label: `${m} phút` }))

// Gõ năm nhanh hơn kéo danh sách 120 năm; ô nhập trả về chuỗi nên đổi sang số ở đây.
const yearText = computed({
  get: () => (form.value.birth_year ? String(form.value.birth_year) : ''),
  set: (value: string | number | null) => {
    const parsed = Number.parseInt(String(value ?? ''), 10)
    form.value.birth_year = Number.isNaN(parsed) ? 0 : parsed
  },
})

// Rời âm lịch thì tháng nhuận không còn nghĩa; ngày 31 không có trên lịch âm.
watch(isLunar, (lunar) => {
  if (!lunar) form.value.is_leap_month = false
  else if (form.value.birth_day > 30) form.value.birth_day = 30
})

// Màn chờ tách khỏi `submitting` để chặng cuối kịp tick xanh trước khi chuyển trang.
const creating = ref(false)
const created = ref(false)

async function onSubmit() {
  if (!store.validate()) return
  creating.value = true
  created.value = false

  const chart = await store.submit()
  if (!chart) {
    creating.value = false
    if (submitError.value) toastError('Chưa lập được lá số', submitError.value)
    return
  }

  created.value = true
  await new Promise((resolve) => setTimeout(resolve, 500))
  store.reset()
  await navigateTo(`/chart/${chart.id}`)
}
</script>

<template>
  <CsContainer size="sm" class="py-12 sm:py-16">
    <template v-if="creating">
      <div class="text-center">
        <CsBadge variant="accent" size="md">
          <Sparkles class="size-3" aria-hidden="true" />
          Đang lập lá số
        </CsBadge>
        <h1 class="mt-5 font-display text-h2 text-[var(--text)]">
          Đang dựng lá số cho {{ form.subject_name }}
        </h1>
      </div>
      <WizardStagedLoading :done="created" />
    </template>

    <template v-else>
      <h1 class="font-display text-h2 text-[var(--text)] sm:text-h1">Lập lá số</h1>
      <p class="mt-2 text-body text-[var(--text-muted)]">
        Nhập ngày giờ sinh, lá số hiện ra ngay. Không cần tài khoản.
      </p>

      <CsCard class="mt-8">
        <form class="space-y-5" novalidate @submit.prevent="onSubmit">
          <CsInput
            v-model="form.subject_name"
            label="Họ tên"
            placeholder="Nhập họ tên…"
            autocomplete="name"
            :maxlength="120"
            :error="errors.subject_name"
          />

          <div>
            <div class="grid grid-cols-[1fr_1.4fr_1.1fr] gap-2">
              <CsSelect
                v-model="form.birth_day"
                label="Ngày"
                :options="dayOptions"
                :error="errors.birth_day"
              />
              <CsSelect
                v-model="form.birth_month"
                label="Tháng"
                :options="monthOptions"
                :error="errors.birth_month"
              />
              <CsInput
                v-model="yearText"
                label="Năm"
                inputmode="numeric"
                placeholder="1995"
                :maxlength="4"
                :error="errors.birth_year"
              />
            </div>

            <fieldset class="mt-2.5">
              <legend class="sr-only">Loại lịch của ngày sinh</legend>
              <div class="flex flex-wrap gap-x-6">
                <label
                  v-for="option in [
                    { value: 'SOLAR', label: 'Lịch dương' },
                    { value: 'LUNAR', label: 'Lịch âm' },
                  ]"
                  :key="option.value"
                  class="inline-flex cursor-pointer items-center gap-2 py-1 text-small text-[var(--text)]"
                >
                  <input
                    v-model="form.calendar_type"
                    type="radio"
                    name="calendar_type"
                    :value="option.value"
                    class="size-4 accent-[var(--accent)]"
                  />
                  {{ option.label }}
                </label>
              </div>
            </fieldset>

            <CsCheckbox
              v-if="isLunar"
              v-model="form.is_leap_month"
              class="mt-2"
              label="Sinh vào tháng nhuận"
            />
            <p v-if="errors.is_leap_month" class="mt-1.5 text-caption text-[var(--danger)]">
              {{ errors.is_leap_month }}
            </p>
          </div>

          <div>
            <div class="grid grid-cols-2 gap-2">
              <CsSelect
                v-model="form.birth_hour"
                label="Giờ sinh"
                :options="hourOptions"
                :error="errors.birth_hour"
              />
              <CsSelect
                v-model="form.birth_minute"
                label="Phút"
                :options="minuteOptions"
                :error="errors.birth_minute"
              />
            </div>
            <!-- 23:xx là giờ Tý sớm: engine chưa chốt quy ước nên sẽ từ chối. Nói trước
                 để người dùng không bấm xong mới gặp lỗi. -->
            <p
              v-if="form.birth_hour === 23"
              class="mt-2 text-caption text-[var(--color-gold-400)]"
            >
              Từ 23:00 là giờ Tý sớm — các trường phái tính ngày sinh khác nhau ở giờ này, và
              Cosmic Signs chưa chốt quy ước nên chưa lập được lá số cho giờ này.
            </p>
          </div>

          <fieldset>
            <legend class="mb-1.5 text-small font-medium text-[var(--text)]">Giới tính</legend>
            <div class="flex flex-wrap gap-x-6">
              <label
                v-for="option in [
                  { value: 'MALE', label: 'Nam' },
                  { value: 'FEMALE', label: 'Nữ' },
                ]"
                :key="option.value"
                class="inline-flex cursor-pointer items-center gap-2 py-1 text-small text-[var(--text)]"
              >
                <input
                  v-model="form.gender"
                  type="radio"
                  name="gender"
                  :value="option.value"
                  class="size-4 accent-[var(--accent)]"
                />
                {{ option.label }}
              </label>
            </div>
          </fieldset>

          <CsErrorState v-if="submitError" title="Chưa lập được lá số" :description="submitError" />

          <CsButton type="submit" size="lg" block :loading="submitting">Lập lá số</CsButton>
        </form>
      </CsCard>
    </template>
  </CsContainer>
</template>
