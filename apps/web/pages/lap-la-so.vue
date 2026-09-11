<script setup lang="ts">
import { ArrowLeft, ArrowRight, Sparkles } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { WIZARD_STEPS } from '~/stores/chart'

useHead({ title: 'Lập lá số' })
useSeoMeta({
  description:
    'Nhập ngày giờ sinh theo dương lịch hoặc âm lịch, Cosmic Signs lập lá số Tử Vi đầy đủ ' +
    '12 cung trong vài giây. Miễn phí, không cần tài khoản.',
})

const store = useChartStore()
const { form, step, isLastStep, errors, submitting, submitError } = storeToRefs(store)
const { error: toastError } = useToast()

// Hiển thị chặng loading tách khỏi `submitting`: nó phải sống thêm một nhịp sau
// khi lá số về, để người dùng kịp thấy chặng cuối tick xanh trước khi chuyển trang.
const creating = ref(false)
const created = ref(false)

function onFormSubmit() {
  if (isLastStep.value) return onSubmit()
  store.next()
}

async function onSubmit() {
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
      <p class="mt-3 text-body text-[var(--text-muted)]">
        Ba bước, khoảng hai phút. Bạn xem được lá số đầy đủ mà không cần tài khoản.
      </p>

      <div class="mt-8">
        <WizardStepIndicator :steps="[...WIZARD_STEPS]" :current="step" @go-to="store.goTo" />
      </div>

      <form class="mt-10" novalidate @submit.prevent="onFormSubmit">
        <WizardStepIdentity v-if="step === 0" v-model="form" :errors="errors" />
        <WizardStepBirth v-else-if="step === 1" v-model="form" :errors="errors" />
        <WizardStepConfirm v-else v-model="form" :errors="errors" @edit="store.goTo" />

        <CsErrorState
          v-if="submitError"
          class="mt-6"
          title="Chưa lập được lá số"
          :description="submitError"
        />

        <div class="mt-10 flex items-center gap-3">
          <CsButton v-if="step > 0" variant="secondary" :disabled="submitting" @click="store.back">
            <template #leading><ArrowLeft class="size-4" aria-hidden="true" /></template>
            Quay lại
          </CsButton>

          <CsButton type="submit" class="ml-auto" size="lg" :loading="submitting">
            {{ isLastStep ? 'Lập lá số' : 'Tiếp tục' }}
            <template v-if="!isLastStep" #trailing>
              <ArrowRight class="size-4" aria-hidden="true" />
            </template>
          </CsButton>
        </div>
      </form>
    </template>
  </CsContainer>
</template>
