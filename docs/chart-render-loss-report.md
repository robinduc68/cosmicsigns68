# Vì sao lá số hiển thị thưa — báo cáo chẩn đoán

*Ngày đo: 2026-09-14 · hồ sơ `COSMIC_SIGNS_NAM_PHAI_V1` · engine `0.3.0-frame`*

Câu hỏi đặt ra: catalog đã có 88 sao, nhưng lá số trên màn hình vẫn trông thưa.
Mất ở đâu — **A** không tính, **B** mất ở API, **C** mất ở ViewModel, **D** không
vẽ, hay **E** vẽ rồi nhưng bị CSS nuốt?

## Kết luận một dòng

Không tầng nào trong A–E làm mất dữ liệu. **Lá số thưa là lá số cũ.**
`chart_json` được đông cứng lúc lập, và bộ phát hiện lá số lạc hậu đã im lặng vì
`ENGINE_VERSION` bị bỏ quên ở `0.2.0-frame` suốt tám đợt việc.

| Hạng mục | Kết luận |
| --- | --- |
| A — engine không tính | **Không.** Engine an đủ 88 sao cho mọi lá số đo được. |
| B — mất ở API | **Không.** API trả đúng 88 sao, `engine == api` là `True`. |
| C — mất ở ViewModel | **Không.** 88 sao vào, 88 sao ra, 0 cung lệch. |
| D — renderer lọc bỏ | **Không.** Không có bộ lọc nào theo tên sao, theo metadata null, hay theo số lượng. |
| E — CSS / layout nuốt | **Không.** 88/88 sao hiện, 0 sao bị cắt, 0 cung tràn. |
| **Nguyên nhân thật** | **Lá số đã lưu lạc hậu + bộ phát hiện lạc hậu bị vô hiệu.** |

## Nguyên nhân gốc

`needs_recalculation()` sinh ra đúng để bắt tình huống này: một lá số đã lưu sẽ
cho kết quả khác nếu lập lại hôm nay. Nó so ba thứ — hồ sơ quy ước, phiên bản hồ
sơ, và **phiên bản engine**.

Phiên bản engine là một chuỗi gõ tay. Nó đứng yên ở `0.2.0-frame` qua tám đợt việc
đã đổi kết quả lá số: catalog sao, Tràng Sinh, đại vận, Tứ Hóa, ba nhóm phụ tinh,
nhóm sát tinh. Số sao đi từ 14 lên 88 mà chuỗi ấy không nhúc nhích.

Hệ quả: mọi lá số lưu dọc đường tự báo **"Khớp hồ sơ quy ước và engine hiện hành"**.
Đây là lỗi của chính người viết bộ phát hiện ấy — dựng một cái chuông rồi tự tháo dây.

### Hiện trạng cơ sở dữ liệu lúc chẩn đoán

| engine | hồ sơ | số lá số | sao/lá số |
| --- | --- | --- | --- |
| `0.1.0-frame` | `COSMIC_SIGNS_STANDARD_V1` | 6 | — (schema v1, chưa có mảng sao) |
| `0.1.0-frame` | *(trống)* | 3 | — |
| `0.2.0-frame` | `COSMIC_SIGNS_NAM_PHAI_V1` | 5 | **27** |
| `0.2.0-frame` | `COSMIC_SIGNS_STANDARD_V1` | 13 | **14** |

Lá số người dùng đang mở, `da2f2a6b…`, nằm ở hàng thứ ba: **27 sao**, và tự nhận
là vẫn mới.

### 61 sao thiếu trong lá số đã lưu `da2f2a6b…`

So bản đã lưu với bản lập lại hôm nay từ cùng dữ liệu sinh:

```
AN_QUANG, BACH_HO, BAC_SI, BAT_TOA, BENH_PHU, CO_THAN, DAI_HAO, DAU_QUAN,
DIA_GIAI, DIA_KHONG, DIA_KIEP, DIA_VONG, DIEU_KHACH, DUONG_PHU, HOA_CAI,
HOA_TINH, HY_THAN, KIEP_SAT, LINH_TINH, LONG_DUC, LONG_TRI, LUC_SI,
NGUYET_DUC, PHA_TOAI, PHI_LIEM, PHONG_CAO, PHUC_BINH, PHUC_DUC_STAR,
PHUONG_CAC, QUAN_PHU_BS, QUAN_PHU_TT, QUA_TU, QUOC_AN, TAM_THAI, TANG_MON,
TAU_THU, THAI_PHU, THAI_TUE, THANH_LONG, THIEN_DIEU, THIEN_DUC, THIEN_GIAI,
THIEN_HINH, THIEN_HU, THIEN_KHOC, THIEN_KHONG, THIEN_LA, THIEN_PHUC,
THIEN_QUAN, THIEN_QUY, THIEN_SU, THIEN_TAI, THIEN_THO, THIEN_THUONG,
THIEU_AM, THIEU_DUONG, TIEU_HAO, TRUC_PHU, TUE_PHA, TUONG_QUAN, TU_PHU
```

Đây là **danh sách sao thiếu ở tầng lưu trữ**, không phải ở tầng nào khác. Ở bốn
tầng còn lại, danh sách sao thiếu là **rỗng** — xem bảng dưới.

## Đo từng cung, lá số lập mới `285d49ae…`

Cùng dữ liệu sinh, lập lại sau khi sửa. Bốn cột là bốn tầng; cột cuối đếm thật
trong DOM qua giao thức debug của trình duyệt.

| Cung | Chi | Engine | API | ViewModel | DOM | Hiện | Bị cắt | Tràn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mệnh | Tuất | 8 | 8 | 8 | 8 | 8 | 0 | không |
| Phụ Mẫu | Hợi | 7 | 7 | 7 | 7 | 7 | 0 | không |
| Phúc Đức | Tý | 4 | 4 | 4 | 4 | 4 | 0 | không |
| Điền Trạch | Sửu | 8 | 8 | 8 | 8 | 8 | 0 | không |
| Quan Lộc | Dần | 10 | 10 | 10 | 10 | 10 | 0 | không |
| Nô Bộc | Mão | 7 | 7 | 7 | 7 | 7 | 0 | không |
| Thiên Di | Thìn | 7 | 7 | 7 | 7 | 7 | 0 | không |
| Tật Ách | Tỵ | 9 | 9 | 9 | 9 | 9 | 0 | không |
| Tài Bạch | Ngọ | 7 | 7 | 7 | 7 | 7 | 0 | không |
| Tử Tức | Mùi | 5 | 5 | 5 | 5 | 5 | 0 | không |
| Phu Thê | Thân | 6 | 6 | 6 | 6 | 6 | 0 | không |
| Huynh Đệ | Dậu | 10 | 10 | 10 | 10 | 10 | 0 | không |
| **Tổng** | | **88** | **88** | **88** | **88** | **88** | **0** | **0 cung** |

**Sao thiếu ở mỗi tầng: không có.** Engine → API → ViewModel → DOM không rơi rụng
một sao nào, và không sao nào lọt ra ngoài khung cung.

### Cùng lá số, năm xem 2026

Bật chế độ soi cung rồi chọn năm xem 2026, đo lại cùng cách:

| Cung | Natal | Annual | Rendered | Lệch |
| --- | --- | --- | --- | --- |
| Mệnh | 8 | 1 | 9 | không |
| Phụ Mẫu | 7 | 1 | 8 | không |
| Phúc Đức | 4 | 2 | 6 | không |
| Điền Trạch | 8 | 0 | 8 | không |
| Quan Lộc | 10 | 1 | 11 | không |
| Nô Bộc | 7 | 2 | 9 | không |
| Thiên Di | 7 | 2 | 9 | không |
| Tật Ách | 9 | 1 | 10 | không |
| Tài Bạch | 7 | 3 | 10 | không |
| Tử Tức | 5 | 0 | 5 | không |
| Phu Thê | 6 | 3 | 9 | không |
| Huynh Đệ | 10 | 2 | 12 | không |
| **Tổng** | **88** | **18** | **106** | **0 cung** |

88 + 18 = 106, đúng bằng số `.tuvi-star` đếm trong DOM. Cột Natal không nhúc nhích
một đơn vị nào khi thêm năm xem — sao bản mệnh không bị lưu niên đụng vào.

### Lưu niên

Lưu niên **đã được cài đặt thật**, không phải chỗ trống. Với năm xem 2026, API trả
**18 lưu tinh và 4 lưu hóa** qua `GET /charts/{id}/annual?year=`. Lưu niên không
nằm trong `chart_json` — nó tính theo yêu cầu, nên đổi năm xem không có đường nào
làm dịch chuyển sao bản mệnh. Khi chưa chọn năm xem, `Annual` bằng 0 ở mọi cung;
đó là giá trị đúng, không phải mất dữ liệu.

## Rà soát bộ lọc ở renderer

Đọc lại `TuViPalace.vue`, `TuViStar.vue`, `TuViChartCanvas.vue` và `useTuViChartViewModel.ts`:

- Không có `slice`, `filter` theo số lượng, hay giới hạn "tối đa N sao mỗi cung".
- Không có nhánh nào ẩn sao vì `element`, `polarity`, `strength` hay `transformation` là `null`.
  Sao thiếu metadata vẫn hiện, chỉ là hiện bằng màu trung tính.
- Không có bảng nào ánh xạ **tên sao** sang CSS. Màu vẫn hoàn toàn theo Ngũ Hành
  lấy từ metadata engine.
- `majorStars` / `minorStars` là hai danh sách bù nhau, hợp lại đúng bằng `stars`.

**Không có bộ lọc nào bị gỡ, vì không có bộ lọc nào tồn tại.**

## CSS / layout

`.tuvi-palace` có `overflow: hidden` — cần thiết, vì không gì được tràn qua đường
kẻ giữa hai cung. Rủi ro là nó cắt âm thầm. Nó không cắt âm thầm: mỗi cung tự đo
`scrollHeight` so với `clientHeight` sau khi web font ổn định, và cảnh báo ra
console kèm số pixel thừa. Trên lá số 88 sao, không cung nào cảnh báo.

## Chế độ soi cung (chỉ ở bản dev)

Thanh công cụ có thêm nút **"Soi cung"**. Bật lên, mỗi cung hiện một dòng:

```
Natal: 8 · Annual: 0 · Rendered: 8
```

Hai số đầu đọc từ view model. Số thứ ba **đếm `.tuvi-star` thật trong DOM của cung
đó**. Đó là chủ ý: nếu `Rendered` chỉ lặp lại `Natal + Annual` thì nó không chứng
minh được gì. Khi ba số không khớp, dòng đếm chuyển nền đỏ.

Khối này gác sau `import.meta.dev`. Kiểm chứng trên bản build thật: biến gác được
gấp thành hằng `false`, nên nhánh vẽ là nhánh chết và không có đường nào chạy ở
production. Phần đánh dấu **vẫn còn trong bundle** (vài trăm byte) — bộ gom không
xoá nhánh chết nằm trong hàm render. Nói "không bao giờ hiện" thì đúng; nói "đã bị
xoá khỏi bản build" thì sai.

## Đã sửa gì

1. **`ENGINE_VERSION` lên `0.3.0-frame`** kèm ghi chú vì sao nó nhảy hẳn một bậc.
   27 lá số cũ lập tức bị đánh dấu cần tính lại.
2. **Thêm vân tay nội dung** — `rule_fingerprint()`: băm của tập id sao và tập luật
   đang chọn, lưu trong `identity` của mỗi lá số. Nó đổi **tự động** khi tập sao
   hoặc tập luật đổi. Một chuỗi phiên bản chỉ hoạt động nếu có người nhớ; lần này
   không ai nhớ, nên bây giờ không cần ai nhớ nữa.
3. **`needs_recalculation()` so thêm vân tay**, sau khi so phiên bản. Lá số lưu
   trước khi có vân tay không mang trường này — bỏ qua vế vân tay thay vì báo lệch
   vô cớ cho toàn bộ dữ liệu cũ.
4. **Test khoá giả định**: `current_rule_fingerprint()` đọc `STAR_CATALOG` thay vì
   tính một lá số, để chạy được trên mỗi lần đọc. Điều đó chỉ đúng chừng nào mọi lá
   số đều an đủ tập sao trong catalog. Bốn lá số mẫu khẳng định điều đó; nếu một
   ngày nào đó có sao chỉ an trong vài trường hợp, test vỡ ở chỗ dễ thấy, chứ không
   vỡ bằng cách im lặng bảo lá số cũ là vẫn mới.

### Kiểm chứng

```
da2f2a6b… (27 sao)  → needed: true
  "Lá số lập bằng engine 0.2.0-frame, hiện dùng 0.3.0-frame…"
285d49ae… (lập mới) → needed: false, vân tay 4ce630d189fdcea6, 88 sao trong 12 cung
```

## Không đụng vào gì

Không có vị trí sao nào thay đổi. Không thêm sao, không thêm công thức, không sửa
phép tính. Toàn bộ thay đổi nằm ở **đường ống và đánh phiên bản**, cộng một lớp phủ
chỉ có ở bản dev. 637 test engine và 41 test API vẫn xanh, trong đó có bộ test cố
định 88 sao và bộ test thứ tự 12 cung.

## Việc còn lại cho người quyết định

27 lá số cũ giờ đã tự khai là lạc hậu. **Chúng không bị tự động tính lại** — một lá
số khách đã xem, và có thể đã trả tiền, không được thay đổi dưới chân họ. Việc chọn
lập lại thuộc về con người, không thuộc về hệ thống đọc dữ liệu.
