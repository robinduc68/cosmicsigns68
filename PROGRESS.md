# Tiến độ Cosmic Signs

Cập nhật: **2026-09-10** · Checkpoint để tiếp tục làm sau.

---

## Đang ở đâu

Đang giữa **Phase 1 (Design System)** trong chuỗi PROMPT 0 → 3.

| Phase | Trạng thái |
| --- | --- |
| PROMPT 0 — Foundation / Architecture | ✅ ~85% (thiếu bộ `docs/`) |
| PROMPT 1 — Design System + Brand | 🟡 ~70% (còn showcase page + wire vào app) |
| PROMPT 2 — Homepage | ⬜ chưa bắt đầu |
| PROMPT 3 — Create Chart UX | ⬜ chưa bắt đầu |

Toàn bộ quality gate hiện tại **đều xanh**: 63 test pass (48 engine + 15 api),
ruff sạch, mypy strict sạch, tsc sạch.

---

## Đã xong

### Hạ tầng & tooling
- Monorepo pnpm workspace: `apps/{api,web}`, `packages/{astrology-engine,shared,ui}`, `docs/`, `infra/`
- `docker-compose.yml` — postgres (5436), redis (profile `cache`), api + web (profile `full`)
- `Makefile` với đầy đủ target: `setup`, `dev`, `migrate`, `lint`, `typecheck`, `test`…
- `.env.example`, `.gitignore`, `.editorconfig`, `.prettierrc.json`, `eslint.config.mjs`, `tsconfig.base.json`
- ESLint flat config (TS + Vue, cấm `any`), Prettier, ruff (lint + format), mypy strict, pytest
- `README.md`, `business.md`

### `packages/astrology-engine` (Python) — **phần giá trị nhất đã xong**
- Chuyển đổi Dương ↔ Âm lịch theo thuật toán thiên văn, đã **nâng lên Meeus ch.49 đầy đủ + hiệu chỉnh ΔT**
  vì bản rút gọn sai tới ~43 phút, đủ để lệch mùng 1 và làm sai cả lá số
- Can chi tứ trụ (năm/tháng/ngày/giờ), ngũ hổ độn, ngũ thử độn, nạp âm 60 hoa giáp
- Khung lá số: 12 cung (địa chi + thiên can + nạp âm), an Mệnh, an Thân, Cục,
  quan hệ Mệnh–Cục (sinh/khắc/hòa), Tuần không, Triệt lộ, tam phương tứ chính, vô chính diệu
- 14 chính tinh ở stage `PREVIEW`, đánh dấu `provisional` (chưa có bộ test đối chiếu)
- 48 test, đối chiếu với ngày Tết chính thống 2000–2026 và tháng nhuận Quý Mão 2023

### `apps/api` (FastAPI)
- Response envelope thống nhất `{data, meta, error}` + exception handler tiếng Việt
- Structured JSON logging (structlog) + request id middleware
- Async SQLAlchemy 2.0 + asyncpg, Alembic (async env), migration đầu tiên đã chạy trên Postgres thật
- Models: `users`, `charts` (UUID, JSONB, `idempotency_key` chống double-submit)
- Endpoints: `GET /health`, `GET /ready`, `POST/GET/DELETE /api/v1/charts`
- Layer tách bạch: router → service → repository → engine
- 15 test chạy trên SQLite (không cần Docker)

### `packages/shared` (TypeScript)
- `types/api.ts` (envelope + `ApiError`), `types/chart.ts` (mirror payload engine)
- `schemas/birth.ts` — zod schema khớp với validation backend
- `constants/astrology.ts`, `constants/content.ts`

### `packages/ui` (Nuxt layer)
- `assets/css/tokens.css` — Tailwind v4, brand violet, semantic token, dark/light,
  typography scale (display/h1/h2/h3/body/small/caption), reduced-motion
- **25 component**: Button, IconButton, Card, Badge, PremiumBadge, Container, SectionHeading,
  Skeleton, Logo, FormField, Input, Textarea, Select, Checkbox, RadioGroup, Dialog, Drawer,
  Tooltip, Popover, Dropdown, Tabs, Toaster, EmptyState, ErrorState, LockedContent
- `composables/useToast.ts`

---

## Việc tiếp theo — làm đúng thứ tự này

1. **Bootstrap `apps/web`** ← *bắt đầu từ đây*
   Hiện chỉ có `package.json` (deps đã cài). Còn thiếu:
   `nuxt.config.ts` (extends `@cosmic/ui`, modules: `@nuxt/fonts`, `@nuxtjs/color-mode`,
   `@pinia/nuxt`, `@vueuse/nuxt`, plugin `@tailwindcss/vite`), `app.vue`, `layouts/default.vue`,
   `tsconfig.json`, `vitest.config.ts`.
   → Xong bước này `make dev-web` phải chạy được.

2. **Design system showcase** `/dev/design-system`, chặn ở production bằng route middleware.
   Review đủ 6 breakpoint: 375 / 390 / 430 / 768 / 1024 / 1440.

3. **Chốt Phase 1**: `make lint typecheck test`.

4. **PROMPT 2 — Homepage** `/`: navbar, hero (headline đã chốt trong prompt), 13 section,
   8 insight card lấy từ `INSIGHT_CATEGORIES`, SEO meta + OpenGraph. CTA trỏ `/lap-la-so`.

5. **PROMPT 3 — Create Chart UX** `/lap-la-so`: wizard 5 bước, staged loading,
   redirect `/chart/[id]`. Backend **đã sẵn sàng**, chỉ cần gọi `POST /api/v1/charts`
   kèm header `Idempotency-Key`. Cần thêm: `composables/useApi.ts` (client tập trung),
   Pinia store `chart`, trang `/chart/[id]`.

6. **Nợ từ Phase 0** — 6 file trong `docs/`:
   `product-requirements.md`, `architecture.md`, `database-schema.md`,
   `design-system.md`, `astrology-engine.md`, `roadmap.md`.

---

## Khởi động lại môi trường

```bash
cd /home/reactplus/Documents/cosmicsigns68
make db-up          # postgres container (dữ liệu nằm trong volume, không mất)
make dev-api        # http://localhost:8100/docs
make test           # xác nhận vẫn xanh
```

Kiểm tra nhanh API còn sống:

```bash
curl -s localhost:8100/health
curl -s -X POST localhost:8100/api/v1/charts -H 'Content-Type: application/json' \
  -d '{"subject_name":"Nguyễn Văn A","gender":"MALE","calendar_type":"SOLAR",
       "birth_day":10,"birth_month":9,"birth_year":1992,"birth_hour":14}'
```

---

## Quyết định kỹ thuật đã chốt (đừng bàn lại)

| Quyết định | Lý do |
| --- | --- |
| Engine viết bằng **Python**, không phải TS | Cùng ngôn ngữ với backend, test chung, không rò rỉ ra frontend |
| **Tailwind v4** qua `@tailwindcss/vite`, không dùng `@nuxtjs/tailwindcss` | Token CSS-first bằng `@theme`, ít lớp trung gian |
| **reka-ui** cho primitive có a11y (dialog, tabs, popover…) | Cách tiếp cận shadcn-vue mà không cần CLI |
| `<select>` **native** thay vì listbox tự viết | Trên điện thoại dùng picker của hệ điều hành — nhanh và dễ tiếp cận hơn |
| **uv** để quản lý venv Python | Máy dev thiếu `python3-venv`, uv không cần `ensurepip` |
| Cổng 3100/8100/5436/6382 | 3000/3001/5432 đã bị project khác chiếm |
| Chart id là **UUIDv4**, `user_id` nullable | Chưa có auth; id không đoán được là lớp bảo vệ duy nhất hiện tại |
| Stage `FRAME` / `PREVIEW` / `FULL` | Không bịa số liệu: cái gì chưa kiểm định thì gắn cờ `provisional`, UI phải hiển thị rõ |

---

## Hạn chế đã biết

- **Chưa có auth** — ai giữ được UUID thì xem được lá số đó. Phải làm trước khi mở public.
- **14 chính tinh chưa được kiểm định** bằng bộ ca chuẩn; phụ tinh, miếu vượng, tứ hóa,
  đại vận, lưu niên **chưa làm**.
- Chưa chốt **trường phái an sao** (Nam phái / Bắc phái) và nguồn đối chiếu để viết test.
- `apps/web` chưa chạy được (thiếu `nuxt.config.ts`).
- Redis khai báo trong compose nhưng **chưa dùng**.
- Dockerfile cho `api` và `web` **chưa viết** (compose profile `full` sẽ fail cho tới khi có).
- AI và thanh toán: chưa đụng tới, đúng theo yêu cầu của PROMPT 0.
