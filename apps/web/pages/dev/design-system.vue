<script setup lang="ts">
import { Bell, Copy, Search, Trash2 } from 'lucide-vue-next'

definePageMeta({ middleware: 'dev-only' })
useHead({ title: 'Design system' })

const { toast, success, error } = useToast()

const text = ref('')
const withError = ref('')
const note = ref('')
const city = ref<string | null>(null)
const agree = ref(false)
const gender = ref<string | null>('MALE')
const tab = ref('tong-quan')
const dialogOpen = ref(false)
const drawerOpen = ref(false)

const cities = [
  { value: 'hn', label: 'Hà Nội' },
  { value: 'hcm', label: 'TP. Hồ Chí Minh' },
  { value: 'dn', label: 'Đà Nẵng' },
]

const sections = [
  'Nền tảng',
  'Typography',
  'Button',
  'Form',
  'Hiển thị',
  'Overlay',
  'Trạng thái',
] as const
</script>

<template>
  <CsContainer class="py-12">
    <header class="mb-12">
      <CsBadge variant="gold">Chỉ có ở môi trường development</CsBadge>
      <h1 class="mt-4 font-display text-h1 text-[var(--text)]">Design system</h1>
      <p class="mt-3 max-w-xl text-body text-[var(--text-muted)]">
        Bảng tra cứu component của Cosmic Signs. Đổi giao diện sáng/tối ở thanh trên cùng và thu
        hẹp cửa sổ để kiểm tra ở 375px.
      </p>
      <nav class="mt-6 flex flex-wrap gap-2">
        <a
          v-for="section in sections"
          :key="section"
          :href="`#${section}`"
          class="rounded-lg border border-[var(--border)] px-3 py-1.5 text-caption text-[var(--text-muted)] transition-colors hover:border-[var(--border-strong)] hover:text-[var(--text)]"
        >
          {{ section }}
        </a>
      </nav>
    </header>

    <section id="Nền tảng" class="scroll-mt-20">
      <h2 class="font-display text-h2 text-[var(--text)]">Nền tảng</h2>
      <p class="mt-2 text-small text-[var(--text-muted)]">
        Màu được khai báo dưới dạng token ngữ nghĩa, không dùng mã màu trực tiếp trong component.
      </p>
      <div class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div
          v-for="token in [
            'bg',
            'surface',
            'card',
            'card-hover',
            'border',
            'text',
            'text-muted',
            'accent',
          ]"
          :key="token"
          class="rounded-xl border border-[var(--border)] p-3"
        >
          <div
            class="h-12 rounded-lg border border-[var(--border)]"
            :style="{ background: `var(--${token})` }"
          />
          <p class="mt-2 font-mono text-caption text-[var(--text-muted)]">--{{ token }}</p>
        </div>
      </div>
    </section>

    <section id="Typography" class="mt-16 scroll-mt-20">
      <h2 class="font-display text-h2 text-[var(--text)]">Typography</h2>
      <div class="mt-6 space-y-4 rounded-[var(--radius-card)] border border-[var(--border)] p-6">
        <p class="font-display text-display text-[var(--text)]">Display · Lá số Tử Vi</p>
        <p class="font-display text-h1 text-[var(--text)]">Heading 1 · Mệnh và Thân</p>
        <p class="font-display text-h2 text-[var(--text)]">Heading 2 · Tam phương tứ chính</p>
        <p class="font-display text-h3 text-[var(--text)]">Heading 3 · Cung Quan Lộc</p>
        <p class="text-body text-[var(--text)]">
          Body · Chữ tiếng Việt đầy đủ dấu: Tử Vi, Thiên Cơ, Vũ Khúc, Liêm Trinh, Phá Quân.
        </p>
        <p class="text-small text-[var(--text-muted)]">Small · Ghi chú phụ trong thẻ và biểu mẫu.</p>
        <p class="text-caption text-[var(--text-subtle)]">Caption · Nhãn nhỏ, siêu dữ liệu.</p>
      </div>
    </section>

    <section id="Button" class="mt-16 scroll-mt-20">
      <h2 class="font-display text-h2 text-[var(--text)]">Button</h2>
      <div class="mt-6 space-y-6 rounded-[var(--radius-card)] border border-[var(--border)] p-6">
        <div class="flex flex-wrap items-center gap-3">
          <CsButton>Primary</CsButton>
          <CsButton variant="secondary">Secondary</CsButton>
          <CsButton variant="outline">Outline</CsButton>
          <CsButton variant="ghost">Ghost</CsButton>
          <CsButton variant="danger">Danger</CsButton>
          <CsButton variant="link">Link</CsButton>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <CsButton size="sm">Small</CsButton>
          <CsButton size="md">Medium</CsButton>
          <CsButton size="lg">Large</CsButton>
          <CsButton loading>Đang xử lý</CsButton>
          <CsButton disabled>Disabled</CsButton>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <CsIconButton label="Tìm kiếm"><Search class="size-4" /></CsIconButton>
          <CsIconButton label="Sao chép" variant="outline"><Copy class="size-4" /></CsIconButton>
          <CsIconButton label="Xóa" variant="solid"><Trash2 class="size-4" /></CsIconButton>
        </div>
        <CsButton block>Nút chiếm toàn bộ chiều ngang</CsButton>
      </div>
    </section>

    <section id="Form" class="mt-16 scroll-mt-20">
      <h2 class="font-display text-h2 text-[var(--text)]">Form</h2>
      <div
        class="mt-6 grid gap-6 rounded-[var(--radius-card)] border border-[var(--border)] p-6 sm:grid-cols-2"
      >
        <CsInput v-model="text" label="Họ và tên" placeholder="Nguyễn Văn A" required />
        <CsInput
          v-model="withError"
          label="Năm sinh"
          placeholder="1992"
          inputmode="numeric"
          error="Năm sinh cần từ 1900 trở đi"
        />
        <CsInput v-model="text" label="Có biểu tượng" placeholder="Tìm nơi sinh">
          <template #leading><Search class="size-4" /></template>
        </CsInput>
        <CsSelect
          v-model="city"
          label="Nơi sinh"
          placeholder="Chọn tỉnh thành"
          :options="cities"
          hint="Dùng select gốc của trình duyệt để trên điện thoại mở picker hệ điều hành."
        />
        <div class="sm:col-span-2">
          <CsRadioGroup
            v-model="gender"
            label="Giới tính"
            :options="[
              { value: 'MALE', label: 'Nam' },
              { value: 'FEMALE', label: 'Nữ' },
            ]"
          />
        </div>
        <div class="sm:col-span-2">
          <CsTextarea v-model="note" label="Ghi chú" :maxlength="200" placeholder="Không bắt buộc" />
        </div>
        <CsCheckbox v-model="agree" label="Tôi đã đọc phần lưu ý" description="Nội dung mang tính tham khảo." />
      </div>
    </section>

    <section id="Hiển thị" class="mt-16 scroll-mt-20">
      <h2 class="font-display text-h2 text-[var(--text)]">Hiển thị</h2>
      <div class="mt-6 grid gap-4 sm:grid-cols-2">
        <CsCard>
          <p class="font-display text-h3 text-[var(--text)]">Card</p>
          <p class="mt-2 text-small text-[var(--text-muted)]">Bề mặt cơ bản cho mọi khối nội dung.</p>
          <div class="mt-4 flex flex-wrap gap-2">
            <CsBadge>Neutral</CsBadge>
            <CsBadge variant="accent">Accent</CsBadge>
            <CsBadge variant="success">Miếu</CsBadge>
            <CsBadge variant="danger">Hãm</CsBadge>
            <CsBadge variant="outline">Tuần</CsBadge>
            <CsPremiumBadge />
          </div>
        </CsCard>
        <CsCard interactive>
          <p class="font-display text-h3 text-[var(--text)]">Card có tương tác</p>
          <p class="mt-2 text-small text-[var(--text-muted)]">
            Chỉ dùng khi toàn bộ thẻ là một vùng bấm được.
          </p>
        </CsCard>
        <CsCard>
          <p class="mb-3 text-small font-medium text-[var(--text)]">Skeleton</p>
          <CsSkeleton class="h-24" />
          <CsSkeleton class="mt-3" :lines="3" />
        </CsCard>
        <CsLockedContent
          title="Sự nghiệp & công danh"
          preview="Thân cư Quan Lộc cho thấy phần lớn năng lượng của bạn dồn vào công việc. Điều này thường biểu hiện ở chỗ…"
          basis="Phân tích dựa trên Mệnh – Thân – tam phương tứ chính và các sao liên quan."
        />
      </div>
    </section>

    <section id="Overlay" class="mt-16 scroll-mt-20">
      <h2 class="font-display text-h2 text-[var(--text)]">Overlay</h2>
      <div
        class="mt-6 flex flex-wrap gap-3 rounded-[var(--radius-card)] border border-[var(--border)] p-6"
      >
        <CsButton variant="secondary" @click="dialogOpen = true">Mở Dialog</CsButton>
        <CsButton variant="secondary" @click="drawerOpen = true">Mở Drawer</CsButton>
        <CsTooltip content="Tuần và Triệt làm giảm tác dụng của cung và sao tại đó.">
          <CsButton variant="secondary">Tooltip</CsButton>
        </CsTooltip>
        <CsPopover>
          <template #trigger><CsButton variant="secondary">Popover</CsButton></template>
          <p class="text-small text-[var(--text-muted)]">
            Popover dùng cho nội dung phụ trợ ngắn, không chặn thao tác phía sau.
          </p>
        </CsPopover>
        <CsDropdown
          :items="[
            { key: 'view', label: 'Xem lá số' },
            { key: 'rename', label: 'Đổi tên' },
            { key: 'delete', label: 'Xóa', danger: true, separatorBefore: true },
          ]"
          @select="(key) => toast(`Đã chọn: ${key}`)"
        >
          <template #trigger><CsButton variant="secondary">Dropdown</CsButton></template>
        </CsDropdown>
        <CsButton variant="secondary" @click="success('Đã lưu lá số')">Toast thành công</CsButton>
        <CsButton variant="secondary" @click="error('Chưa lập được lá số', 'Bạn thử lại sau vài giây nhé.')">
          Toast lỗi
        </CsButton>
      </div>

      <div class="mt-6">
        <CsTabs
          v-model="tab"
          aria-label="Ví dụ tabs"
          :items="[
            { value: 'tong-quan', label: 'Tổng quan' },
            { value: 'menh', label: 'Mệnh' },
            { value: 'su-nghiep', label: 'Sự nghiệp', locked: true },
          ]"
        >
          <template #tong-quan>
            <p class="text-body text-[var(--text-muted)]">Nội dung tab Tổng quan.</p>
          </template>
          <template #menh>
            <p class="text-body text-[var(--text-muted)]">Nội dung tab Mệnh.</p>
          </template>
          <template #su-nghiep>
            <p class="text-body text-[var(--text-muted)]">Nội dung tab Sự nghiệp.</p>
          </template>
        </CsTabs>
      </div>

      <CsDialog
        v-model:open="dialogOpen"
        title="Xóa lá số này?"
        description="Thao tác này không hoàn tác được."
      >
        <p class="text-small text-[var(--text-muted)]">
          Toàn bộ dữ liệu ngày giờ sinh của lá số sẽ bị xóa khỏi hệ thống.
        </p>
        <template #footer>
          <CsButton variant="secondary" @click="dialogOpen = false">Hủy</CsButton>
          <CsButton variant="danger" @click="dialogOpen = false">Xóa lá số</CsButton>
        </template>
      </CsDialog>

      <CsDrawer v-model:open="drawerOpen" title="Bộ lọc" description="Ví dụ drawer bên phải">
        <p class="text-small text-[var(--text-muted)]">
          Trên điện thoại nên dùng biến thể trượt từ dưới lên.
        </p>
      </CsDrawer>
    </section>

    <section id="Trạng thái" class="mt-16 mb-20 scroll-mt-20">
      <h2 class="font-display text-h2 text-[var(--text)]">Trạng thái</h2>
      <div class="mt-6 grid gap-4 sm:grid-cols-2">
        <CsEmptyState
          title="Bạn chưa có lá số nào"
          description="Lập lá số đầu tiên để bắt đầu."
        >
          <template #icon><Bell class="size-5" /></template>
          <template #action><CsButton to="/lap-la-so">Lập lá số đầu tiên</CsButton></template>
        </CsEmptyState>
        <CsErrorState @retry="toast('Đang thử lại…')" />
      </div>
    </section>
  </CsContainer>
</template>
