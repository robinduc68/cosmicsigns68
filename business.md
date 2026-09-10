# COSMIC SIGNS — Business & Product Requirements Note

> Tài liệu này là bản **đọc – hiểu – chốt lại** yêu cầu nghiệp vụ trước khi viết bất kỳ dòng code nào.
> Nó trả lời: *sản phẩm là gì, bán cho ai, bán cái gì, ràng buộc nào là bất biến, đâu là ranh giới của MVP.*
> Các quyết định **kỹ thuật chi tiết** (schema, API contract, folder structure, design tokens) sẽ nằm ở
> `docs/architecture.md`, `docs/database-schema.md`, `docs/design-system.md`, `docs/astrology-engine.md`, `docs/roadmap.md`.
>
> Trạng thái: **v1 — draft chốt phạm vi** · Ngày: 2026-09-10 · Owner: ducnv1

---

## 0. Hiện trạng repository (kết quả inspect)

| Hạng mục | Kết quả |
|---|---|
| Repo | `/home/reactplus/Documents/cosmicsigns68`, branch `main`, **0 commit**, không có file nào ngoài `.git` |
| Stack hiện tại | **Không có** — greenfield hoàn toàn |
| Code có thể reuse | Không có |
| Code cần refactor | Không có |
| Thứ còn thiếu | **Toàn bộ**: monorepo skeleton, web, api, astrology-engine, DB, CI, docs, infra |

Tooling sẵn có trên máy dev: Node `v20.20.2`, npm `10.8.2`, Python `3.12.3`, Docker `29.3.1` + compose plugin, `psql` 16 client, GNU Make `4.3`.
**Thiếu:** `pnpm` (sẽ bật qua `corepack enable`), `redis-cli` (không bắt buộc — Redis chạy trong Docker).

Hệ quả: không có ràng buộc legacy → được tự do chọn kiến trúc sạch ngay từ đầu, nhưng **phải tự kỷ luật** về ranh giới module (mục 3).

---

## 1. Sản phẩm là gì

**Cosmic Signs** là nền tảng web (mobile-first) lập và luận giải **lá số Tử Vi Đẩu Số**:
người dùng nhập ngày–giờ–nơi sinh → hệ thống **tự tính** lá số bằng engine tất định →
hiển thị lá số trực quan → **AI diễn giải** dữ liệu đã tính thành bản luận giải có cấu trúc →
người dùng mua gói để mở khoá phần chuyên sâu, chat hỏi thêm, và xuất PDF.

**Một câu định vị:** *Không phải web bói toán. Là công cụ giúp bạn hiểu chính mình, có dữ liệu và có lập luận.*

**Không phải:** landing page demo, blog tử vi, chatbot bói tổng quát, dịch vụ xem bói người thật.

### 1.1 Vấn đề đang giải quyết

1. Web tử vi hiện tại: giao diện cũ, quảng cáo dày, tin cậy thấp, khó dùng trên điện thoại.
2. Nội dung luận giải chung chung, copy–paste theo sao, không gắn với lá số cụ thể.
3. Các app dùng LLM thì **để AI tự bịa lá số** → sai vị trí sao, sai Mệnh/Cục, mất uy tín ngay khi người biết nghề đọc.
4. Không có nơi lưu lại lá số của mình và người thân để xem lại, đối chiếu theo thời gian.

### 1.2 Khác biệt cốt lõi (bán được vì cái này)

- **Engine tính toán riêng, tất định** — cùng input luôn ra cùng lá số, có test đối chiếu.
- **AI chỉ diễn giải, không tính** — mọi luận điểm phải trỏ được về *evidence* trong chart JSON.
- **Luận giải có cơ chế**: dấu hiệu → cơ chế → biểu hiện thực tế, không phán mơ hồ hai chiều.
- **Trải nghiệm premium**: đẹp trên điện thoại, tối giản, huyền bí nhưng hiện đại.
- **Lưu trữ & sở hữu**: nhiều lá số/tài khoản, xem lại bất kỳ lúc nào, xuất PDF, xoá được dữ liệu.

---

## 2. Đối tượng người dùng

| Persona | Mô tả | Job-to-be-done | Sẵn sàng trả tiền cho |
|---|---|---|---|
| **P1 — Người tò mò về bản thân** (22–35, nữ nhiều hơn) | Biết tử vi qua mạng xã hội, không rành thuật ngữ | "Hiểu tính cách, điểm mạnh/yếu của mình" | Gói trọn đời, share card |
| **P2 — Người đang ở ngã rẽ** (26–40) | Đổi việc, khởi nghiệp, chuyện tình cảm, mua nhà | "Năm nay nên tiến hay thủ? Vì sao mình cứ đổi việc?" | Gói Sự nghiệp / Tài chính / Tình yêu, lưu niên |
| **P3 — Người có nền tử vi** | Đọc được lá số, khắt khe về tính đúng | "Lập lá số nhanh, chuẩn, xem tam phương tứ chính" | Trọn đời + PDF; là nhóm **thẩm định uy tín** cho sản phẩm |
| **P4 — Người xem cho gia đình/người yêu** | Đã tin sản phẩm | "Xem cho bố mẹ, người yêu; so đôi" | Nhiều lá số, Compatibility |
| **P5 — Admin/vận hành nội bộ** | Team Cosmic Signs | "Chỉnh giá, prompt, xem doanh thu, chi phí AI" | — |

**Nhóm quyết định chất lượng:** P3 (đúng sai của engine) và P1/P2 (chuyển đổi doanh thu). Sai với P3 → mất uy tín; xấu/khó dùng với P1 → không có doanh thu. Phải đạt cả hai.

---

## 3. Nguyên tắc bất biến (không được vi phạm ở bất kỳ đâu)

1. **Pipeline một chiều, tách 3 lớp:**
   `Birth Info → Calendar Conversion → Deterministic Astrology Engine → Chart JSON → Rule/Analysis Engine → AI Interpretation → Reading`
   - **CALCULATION**: 100% tất định, không AI, không random, có test.
   - **INTERPRETATION RULES**: logic có cấu trúc, cho ra *facts + score + evidence*.
   - **LANGUAGE GENERATION**: AI, chỉ nhận facts/evidence đã có, chỉ tạo lời văn.
   - Ba lớp **không được trộn**. AI không bao giờ được suy ra vị trí sao, Mệnh, Cục, Tuần, Triệt.
2. **Không fake dữ liệu**: không hardcode kết quả lá số, không giả lập tính toán, không seed kết quả AI vào production.
3. **Frontend không chứa business logic tử vi.** Web chỉ render chart JSON.
4. **Không hardcode giá, prompt, feature flag vào frontend/business logic** — nằm ở DB/config, admin sửa được.
5. **Provider abstraction**: LLM và Payment đều đi qua interface; đổi nhà cung cấp không đụng domain logic.
6. **Dữ liệu ngày sinh là thông tin cá nhân**: UUID không đoán được, xoá được, không log thừa.
7. **Definition of Done > "chạy được"** (mục 13).

---

## 4. Phạm vi nghiệp vụ (feature inventory)

### 4.1 Public / Marketing
- Landing page (Hero + 9 section: góc nhìn, demo chart, how-it-works, why, pricing, testimonials, FAQ, CTA, footer).
- SEO pages: `/tu-vi`, `/la-so-tu-vi`, `/tu-vi-{year}`, `/blog/[slug]`.
- Trang pháp lý: Privacy, Terms, Disclaimer.

### 4.2 Tài khoản
- Đăng ký/đăng nhập bằng **email + mật khẩu** và **Google**. (Magic link: kiến trúc chừa sẵn, chưa bật.)
- Quên mật khẩu, đổi mật khẩu, xoá tài khoản (xoá dữ liệu thật).
- Vai trò: `USER`, `ADMIN`.

### 4.3 Lập lá số (`/lap-la-so`)
- Wizard 4 bước: Thông tin cá nhân → Ngày giờ sinh → Xác nhận → Lập lá số.
- Input: họ tên, giới tính (Nam/Nữ), ngày sinh (**Dương lịch hoặc Âm lịch**), giờ sinh, nơi sinh, timezone, ghi chú, nhãn quan hệ (`relationship_label`).
- Không hỏi dồn; có progress indicator; validate rõ ràng, thân thiện.
- Màn hình tạo lá số kể được tiến trình thật ("Đang chuyển đổi lịch…", "Đang an Mệnh và Thân…", …) rồi reveal chart.

### 4.4 Astrology Engine (giá trị lõi)
- Chuyển đổi Dương ↔ Âm lịch, can chi năm/tháng/ngày/giờ.
- An Mệnh, Thân, **12 cung** (Mệnh, Phụ Mẫu, Phúc Đức, Điền Trạch, Quan Lộc, Nô Bộc, Thiên Di, Tật Ách, Tài Bạch, Tử Tức, Phu Thê, Huynh Đệ).
- Âm dương, ngũ hành nạp âm, **Cục** và quan hệ **Mệnh – Cục** (sinh/khắc/hoà).
- **14 chính tinh**, hệ **phụ tinh** (Tứ Hoá, Lộc Tồn, Đào Hoa/Hồng Loan/Thiên Hỷ, Xương Khúc, Tả Hữu, Khôi Việt, Kình Đà, Không Kiếp, Hoả Linh, Đại/Tiểu Hao…).
- **Tuần / Triệt**, **miếu vượng đắc bình hãm**, **vô chính diệu** (`is_empty_main_star`, mượn chính tinh đối cung).
- **Tam phương tứ chính**: hàm truy vấn cung chính / tam hợp / đối cung.
- **Đại vận** (MajorCycle) và **Lưu niên** (AnnualCycle) theo năm động, không hardcode năm. Lưu nguyệt: chừa kiến trúc, chưa bật.
- Output: **Chart JSON có cấu trúc**, data-driven, star data không nằm trong UI.

### 4.5 Rule / Analysis Engine
- Nhận Chart JSON → sinh **analytical facts** dạng `{type, score, evidence[]}`.
- **Core Theme Engine**: rút ra 3–5 trục chính của lá số (vd: tự chủ vs phụ thuộc, chuyên môn vs thương mại, ổn định vs biến động) kèm evidence.
- Mọi claim gửi cho AI đều phải có `evidence[]` (chống hallucination).

### 4.6 Chart page (`/chart/[id]`) — màn hình quan trọng nhất
- Desktop: lá số trái / insight phải. Mobile: chart trên, tabs dưới (Tổng quan, Mệnh, Sự nghiệp, Tài chính, Tình yêu, Vận hạn).
- Lá số vẽ bằng CSS Grid/SVG, 12 cung quanh trung cung; trung cung hiển thị tên, ngày sinh dương/âm, Mệnh, Cục, Thân cư.
- Mỗi cung: tên cung, can chi, chính tinh, phụ tinh, trạng thái miếu/vượng/đắc/hãm, Tuần/Triệt, nhãn quan trọng.
- Zoom, fullscreen, export ảnh. Chữ phải đọc được trên màn 375px.

### 4.7 Luận giải AI
- Sections: Tổng quan, Mệnh & tính cách, Sự nghiệp, Tài chính, Tình yêu, Hôn nhân, Gia đình, Sức khoẻ, Quan hệ xã hội, Thiên di, Đại vận, Năm hiện tại, Điểm mạnh, Điểm cần lưu ý.
- LLM trả **JSON có cấu trúc trước**, frontend render; không lưu mỗi markdown thô.
- **Cache**: chart không đổi → tái sử dụng reading, không gọi lại LLM mỗi lần mở trang.

### 4.8 Kiếm tiền
- Free vs Premium (mục 6), sản phẩm & giá (mục 7), thanh toán + entitlement (mục 8).

### 4.9 Sau khi mua
- Mở khoá section, **PDF report** (cover → thông tin → ảnh lá số → executive summary → core themes → 12 cung → sự nghiệp/tài chính/tình yêu → đại vận → lưu niên → kết luận → footer).
- **AI Chat "Hỏi lá số"**: chỉ trả lời trong ngữ cảnh chart đã load, có lịch sử hội thoại.
- **Share card** 9:16 / 1:1, có watermark, tải về đăng mạng xã hội.

### 4.10 Dashboard người dùng (`/dashboard`)
- Danh sách lá số (tên, ngày sinh, ngày tạo, preview) — xem / đổi tên / xoá / export.
- Gói đã mua, các bản luận giải, nút "Lập lá số mới".
- Empty state: "Bạn chưa có lá số nào." + CTA.

### 4.11 Nhiều lá số & so đôi
- 1 user – N lá số (của tôi, người yêu, bố, mẹ…) qua `relationship_label`.
- `/compatibility`: chọn 2 lá số, phân tích tương tác Mệnh, Phu Thê, Tài Bạch, Quan Lộc, Tử Tức. **Feature-flag, Phase 3.**

### 4.12 Admin (`/admin`)
- Quản lý: Users, Charts, Orders, Payments, Products/Pricing, AI usage, Blog, **Prompt templates (có version, bật/tắt)**, Rules, System config, Feature flags.
- Metrics: Total Users, Charts Generated, Paid Orders, Revenue, Conversion Rate, AI Requests, Charts Today, New Users Today; biểu đồ revenue/ngày, charts/ngày, conversion funnel.
- **Audit log** cho mọi hành động admin: actor, action, entity, entity_id, timestamp.

### 4.13 Blog / CMS
- Admin soạn bài (markdown/rich text), phân loại: Tử Vi cơ bản, 12 cung, Các sao, Tình yêu, Sự nghiệp, Tài chính, Vận hạn.

---

## 5. User journey chính

**J1 — Khách lạ → có lá số (không cần trả tiền):**
Landing → CTA "Lập lá số miễn phí" → wizard → loading kể tiến trình → chart hiện ra → Tổng quan + 1 insight nổi bật miễn phí → phần chuyên sâu bị khoá.

**J2 — Free → Paid:**
Chạm section khoá → xem preview 15–20% + giải thích cơ sở phân tích → chọn gói → checkout → thanh toán → webhook xác nhận → cấp entitlement → AI sinh bản luận giải → lưu vào tài khoản.

**J3 — Quay lại:**
Đăng nhập → dashboard → mở lá số cũ → đọc lại (từ cache, không tốn AI) → chat hỏi thêm → export PDF.

**J4 — Xem cho người thân:** dashboard → lập lá số mới với `relationship_label` → (Phase 3) so đôi.

**J5 — Admin:** đăng nhập admin → xem doanh thu & chi phí AI → chỉnh giá/prompt/feature flag → thay đổi có hiệu lực không cần deploy.

**Quy tắc thứ tự triển khai:** J1 phải hoàn hảo trước khi động tới J2. *Không làm payment trước khi core chart flow chạy tốt.*

---

## 6. Free vs Premium

| | Nội dung |
|---|---|
| **Miễn phí** | Lập lá số không giới hạn hợp lý, xem lá số đầy đủ, Tổng quan, một phần Mệnh, 1 insight nổi bật |
| **Khoá** | Sự nghiệp, Tài chính, Tình yêu, Phu Thê, Đại vận, Lưu niên, AI full reading, AI chat, PDF export |

**Nguyên tắc UX của phần khoá (quan trọng cho conversion):**
- Không blur toàn trang gây khó chịu. Hiện **15–20% nội dung thật**, rồi dừng.
- Nói rõ *sẽ nhận được gì*: "Phần luận giải chuyên sâu — phân tích dựa trên Mệnh – Thân – tam phương tứ chính và các sao liên quan."
- CTA: **[Mở luận giải]**. Không dùng đếm ngược giả, không khan hiếm giả.

---

## 7. Sản phẩm & giá (configurable, không hardcode)

| Mã sản phẩm | Tên | Giá khởi điểm | Cấp entitlement |
|---|---|---|---|
| `CAREER_READING` | Công danh & Sự nghiệp | 99.000 ₫ | `CAREER_READING` |
| `FINANCE_READING` | Tài chính | 99.000 ₫ | `FINANCE_READING` |
| `LOVE_READING` | Tình yêu & Hôn nhân | 99.000 ₫ | `LOVE_READING` |
| `FULL_LIFETIME_READING` | Trọn đời (toàn bộ section) | 250.000 ₫ | `FULL_LIFETIME_READING` + `PDF_EXPORT` |

- Giá, tên, mô tả, trạng thái bán **nằm trong DB**, admin sửa được; frontend đọc từ API.
- Đơn vị tiền: VND, số nguyên (không thập phân).
- **Phạm vi entitlement gắn theo lá số hay theo tài khoản?** → *Quyết định: gắn theo (user, chart, product)*. Mua gói cho lá số nào mở lá số đó; "Trọn đời" trong v1 nghĩa là **trọn đời của một lá số**, không giới hạn thời gian, không phải toàn bộ lá số trong tài khoản. Phải nói rõ điều này trong copy để tránh tranh chấp hoàn tiền.

---

## 8. Thanh toán & Entitlement

- **PaymentProvider abstraction** — v1 nhắm PayOS/VietQR (thị trường VN), Stripe để mở quốc tế sau.
- Entities: `Product`, `Order`, `Payment`, `Entitlement`.
- Order status: `pending → paid | failed | cancelled | refunded`.
- **Webhook bắt buộc: verify signature + idempotent** (một sự kiện xử lý nhiều lần vẫn ra một kết quả).
- Quyền truy cập **không bao giờ** kiểm tra bằng "có payment thành công không" ở tầng UI; luôn kiểm tra qua bảng `entitlements` ở backend.
- Không giả lập thanh toán thành công ở môi trường production. Mock chỉ tồn tại ở dev/test.

---

## 9. Nội dung, giọng văn & guardrails

### 9.1 Giọng văn
- Xưng hô **"mình – bạn"**. Nhẹ nhàng, chuyên nghiệp, gần gũi, không hù doạ, không tuyệt đối hoá.
- Có điểm đẹp thì nói thẳng: *"Đây là một điểm đẹp của lá số."* rồi giải thích vì sao.
- Copy tiếng Việt tự nhiên, không giống dịch máy, hạn chế emoji, không dùng ngôn ngữ mê tín tuyệt đối.

### 9.2 Cấm tuyệt đối trong output AI
- Nước đôi vô nghĩa: "bạn có thể giàu nhưng cũng có thể không".
- Khẳng định số phận: "bạn sẽ ly hôn", "chắc chắn giàu", "sẽ chết năm…".
- **Chẩn đoán y tế**, lời khuyên pháp lý/tài chính mang tính chỉ định.
- Nói về sao/cung mà chart JSON không hề có.

### 9.3 Bắt buộc trong output AI
- Cấu trúc **dấu hiệu → cơ chế → biểu hiện thực tế**.
- Ngôn ngữ xác suất, có điều kiện ("thường", "khả năng cao khi…", "nếu bạn ở môi trường…").
- Mỗi section neo được vào evidence từ rule engine.

### 9.4 Disclaimer (hiển thị tinh tế, không popup phiền)
> Nội dung Tử Vi trên Cosmic Signs mang tính tham khảo và định hướng tự nhìn nhận. Không nên sử dụng như lời khuyên thay thế cho chuyên gia y tế, pháp lý, tài chính hoặc các quyết định quan trọng.

Vị trí: footer, cuối mỗi bản luận giải, trang PDF cuối, và ở chỗ chat.

---

## 10. Yêu cầu phi chức năng

| Nhóm | Cam kết |
|---|---|
| **Thương hiệu / cảm giác** | Huyền bí nhưng hiện đại, premium, tinh tế, đáng tin. Không đỏ–vàng truyền thống, không mê tín rẻ tiền. Tham chiếu chất lượng: Linear/Vercel/Notion/Apple/Stripe. Không copy UI ai. |
| **Mobile-first** | Ưu tiên số 1. Test bắt buộc 375 / 390 / 430 / 768 / 1024 / 1440 px |
| **Theme** | Dark mặc định, Light phải đẹp ngang ngửa |
| **Performance** | Lighthouse: Performance > 90, SEO > 95, A11y > 90, Best Practices > 90. Lazy load, code splitting, không kéo thư viện chart khổng lồ |
| **Accessibility** | Keyboard nav, ARIA, contrast, focus state, form label, `prefers-reduced-motion` |
| **Security** | JWT/secure session, HttpOnly cookie, CSRF, rate limit, hash mật khẩu, validate input, chống SQLi/XSS, RBAC, verify webhook signature, không lộ secret |
| **Privacy** | UUID cho chart, xoá lá số, xoá tài khoản, trang Privacy/Terms, không log dữ liệu nhạy cảm |
| **Observability** | `/health`, `/ready`, structured JSON log có request_id + user_id, kiến trúc sẵn sàng gắn metrics |
| **AI cost** | Log provider, model, input/output tokens, cost ước tính, latency, feature, user_id, chart_id |
| **i18n** | v1 tiếng Việt; kiến trúc chuẩn bị `vi` / `en`, không hardcode text trong component |
| **API contract** | Thống nhất `{ data, meta, error }`; lỗi có `code`, `message`, `details` |
| **Lỗi hiển thị cho user** | Không lộ lỗi kỹ thuật. Ví dụ: "Có lỗi khi lập lá số. Bạn có thể thử lại sau vài giây." + nút Thử lại |
| **Trạng thái UI** | Mọi trang có data đều phải có skeleton, empty state, error state; không layout jump |

---

## 11. Đo lường

**Analytics abstraction:** `track(event, metadata)`.

Events: `landing_view`, `chart_start`, `chart_created`, `reading_view`, `premium_click`, `checkout_start`, `payment_success`, `pdf_export`, `chat_question`.

**Funnel bắc cầu doanh thu:**
`landing_view → chart_start → chart_created → reading_view → premium_click → checkout_start → payment_success`

**KPI theo dõi:**
- Tỷ lệ hoàn thành wizard (`chart_start → chart_created`) — đo chất lượng form.
- Tỷ lệ xem premium (`chart_created → premium_click`) — đo sức hút của phần khoá.
- Conversion (`premium_click → payment_success`) — đo giá & checkout.
- Chi phí AI / đơn hàng — đo biên lợi nhuận.
- Tỷ lệ quay lại xem lại lá số — đo giá trị lưu trữ.

**Feature flags** (admin bật/tắt): `AI_CHAT`, `COMPATIBILITY`, `YEARLY_FORECAST`, `SOCIAL_CARD`.

---

## 12. Roadmap & ranh giới MVP

| Phase | Nội dung | Coi là xong khi |
|---|---|---|
| **P0 — Nền móng** | Monorepo, docs (architecture/schema/design-system/astrology-engine/roadmap), Docker Compose, CI lint+typecheck+test | `docker compose up` / `make dev` chạy được, docs đầy đủ |
| **P1 — MVP** | Landing, Auth, Create Chart, Chart UI, **astrology engine cơ bản**, free reading, Dashboard | Người lạ vào web tự lập được lá số đúng và đẹp trên điện thoại |
| **P2 — Kiếm tiền** | AI Full Reading, Products, Payment, Entitlements, PDF, Admin | Có thể thu tiền thật và giao hàng tự động |
| **P3 — Mở rộng** | AI Chat, Compatibility, Annual forecast, Social share card, Blog/SEO | Tăng retention & organic |
| **Sau** | Lưu nguyệt, i18n `en`, magic link | — |

**Thứ tự thực thi đã chốt:** docs → skeleton → **homepage (đẹp mức production)** → lập lá số → chart demo → dashboard → rồi mới tới payment.

---

## 13. Definition of Done (áp cho mọi feature)

Một feature chỉ Done khi **tất cả** đúng:
UX hoàn chỉnh · responsive (6 breakpoint) · error handling · loading state · empty state ·
TypeScript sạch (không `any` tuỳ tiện, không bỏ qua lỗi) · lint + typecheck + test pass ·
không console error · dark & light mode đều đẹp · a11y cơ bản · code dễ maintain · UI nhất quán với design system.

Sau mỗi màn hình: **tự review như senior designer** (visual hierarchy, spacing, alignment, contrast, typography, mobile, độ nổi của CTA). Nếu nhìn như template generic → làm lại.

---

## 14. Rủi ro & cách xử lý

| Rủi ro | Mức | Xử lý |
|---|---|---|
| **Engine an sao sai** → mất uy tín với P3 | Cao | Test đối chiếu bộ ca kiểm thử chuẩn; tách rõ từng bước an sao; ghi rõ trường phái áp dụng trong `docs/astrology-engine.md` |
| **Âm–dương lịch & timezone sai** (giờ Tý đầu/cuối ngày, sinh sát giao ngày) | Cao | Module lịch độc lập + unit test biên; lưu cả input gốc lẫn kết quả quy đổi |
| **AI hallucinate sao/cung** | Cao | Chỉ truyền facts + evidence; yêu cầu output JSON; validate output theo schema; reject & retry nếu nhắc sao không có trong chart |
| **Chi phí LLM vượt biên lợi nhuận** | Trung bình | Cache reading theo chart + prompt_version; log cost; giới hạn chat |
| **Webhook trùng/lặp → cấp quyền nhiều lần hoặc mất đơn** | Trung bình | Idempotency key + verify signature + reconcile job |
| **Tranh cãi "trọn đời" gồm những gì** | Trung bình | Copy nói rõ phạm vi theo lá số (mục 7) |
| **Rò rỉ dữ liệu ngày sinh** | Cao | UUID, RBAC, không log PII, xoá được, trang Privacy |
| **Over-engineering làm chậm MVP** | Trung bình | Bám ranh giới Phase; abstraction chỉ ở 3 chỗ: AI provider, Payment provider, Rule engine |

---

## 15. Quyết định đã chốt (không hỏi lại)

1. Stack: Nuxt 3 + Vue 3 + TS + Tailwind + Pinia (web); FastAPI + Python 3.12 + Pydantic + SQLAlchemy + Alembic (api); PostgreSQL; Redis.
2. Monorepo: `apps/{web,api}`, `packages/{shared,ui,astrology-engine}`, `infra/`, `docs/`.
3. Astrology engine viết bằng **Python**, đặt trong `packages/astrology-engine` như package độc lập, api import vào — không lẫn vào tầng HTTP; frontend không tính gì cả.
4. Ngôn ngữ v1: tiếng Việt; hạ tầng i18n sẵn sàng.
5. Entitlement theo (user, chart, product) — xem mục 7.
6. Thanh toán v1: PayOS/VietQR qua abstraction; Stripe để sau.
7. Auth v1: email/password + Google; magic link chừa kiến trúc.
8. Compatibility, AI chat, share card, lưu nguyệt: sau MVP, có feature flag.
9. Package manager: **pnpm** (bật bằng `corepack enable`) cho phía JS.

## 16. Câu hỏi mở (không chặn MVP, cần trả lời trước Phase 2)

- Trường phái an sao áp dụng (Nam phái / Bắc phái / biến thể) và nguồn đối chiếu để viết test.
- Chính sách hoàn tiền và thời hạn.
- Xuất hoá đơn / thông tin pháp nhân cho thanh toán.
- Giới hạn số lá số miễn phí mỗi tài khoản (chống lạm dụng tài nguyên AI/tính toán).
- Có cho xem lá số bằng link chia sẻ công khai không (ảnh hưởng privacy & SEO).

---

## 17. Thuật ngữ

| Thuật ngữ | Nghĩa trong hệ thống |
|---|---|
| **Chart / Lá số** | Bản ghi kết quả tính toán cho một bộ thông tin sinh |
| **Cung (Palace)** | 1 trong 12 ô; có địa chi, thiên can, ngũ hành, sao, Tuần/Triệt |
| **Chính tinh** | 14 sao chính; **Phụ tinh**: các sao còn lại |
| **Mệnh / Thân** | Cung Mệnh và vị trí Thân cư |
| **Cục** | Ngũ hành cục (Thuỷ nhị, Mộc tam, Kim tứ, Thổ ngũ, Hoả lục) |
| **Tuần / Triệt** | Hai vị trí đặc biệt làm suy giảm/ngăn trở tác dụng cung–sao |
| **Miếu/Vượng/Đắc/Bình/Hãm** | Mức độ đắc địa của sao tại cung |
| **Vô chính diệu** | Cung không có chính tinh |
| **Tam phương tứ chính** | Cung chính + tam hợp + đối cung |
| **Đại vận / Lưu niên** | Chu kỳ ~10 năm / chu kỳ theo năm |
| **Core theme** | 3–5 trục chủ đạo rút ra từ lá số, kèm evidence |
| **Fact / Evidence** | Đầu ra của rule engine, đầu vào cho AI |
| **Entitlement** | Quyền truy cập nội dung đã mua |
| **Reading** | Bản luận giải đã sinh và lưu cache |
