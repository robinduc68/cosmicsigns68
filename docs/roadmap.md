# Lộ trình Cosmic Signs

Cập nhật: **2026-09-11**

Tài liệu này nói *đang ở đâu* và *đi tiếp thế nào*. Chi tiết kỹ thuật của từng
phần nằm trong `PROGRESS.md`; yêu cầu nghiệp vụ nằm trong `business.md`.

---

## ✅ Đã xong

### Phase 0 — Foundation
Monorepo pnpm (`apps/{api,web}`, `packages/{astrology-engine,shared,ui}`), Docker Compose
(Postgres 5436, Redis), Makefile, ESLint flat config + Prettier + ruff + mypy strict,
pytest + vitest. FastAPI với envelope `{data, meta, error}`, structlog + request id,
async SQLAlchemy 2.0 + Alembic.

### Phase 1 — Design System
`@cosmic/ui` là Nuxt layer: token CSS-first trên Tailwind v4 (sáng/tối, reduced-motion),
25 component dựng trên reka-ui, `useToast`. Showcase ở `/dev/design-system`, chặn bằng
route middleware nên **404 trên bản production** (đã kiểm chứng trên `.output`).

### Phase 2 — Homepage
Hero, 8 góc nhìn, khung địa bàn, cách hoạt động, vì sao Cosmic Signs, bảng giá, FAQ,
CTA cuối. SEO meta + OpenGraph. Bảng giá đọc từ `GET /api/v1/products`.

### Phase 3 — Create Chart UX
Wizard 3 bước → staged loading → `/chart/[id]`. Luật validate và điều hướng bước nằm
trọn trong Pinia store nên test được. `Idempotency-Key` chống double-submit.
Trang lá số hiển thị đủ 12 cung từ chart JSON, `noindex` vì là dữ liệu cá nhân.

---

### Phase 4–5 — Engine nền + Renderer
Lịch âm/dương, tứ trụ, 12 cung, Mệnh/Thân/Cục, Tuần/Triệt, 14 chính tinh, vòng Tràng
Sinh, đại vận. Hợp đồng dữ liệu lá số đóng băng ở schema v2
([`chart-data-contract.md`](chart-data-contract.md)). Renderer vẽ đủ lá số truyền
thống, xuất PNG/PDF ([`chart-renderer.md`](chart-renderer.md)).

**Tất cả ở mức `PROVISIONAL`** — chưa chốt ấn bản chuẩn nên chưa có gì `VERIFIED`.

---

## ⏭️ Làm tiếp

Ba phase dưới đây đều nằm trong `packages/astrology-engine`. **Không phase nào cần
frontend đổi cấu trúc** — web chỉ render chart JSON, thêm sao là thêm dữ liệu trong
`palaces[].major_stars` / `minor_stars` / `transformations`, các trường đã có sẵn.

### Phase 4 — Calendar Engine
> ⚠️ **Phần lớn đã xong từ Phase 0.** Đổi Dương ↔ Âm lịch chạy theo Meeus ch.49 đầy đủ
> kèm hiệu chỉnh ΔT, có 48 test đối chiếu ngày Tết chính thống 2000–2026 và tháng nhuận
> Quý Mão 2023. Còn lại là mở rộng dải năm kiểm chứng và chốt cách xử lý múi giờ lịch sử.

### Phase 5 — Tử Vi Chart Engine Foundation
> ⚠️ **Phần lớn đã xong từ Phase 0.** Tứ trụ, ngũ hổ độn, ngũ thử độn, nạp âm 60 hoa giáp,
> 12 cung, an Mệnh, an Thân, Cục, quan hệ Mệnh–Cục, Tuần, Triệt, tam phương tứ chính,
> vô chính diệu — đều đã có và có test.

### Phase 6 — Star Placement Engine ← **việc thật sự còn lại**
- **Chốt trường phái an sao** (Nam phái / Bắc phái) và nguồn đối chiếu để viết test.
  Đây là câu hỏi mở đang chặn mọi thứ, không phải việc code.
  → Toàn bộ quy ước và 12 câu hỏi cần chốt nằm ở
  [`astrology-conventions.md`](astrology-conventions.md); quy trình kiểm định ở
  [`astrology-verification.md`](astrology-verification.md).
  Chạy `make astrology-verification-report` để xem trạng thái hiện hành, và
  `make astrology-star-metadata-report` để xem độ phủ ngũ hành / âm dương của catalog sao.
- Kiểm định vị trí **14 chính tinh** (hiện ở stage `PREVIEW`, gắn cờ `provisional`,
  UI hiển thị dấu `*` và nói rõ là chưa kiểm định).
- Phụ tinh: Tứ Hoá, Lộc Tồn, Đào Hoa / Hồng Loan / Thiên Hỷ, Xương Khúc, Tả Hữu,
  Khôi Việt, Kình Đà, Không Kiếp, Hoả Linh, Đại/Tiểu Hao.
  → **Hợp đồng dữ liệu đã sẵn sàng đón chúng**: model sao đã chuẩn hóa một kiểu duy
  nhất với `category`, `strength` + `strength_verification`, `provenance`; cung đã có
  `annual_stars`, `cycles`, `month_number`. Thêm phụ tinh là điền giá trị, không phải
  đổi hợp đồng. Xem [`chart-data-contract.md`](chart-data-contract.md).
- Miếu vượng đắc hãm, đại vận, lưu niên.
- Khi đủ bộ thì nâng stage lên `FULL`, cờ `provisional` tắt, banner trên trang lá số
  tự biến mất.

---

## 🕓 Để sau

| Hạng mục | Phụ thuộc |
| --- | --- |
| **Rule / Analysis Engine** — sinh *facts + score + evidence* từ chart JSON | Phase 6. Không có nó thì không mở được section luận giải nào mà không bịa. |
| **Auth** — email/password + Google, vai trò USER/ADMIN | Bảng `users` đã có sẵn. Phải xong trước khi mở public. |
| **Payment** — PayOS/VietQR qua abstraction | Catalogue `products` đã sẵn sàng. |
| **Entitlement** — theo (user, chart, product) | Auth + Payment. Đây mới là nơi map 8 khía cạnh ↔ mã sản phẩm. |
| **Admin product management** — sửa giá, prompt, feature flag không cần deploy | Auth. Hiện sửa giá **chỉ làm được bằng SQL trực tiếp**. |
| **AI Interpretation** — chỉ nhận facts/evidence, chỉ tạo lời văn | Rule engine. |
| Compatibility, AI chat, share card, PDF export, blog/CMS | Sau MVP, có feature flag. |

---

## Ranh giới không được vượt

Nhắc lại từ `business.md` mục 3, vì đây là chỗ dễ trượt nhất khi làm nhanh:

1. **Pipeline một chiều, ba lớp không trộn:** CALCULATION (tất định, không AI) →
   INTERPRETATION RULES (facts + evidence) → LANGUAGE GENERATION (AI chỉ viết lời).
   AI không bao giờ được suy ra vị trí sao, Mệnh, Cục, Tuần, Triệt.
2. **Không fake dữ liệu.** Không hardcode kết quả lá số, không giả lập tính toán.
3. **Frontend không chứa business logic tử vi.** Web chỉ render chart JSON.
   Hằng số nào thuộc về tử vi thì đặt ở `packages/shared`, không rải trong component.
4. **Không hardcode giá, prompt, feature flag** vào frontend hay business logic.
5. **Dữ liệu ngày sinh là thông tin cá nhân.** UUID không đoán được, xoá được, không log thừa.
