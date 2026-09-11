<script setup lang="ts">
import { Check } from 'lucide-vue-next'
import type { Product } from '@cosmic/shared'

/**
 * Giá đến từ `GET /api/v1/products`, không có con số nào viết trong file này —
 * admin đổi giá trong DB là trang này đổi theo, không cần deploy.
 */
// Chưa lấy được bảng giá thì ẩn hẳn section thay vì dựng khung rỗng.
const { request } = useApi()
const { data: products } = await useAsyncData('products', () =>
  request<Product[]>('/api/v1/products').catch(() => [] as Product[]),
)

function formatPrice(product: Product): string {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: product.currency,
    maximumFractionDigits: 0,
  }).format(product.price_amount)
}

const FREE_INCLUDES = [
  'Lá số đầy đủ 12 cung',
  'Mệnh, Thân, Cục, Tuần, Triệt, nạp âm',
  'Lưu lại và xem lại bất cứ lúc nào',
]
</script>

<template>
  <section v-if="products && products.length" id="bang-gia" class="scroll-mt-20 py-20 sm:py-24">
    <CsContainer>
      <CsSectionHeading
        align="center"
        eyebrow="Bảng giá"
        title="Lá số miễn phí, chỉ trả tiền cho phần luận giải"
        description="Mua một lần cho từng lá số, không đăng ký định kỳ, không tự động gia hạn."
      />

      <CsCard class="mt-12">
        <div class="flex flex-wrap items-center justify-between gap-6">
          <div>
            <p class="font-display text-h3 text-[var(--text)]">Lá số — miễn phí</p>
            <p class="mt-2 text-small text-[var(--text-muted)]">
              Không cần tài khoản, không giới hạn hợp lý số lá số bạn lập.
            </p>
            <ul class="mt-4 flex flex-wrap gap-x-5 gap-y-2">
              <li
                v-for="item in FREE_INCLUDES"
                :key="item"
                class="flex items-start gap-2 text-small text-[var(--text-muted)]"
              >
                <Check class="mt-0.5 size-4 shrink-0 text-[var(--success)]" aria-hidden="true" />
                {{ item }}
              </li>
            </ul>
          </div>
          <CsButton to="/lap-la-so">Lập lá số</CsButton>
        </div>
      </CsCard>

      <!-- auto-fit: số sản phẩm do DB quyết định, lưới phải tự co theo chứ
           không được cố định 4 cột rồi để thẻ thứ năm rớt xuống một mình. -->
      <div
        class="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-[repeat(auto-fit,minmax(15rem,1fr))]"
      >
        <CsCard
          v-for="product in products"
          :key="product.id"
          class="flex h-full flex-col"
          :class="product.is_featured && 'border-[var(--accent)]'"
        >
          <div class="flex min-h-14 items-start justify-between gap-2">
            <p class="font-display text-h3 text-[var(--text)]">{{ product.name }}</p>
            <CsPremiumBadge v-if="product.is_featured" label="Trọn gói" />
          </div>
          <p class="mt-3 font-display text-h2 text-[var(--text)]">{{ formatPrice(product) }}</p>
          <p class="mt-3 text-small text-[var(--text-muted)]">{{ product.description }}</p>
          <CsButton variant="secondary" class="mt-auto" block disabled>Sắp mở</CsButton>
        </CsCard>
      </div>

      <p class="mt-8 text-center text-caption text-[var(--text-subtle)]">
        Thanh toán sẽ mở khi phần luận giải sẵn sàng. Mình không thu tiền trước cho thứ chưa
        giao được.
      </p>
    </CsContainer>
  </section>
</template>
