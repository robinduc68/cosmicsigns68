# Tiến độ Cosmic Signs

Cập nhật: **2026-09-11** · Checkpoint để tiếp tục làm sau.

> Đọc `docs/chart-data-contract.md` trước khi đụng vào hình dạng dữ liệu lá số.

> Trạng thái từng phase và thứ tự làm tiếp: xem [`docs/roadmap.md`](docs/roadmap.md).

---

## Đang ở đâu

Luồng "khách lạ → có lá số" chạy thông, **lá số vẽ được đầy đủ theo lối truyền thống**,
và engine đã có vòng Tràng Sinh + đại vận.

| Phase | Trạng thái |
| --- | --- |
| Phase 0 — Foundation | ✅ xong |
| Phase 1 — Design System | ✅ xong |
| Phase 2 — Homepage | ✅ xong |
| Phase 3 — Create Chart UX | ✅ xong |
| Phase 4 — Calendar / tứ trụ / 12 cung | ✅ xong (PROVISIONAL) |
| Phase 5 — Renderer lá số | ✅ xong |
| Phase 6 — An sao | 🟡 27 sao + Tứ Hóa; miếu vượng đã nối nhưng **bảng còn rỗng** |

Hồ sơ quy ước đang dùng: **`COSMIC_SIGNS_NAM_PHAI_V1`** — đã nêu trường phái (Nam phái)
nhưng **chưa chốt ấn bản**, nên mọi luật an sao vẫn `PROVISIONAL`.

Quality gate **đều xanh**: **658 test pass** (445 engine + 41 api + 172 web),
ruff sạch, mypy strict sạch, eslint sạch, `nuxt typecheck` + `tsc` sạch,
`nuxt build` production thành công.
Đã soát responsive thật bằng Chrome headless ở 375 / 390 / 430 / 768 / 1024 / 1440.

> **Điều quan trọng nhất cần nhớ khi mở lại:** engine **chưa có nguồn chuẩn nào được
> chốt** (`sources.json` rỗng, `primary_selected_reference: null`). Vì vậy **không quy
> tắc an sao nào là `VERIFIED`**, banner `ENGINE PROVISIONAL — NOT FOR CUSTOMER USE`
> vẫn phải hiện, và không được bán lá số. Đây là quyết định, không phải việc chưa làm.
> Xem `docs/astrology-conventions.md` mục 0.

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
- **Hệ quy ước (`conventions/`)**: 23 `RuleId`, mỗi luật gắn policy + `VerificationStatus`
  + provenance + câu hỏi mở đang chặn. Luật chưa chốt thì engine **dừng**, không đoán.
  `needs_recalculation()` so cả hồ sơ quy ước lẫn `engine_version`.
- **Catalog sao (`stars/catalog.py`)**: định danh, ngũ hành, âm dương, category,
  display priority. Luật an sao chỉ mang **id**, không mang tên — một nguồn sự thật.
- **Vòng Tràng Sinh + đại vận (`cycles/`)**: 12 chặng, chiều, tuổi khởi, dãy 12 đại vận.
  Làm trên **chỉ số địa chi**, tên 12 cung không đảo theo.
- **Phụ tinh nhóm 1 (`stars/placement.py`)** theo Nam phái: Xương Khúc, Tả Hữu, Khôi Việt,
  Lộc Tồn, Kình Đà, Đào Hoa, Hồng Loan, Thiên Hỷ, Thiên Mã. Mỗi hàm trả về **một địa chi**;
  tên cung và toạ độ lưới là hai chuyện khác. 4 bất biến kiểm được không cần nguồn ngoài.
- **Độ sáng (`stars/strength.py`)**: tra cứu `star_id + địa chi` đã nối xong, render
  dạng `THÁI ÂM (M)`. **Bảng 168 ô còn RỖNG** — phải do người thẩm định chép từ nguồn
  vào `stars/data/nam_phai_star_strength_v1.json`. Engine từ chối nạp bảng điền nửa vời.
  `make astrology-star-strength-report`.
- **Tứ Hóa (`stars/four_transformations.py`)**: bảng 10 can × 4 hóa. **Không sinh sao mới** —
  hóa gắn vào sao đã an, nên tổng sao không đổi theo năm sinh. Hàng Canh chọn phương án 1
  (Thái Âm Khoa, Thiên Đồng Kỵ); cả 3 biến thể nằm sẵn trong `CANH_VARIANTS`, **Q7 vẫn mở**.
- **Bàn kiểm định (`review/`)** + trace giải thích được từng bước (inputs, policy,
  rule id, convention, source, verification).
- 355 test, đối chiếu ngày Tết chính thống 2000–2026 và tháng nhuận Quý Mão 2023

### Renderer lá số (`apps/web/components/astrology/chart/`)
- Canvas cố định 1400×1750, lưới 4×4 theo địa bàn; zoom/pan, chế độ đọc từng cung
- Xuất PNG 2800×3500 và In/PDF qua canvas ngoài màn hình (ghi chú dev không lọt vào)
- Màu chữ sao theo **ngũ hành**, bằng class ngữ nghĩa; không có ánh xạ nào từ tên sao
- Trung tâm đủ 15 mục truyền thống; dòng chưa có dữ liệu thì **bỏ hẳn**, không lấp
- Toàn bộ diễn đạt tiếng Việt nằm ở `utils/tuvi-format.ts`

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

0. **Chốt ấn bản chuẩn (Q1/Q2/Q3)** ← *đây là việc của con người, không phải việc code*
   Đây là thứ chặn mọi thứ phía sau. Cần một cuốn sách cụ thể và một người thẩm định
   ký duyệt. Chừng nào chưa có, mọi quy tắc an sao ở lại `PROVISIONAL` và không lá số
   nào được bán. Danh sách đầy đủ ở `docs/astrology-conventions.md` mục 0.
   Việc code duy nhất liên quan: điền `tests/fixtures/sources.json` khi đã chốt.
1. **Kiểm định 14 chính tinh** — dùng bàn kiểm định nội bộ ở `/_internal/astrology-verification`.
   Quy trình chống tự xác nhận đã dựng sẵn: không được tự nâng nhãn chỉ vì test xanh.
2. **Phụ tinh nhóm 2** (Không Kiếp, Hỏa Linh, Khốc Hư, Long Phượng, Tam Thai Bát Tọa,
   Thai Phụ Phong Cáo, Ân Quang Thiên Quý, Cô Thần Quả Tú, Đại/Tiểu Hao, vòng Thái Tuế,
   vòng Bác Sĩ) → **Tứ Hóa** (Q7/Q8/Q9) → **Miếu/Vượng/Đắc/Hãm** (bảng 168 ô, phải chép
   từ nguồn, tuyệt đối không bịa) → **lưu niên** (chặn bởi Q11/Q12).
   Nhóm 1 đã chứng minh đường ống: thêm sao = thêm luật trong `stars/placement.py` +
   mục trong catalog + một dòng trong `_SUPPORTING_GROUP_1`. **Không đụng frontend.**
3. **Rule / Analysis engine** — sinh *facts + score + evidence* từ chart JSON.
   Không có nó thì không thể mở bất kỳ section luận giải nào mà không bịa.
4. **Auth** (email/password + Google). Phải xong trước khi mở public.
5. **Thanh toán** (PayOS/VietQR qua abstraction) + bảng `entitlements` theo
   (user, chart, product). Catalogue đã sẵn sàng, chỉ còn checkout và webhook.
   Cần luôn **admin API** để sửa giá — hiện chỉ sửa được bằng SQL.
6. **Nợ từ Phase 0** — còn 4 file trong `docs/`: `product-requirements.md`,
   `architecture.md`, `database-schema.md`, `design-system.md`.
   (`roadmap.md`, `astrology-engine.md`, `astrology-conventions.md`,
   `astrology-verification.md` đã viết.)
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
| Mọi quy tắc phụ thuộc trường phái nằm trong **ConventionProfile**, không nấp trong code | Hai lá số theo hai giả định khác nhau không thể bị nhầm là một; quy tắc chưa chốt thì engine dừng thay vì đoán |
| Múi giờ tra **IANA tzdb**, `tzdata` ghim thành dependency | Hardcode +7 sai nguyên giờ với người sinh 1960–1975; và hai máy không được bất đồng về năm 1968 |

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

- **Ảnh PNG xuất ra vỡ dòng dù màn hình vẫn đẹp**: `modern-screenshot` chép nguyên kích
  thước đo được của từng phần tử; chữ rộng hơn chút trong SVG là gãy dòng, đè hàng dưới.
  Nhãn ngắn trên canvas phải `white-space: nowrap`. Xem `docs/chart-renderer.md`.
- **Cỡ chữ phải đặt trên `li`, không chỉ trên `span` bên trong**: `li` giữ line-height 1.5
  kế thừa từ trang, mỗi hàng sao cao ~27 px thay vì ~21 px và cung đầy bị cắt mất hàng cuối.
- **`Math.sin/cos` lệch ở chữ số cuối giữa Node và Chrome** → lỗi hydration trên thuộc
  tính SVG. Làm tròn tọa độ trước khi render.
- **Đừng ẩn canvas cho tới khi chunk lazy tải xong**: route vào lần đầu chỉ thấy ô trống.
  Scale ngay khi mount, thư viện tương tác tới sau.
- **Tiến trình API không tự nạp lại code engine**: sau khi sửa engine phải khởi động lại
  uvicorn, nếu không lá số mới vẫn mang `engine_version` cũ.

## Hạn chế đã biết

- **Chưa có auth** — ai giữ được UUID thì xem được lá số đó.
- **14 chính tinh chưa được kiểm định**; phụ tinh, miếu vượng, tứ hóa, lưu niên chưa làm.
  Vòng Tràng Sinh và đại vận **đã làm** nhưng ở mức `PROVISIONAL`.
- **Bảng miếu vượng RỖNG (0/324 ô).** Mọi `star.strength` là `null`, lá số render tên
  sao trơn. Đây là trạng thái đúng — 168 ô không suy ra được bằng công thức, phải chép
  từ ấn bản. Chặn bởi Q2/Q3.
- **Tứ Hóa hàng Canh đang chọn phương án 1.** Phương án 1 và 2 **đảo Khoa với Kỵ** —
  chọn nhầm lật cát tinh thành hung tinh trên mọi lá số sinh năm Canh. Cần Q3 quyết.
- **Ngũ hành của sao: 23/27**. Để trống: Tham Lang, Cự Môn, Hữu Bật, Đào Hoa — các
  trường phái ghi khác nhau, vẽ bằng mực trung tính, không đoán.
  `make astrology-star-metadata-report`.
- **Hai phân kỳ trường phái đang chọn theo cách đọc đa số**, cả hai cách đều ghi trong
  policy: Thổ cục khởi Tràng Sinh ở Thân hay Dần; chiều vòng Tràng Sinh theo âm dương
  nam nữ hay theo âm dương Cục. Xem `docs/astrology-conventions.md` mục 24.
- Chưa chốt **trường phái an sao** và nguồn đối chiếu để viết test. Toàn bộ 12 câu
  hỏi cần chốt đã được liệt kê ở `docs/astrology-conventions.md` — đây là thứ chặn Phase 6.
- **Giờ Tý muộn (23:xx)**: mâu thuẫn code đã gỡ — quyết định nay thuộc `LateZiPolicy`
  trong hồ sơ quy ước, và engine **từ chối** lập lá số sinh 23:xx thay vì đoán.
  Nhưng **Q6 vẫn chưa được trả lời**; cái đã sửa là chỗ để câu trả lời.
- **Múi giờ đã sửa**: offset tra từ IANA tzdb tại thời điểm sinh thay vì cứng +7.
  Khoảng **5% ngày sinh trong 1960–1975 ra lá số khác trước đây** (miền Nam chạy
  UTC+8 giai đoạn đó). Lá số sau 1975 không đổi.
- Staged loading ở `/lap-la-so` chạy theo nhịp thời gian vì API chỉ trả về một lần ở cuối.
  Phần reveal luôn đợi phản hồi thật, không có chặng nào tự nhận "xong" khi lá số chưa về.
- `birth_place` mới chỉ lưu lại, **chưa dùng để suy ra múi giờ**.
- Sửa giá hiện chỉ làm được bằng SQL trực tiếp — chưa có admin API.
- Redis khai báo trong compose nhưng **chưa dùng**.
- Dockerfile cho `api` và `web` **chưa viết**.
- AI và thanh toán: chưa đụng tới.
