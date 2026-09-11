<script setup lang="ts">
import { AlertTriangle, Download, RefreshCw } from 'lucide-vue-next'
import type { FixtureReview, ReviewState } from '~/composables/useVerification'

/**
 * Internal verification workbench. Development only — the route middleware 404s
 * it in a production build, and the API refuses the endpoints there too.
 */
definePageMeta({
  path: '/_internal/astrology-verification',
  middleware: 'dev-only',
  layout: 'default',
})

useHead({ title: 'Kiểm định engine Tử Vi (nội bộ)' })
useSeoMeta({ robots: 'noindex, nofollow, noarchive' })

const api = useVerification()
const { error: toastError, success: toastSuccess } = useToast()

const { data: fixtures, refresh: refreshFixtures } = await useAsyncData('verif-fixtures', () =>
  api.listFixtures(),
)
const { data: progress, refresh: refreshProgress } = await useAsyncData('verif-progress', () =>
  api.progress(),
)
const { data: sourceData } = await useAsyncData('verif-sources', () => api.sources())

const FILTERS = [
  { value: 'ALL', label: 'Tất cả' },
  { value: 'PENDING', label: 'Chờ thẩm định' },
  { value: 'IN_REVIEW', label: 'Đang thẩm định' },
  { value: 'VERIFIED', label: 'Đã kiểm định' },
  { value: 'DISAGREEMENT', label: 'Bất đồng' },
  { value: 'BLOCKED', label: 'Bị chặn' },
]
const filter = ref<'ALL' | ReviewState>('ALL')

const visible = computed(() =>
  (fixtures.value ?? []).filter((f) => filter.value === 'ALL' || f.state === filter.value),
)

const selectedId = ref<string | null>(null)
const { data: detail, refresh: refreshDetail } = await useAsyncData(
  'verif-detail',
  () => (selectedId.value ? api.fixtureDetail(selectedId.value) : Promise.resolve(null)),
  { watch: [selectedId] },
)

const saving = ref(false)
async function onSave(payload: Partial<FixtureReview>) {
  if (!selectedId.value) return
  saving.value = true
  try {
    const result = await api.saveReview(selectedId.value, payload)
    await Promise.all([refreshDetail(), refreshFixtures(), refreshProgress()])
    if (result.state.state === 'VERIFIED') {
      toastSuccess('Đã ghi nhận là đã kiểm định')
    } else if (result.state.state === 'DISAGREEMENT') {
      toastError('Có bất đồng với engine', 'Đã lưu. Engine không bị sửa tự động.')
    } else {
      toastSuccess('Đã lưu', result.state.blockers[0] ?? undefined)
    }
  } catch {
    toastError('Chưa lưu được kết quả thẩm định')
  } finally {
    saving.value = false
  }
}

const { baseURL } = useApi()
const exportUrl = (fmt: string) =>
  `${baseURL}/api/v1/_internal/verification/export?fmt=${fmt}`

const ruleRows = computed(() => progress.value?.rules ?? [])

/** Flattened for display: the raw frame has nested objects that wreck a grid. */
const birthRows = computed(() => {
  const frame = detail.value?.derived_frame
  if (!frame) return []
  const solar = frame.solar as Record<string, number> | undefined
  const lunar = frame.lunar as Record<string, number | boolean> | undefined
  const pad = (n: number | undefined) => String(n ?? 0).padStart(2, '0')
  return [
    {
      label: 'Dương lịch',
      value: solar
        ? `${pad(solar.day)}/${pad(solar.month)}/${solar.year} ${pad(solar.hour)}:${pad(solar.minute)}`
        : '—',
    },
    {
      label: 'Âm lịch',
      value: lunar
        ? `${lunar.day}/${lunar.month}${lunar.is_leap_month ? ' nhuận' : ''}/${lunar.year}`
        : '—',
    },
    { label: 'Múi giờ', value: String(detail.value?.timezone_context?.source ?? '—') },
    { label: 'Giờ sinh (canh)', value: String(frame.hour_branch ?? '—') },
    { label: 'Trụ năm', value: String(frame.year_pillar ?? '—') },
    { label: 'Trụ ngày', value: String(frame.day_pillar ?? '—') },
    { label: 'Âm dương', value: String(frame.yin_yang ?? '—') },
    { label: 'Mệnh', value: `${frame.menh ?? '—'} · ${frame.menh_element ?? ''}` },
    { label: 'Thân', value: `${frame.than ?? '—'} (cư ${frame.than_cu ?? '—'})` },
    { label: 'Cục', value: String(frame.cuc ?? '—') },
    { label: 'Mệnh – Cục', value: String(frame.menh_cuc_relation ?? '—') },
    { label: 'Tuần', value: (frame.tuan as string[] | undefined)?.join(', ') ?? '—' },
    { label: 'Triệt', value: (frame.triet as string[] | undefined)?.join(', ') ?? '—' },
  ]
})
</script>

<template>
  <CsContainer class="py-10">
    <header class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <CsBadge variant="gold">Nội bộ · chỉ dành cho developer và người thẩm định</CsBadge>
        <h1 class="mt-3 font-display text-h2 text-[var(--text)]">Kiểm định engine Tử Vi</h1>
        <p v-if="progress" class="mt-2 text-small text-[var(--text-muted)]">
          Hồ sơ quy ước {{ progress.profile }}@{{ progress.version }}
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <CsButton variant="secondary" size="sm" :href="exportUrl('csv')">
          <template #leading><Download class="size-4" aria-hidden="true" /></template>
          Gói thẩm định (CSV)
        </CsButton>
        <CsButton variant="secondary" size="sm" :href="exportUrl('json')">
          <template #leading><Download class="size-4" aria-hidden="true" /></template>
          JSON
        </CsButton>
        <CsIconButton label="Tải lại" @click="refreshFixtures(); refreshProgress()">
          <RefreshCw class="size-4" aria-hidden="true" />
        </CsIconButton>
      </div>
    </header>

    <!-- Dashboard: mọi con số lấy từ fixture và hồ sơ quy ước, không hardcode. -->
    <div v-if="progress" class="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <CsCard>
        <p class="text-caption text-[var(--text-subtle)]">Ma trận 14 chính tinh</p>
        <dl class="mt-3 space-y-1.5 text-small">
          <div
            v-for="key in ['VERIFIED', 'IN_REVIEW', 'PENDING', 'DISAGREEMENT', 'BLOCKED']"
            :key="key"
            class="flex justify-between gap-4"
          >
            <dt class="text-[var(--text-muted)]">{{ key }}</dt>
            <dd class="font-medium text-[var(--text)]">{{ progress.fixtures[key] ?? 0 }}</dd>
          </div>
          <div class="flex justify-between gap-4 border-t border-[var(--border)] pt-1.5">
            <dt class="text-[var(--text-muted)]">Tổng</dt>
            <dd class="font-medium text-[var(--text)]">{{ progress.fixtures.TOTAL }}</dd>
          </div>
        </dl>
      </CsCard>

      <CsCard class="lg:col-span-2">
        <p class="text-caption text-[var(--text-subtle)]">Trạng thái từng quy tắc</p>
        <div class="mt-3 grid gap-x-6 gap-y-1.5 sm:grid-cols-2">
          <div
            v-for="rule in ruleRows"
            :key="rule.rule"
            class="flex items-center justify-between gap-3 text-caption"
          >
            <span class="truncate text-[var(--text-muted)]">{{ rule.rule }}</span>
            <span
              class="shrink-0 font-medium"
              :class="{
                'text-[var(--success)]': rule.status === 'VERIFIED',
                'text-[var(--color-gold-400)]': rule.status === 'BLOCKED',
                'text-[var(--text-subtle)]': !['VERIFIED', 'BLOCKED'].includes(rule.status),
              }"
            >
              {{ rule.status }}
            </span>
          </div>
        </div>
        <div
          v-if="!progress.production_ready"
          class="mt-4 flex gap-2 border-t border-[var(--border)] pt-3"
        >
          <AlertTriangle
            class="mt-0.5 size-4 shrink-0 text-[var(--color-gold-400)]"
            aria-hidden="true"
          />
          <div class="text-caption text-[var(--text-muted)]">
            <p class="font-medium text-[var(--text)]">Chưa sẵn sàng cho production</p>
            <ul class="mt-1 space-y-0.5">
              <li v-for="f in progress.failures" :key="f">{{ f }}</li>
            </ul>
          </div>
        </div>
      </CsCard>
    </div>

    <div class="mt-10 grid gap-6 lg:grid-cols-[22rem_1fr]">
      <div>
        <CsSelect v-model="filter" label="Lọc theo trạng thái" :options="FILTERS" />
        <ul class="mt-4 space-y-2">
          <li v-for="fixture in visible" :key="fixture.id">
            <button
              type="button"
              class="w-full rounded-[var(--radius-card)] border p-3 text-left transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
              :class="
                selectedId === fixture.id
                  ? 'border-[var(--accent)] bg-[var(--accent-soft)]'
                  : 'border-[var(--border)] bg-[var(--card)] hover:border-[var(--border-strong)]'
              "
              @click="selectedId = fixture.id"
            >
              <div class="flex items-center justify-between gap-2">
                <span class="font-medium text-small text-[var(--text)]">{{ fixture.id }}</span>
                <VerificationStateBadge :state="fixture.state" />
              </div>
              <p class="mt-1 text-caption text-[var(--text-muted)]">{{ fixture.purpose }}</p>
              <p class="mt-1.5 text-caption text-[var(--text-subtle)]">
                {{ fixture.birth_date }} {{ fixture.birth_time }} ·
                {{ fixture.gender === 'MALE' ? 'Nam' : 'Nữ' }}
                <template v-if="fixture.utc_offset"> · UTC+{{ fixture.utc_offset }}</template>
              </p>
              <p v-if="fixture.menh" class="text-caption text-[var(--text-subtle)]">
                Mệnh {{ fixture.menh }} · {{ fixture.cuc }}
                <template v-if="fixture.lunar_date"> · âm {{ fixture.lunar_date }}</template>
              </p>
              <p v-if="fixture.reviewer" class="mt-1 text-caption text-[var(--text-subtle)]">
                {{ fixture.reviewer }}<template v-if="fixture.source">
                  · {{ fixture.source.title }}</template>
              </p>
            </button>
          </li>
        </ul>
        <CsEmptyState
          v-if="!visible.length"
          class="mt-4"
          title="Không có ca nào"
          description="Đổi bộ lọc để xem các ca khác."
        />
      </div>

      <div v-if="detail" class="min-w-0 space-y-10">
        <section>
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 class="font-display text-h2 text-[var(--text)]">{{ detail.id }}</h2>
              <p class="mt-1 text-small text-[var(--text-muted)]">{{ detail.purpose }}</p>
            </div>
            <VerificationStateBadge :state="detail.state.state" />
          </div>

          <CsCard
            v-if="detail.blocked_reason"
            class="mt-4 border-[var(--color-gold-400)]/40"
          >
            <p class="text-small font-medium text-[var(--text)]">Ca này đang bị chặn</p>
            <p class="mt-1.5 text-caption text-[var(--text-muted)]">{{ detail.blocked_reason }}</p>
            <div v-if="detail.late_zi_demonstration" class="mt-4 overflow-x-auto">
              <table class="w-full border-collapse text-caption">
                <thead>
                  <tr class="border-b border-[var(--border)] text-left">
                    <th class="py-1.5 pr-3 font-medium text-[var(--text-muted)]">Chính sách</th>
                    <th class="py-1.5 pr-3 font-medium text-[var(--text-muted)]">Ngày âm</th>
                    <th class="py-1.5 pr-3 font-medium text-[var(--text-muted)]">Trụ ngày</th>
                    <th class="py-1.5 pr-3 font-medium text-[var(--text-muted)]">Tử Vi</th>
                    <th class="py-1.5 font-medium text-[var(--text-muted)]">Nhất quán</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(row, policy) in detail.late_zi_demonstration"
                    :key="policy"
                    class="border-b border-[var(--border)] last:border-0"
                  >
                    <td class="py-1.5 pr-3 text-[var(--text)]">{{ policy }}</td>
                    <td class="py-1.5 pr-3 text-[var(--text-muted)]">{{ row.lunar_day }}</td>
                    <td class="py-1.5 pr-3 text-[var(--text-muted)]">{{ row.day_pillar }}</td>
                    <td class="py-1.5 pr-3 text-[var(--text-muted)]">{{ row.tu_vi }}</td>
                    <td class="py-1.5">
                      <span
                        :class="
                          row.internally_consistent
                            ? 'text-[var(--success)]'
                            : 'text-[var(--danger)]'
                        "
                      >
                        {{ row.internally_consistent ? 'có' : 'không' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CsCard>

          <CsCard v-if="birthRows.length" class="mt-4">
            <dl class="grid gap-x-6 gap-y-3 text-caption sm:grid-cols-3">
              <div v-for="row in birthRows" :key="row.label">
                <dt class="text-[var(--text-subtle)]">{{ row.label }}</dt>
                <dd class="mt-0.5 text-small text-[var(--text)]">{{ row.value }}</dd>
              </div>
            </dl>
          </CsCard>

          <CsCard v-if="detail.anchor_basis" class="mt-3">
            <p class="text-caption text-[var(--text-muted)]">
              <span class="font-medium text-[var(--text)]">Ca neo:</span>
              Tử Vi kỳ vọng theo bảng kinh điển là <strong>{{ detail.anchor_tu_vi }}</strong>.
              {{ detail.anchor_basis }}
            </p>
          </CsCard>
        </section>

        <VerificationStarDiff :comparisons="detail.comparisons" />
        <VerificationPalaceDiff v-if="detail.palaces.length" :palaces="detail.palaces" />
        <VerificationTraceView v-if="detail.trace.length" :trace="detail.trace" />

        <VerificationReviewForm
          :key="detail.id"
          :review="detail.review"
          :sources="sourceData?.sources.sources ?? []"
          :saving="saving"
          @save="onSave"
        />
      </div>

      <CsEmptyState
        v-else
        title="Chọn một ca để bắt đầu"
        description="Danh sách bên trái là 17 ca kiểm định. Mỗi ca hiển thị kết quả engine, giá trị kỳ vọng và vì sao engine đặt sao ở đó."
      />
    </div>
  </CsContainer>
</template>
