# Renderer lá số Tử Vi

Cập nhật: **2026-09-11** · Mã: `apps/web/components/astrology/chart/`

Renderer vẽ lá số **tất định từ chart JSON** của engine. Không dùng AI, không dùng
ảnh dựng sẵn, và **không chứa một quy tắc tử vi nào**.

---

## 1. Luồng dữ liệu

```
Astrology engine → Chart DTO → mapChartDtoToViewModel() → component Vue
```

| Tầng | File | Được làm | Không được làm |
|---|---|---|---|
| Mapper | `composables/useTuViChartViewModel.ts` | Đổi hình dạng, gắn nhãn, sắp thứ tự hiển thị, tính vị trí vẽ | An sao, chọn cung, điền giá trị engine chưa gửi |
| Hằng số hiển thị | `utils/tuvi-chart.ts` | Màu ngũ hành, thứ tự hiển thị, hình học lưới, chỉ số sức chứa | Bất cứ thứ gì mang nghĩa tử vi |
| Component | `components/astrology/chart/*.vue` | Hiển thị view model | Đọc DTO trực tiếp, tính toán |

Trường engine **chưa gửi** thì là `null` và bị bỏ qua khi vẽ. Mapper đọc phòng thủ các
trường engine có thể thêm sau (`element` của sao, `strength`, `major_cycle_age`,
`life_stage`, …) nên chúng tự hiện ra khi có, **không cần sửa giao diện**.

---

## 2. Component

| Component | Vai trò |
|---|---|
| `TuViChart` | Viewer: toolbar, pan/zoom, chế độ đọc, xuất PNG, in |
| `TuViChartCanvas` | Lá số chuẩn 1400 × 1750. Màn hình, in và PNG đều dùng chính nó |
| `TuViPalace` | Một cung: header, chính tinh, phụ tinh hai cột, footer |
| `TuViCenter` | Khung giữa 2 × 2: thông tin lá số, hình mờ, đường tam phương tứ chính |
| `TuViStar` | Một sao; màu theo ngũ hành engine khai báo, không có thì mực trung tính |
| `TuViVoidMarker` | Nhãn Tuần / Triệt đặt trên viền chung của hai cung |
| `TuViChartConnections` | SVG tam phương tứ chính, lấy từ `menh.three_directions_four_positions` |
| `TuViChartLegend` | Chú giải miếu vượng, ngũ hành, phiên bản engine + quy ước, badge cảnh báo |
| `TuViReadingMode` | Bố cục từng cung cho màn hẹp |
| `TuViChartToolbar` | Các nút thao tác |

---

## 3. Bố cục

- **Canvas chuẩn 1400 × 1750** (4:5), lưới CSS 4 × 4, khung giữa chiếm cột 2–3, hàng 2–3.
- Cung nào ở ô nào lấy từ `CHART_GRID_BRANCH_INDEXES` trong `packages/shared` — theo
  **địa chi**, không bao giờ theo thứ tự phần tử trong mảng.
- Canvas **không reflow**: mọi kích thước tính bằng pixel canvas, rồi scale từ ngoài vào.
- Nền **giấy sáng** bất kể giao diện trang đang sáng hay tối.

### Tuần / Triệt
- Hai cung kề nhau theo **chiều dọc** → nhãn đặt ở giữa viền ngang chung.
- Hai cung kề nhau theo **chiều ngang** → nhãn đặt trên viền dọc chung, **hạ thấp** gần
  đáy hàng, vì giữa cung là vùng sao.
- Engine đánh dấu không đúng hai cung kề nhau → **không vẽ và báo cảnh báo dev**, không đoán.

### Thứ tự hiển thị sao trong một cung (`STAR_CATEGORY_PRIORITY`)

`MAJOR` → `TRANSFORMATION` → `SUPPORTING` → `MALEFIC` → `MINOR` → `ANNUAL`.
Chỉ ảnh hưởng vị trí chữ trên trang, **không mang nghĩa tử vi**; trong cùng một nhóm
giữ nguyên thứ tự engine gửi. Thay bằng độ ưu tiên do engine cấp khi có.

---

## 4. Màu

Toàn bộ màu khai báo **một chỗ** trong `tuvi-chart.css` (token `--chart-*`) và được đặt
tên trong `ELEMENT_COLOR_MAP`. Màu ngũ hành đã chỉnh để đạt tối thiểu 4,5 : 1 trên nền giấy.

> Hiện engine **chưa khai báo ngũ hành cho sao**, nên mọi sao hiện màu mực trung tính.
> Đây là đúng thiết kế, không phải lỗi: renderer không được suy ngũ hành từ tên sao
> (Tham Lang, Thất Sát có biến thể giữa các trường phái).

---

## 5. Chống tràn chữ

Cung không được tràn qua viền, **và cũng không được cắt âm thầm**. Hai lớp bảo vệ:

1. **Ước lượng chiều cao theo pixel** (`estimatePalaceHeight`, `PALACE_METRICS`) — cảnh
   báo trong `model.warnings`, hiện ngay trên viewer ở chế độ dev.
2. **Đo DOM thật** trong dev (`TuViPalace`) — `console.warn` kèm số px bị che. Lớp này
   bắt được cả những gì ước lượng bỏ sót, ví dụ tên dài xuống nhiều dòng.

---

## 6. Xuất PNG

- `useChartExport` dùng `modern-screenshot` (`domToBlob`), **scale 2 → 2800 × 3500**.
- Luôn chụp **canvas chuẩn gắn sẵn ngoài màn hình** (`#tuvi-offscreen-host`), không bao giờ
  chụp bố cục đang bị thu nhỏ trên điện thoại.
- Đợi `document.fonts.ready` trước khi chụp — chụp sớm là rơi về font hệ thống và vỡ dấu.
- Tên file: `la-so-tu-vi-{slug}-{yyyy-mm-dd}.png`, slug bỏ dấu (xử lý riêng chữ `đ`).

> **Vì sao các nhãn ngắn có `white-space: nowrap`:** `modern-screenshot` chép nguyên kích
> thước đã đo của từng phần tử. Chữ chỉ cần rộng hơn một chút khi render trong SVG là gãy
> dòng và đè lên hàng dưới — trên màn hình không thấy, trong ảnh tải về thì vỡ. Chế độ đọc
> không bao giờ được xuất nên được phép xuống dòng.

## 7. In / PDF

A4 dọc, lề 8 mm, canvas scale 0,5237 để vừa đúng một trang. In từ canvas ngoài màn hình,
nên nút "In / PDF" và Ctrl+P đều ra lá số đầy đủ. Quy tắc ẩn phần còn lại của trang được
giới hạn bằng `body:has(> #tuvi-offscreen-host)` — không giới hạn thì stylesheet còn nạp
sau khi chuyển trang sẽ in mọi trang khác thành giấy trắng.

---

## 8. Màn hẹp

- ≤ 767 px mặc định vào **Đọc từng cung**: tóm tắt trước, rồi 12 cung theo thứ tự engine
  gửi; Tuần/Triệt chuyển vào trong cung vì không còn viền chung.
- **Toàn lá số** vẫn dùng được, có pinch/zoom/pan (`@panzoom/panzoom`). Lăn chuột thường vẫn
  cuộn trang; chỉ Ctrl + lăn hoặc pinch mới zoom.
- Canvas được scale **ngay khi mount**; panzoom tải sau chỉ để tương tác. Đợi panzoom
  mới hiện thì route mới vào lần đầu chỉ thấy một ô trống.

---

## 9. Trang demo nội bộ

`/_internal/chart-renderer?scenario=<id>&mode=overview|reading` — chỉ chạy ở dev.

| Kịch bản | Nguồn |
|---|---|
| `cross-check-2001`, `reference-1992`, `at-suu-1985`, `cross-check-2001-frame` | **Đầu ra engine thật**, sinh bằng engine 0.2.0 |
| `dense-demo`, `overflow-demo`, `long-names-demo`, `authoritative-demo` | **Dữ liệu giả**, dán nhãn "Sao mẫu"/"(mẫu)", chỉ để thử bố cục |

Dữ liệu giả **không bao giờ** được hiển thị cho khách.

---

## 10. Hạn chế đã biết

- Engine chưa gửi phụ tinh, miếu vượng, tứ hóa, đại vận, tràng sinh, lưu niên, ngũ hành của
  sao, chủ mệnh / chủ thân — renderer có sẵn chỗ nhưng **không hiển thị gì** cho tới khi có.
- Chưa có screenshot regression tự động: Playwright chưa được cài. Việc soát ảnh hiện làm
  bằng Chrome headless qua CDP.
- Ở chế độ "Toàn lá số" trên cảm ứng, vuốt trên vùng lá số không cuộn được trang (panzoom
  giữ `touch-action`). Màn hẹp mặc định ở chế độ đọc nên ít gặp.
- Badge `ENGINE PROVISIONAL — NOT FOR CUSTOMER USE` hiện **bất cứ khi nào** lá số chưa
  authoritative, kể cả ngoài dev — an toàn hơn là chỉ hiện ở dev.
