# Tiến độ Cosmic Signs

Cập nhật: **2026-09-11** · Checkpoint để tiếp tục làm sau.

> Trạng thái từng phase và thứ tự làm tiếp: xem [`docs/roadmap.md`](docs/roadmap.md).

---

## Đang ở đâu

Xong **J1** — luồng "khách lạ → có lá số" đã chạy thông từ landing đến trang lá số.

| Phase | Trạng thái |
| --- | --- |
| Phase 0 — Foundation | ✅ xong |
| Phase 1 — Design System | ✅ xong |
| Phase 2 — Homepage | ✅ xong |
| Phase 3 — Create Chart UX | ✅ xong |
| Phase 4–6 — Astrology engine | ⏭️ tiếp theo, xem `docs/roadmap.md` |

Quality gate **đều xanh**: 131 test pass (92 engine + 21 api + 18 web),
ruff sạch, mypy strict sạch, eslint sạch, `nuxt typecheck` + `tsc` sạch,
`nuxt build` production thành công, backend import sạch.
Đã soát responsive thật bằng Chrome headless ở 375 / 390 / 430 / 768 / 1024 / 1440:
không trang nào tràn ngang, không vùng chạm nào dưới 24px.

---

## Đã xong

### Hạ tầng & tooling
- Monorepo pnpm workspace: `apps/{api,web}`, `packages/{astrology-engine,shared,ui}`, `docs/`, `infra/`
- `docker-compose.yml` — postgres (5436), redis (profile `cache`), api + web (profile `full`)
- `Makefile` đầy đủ target; `make lint typecheck test` chạy được hết
- ESLint flat config (TS + Vue, cấm `any`), Prettier, ruff, mypy strict, pytest, vitest

### `packages/astrology-engine` (Python) — **phần giá trị nhất đã xong**
- Đổi Dương ↔ Âm lịch theo Meeus ch.49 đầy đủ + hiệu chỉnh ΔT
- Can chi tứ trụ, ngũ hổ độn, ngũ thử độn, nạp âm 60 hoa giáp
- 12 cung, an Mệnh, an Thân, Cục, quan hệ Mệnh–Cục, Tuần, Triệt,
  tam phương tứ chính, vô chính diệu
- 14 chính tinh ở stage `PREVIEW`, đánh dấu `provisional`
- 48 test, đối chiếu ngày Tết chính thống 2000–2026 và tháng nhuận Quý Mão 2023

### `apps/api` (FastAPI)
- Envelope `{data, meta, error}`, structlog + request id, async SQLAlchemy 2.0, Alembic
- `GET /health`, `GET /ready`, `POST/GET/DELETE /api/v1/charts`
- `Idempotency-Key` chống double-submit — đã kiểm chứng bằng tay: gửi hai lần ra cùng một id
- **`GET /api/v1/products`** + `GET /api/v1/products/{code}` — bảng giá đọc từ bảng `products`.
  Giá là số nguyên đồng (`price_amount`), không bao giờ là float. `entitlements` là mảng vì
  `FULL_LIFETIME_READING` cấp nhiều quyền hơn chính mã của nó.
  Migration `070bdd944031` tạo bảng **và seed 4 sản phẩm với giá khởi điểm**; sau đó DB là
  nguồn duy nhất, admin đổi giá không cần deploy. Id sản phẩm cố định để mọi môi trường
  giống nhau. Đã kiểm chứng: `UPDATE products SET price_amount=…` là trang chủ đổi theo ngay.
- 21 test chạy trên SQLite

### `packages/shared` (TypeScript)
- `types/api.ts`, `types/chart.ts`, `schemas/birth.ts` (zod, khớp backend),
  `constants/astrology.ts` (có `BIRTH_HOUR_OPTIONS` — bảng canh giờ dùng cho picker),
  `constants/content.ts`

### `packages/ui` (Nuxt layer)
- `tokens.css` Tailwind v4, 25 component, `useToast`
- `vue` + `@nuxt/kit` khai báo là **peerDependencies**; bản thân hai gói này nằm ở
  devDependencies của root để vue-tsc resolve được từ `packages/ui` (xem "Bẫy đã gặp")

### `apps/web` (Nuxt 3) — **mới trong đợt này**
- Bootstrap: `nuxt.config.ts` (extends `@cosmic/ui`), `app.vue`, `error.vue`,
  `layouts/default.vue` (navbar + theme toggle + footer + disclaimer), `middleware/dev-only.ts`,
  `plugins/dev-mode.ts`, `composables/useApi.ts` (cửa duy nhất ra backend)
- `/dev/design-system` — showcase, chặn ở production bằng route middleware
- `/` — Hero, 8 góc nhìn, khung địa bàn, cách hoạt động (4 bước pipeline),
  vì sao Cosmic Signs (5 điểm), **bảng giá (lấy từ API, không có con số nào trong code)**,
  FAQ (6 câu), CTA cuối; SEO meta + OpenGraph
- `/lap-la-so` — wizard 3 bước (Thông tin → Ngày giờ sinh → Xác nhận) + staged loading,
  Pinia store `stores/chart.ts` giữ toàn bộ luật validate và điều hướng bước
- `/chart/[id]` — địa bàn 4×4 đủ 12 cung, Mệnh/Thân/Tuần/Triệt/nạp âm, tứ trụ ở giữa,
  8 section luận giải khoá bằng `CsLockedContent`, sao chép link, xoá lá số (có xác nhận),
  `noindex` vì lá số là dữ liệu cá nhân

---

## Việc tiếp theo — làm đúng thứ tự này

1. **Kiểm định 14 chính tinh** ← *bắt đầu từ đây*
   Đây là thứ chặn mọi thứ phía sau: chưa chốt trường phái an sao (Nam/Bắc phái) và
   chưa có nguồn đối chiếu để viết test. Cho tới lúc đó sao vẫn mang cờ `provisional`
   và UI vẫn phải nói rõ điều đó.
2. **Phụ tinh, tứ hoá, miếu vượng, đại vận, lưu niên** — phần còn thiếu của engine.
3. **Rule / Analysis engine** — sinh *facts + score + evidence* từ chart JSON.
   Không có nó thì không thể mở bất kỳ section luận giải nào mà không bịa.
4. **Auth** (email/password + Google). Phải xong trước khi mở public.
5. **Thanh toán** (PayOS/VietQR qua abstraction) + bảng `entitlements` theo
   (user, chart, product). Catalogue đã sẵn sàng, chỉ còn checkout và webhook.
   Cần luôn **admin API** để sửa giá — hiện chỉ sửa được bằng SQL.
6. **Nợ từ Phase 0** — còn 4 file trong `docs/`: `product-requirements.md`,
   `architecture.md`, `database-schema.md`, `design-system.md`.
   (`roadmap.md`, `astrology-engine.md`, `astrology-conventions.md` đã viết.)
7. **Dockerfile** cho `api` và `web` — compose profile `full` còn fail cho tới khi có.

---

## Cố ý chưa làm (không phải quên)

| Việc | Lý do |
| --- | --- |
| Section **testimonials** | Chưa có khách hàng thật. Bịa lời chứng thực cùng loại với "khan hiếm giả" mà business.md đã cấm. |
| **Insight nổi bật miễn phí** trên `/chart/[id]` | Cần rule engine mới có evidence để viết. Hiện chỉ hiển thị dữ kiện engine tính được. |
| Nút CTA trong phần khoá và trong bảng giá | Ghi "Sắp có" / "Sắp mở" vì chưa có checkout — không dẫn người dùng vào ngõ cụt, cũng không thu tiền trước cho thứ chưa giao được. |
| Map 8 khía cạnh ↔ mã sản phẩm | Quan hệ này chưa có trong dữ liệu; tự đoán ở frontend là bịa. Thuộc về bảng entitlement lúc làm thanh toán. |

---

## Khởi động lại môi trường

```bash
cd /home/reactplus/Documents/cosmicsigns68
make db-up          # postgres container (dữ liệu nằm trong volume, không mất)
make dev            # api :8100 + web :3100
make lint typecheck test
```

Kiểm tra nhanh cả chuỗi còn sống:

```bash
curl -s localhost:8100/health
curl -s -X POST localhost:8100/api/v1/charts -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: smoke-1' \
  -d '{"subject_name":"Nguyễn Văn A","gender":"MALE","calendar_type":"SOLAR",
       "birth_day":10,"birth_month":9,"birth_year":1992,"birth_hour":13}'
# rồi mở http://localhost:3100/chart/<id>
```

---

## Quyết định kỹ thuật đã chốt (đừng bàn lại)

| Quyết định | Lý do |
| --- | --- |
| Engine viết bằng **Python**, không phải TS | Cùng ngôn ngữ với backend, test chung, không rò rỉ ra frontend |
| **Tailwind v4** qua `@tailwindcss/vite` | Token CSS-first bằng `@theme`, ít lớp trung gian |
| **reka-ui** cho primitive có a11y | Cách tiếp cận shadcn-vue mà không cần CLI |
| `<select>` **native** thay vì listbox tự viết | Trên điện thoại dùng picker của hệ điều hành |
| **uv** để quản lý venv Python | Máy dev thiếu `python3-venv` |
| Cổng 3100/8100/5436/6382 | 3000/3001/5432 đã bị project khác chiếm |
| Chart id là **UUIDv4**, `user_id` nullable | Chưa có auth; id không đoán được là lớp bảo vệ duy nhất |
| Stage `FRAME` / `PREVIEW` / `FULL` | Không bịa số liệu: chưa kiểm định thì gắn cờ `provisional`, UI phải nói rõ |
| Picker giờ sinh chọn **canh giờ**, không phải giờ:phút | Bảng canh giờ nằm ở `packages/shared`, không để frontend tự quy đổi (nguyên tắc #3) |
| Toàn bộ luật wizard nằm trong **Pinia store** | Component chỉ render; "không cho nhảy bước" được test được |

---

## Bẫy đã gặp (đừng mất thời gian lại)

- `make typecheck` từng chết vì script root gọi `pnpm` trần trong khi máy chỉ có shim
  `corepack pnpm`. Makefile giờ gọi thẳng `$(PNPM) -r --workspace-concurrency=1 typecheck`.
  pnpm 12 **không có** cờ `--sequential`.
- `packages/ui` import `vue` và `@nuxt/kit` nhưng không khai báo → vue-tsc báo hơn 200 lỗi
  `Property ... does not exist on type '{}'`, tất cả chỉ vì một lỗi gốc `Cannot find module 'vue'`.
  Khai báo chúng là `dependencies` lại càng hỏng: pnpm resolve ra biến thể không có peer
  (`vue@3.5.42`) mà nó không bao giờ tạo ra trong store, để lại symlink treo.
  Cách đúng: **peerDependencies** ở `packages/ui` + devDependencies ở root.
- `useAsyncData` **bọc lỗi gốc lại**, nên `ApiError` nằm ở `error.value.cause`.
  Kiểm tra nhầm ở `error.value` thì mọi lá số không tồn tại đều trả 500 thay vì 404.
- Test backend dựng schema bằng `create_all`, **không chạy migration**, nên dữ liệu seed
  trong migration không có trong test. Test nào cần sản phẩm thì phải tự insert.
- `nuxt build` **không chạy được khi dev server đang bật** (lock file). Tắt dev trước.
- Nuxt **inline toàn bộ CSS vào HTML**, không sinh file `.css` trong `.output/public`.
  Không thấy `<link rel=stylesheet>` là bình thường, không phải build hỏng.
- Lưới bảng giá phải là `auto-fit`: số sản phẩm do DB quyết định, cố định 4 cột thì
  sản phẩm thứ năm rớt xuống một mình.

---

## Hạn chế đã biết

- **Chưa có auth** — ai giữ được UUID thì xem được lá số đó.
- **14 chính tinh chưa được kiểm định**; phụ tinh, miếu vượng, tứ hóa, đại vận, lưu niên chưa làm.
- Chưa chốt **trường phái an sao** và nguồn đối chiếu để viết test. Toàn bộ 12 câu
  hỏi cần chốt đã được liệt kê ở `docs/astrology-conventions.md` — đây là thứ chặn Phase 6.
- **Giờ Tý muộn (23:xx) đang xử lý không nhất quán**: trụ ngày dịch sang ngày sau
  nhưng ngày âm thì không, mà Tử Vi lại an theo ngày âm. Chờ quyết định Q6, đừng sửa vội.
- Staged loading ở `/lap-la-so` chạy theo nhịp thời gian vì API chỉ trả về một lần ở cuối.
  Phần reveal luôn đợi phản hồi thật, không có chặng nào tự nhận "xong" khi lá số chưa về.
- `birth_place` mới chỉ lưu lại, **chưa dùng để suy ra múi giờ**.
- Sửa giá hiện chỉ làm được bằng SQL trực tiếp — chưa có admin API.
- Redis khai báo trong compose nhưng **chưa dùng**.
- Dockerfile cho `api` và `web` **chưa viết**.
- AI và thanh toán: chưa đụng tới.
