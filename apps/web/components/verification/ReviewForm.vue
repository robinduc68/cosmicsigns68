<script setup lang="ts">
import {
  BRANCH_OPTIONS,
  MAJOR_STAR_CODES,
  STAR_LABELS,
  type FixtureReview,
  type VerificationSource,
} from '~/composables/useVerification'

const props = defineProps<{
  review: FixtureReview
  sources: VerificationSource[]
  saving: boolean
}>()
const emit = defineEmits<{ save: [payload: Partial<FixtureReview>] }>()

/**
 * The reviewer's own findings. There is no "copy from engine" affordance here,
 * and that absence is the point: an expected value has to be typed from a
 * source, or the fixture proves nothing.
 */
const expectedStars = ref<Record<string, string | null>>(
  Object.fromEntries(MAJOR_STAR_CODES.map((c) => [c, props.review.expected_stars?.[c] ?? null])),
)
const expectedTuVi = ref<string | null>(props.review.expected_tu_vi)
const expectedTuan = ref<string | null>(props.review.expected_tuan?.join(', ') ?? null)
const expectedTriet = ref<string | null>(props.review.expected_triet?.join(', ') ?? null)
const reviewer = ref<string | null>(props.review.reviewer)
const sourceId = ref<string | null>(props.review.source_id)
const page = ref<string | null>(props.review.page)
const notes = ref<string | null>(props.review.notes)
const confirmed = ref(props.review.independently_confirmed)

const filled = computed(() => MAJOR_STAR_CODES.filter((c) => expectedStars.value[c]).length)
const complete = computed(() => filled.value === MAJOR_STAR_CODES.length && !!expectedTuVi.value)

const sourceOptions = computed(() =>
  props.sources.map((s) => ({
    value: s.id,
    label: `${s.title}${s.publication_year ? ` (${s.publication_year})` : ''} · ${s.source_type}`,
  })),
)

function onSave() {
  const stars = Object.fromEntries(
    MAJOR_STAR_CODES.filter((c) => expectedStars.value[c]).map((c) => [
      c,
      expectedStars.value[c] as string,
    ]),
  )
  emit('save', {
    expected_tu_vi: expectedTuVi.value,
    expected_stars: Object.keys(stars).length ? stars : null,
    expected_tuan: expectedTuan.value
      ? expectedTuan.value.split(',').map((s) => s.trim()).filter(Boolean)
      : null,
    expected_triet: expectedTriet.value
      ? expectedTriet.value.split(',').map((s) => s.trim()).filter(Boolean)
      : null,
    independently_confirmed: confirmed.value,
    reviewer: reviewer.value,
    source_id: sourceId.value,
    page: page.value,
    notes: notes.value ?? '',
  })
}
</script>

<template>
  <section>
    <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
      <h3 class="font-display text-h3 text-[var(--text)]">Nhập kết quả thẩm định</h3>
      <CsBadge :variant="complete ? 'success' : 'neutral'">
        {{ filled }}/{{ MAJOR_STAR_CODES.length }} sao
      </CsBadge>
    </div>

    <CsCard>
      <p class="text-caption text-[var(--text-subtle)]">
        Tra nguồn rồi điền. Cố ý không có nút "lấy từ engine" — chép lại thì bản thẩm định
        không chứng minh được gì.
      </p>

      <div class="mt-5 grid gap-3 sm:grid-cols-2">
        <CsSelect
          v-model="expectedTuVi"
          label="Tử Vi ở cung"
          :options="BRANCH_OPTIONS"
          placeholder="Chọn địa chi…"
        />
        <div />
        <CsSelect
          v-for="code in MAJOR_STAR_CODES.filter((c) => c !== 'TU_VI')"
          :key="code"
          v-model="expectedStars[code]"
          :label="STAR_LABELS[code]"
          :options="BRANCH_OPTIONS"
          placeholder="Chọn địa chi…"
        />
      </div>

      <!-- Tử Vi lives in both places on purpose: the anchor of the whole chart
           is worth stating twice so a slip is visible. -->
      <div class="mt-3">
        <CsSelect
          v-model="expectedStars.TU_VI"
          :label="`${STAR_LABELS.TU_VI} (nhắc lại để đối chiếu)`"
          :options="BRANCH_OPTIONS"
          placeholder="Chọn địa chi…"
        />
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-2">
        <CsInput v-model="expectedTuan" label="Tuần ở các cung" placeholder="Tuất, Hợi" />
        <CsInput v-model="expectedTriet" label="Triệt ở các cung" placeholder="Dần, Mão" />
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-2">
        <CsSelect
          v-model="sourceId"
          label="Nguồn đối chiếu"
          :options="sourceOptions"
          :placeholder="sources.length ? 'Chọn nguồn…' : 'Chưa có nguồn nào trong sổ'"
          :disabled="!sources.length"
        />
        <CsInput v-model="page" label="Trang" placeholder="tr. 128" />
        <CsInput v-model="reviewer" label="Người thẩm định" placeholder="Họ tên" />
      </div>

      <CsTextarea v-model="notes" class="mt-5" label="Ghi chú" :maxlength="2000" />

      <div class="mt-5">
        <CsCheckbox
          v-model="confirmed"
          label="Tôi đã tra nguồn độc lập, không chép từ kết quả engine"
          description="Bắt buộc tích khi kỳ vọng trùng khít engine — nếu không, ca này không được coi là đã kiểm định."
        />
      </div>

      <CsButton class="mt-6" :loading="saving" @click="onSave">Lưu kết quả thẩm định</CsButton>
    </CsCard>
  </section>
</template>
