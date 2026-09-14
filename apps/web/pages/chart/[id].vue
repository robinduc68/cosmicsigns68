<script setup lang="ts">
import { Check, Link2, Trash2 } from 'lucide-vue-next'
import {
  ApiError,
  INSIGHT_CATEGORIES,
  type AnnualChart,
  type ChartDetail,
} from '@cosmic/shared'
import TuViChart from '~/components/astrology/chart/TuViChart.vue'
import { useTuViChartViewModel } from '~/composables/useTuViChartViewModel'

const route = useRoute()
const { request } = useApi()
const { success: toastSuccess, error: toastError } = useToast()

const id = computed(() => String(route.params.id))

const { data: chart, error } = await useAsyncData(
  () => `chart-${id.value}`,
  () => request<ChartDetail>(`/api/v1/charts/${id.value}`),
  { watch: [id] },
)

if (error.value) {
  // `useAsyncData` bọc lỗi gốc lại, nên ApiError nằm ở `cause` chứ không phải
  // ở chính `error.value` — quên chỗ này là mọi lá số không tồn tại đều ra 500.
  const cause = error.value.cause ?? error.value
  const isMissing = cause instanceof ApiError && cause.status === 404
  throw createError({
    statusCode: isMissing ? 404 : 500,
    message: isMissing ? 'Không tìm thấy lá số' : 'Không tải được lá số',
    fatal: true,
  })
}

const payload = computed(() => chart.value?.chart)

/**
 * Năm xem. `null` nghĩa là chỉ hiển thị lá số gốc.
 *
 * Đổi năm chỉ nạp lại **khối lưu niên** — lá số gốc không được tải lại, không được
 * tính lại, và vì thế không thể xê dịch.
 */
const viewingYear = ref<number | null>(null)
const yearOptions = computed(() => {
  const thisYear = new Date().getFullYear()
  return [
    { value: '', label: 'Không xem lưu niên' },
    ...Array.from({ length: 5 }, (_, i) => thisYear - 1 + i).map((y) => ({
      value: String(y),
      label: String(y),
    })),
  ]
})
const yearChoice = computed({
  get: () => (viewingYear.value === null ? '' : String(viewingYear.value)),
  set: (value: string | number | undefined) => {
    viewingYear.value = value ? Number(value) : null
  },
})

const { data: annual } = await useAsyncData<AnnualChart | null>(
  // Khóa gồm cả năm xem, nên kết quả 2026 không bao giờ bị dùng lại cho 2027.
  () => `annual-${id.value}-${viewingYear.value ?? 'none'}`,
  () =>
    viewingYear.value
      ? request<AnnualChart>(`/api/v1/charts/${id.value}/annual?year=${viewingYear.value}`)
      : Promise.resolve(null),
  { watch: [id, viewingYear], default: () => null },
)

// Engine output → view model. The renderer never decides astrology.
const chartModel = useTuViChartViewModel(
  () => payload.value,
  () => annual.value,
)

useHead({ title: () => (chart.value ? `Lá số của ${chart.value.subject_name}` : 'Lá số') })
// Lá số là dữ liệu cá nhân và địa chỉ của nó là lớp bảo vệ duy nhất lúc này —
// không để công cụ tìm kiếm lập chỉ mục.
useSeoMeta({ robots: 'noindex, nofollow' })

const pillars = computed(() => {
  const p = payload.value?.pillars
  if (!p) return []
  return [
    { label: 'Năm', pillar: p.year },
    { label: 'Tháng', pillar: p.month },
    { label: 'Ngày', pillar: p.day },
    { label: 'Giờ', pillar: p.hour },
  ]
})

const copied = ref(false)
async function copyLink() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    toastError('Chưa sao chép được', 'Bạn copy thủ công từ thanh địa chỉ giúp mình nhé.')
  }
}

const deleting = ref(false)
const confirmingDelete = ref(false)
async function remove() {
  deleting.value = true
  try {
    await request(`/api/v1/charts/${id.value}`, { method: 'DELETE' })
    toastSuccess('Đã xoá lá số')
    await navigateTo('/')
  } catch (caught: unknown) {
    toastError(
      'Chưa xoá được lá số',
      caught instanceof ApiError ? caught.message : 'Bạn thử lại sau vài giây nhé.',
    )
  } finally {
    deleting.value = false
    confirmingDelete.value = false
  }
}
</script>

<template>
  <CsContainer v-if="chart && payload" class="py-12 sm:py-16">
    <header class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-2">
          <CsBadge variant="neutral">
            {{ chart.gender === 'MALE' ? 'Nam' : 'Nữ' }} · {{ payload.yin_yang.label }}
          </CsBadge>
          <CsBadge v-if="chart.relationship_label" variant="outline">
            {{ chart.relationship_label }}
          </CsBadge>
        </div>
        <h1 class="mt-3 font-display text-h2 text-[var(--text)] sm:text-h1">
          Lá số của {{ chart.subject_name }}
        </h1>
        <p class="mt-2 text-small text-[var(--text-muted)]">
          {{ payload.birth.solar.day }}/{{ payload.birth.solar.month }}/{{
            payload.birth.solar.year
          }}
          dương lịch · giờ {{ payload.birth.hour_branch }} · nhằm ngày
          {{ payload.lunar_birth.day }}/{{ payload.lunar_birth.month
          }}{{ payload.lunar_birth.is_leap_month ? ' nhuận' : '' }} năm
          {{ payload.lunar_birth.year_pillar }}
        </p>
      </div>

      <div class="flex gap-2">
        <CsButton variant="secondary" size="sm" @click="copyLink">
          <template #leading>
            <Check v-if="copied" class="size-4" aria-hidden="true" />
            <Link2 v-else class="size-4" aria-hidden="true" />
          </template>
          {{ copied ? 'Đã sao chép' : 'Sao chép link' }}
        </CsButton>
        <CsButton variant="ghost" size="sm" @click="confirmingDelete = true">
          <template #leading><Trash2 class="size-4" aria-hidden="true" /></template>
          Xoá
        </CsButton>
      </div>
    </header>

    <!-- Lá số cũ vẫn hiện đúng như lúc lập. Không tự tính lại: người xem quyết. -->
    <CsCard
      v-if="chart.recalculation?.needed"
      class="mt-6 border-[var(--color-gold-400)]/50"
    >
      <p class="text-small font-medium text-[var(--text)]">
        Lá số này lập bằng phiên bản engine cũ
      </p>
      <p class="mt-1.5 text-caption text-[var(--text-muted)]">
        {{ chart.recalculation.reason }} Cụ thể, engine 0.1.0 gắn <strong>tên 12 cung</strong>
        theo chiều ngược, nên các cặp như Phu Thê ↔ Phúc Đức, Tài Bạch ↔ Quan Lộc bị đổi
        chỗ cho nhau (Mệnh và Thiên Di vẫn đúng). Vị trí sao theo địa chi thì không sai.
        Mình không tự sửa lá số đã lưu — bạn lập lại để có bản đúng nhé.
      </p>
      <CsButton to="/lap-la-so" size="sm" class="mt-4">Lập lại lá số</CsButton>
    </CsCard>

    <CsCard v-if="payload.engine.stage !== 'FULL'" class="mt-6">
      <p class="text-small font-medium text-[var(--text)]">Lá số này chưa đầy đủ</p>
      <p class="mt-1.5 text-caption text-[var(--text-muted)]">
        Khung lá số — 12 cung, Mệnh, Thân, Cục, Tuần, Triệt — đã tính xong và ổn định. Vị trí 14
        chính tinh (đánh dấu <span class="text-[var(--text-subtle)]">*</span>) chưa được kiểm định
        bằng bộ ca chuẩn, còn phụ tinh, tứ hoá, đại vận và lưu niên thì chưa làm. Mình hiển thị
        đúng những gì engine tính được, không suy đoán thêm.
      </p>
    </CsCard>

    <div class="mt-8">
      <div class="mb-4 max-w-xs">
        <CsSelect v-model="yearChoice" label="Năm xem (lưu niên)" :options="yearOptions" />
      </div>
      <TuViChart v-if="chartModel" :model="chartModel" :file-slug="chart.subject_name" />
    </div>

    <section class="mt-14">
      <CsSectionHeading
        as="h2"
        title="Nạp âm từng trụ"
        description="Ngũ hành nạp âm của bốn trụ, nền để đọc Cục và quan hệ Mệnh – Cục."
      />
      <div class="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <CsCard v-for="item in pillars" :key="item.label">
          <p class="text-caption text-[var(--text-subtle)]">Trụ {{ item.label }}</p>
          <p class="mt-1 font-display text-h3 text-[var(--text)]">{{ item.pillar.name }}</p>
          <p class="mt-1 text-small text-[var(--text-muted)]">{{ item.pillar.nap_am }}</p>
        </CsCard>
      </div>
    </section>

    <section class="mt-14">
      <CsSectionHeading
        as="h2"
        eyebrow="Luận giải"
        title="Đọc lá số theo từng khía cạnh"
        description="Phần này cần hệ luận giải đọc lá số của bạn rồi mới viết được. Mình đang hoàn thiện và sẽ mở dần."
      />
      <div class="mt-8 grid gap-4 lg:grid-cols-2">
        <CsLockedContent
          v-for="category in INSIGHT_CATEGORIES"
          :key="category.key"
          :title="category.title"
          :preview="category.description"
          basis="Phân tích dựa trên Mệnh – Thân, tam phương tứ chính và các sao trong cung tương ứng của lá số này."
          cta-label="Sắp có"
          cta-disabled
        />
      </div>
    </section>

    <p class="mt-14 text-caption text-[var(--text-subtle)]">
      Lá số được lập lúc {{ new Date(chart.created_at).toLocaleString('vi-VN') }} · engine
      {{ payload.engine.version }}
    </p>

    <CsDialog
      v-model:open="confirmingDelete"
      title="Xoá lá số này?"
      description="Lá số sẽ bị xoá khỏi máy chủ và link hiện tại không mở được nữa. Việc này không hoàn tác được."
    >
      <template #footer>
        <CsButton variant="secondary" :disabled="deleting" @click="confirmingDelete = false">
          Giữ lại
        </CsButton>
        <CsButton variant="danger" :loading="deleting" @click="remove">Xoá lá số</CsButton>
      </template>
    </CsDialog>
  </CsContainer>
</template>
