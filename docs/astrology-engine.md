# Astrology Engine — đặc tả kỹ thuật

Cập nhật: **2026-09-11** · Gói: `packages/astrology-engine` · Ngôn ngữ: Python 3.12

Tài liệu này mô tả **kiến trúc và hợp đồng dữ liệu** của engine.
Quy tắc Tử Vi cụ thể nằm ở [`astrology-conventions.md`](astrology-conventions.md) —
đọc tài liệu đó trước khi sửa bất kỳ phép tính nào.

> **Trạng thái: engine chưa hoàn chỉnh và cố ý như vậy.** Phần khung lá số đã
> kiểm chứng; phần an sao mới ở mức xem trước và mang cờ `provisional`.
> Điều đang chặn không phải là code mà là **quyết định chọn trường phái và nguồn
> chuẩn** (mục 0 của tài liệu quy ước).

---

## 1. Engine nằm ở đâu trong hệ thống

```
Birth Info
    ↓
Calendar Conversion          ─┐
Deterministic Astrology Engine│  packages/astrology-engine  ← tài liệu này
    ↓                         │  100% tất định, không AI, không random
Chart JSON                   ─┘
    ↓
Rule / Analysis Engine          (chưa làm) → facts + score + evidence
    ↓
AI Interpretation               (chưa làm) → chỉ sinh lời văn
    ↓
Reading
```

**Ràng buộc cứng, lấy từ `business.md` mục 3:**

- Engine **không** phụ thuộc database, HTTP, config hay Pydantic. Chỉ dataclass thuần.
- Engine **không** dùng `random`, `datetime.now()`, `uuid4` hay bất cứ nguồn phi
  tất định nào. Đã kiểm chứng bằng grep và bằng test so sánh hai lần dựng.
- AI **không bao giờ** được suy ra vị trí sao. Sao nào không có trong chart JSON
  thì không tồn tại.
- Frontend **không** chứa logic tử vi. Hằng số thuộc về tử vi mà giao diện cần
  (thứ tự cung, bảng canh giờ, layout địa bàn) đặt ở `packages/shared`.

---

## 2. Cấu trúc gói

```
packages/astrology-engine/src/cosmic_astrology/
├── calendar/
│   ├── lunar.py        Dương ↔ Âm lịch (Meeus ch.49 + ΔT)
│   └── sexagenary.py   Can chi tứ trụ, nạp âm 60 hoa giáp
└── chart/
    ├── types.py        BirthInput, Chart, Palace, Star (dataclass thuần)
    └── builder.py      build_chart() — điểm vào duy nhất
```

Điểm vào công khai duy nhất:

```python
from cosmic_astrology import BirthInput, build_chart
chart = build_chart(birth_input, stage=EngineStage.PREVIEW)
```

`apps/api/app/services/chart_service.py` là **nơi duy nhất** gọi engine.

---

## 3. Ba mức hoàn thiện (`EngineStage`)

Chuỗi `FRAME → PREVIEW → FULL` tồn tại để **không bao giờ phải bịa số liệu**.

| Stage | Nội dung | Dùng ở đâu |
|---|---|---|
| `FRAME` | Chỉ phần đã kiểm chứng: lịch, tứ trụ, 12 cung, Mệnh, Thân, Cục, Tuần, Triệt. **Không an sao nào.** | An toàn ở mọi môi trường |
| `PREVIEW` | `FRAME` + 14 chính tinh, **mọi sao mang `provisional: true`** | Hiện tại. UI bắt buộc hiển thị cảnh báo |
| `FULL` | Engine đầy đủ | **Chưa làm** — `build_chart` ném `NotImplementedError` |

Stage hiện hành cấu hình qua biến môi trường `CHART_ENGINE_STAGE` (mặc định `PREVIEW`).

`Chart.engine.is_authoritative` chỉ `true` khi stage là `FULL`. UI dùng cờ này
để quyết định có hiện băng cảnh báo hay không — không hard-code.

### Điều kiện để lên `FULL`

Tất cả phải đúng, không được bỏ qua mục nào:

1. Đóng **toàn bộ** câu hỏi 🔴 trong tài liệu quy ước (Q1–Q12).
2. Ma trận kiểm định 14 chính tinh được người có chuyên môn **ký duyệt**
   (`verified_against_source: true` cho mọi ca).
3. Có bảng miếu vượng đắc hãm đủ 168 ô, chép từ nguồn đã chốt.
4. Tứ Hóa, Lộc Tồn và nhóm phụ tinh đã cài và có test.
5. Không còn sao nào mang `provisional: true`.

---

## 4. Hợp đồng dữ liệu

### Đầu vào — `BirthInput`

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `name` | `str` | Chỉ để nhận diện, không tham gia tính toán |
| `gender` | `MALE \| FEMALE` | **Là dữ liệu tính toán**: cùng âm dương năm sinh quyết định chiều đại vận |
| `calendar_type` | `SOLAR \| LUNAR` | |
| `day`, `month`, `year` | `int` | Theo lịch đã chọn ở `calendar_type` |
| `hour` | `int` 0–23 | Chỉ canh giờ có ý nghĩa |
| `minute` | `int` 0–59 | **Hiện bị bỏ qua hoàn toàn** — xem Q4 |
| `is_leap_month` | `bool` | Chỉ hợp lệ với `LUNAR` |
| `tz_offset` | `float` | Mặc định `7.0`. **API luôn gửi 7.0** — xem Q5 |
| `birth_place` | `str \| None` | Hiện chỉ lưu, chưa dùng để suy múi giờ |

Dải năm hợp lệ: **1900–2100** (giới hạn của đa thức ΔT đã cài).

### Đầu ra — `Chart`

Xem `chart/types.py` và bản mirror TypeScript ở
`packages/shared/src/types/chart.ts`. Hai bên **phải luôn khớp nhau**.

Các khối chính: `engine`, `birth`, `lunar_birth`, `pillars`, `yin_yang`, `menh`,
`than`, `cuc`, `palaces[12]`, và ba khối rỗng dành sẵn cho phase sau:
`major_cycles`, `annual_cycles`, `four_transformations`.

### `Star` — mọi sao đều mang cờ tin cậy

```python
@dataclass
class Star:
    code: str            # TU_VI, THIEN_CO, …
    label: str           # "Tử Vi"
    kind: StarKind       # MAJOR | MINOR | TRANSFORMATION
    strength: StarStrength | None   # MIEU|VUONG|DAC|BINH|HAM — hiện LUÔN None
    provisional: bool    # true = vị trí chưa được kiểm định
```

`provisional` **không phải trang trí**. Nó là cam kết với người dùng: cái gì chưa
kiểm định thì nói thẳng. UI hiện dấu `*` và một dòng giải thích.

---

## 5. Đã cài và đã kiểm chứng

| Phần | Trạng thái | Test |
|---|---|---|
| Dương ↔ Âm lịch (Meeus ch.49 + ΔT) | ✅ | Ngày Tết chính thống 2000–2026, nhuận Quý Mão 2023 |
| Can chi tứ trụ, ngũ hổ độn, ngũ thử độn | ✅ | `test_sexagenary.py` |
| Nạp âm 60 hoa giáp | ✅ | |
| 12 cung: địa chi, thiên can, nạp âm | ✅ | `test_chart_frame.py` |
| An Mệnh, an Thân, Thân cư | ✅ | |
| Cục và quan hệ Mệnh–Cục | ✅ | |
| Tuần không, Triệt lộ | ✅ | |
| Tam phương tứ chính, vô chính diệu | ✅ | |
| An Tử Vi | 🟡 khớp 5 mốc kinh điển mùng 1 | ma trận `TV-A1`…`TV-A5` |
| 14 chính tinh (2 chòm) | 🟡 `provisional` | chưa có ca nào ký duyệt |

**48 test đang xanh.**

---

## 6. Chưa cài — và vì sao

| Phần | Chặn bởi |
|---|---|
| Bảng miếu vượng đắc hãm (168 ô) | Q1, Q2 — **tuyệt đối không bịa** |
| Tứ Hóa | Q7, Q8 (hàng Canh/Mậu/Nhâm tranh chấp) + cần phụ tinh trước |
| Lộc Tồn, Kình Dương, Đà La | Q2 |
| Nhóm phụ tinh còn lại | Q1, Q2 |
| Đại vận, tiểu vận, lưu niên | Q11, Q12 |
| Xử lý giờ Tý muộn | **Q6 — code hiện tại tự mâu thuẫn, xem mục 8** |

---

## 7. Ma trận kiểm định 14 chính tinh

File: `packages/astrology-engine/tests/fixtures/major_stars_matrix.json`

**17 ca**, phủ:

| Chiều phủ | Giá trị |
|---|---|
| Cục | cả 5 (Thủy nhị → Hỏa lục) |
| Vị trí Mệnh | 9 địa chi khác nhau |
| Vị trí Tử Vi | 10 địa chi khác nhau |
| Âm dương × giới tính | cả 4 tổ hợp |
| Ca neo có kỳ vọng kinh điển | 5 |
| Ca bị chặn | 1 (`TV-B1`, giờ Tý muộn) |

Ca đặc biệt: Tử Vi trùng Thiên Phủ tại Dần và tại Thân (`TV-C1`…`TV-C4`),
Thân cư Mệnh (`TV-S5`), ngày 30 âm lịch (`TV-S6`), tháng nhuận (`TV-L1`).

### Cách đọc file — đọc kỹ chỗ này

Mỗi ca có ba khối, **đừng nhầm**:

| Khối | Nghĩa |
|---|---|
| `derived_frame` | Kết quả phần khung (đã kiểm chứng). Tin được. |
| `engine_candidate_stars` | **ĐẦU RA HIỆN TẠI của engine. KHÔNG phải giá trị kỳ vọng.** Đây là thứ cần đem đi đối chiếu, không phải thứ để assert. |
| `expected_stars` | Hiện `null`. Người thẩm định điền vào **từ nguồn chuẩn**, rồi đặt `verified_against_source: true`. |

**Test chỉ được assert trên `expected_stars`.** Ca nào chưa `verified` thì skip.
Nếu viết test assert trên `engine_candidate_stars` thì chỉ là engine tự xác nhận
chính nó — vô nghĩa.

### Quy trình thẩm định

1. Chốt nguồn chuẩn (Q1, Q2) và ghi vào ô `source_of_truth`.
2. Với từng ca: dựng lá số **bằng tay hoặc bằng phần mềm của nguồn đã chốt**.
3. Điền `expected_stars`. **Không** chép từ `engine_candidate_stars`.
4. So sánh. Lệch thì ghi vào sổ mâu thuẫn (mục 21 tài liệu quy ước) — có thể
   engine sai, cũng có thể nguồn dùng quy ước khác.
5. Đặt `verified_against_source: true`.

---

## 8. Lỗi đã biết trong code hiện tại

### 8.1 Giờ Tý muộn xử lý không nhất quán 🔴

Sinh lúc 23:xx: `pillars_for_birth()` dịch **trụ ngày** sang ngày hôm sau
(`day_jd = jd + 1 if hour == 23`), nhưng `build_chart()` lấy `lunar.day` từ ngày
dương gốc, **không dịch**.

Đo được trên ca 10/09/1992 23:00 — trụ ngày `Canh Dần` (của 11/09) đi cùng ngày
âm `14` (của 10/09). Vì Tử Vi an theo ngày âm, chọn sai quy ước **dịch Tử Vi 3 cung**.

**Không sửa vội.** Phải chốt Q6 trước, rồi sửa cho nhất quán ở cả hai chỗ.

### 8.2 `minute` bị bỏ qua

Hợp lý khi canh giờ là đơn vị duy nhất có ý nghĩa — nhưng sẽ **không còn hợp lý**
nếu Q4 chọn giờ mặt trời thật, lúc đó phút trở thành đầu vào thật.

### 8.3 `tz_offset` luôn là 7.0 trên thực tế

Engine nhận tham số nhưng API và frontend không bao giờ gửi giá trị khác.
Người sinh trước 1975 có nguy cơ sai ngày âm nếu sinh gần nửa đêm (Q5).

---

## 9. Nguyên tắc khi viết code cho phase sau

1. **Một quy tắc = một nguồn.** Không ghép nửa trường phái này nửa trường phái kia.
2. **Bảng tra thì chép nguyên, không suy ra bằng công thức** trừ khi nguồn nói rõ
   là có công thức.
3. **Sao mới mặc định `provisional: true`** cho tới khi có ca kiểm định ký duyệt.
4. **Thêm sao là thêm dữ liệu, không đổi cấu trúc.** Frontend đã render sẵn
   `major_stars` / `minor_stars` / `transformations` — không cần sửa giao diện.
5. **Mỗi quy tắc mới phải kèm ít nhất một bất biến kiểm được.**
   Ví dụ: "Lộc Tồn không bao giờ ở tứ mộ", "Thân chỉ cư được 6 cung".
