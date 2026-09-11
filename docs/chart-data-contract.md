# Hợp đồng dữ liệu lá số

Tài liệu này mô tả **hình dạng** dữ liệu lá số qua từng tầng. Nó không quyết định
một luật tử vi nào — luật nằm ở `astrology-conventions.md`.

```
Birth Data → Astrology Engine → Domain Chart → API DTO → Chart ViewModel → Renderer
```

Mỗi mũi tên chỉ đi một chiều. Renderer **không bao giờ** tính tử vi; API DTO **không
bao giờ** bù giá trị tử vi bị thiếu.

---

## 0. Quy tắc trung tâm: DỮ LIỆU TỬ VI CHƯA BIẾT PHẢI LÀ `null`

Đây là quy tắc bao trùm cả dự án, không phải mẹo viết code.

**Trong domain và API, tuyệt đối không dùng:**

| Không được dùng | Vì sao |
| --- | --- |
| `"Unknown"`, `"N/A"`, `"—"`, `"?"` | Là chuỗi, nên mọi phép kiểm `if (value)` đều cho là *có* dữ liệu |
| Độ sáng đoán (`"BINH"` cho mọi sao) | Người có nền Tử Vi phát hiện ngay, và mất hết uy tín |
| Sao giữ chỗ | Một sao không tồn tại trông y như một sao thật |
| `0` hoặc `-1` thay cho "chưa tính" | Lẫn với giá trị thật |
| Suy ngũ hành từ tên sao | Là đoán, dù đoán đúng phần lớn |

**Được dùng:** `null`. Chỉ `null`.

Ai quyết định hiển thị gì khi thiếu? **Renderer** — nó có thể bỏ dòng đó, hoặc để
trống, hoặc ghi một câu giải thích. Nhưng quyết định đó nằm ở tầng trình bày, không
được leo vào domain.

Hai bất biến đã được cưỡng chế trong code, không chỉ nằm trong tài liệu:

- `Star.__post_init__` — `strength` và `strength_verification` phải **cùng có hoặc
  cùng thiếu**. Có giá trị mà không có mức tin cậy chính là cách "chưa biết" bị đọc
  thành "đã kiểm định".
- `StarMetadata.__post_init__` — ngũ hành và âm/dương cùng có hoặc cùng thiếu; để
  trống thì buộc phải liệt kê ≥ 2 cách đọc đang mâu thuẫn.

Test chặn: `tests/test_data_contract.py::test_no_string_field_smuggles_in_a_placeholder`
quét toàn bộ payload tìm các chuỗi giữ chỗ nói trên.

---

## 1. Phiên bản schema

`schema_version` nằm ở gốc payload.

| Phiên bản | Nghĩa |
| --- | --- |
| 1 | Lá số lưu **trước** khi có hợp đồng này. Không có khóa `schema_version`. |
| 2 | Hợp đồng hiện hành. |

Lá số đã lưu **không bị ghi lại**. API tính `chart_schema_version` khi đọc và trả về
cho client; client phải rẽ nhánh theo nó chứ không được dò từng field. `CHART_SCHEMA_VERSION`
trong `chart/model.py` là nguồn duy nhất.

---

## 2. Chart identity

Nguồn: engine, trừ `chart_id`.

| Field | Nghĩa | Tầng sinh ra | Null? | Đã cài? | Đã kiểm định? |
| --- | --- | --- | --- | --- | --- |
| `chart_id` | Id của lá số | **Tầng lưu trữ** | Có — `null` trong engine | ✅ | n/a |
| `engine_version` | Phiên bản engine đã tính | Engine | Không | ✅ | n/a |
| `convention_profile` | Bộ quy ước đã dùng | Engine | Không | ✅ | n/a |
| `convention_version` | Phiên bản bộ quy ước | Engine | Không | ✅ | n/a |
| `production_ready` | Mọi luật tối quan trọng đã VERIFIED chưa | Engine (cổng của hồ sơ) | Không | ✅ | n/a |
| `generated_at` | Lúc **chạy phép tính**, UTC ISO-8601 | Engine (truyền vào được) | Không | ✅ | n/a |

`chart_id` là `null` trong engine có chủ đích: nếu tầng tính toán tự sinh id thì cùng
một ngày sinh sẽ cho id khác nhau mỗi lần chạy.

`generated_at` truyền vào được để fixture pin cứng giá trị — lá số tự đóng dấu thời
gian mỗi lần chạy thì không thể so fixture theo byte.

---

## 3. Birth information

| Field | Nghĩa | Tầng | Null? | Đã cài? | Đã kiểm định? |
| --- | --- | --- | --- | --- | --- |
| `name` / `full_name` | Họ tên | Đầu vào | Không | ✅ | n/a |
| `gender` | Nam/Nữ | Đầu vào | Không | ✅ | n/a |
| `calendar_type` | Dương hay Âm lịch | Đầu vào | Không | ✅ | n/a |
| `solar.{day,month,year,hour,minute}` | Ngày giờ dương lịch | Engine (quy đổi) | Không | ✅ | ✅ §1 |
| `local_birth_time` | `"09:30"` — giờ đồng hồ như đã nhập | Engine | Không | ✅ | n/a |
| `timezone_id` | IANA zone | Đầu vào | Có | ✅ | 🟡 §2 |
| `historical_utc_offset` | Offset **thật sự đã dùng**, tra tzdb tại thời điểm sinh | Engine | Không | ✅ | 🟡 §2 |
| `tz_offset` | Khóa v1, cùng giá trị với `historical_utc_offset` | Engine | Không | ✅ | 🟡 §2 |
| `birth_place` | Nơi sinh, chỉ để hiển thị | Đầu vào | Có | ✅ | n/a |
| `hour_branch`, `hour_branch_index` | Địa chi giờ sinh | Engine | Không | ✅ | ✅ |

`historical_utc_offset` tách khỏi `timezone_id` vì offset của Việt Nam đã đổi: một ca
sinh 1968 ở Hà Nội là UTC+8, không phải UTC+7. Lá số chỉ ghi zone id sẽ che mất điều đó.

`lunar_birth.{day,month,year,is_leap_month,year_pillar}`: engine, không null, đã cài,
đã kiểm định (§1).

---

## 4. Tứ trụ

`pillars.{year,month,day,hour}`, mỗi trụ là `{can, chi, can_index, chi_index, name,
is_yang, nap_am, element}`. Engine sinh ra, không null, đã cài. Kiểm định: ✅ can chi,
🟡 nạp âm (§8).

---

## 5. Core chart

**Không có block `core` riêng.** Các giá trị §2 của đề bài đã nằm đủ trong
`yin_yang` / `menh` / `than` / `cuc`; thêm một block nữa chỉ là nhân đôi dữ liệu.
Ánh xạ:

| Khái niệm | Nằm ở | Null? | Kiểm định |
| --- | --- | --- | --- |
| `yin_yang` | `yin_yang.label`, `.year_is_yang`, `.gender_is_male`, `.is_thuan_ly` | Không | ✅ §4 |
| `birth_element` (bản mệnh) | `menh.element`, `menh.element_label`, `menh.nap_am` | Không | ✅ §8 |
| `cuc` | `cuc.number`, `.element`, `.label` | Không | 🟡 §9 |
| `menh_cuc_relationship` | `cuc.relation`, `cuc.relation_label` | Không | ✅ §10 |
| `menh_palace` | `menh.branch`, `menh.branch_index` | Không | ✅ §5 |
| `than_palace` | `than.branch`, `than.branch_index` | Không | ✅ §6 |
| `than_cu` | `than.resides_in`, `than.resides_in_label` | Không | ✅ §7 |

`menh.three_directions_four_positions` — tam phương tứ chính, engine sinh, renderer
chỉ vẽ.

---

## 6. Traditional metadata — **toàn bộ `null`**

| Field | Nghĩa | Null? | Đã cài? | Kiểm định |
| --- | --- | --- | --- | --- |
| `chu_menh` | Chủ Mệnh | **Luôn `null`** | ❌ | ❌ |
| `chu_than` | Chủ Thân | **Luôn `null`** | ❌ | ❌ |
| `lai_nhan_cung` | Lai nhân cung | **Luôn `null`** | ❌ | ❌ |
| `can_luong` | Cân lượng (cân xương tính số) | **Luôn `null`** | ❌ | ❌ |
| `nam_xem` | Năm xem | **Luôn `null`** | ❌ | ❌ |
| `tuoi_xem` | Tuổi xem | **Luôn `null`** | ❌ | ❌ |

Có mặt trong hợp đồng để phân biệt **"chưa tính"** với **"không tồn tại"**, và để khi
cài thì không phải đổi hợp đồng. Không được điền bằng bất cứ giá trị nào cho tới khi
có nguồn đã chốt.

`nam_xem` và `tuoi_xem` đi thành cặp: năm xem đứng một mình chỉ là một con số lịch,
nó chỉ có nghĩa khi đi cùng tuổi — mà cách tính tuổi (tuổi ta hay tuổi tròn) là câu
hỏi mở Q11, và hai cách lệch nhau một năm, đủ để dịch chuyển mọi lá lưu niên.

**Cách hiển thị khi thiếu.** View model giữ đủ mọi dòng, dòng không có dữ liệu mang
`value: null` và `pending: true`. **Renderer mới là nơi quyết định**: lá số của khách
**bỏ hẳn dòng**, còn màn hình nội bộ có thể bật `showPendingFields` để thấy chỗ còn
trống. Bản xuất PNG và bản in luôn dùng canvas ngoài màn hình, nơi cờ này không bao
giờ được bật — nên một ghi chú dev không thể lọt vào file khách cầm.

---

## 7. Palace

| Field | Nghĩa | Tầng | Null? | Đã cài? | Kiểm định |
| --- | --- | --- | --- | --- | --- |
| `id` | = `name`, để địa chỉ hóa cung | Engine | Không | ✅ | n/a |
| `name` | **Cung nào** (`PHU_THE`…) | Engine | Không | ✅ | 🟡 §11 |
| `label` | Tên tiếng Việt | Engine | Không | ✅ | 🟡 §11 |
| `branch`, `branch_index` | **Chỗ nào** trên địa bàn | Engine | Không | ✅ | ✅ |
| `palace_index` | Vị trí tên cung trong trình tự từ Mệnh (0–11) | Engine | Không (v1: `null`) | ✅ | 🟡 §11 |
| `stem`, `stem_index` | Thiên can của cung | Engine | Không | ✅ | 🟡 §12 |
| `element`, `nap_am` | Ngũ hành / nạp âm của cung | Engine | Không | ✅ | 🟡 §8 |
| `is_menh`, `is_than` | Cung Mệnh / Thân | Engine | Không | ✅ | ✅ |
| `is_empty_main_star` | Vô chính diệu | Engine | Không | ✅ | 🟡 |
| `month_number` | Tháng âm ứng với cung | — | **Luôn `null`** | ❌ | ❌ |
| `tuan`, `triet` | `{present, verification, source_rule}` | Engine | Không | ✅ | 🟡 §17/§18 |
| `has_tuan`, `has_triet` | Khóa v1, = `tuan.present` | Engine | Không | ✅ | 🟡 |
| `cycles.major_cycle_age_start/end` | Khoảng tuổi đại vận | Engine | Không | ✅ | 🟡 §25 |
| `cycles.major_cycle_index` | Đại vận thứ mấy (1 = cung Mệnh) | Engine | Không | ✅ | 🟡 §25 |
| `cycles.major_cycle_direction` | `FORWARD` / `BACKWARD` — chỉ **đường đi**, tên cung không đảo | Engine | Không | ✅ | 🟡 §25 |
| `cycles.trang_sinh_stage` | Một trong 12 chặng vòng Tràng Sinh | Engine | Không | ✅ | 🟡 §24 |
| `cycles.major_cycle_target`, `cycles.annual_target` | Lưu niên | — | **Luôn `null`** | ❌ | ❌ |
| `metadata` | Dữ kiện cung không phải sao/chu kỳ | Engine | Không (`{}`) | ✅ | n/a |
| `major_stars`, `minor_stars`, `transformations`, `annual_stars` | Sao đã nhóm sẵn cho renderer | Engine | Không | ✅ | 🟡 §14 |
| `stars` | **Cùng tập sao đó**, phẳng | Engine | Không | ✅ | 🟡 §14 |

> **`branch` và `name` là hai khái niệm khác nhau.** `branch` là *chỗ*, `name` là
> *cung nào*. Suy cái này từ cái kia chính là lỗi lật gương tên cung đã sửa ở engine
> 0.2.0. `palace_index` cố tình suy từ `PALACE_ORDER` (tên cung), **không** từ địa chi
> — có test chặn việc nó trùng `branch_index`.

`cycles.*` đều `null`: chiều và tuổi khởi đại vận bị chặn bởi Q11/Q12, Tràng Sinh chưa
cài. `month_number` phụ thuộc cách đánh số đại vận nên cũng `null`.

---

## 8. Star — **một model duy nhất**

Không có `MajorStarDTO` / `MinorStarDTO` / `AnnualStarDTO`. Chúng chỉ khác nhau ở
`category`, và ba hình dạng gần giống nhau sẽ buộc renderer rẽ nhánh theo kiểu thay vì
duyệt một danh sách.

| Field | Nghĩa | Tầng | Null? | Đã cài? | Kiểm định |
| --- | --- | --- | --- | --- | --- |
| `id` | Mã sao (`THAI_AM`) | Engine | Không | ✅ | n/a |
| `name` | Tên tiếng Việt | Engine | Không | ✅ | n/a |
| `category` | `StarCategory` | Engine | Không | ✅ (chỉ `MAJOR`) | 🟡 |
| `element` | Ngũ hành **của sao** | Engine | **Có** | ✅ 12/14 | 🟡 §23 |
| `polarity` | Âm/dương của sao | Engine | **Có** | ✅ 12/14 | 🟡 §23 |
| `strength` | Miếu/Vượng/Đắc/Bình/Hãm | — | **Luôn `null`** | ❌ | ❌ §19 |
| `strength_verification` | Mức tin cậy của `strength` | Engine | **Luôn `null`** | ❌ | ❌ |
| `palace_branch` | Địa chi sao đang ngồi | Engine | Có (v1: `null`) | ✅ | ✅ |
| `is_major` / `is_annual` / `is_transformation` | Suy từ `category` | Engine | Không | ✅ | n/a |
| `display_priority` | Thứ tự hiển thị trong cung | Engine | Không (v1: `null`) | ✅ | n/a |
| `verification_status` | Mức tin cậy của **vị trí** sao | Engine | Không | ✅ | n/a |
| `provenance` | `{rule, verification, blocked_by, note}` | Engine | Có | ✅ | n/a |
| `provisional` | Suy ra: chưa `VERIFIED` | Engine | Không | ✅ | n/a |

`id`, `name`, `category`, `element`, `polarity` và `display_priority` đều lấy từ
**catalog sao** (`stars/catalog.py`). Luật an sao chỉ giữ id và offset, nên không có
chỗ nào trong thuật toán an sao còn giữ tên hay thuộc tính của sao.

`display_priority` chỉ dịch chữ trên trang, **không** hàm ý sức nặng tử vi nào. Trước
đây nó là bảng tự đặt trong frontend; giờ engine cấp, frontend chỉ còn dùng bảng dự
phòng cho lá số v1.

Hai mức kiểm định khác nhau, đừng lẫn:

| Câu hỏi | Nằm ở | Hiện tại |
| --- | --- | --- |
| Sao nằm **đúng chỗ** chưa? | `star.verification_status`, `star.provenance` | `PROVISIONAL` (luật `major_stars`) |
| Sao này **là hành gì**? | `StarDefinition.verification_status` trong catalog | `PROVISIONAL` 12/14, `UNVERIFIED` 2/14 |

`verification_status` lấy từ luật đã an sao, nên **một sao không bao giờ tự nhận mức
tin cậy cao hơn luật đã đặt nó** — có test chặn.

---

## 9. API DTO

| Field | Nghĩa | Tính hay lưu? |
| --- | --- | --- |
| `chart` | Payload engine, y nguyên như lúc lưu | **Lưu** |
| `chart_schema_version` | Payload thuộc schema nào | **Tính khi đọc** |
| `recalculation` | `{needed, reason}` — lá số có lạc hậu không | **Tính khi đọc** |
| `engine_version`, `convention_profile`, `convention_version` | Cột riêng để truy vấn | **Lưu** |

Hai field tính khi đọc là có chủ đích: một dòng đã lưu được trả về **đúng như lúc
ghi**. Không migration nào viết lại `chart_json`.

---

## 10. ViewModel

Được phép: nhãn tiếng Việt, thứ tự hiển thị, định dạng an toàn với `null`, nhóm chính
tinh / phụ tinh, toạ độ lưới, hình học Tuần/Triệt, `aria-label`.

Toàn bộ việc **diễn đạt tiếng Việt** nằm ở `apps/web/utils/tuvi-format.ts`, không rải
trong từng component. Các hàm ở đó **ghép và gán nhãn**, không tính tử vi: can chi do
engine gửi dưới dạng can và chi riêng, formatter chỉ nối lại — viết lại vòng lục thập
hoa giáp trong trình duyệt là thêm một chỗ nữa có thể sai. Mỗi formatter trả `null`
cho đầu vào không dựng được, và `null` nghĩa là **bỏ dòng**, không bao giờ biến thành
`"—"`, `"Không rõ"` hay số 0.

Engine đã gửi sẵn `yin_yang.label`, `cuc.label`, `pillar.name`; formatter dựng lại
được từ các phần rời. Hai cách viết cho cùng một giá trị chính là cách một lá số tự
mâu thuẫn với chính nó, nên có test ghim chúng bằng nhau.

**Không được phép:** an sao, gán tên cung, tính độ sáng, suy ngũ hành, tính Tuần/Triệt.

Việc chuẩn hóa v1 → v2 nằm ở đây: `mapStar` đọc `id ?? code` và `name ?? label`, và
`kind` v1 được ánh xạ sang `category`. Không cái nào suy ra từ cái kia.

Ba quy tắc đọc phòng vệ, vì đây là chỗ dữ liệu lạ có thể lọt vào:

- `verification_status` không nhận diện được → `UNVERIFIED`. Cách đọc an toàn, không
  phải cách đọc dễ chịu.
- `provenance` điền nửa vời → `null`. Thà không có provenance hơn là có một nửa.
- `element` không thuộc 5 hành → `null`, vẽ mực trung tính.

---

## 11. Fixture

`apps/web/fixtures/charts/*.json` là **DEVELOPMENT FIXTURE**: output engine nguyên
bản, `generated_at` pin cứng, sinh lại bằng
`scripts/dump_web_fixtures.py`. **Không phải giá trị tử vi đúng** — đừng suy kỳ vọng
test mới từ chúng. Xem `apps/web/fixtures/charts/README.md`.

Giá trị kỳ vọng **suy từ định nghĩa** nằm ở `packages/astrology-engine/tests/fixtures/`.

---

## 12. Chưa hỗ trợ

Có mặt trong hợp đồng nhưng luôn rỗng/`null`:

| Mục | Trạng thái | Chặn bởi |
| --- | --- | --- |
| `four_transformations` | `{}` | §15 — chưa chốt nguồn |
| `major_cycles` | `[]` | Q11/Q12 |
| `annual_cycles` | `[]` | Q11/Q12 |
| `cycles.annual_target` | `null` | Q11/Q12 — lưu niên |
| `star.strength` | `null` | §19 — bảng 168 ô, phải chép từ nguồn |
| `traditional.*` | `null` | Chưa cài |
| `palace.month_number` | `null` | Phụ thuộc đánh số đại vận |
