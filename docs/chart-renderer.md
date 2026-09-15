# Renderer lá số Tử Vi

Cập nhật: **2026-09-11** · Mã: `apps/web/components/astrology/chart/`

Renderer vẽ lá số **tất định từ chart JSON** của engine. Không dùng AI, không dùng
ảnh dựng sẵn, và **không chứa một quy tắc tử vi nào**.

---

> Hình dạng dữ liệu từng tầng — field nào nullable, đã cài, đã kiểm định — nằm ở
> [`chart-data-contract.md`](chart-data-contract.md). Tài liệu này chỉ nói cách vẽ.

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

Ngũ hành **của sao** do engine khai báo (`star.element`, xem
`cosmic_astrology/stars/catalog.py`). Renderer chỉ đổi `element → class ngữ nghĩa`
(`is-element-kim`, `is-element-moc`, …, `is-element-none`) và **không bao giờ** suy
hành từ tên sao. Class phủ cả nhãn — dấu âm/dương, tên, độ sáng — vì hành thuộc về cả
ngôi sao, không thuộc một chữ nào.

Ánh xạ `element → màu` tồn tại **đúng một chỗ**: sáu quy tắc `.tuvi-star.is-element-*`
trong `tuvi-chart.css`. `tests/no-star-name-styling.spec.ts` quét mã nguồn renderer và
sẽ đỏ nếu bất kỳ tên sao hay id sao nào xuất hiện trong đó.

| Nguồn màu | Dùng ở đâu |
| --- | --- |
| `star.element` | Toàn bộ nhãn sao |
| `palace.element` | Chỉ chữ nạp âm trong cung |
| `menh.element`, `cuc.element` | Chỉ hai giá trị "Bản mệnh" và "Cục" ở trung tâm |

> **Sao chưa có hành thì vẽ mực trung tính**, không đoán để cho đủ màu. Hôm nay là
> **Tham Lang** và **Cự Môn** — các trường phái ghi khác nhau. Bảng độ phủ nằm trong
> `python -m cosmic_astrology.verification`.

Độ sáng (M/V/Đ/B/H) **không** đổi màu: một sao Hỏa bị Hãm vẫn là màu Hỏa. Cấp sao
(chính/phụ) chỉ đổi **typography**, không đổi màu.

Ở môi trường dev, sao thiếu hành được cảnh báo ra console (`[TuVi Renderer] Thiếu
metadata ngũ hành: …`). Cảnh báo **không** đi vào DOM, nên không lọt vào PNG hay bản in.

---

## 4b. Diễn đạt tiếng Việt

`utils/tuvi-format.ts` là nơi duy nhất quyết định một giá trị được viết ra sao.

| Hàm | Ví dụ |
| --- | --- |
| `formatGender` | `FEMALE` → `Nữ` |
| `formatYinYang` | `(false, FEMALE)` → `Âm Nữ` |
| `formatPillar` | `{can:'Tân', chi:'Tỵ'}` → `Tân Tỵ` |
| `formatSolarDate` | → `04/03/2001` |
| `formatLunarDate` | → `10/02 Tân Tỵ` (có `nhuận` khi cần) |
| `formatBirthTime` | → `09:30 (giờ Tỵ)` |
| `formatCuc` | `(MOC, 3)` → `Mộc Tam Cục` |
| `formatMenhCucRelation` | `(MENH_KHAC_CUC, KIM, MOC)` → `Mệnh Kim khắc Cục Mộc` |
| `formatAgeRange` | `(6, 15)` → `6 – 15` |

Thứ tự câu trong `formatMenhCucRelation` theo chủ thể: `CUC_SINH_MENH` cho ra
`Cục Mộc sinh Mệnh Hỏa`, không phải một câu đảo ngược đọc gượng.

Không hàm nào tính tử vi. Trả `null` thì **bỏ dòng**, không thay bằng ký tự giữ chỗ.

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

## 9b. Chế độ soi cung (chỉ ở bản dev)

Nút **"Soi cung"** trên thanh công cụ bật một dòng đếm ở mỗi cung:

```
Natal: 8 · Annual: 0 · Rendered: 8
```

Hai số đầu đọc từ view model; số thứ ba **đếm `.tuvi-star` thật trong DOM của cung
đó**. Nếu `Rendered` chỉ lặp lại `Natal + Annual` thì nó không chứng minh được gì —
đếm trong DOM mới bắt được bộ lọc âm thầm ở renderer và sao bị CSS nuốt. Ba số lệch
nhau thì dòng đếm chuyển nền đỏ.

Khối này gác sau `import.meta.dev`, được gấp thành hằng `false` lúc build — nhánh
chết, không bao giờ chạy ở production. Phần đánh dấu vẫn nằm trong bundle; bộ gom
không xoá nhánh chết bên trong hàm render.
Xem `docs/chart-render-loss-report.md` để biết vì sao nó tồn tại.

---

## 9c. Tứ Hóa xuống dòng riêng

Một lá số in để hóa trên **dòng của nó**, ngay dưới ngôi sao mang hóa:

```
Tham Lang
  Hóa Quyền
```

Trước đây nó là nhãn vuông dính đuôi tên sao — `THAM LANG[Quyền]` — và đọc như một
phần của tên. Dòng hóa dùng class `.tuvi-hoa-line`, **không** phải `.tuvi-star`: hóa
là một *trạng thái* của ngôi sao đã an, nên nó không được cộng vào bất kỳ phép đếm
sao nào, kể cả bộ đếm soi cung ở mục 9b. Có test chặn riêng điều này.

Màu của dòng hóa là **ngũ hành của ngôi sao mang hóa**. Hóa Lộc không xanh, Hóa Kỵ
không đỏ — màu trên lá số này chỉ có một nghĩa.

---

## 9d. Mật độ: đo rồi mới chỉnh

Lá số từng trông thưa, và lý do đo được chứ không phải cảm tính:

| | Trước | Sau |
|---|---|---|
| Chiều cao một cung | 396px | 402px |
| Nội dung dùng | 157–244px | 176–275px |
| Tỉ lệ lấp | **44–68%** | **47–73%** |
| Khoảng trống chết | **91–178px** | **42–92px** |

Hai thay đổi, theo thứ tự quan trọng:

1. **Chỗ thừa được chia đôi.** Trước đây chỉ footer có `margin-top: auto`, nên toàn bộ
   phần thừa gom thành một khoảng trống nằm giữa ngôi sao cuối và footer — trên cả 12
   cung. Nay `header` có `margin-bottom: auto` đối lại, flexbox chia đều, và khối sao
   nằm giữa thay vì treo lơ lửng ở trên. Không thêm thẻ bọc nào.
2. **Thang chữ lớn hơn một bậc** — chính tinh 21→27px, phụ tinh 15→19px. Cung đông
   nhất đo được là 12 sao (6 hàng phụ tinh); thang này chừa chỗ tới 8 hàng.

Legend cũng gọn từ 132px xuống 106px, và mỗi pixel trả về là một pixel lưới.

---

## 9e. Chữ có chân

Tên cung, chính tinh, dòng Tứ Hóa và khối giữa dùng **Noto Serif**; phụ tinh và
metadata giữ **Be Vietnam Pro**. Hai tầng có chủ ý: chữ có chân cho thứ cần ra dáng
bản in, chữ không chân cho thứ xếp hai cột và cần đọc nhanh ở cỡ nhỏ.

Chế độ đọc trên màn hẹp có **thang chữ riêng** (chính tinh 20px, phụ tinh 15.5px).
Thang lớn kia được chọn để lấp một ô cao 402px; thẻ trên điện thoại cao theo nội
dung, nên dùng lại thang ấy chỉ làm chữ quá khổ. **Dữ liệu không đổi giữa hai chế độ.**

---

## 9f. Hai chỗ dữ liệu **có mà không đọc được**

Đợt soát cuối không tìm ra dữ liệu nào bị mất — 92 sao bản mệnh, 18 lưu tinh, 8 dòng
Tứ Hóa đều có trong DOM. Nó tìm ra hai chỗ **trình bày** khiến dữ liệu đúng bị đọc sai.

**Tứ Hóa từng hiện ở hai cỡ khác nhau.** Dòng hóa dùng cỡ tương đối `0.76em`, nên nó
thừa hưởng cỡ của ngôi sao mang nó: treo dưới một chính tinh thì ra **20.5px**, treo
dưới một phụ tinh thì chỉ **14.4px**. Cùng một loại thông tin, chênh 42%, và cái nhỏ
hơn gần như biến mất — đủ để người đọc kết luận rằng nó không được tính. Nay dòng hóa
có cỡ **tuyệt đối** (`--chart-hoa-size`): Hóa là Hóa, bất kể ngôi sao nào mang nó.

**Lưu tinh chỉ khác sao bản mệnh ở chữ nghiêng.** Ở cỡ 19px giữa một cột phụ tinh,
nghiêng không đủ. Cộng thêm dấu âm/dương dán sát tên, một sao bản mệnh mang dấu `−`
đọc như một cái tên có tiền tố và bị gộp vào nhóm lưu tinh `L.` bên cạnh. Nay lưu tinh
nhỏ và nhẹ hơn một nhịp, dấu âm/dương nhỏ hơn và tách ra một nhịp.

**Màu không đổi ở cả hai chỗ** — ngũ hành vẫn là thứ duy nhất quyết định màu.

---

## 9g. Trật tự nhóm trong một cung

```
TIÊU ĐỀ
KHỐI CHÍNH TINH      ← liền nhau, không gì chen vào
KHỐI TỨ HÓA
LƯỚI PHỤ TINH        ← hai cột
LƯỚI LƯU TINH        ← hai cột, khối riêng
FOOTER
```

**Bất biến quan trọng nhất của lớp trình bày: không dòng Tứ Hóa nào được nằm giữa
hai chính tinh.** Trước đây mỗi dòng hóa dựng *bên trong* ngôi sao mang nó, nên ở một
cung có hai chính tinh mà sao thứ nhất mang hóa, dòng hóa rơi vào giữa và khối vỡ
thành hai cụm rời. Nay Tứ Hóa gom thành một khối sau **toàn bộ** chính tinh; dòng hóa
vẫn mang màu ngũ hành của sao mang nó và nói tên sao ấy trong tooltip.

Có test canh **thứ tự DOM thật**, không canh số đếm.

### Đã thử grid và hỏng

Bản thử dùng `display: grid` với bốn hàng `auto / auto / 1fr / auto`. Khối chính tinh
và khối Tứ Hóa cùng ở hàng 2, nên lưới **tự sinh một cột ngầm thứ hai** và đặt chúng
cạnh nhau. Cột 1 hẹp lại cho *mọi* hàng: tên cung xuống dòng, chữ tràn vào footer.

Flex một cột với `margin-top: auto` ở footer làm đúng việc ấy — canh trên, footer dính
đáy — và không có cách nào sinh ra cột thứ hai.

---

## 9h. Hồ sơ hiển thị lưu tinh

Engine an **18** lưu tinh; bản in đối chiếu ghi ra **9**. Dữ liệu thừa thì cắt được ở
tầng hiển thị, dữ liệu thiếu thì không — nên engine vẫn tính đủ.

`TRADITIONAL_REFERENCE_V1` (mặc định) hiện 9 sao của bản in; `FULL_ANNUAL` hiện tất cả.
Hồ sơ **chỉ lọc nhãn**: `annual.stars` không hề bị đụng, nên đổi hồ sơ không thể làm
một ngôi sao dịch chỗ.

Danh sách sao nào thuộc bản in nằm ở **engine** (`TRADITIONAL_DISPLAY_STAR_IDS`), và
mỗi lưu tinh mang sẵn cờ `traditional_display`. Renderer chỉ đọc cờ — nó không được
phép rẽ nhánh theo mã sao, và `no-star-name-styling.spec.ts` quét mã nguồn renderer để
giữ đúng điều đó. Bản thử đầu đặt danh sách ở renderer và bài test ấy đỏ ngay.

---

## 9i. Nhịp dọc: đo bác một giả định

Yêu cầu là "rút khoảng tiêu đề → chính tinh khoảng 6–10px". Đo ra: khoảng ấy **đã là
6px** ở cả 12 cung — đúng cận dưới của mục tiêu, không còn gì để rút mà sao không chạm
vào dòng nạp âm.

Chỗ trống thật nằm **dưới** nội dung (60–208px), và đó là thiết kế canh trên có chủ ý.

Nên thay vì rút khoảng 6px ấy, cả khối tiêu đề được đẩy lên: đệm trên của cung
16 → 12px, lề trên khối chính tinh 8 → 6px. Khoảng tiêu đề → chính tinh còn **3px**,
và toàn bộ nội dung bắt đầu cao hơn ~6px — đúng hiệu quả mà yêu cầu nhắm tới.

### Cỡ phụ tinh: đã thử 19.5px và lùi lại

Yêu cầu là "tăng cỡ phụ tinh **nếu an toàn**". Ở 19.5px, nhãn dài nhất —
`+Kình Dương(Đ)`, tên hai chữ có cả dấu âm dương lẫn hậu tố độ sáng — **xuống dòng**
và phá vỡ thẳng hàng hai cột. Không an toàn, nên giữ 19px.

Chỗ dễ đọc hơn đến từ **khoảng cách**, không từ cỡ chữ: `line-height` 1.14 → 1.08,
`row-gap` 2 → 1px, và cột rộng thêm bằng cách giảm đệm ngang 13 → 11px và khe cột
10 → 6px. Sau đó **không nhãn nào xuống dòng**.

---

## 10. Hạn chế đã biết

- **Miếu vượng: đường ống xong, bảng rỗng.** Hậu tố `(M)(V)(Đ)(B)(H)` đã dựng và có
  test, nhưng bảng 14 × 12 chưa có ấn bản nào để chép, nên mọi sao hiện **không có**
  hậu tố. Đây là thiếu *dữ liệu*, không phải thiếu *chức năng*.
- Engine chưa gửi cân lượng và lai nhân cung — renderer có sẵn chỗ nhưng **không hiển
  thị gì** cho tới khi có. Chủ Mệnh, Chủ Thân, phụ tinh, tứ hóa, đại vận, tràng sinh,
  lưu niên và ngũ hành của sao thì đã có.
- Chưa có screenshot regression tự động: Playwright chưa được cài. Việc soát ảnh hiện làm
  bằng Chrome headless qua CDP.
- Ở chế độ "Toàn lá số" trên cảm ứng, vuốt trên vùng lá số không cuộn được trang (panzoom
  giữ `touch-action`). Màn hẹp mặc định ở chế độ đọc nên ít gặp.
- Badge `ENGINE PROVISIONAL — NOT FOR CUSTOMER USE` hiện **bất cứ khi nào** lá số chưa
  authoritative, kể cả ngoài dev — an toàn hơn là chỉ hiện ở dev.
