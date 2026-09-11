# Quy trình kiểm định engine Tử Vi

Cập nhật: **2026-09-11**

Tài liệu này trả lời hai câu hỏi:
**"Engine được phép tuyên bố điều gì?"** và **"Làm sao để nó được phép tuyên bố nhiều hơn?"**

---

## 1. Xem trạng thái hiện tại

```bash
make astrology-verification-report
```

Mọi con số trong báo cáo đều **tính từ dữ liệu thật** — hồ sơ quy ước và file
fixture — chứ không viết tay. Sửa một `RuleBinding` là báo cáo đổi theo; không
có cách nào để báo cáo đẹp hơn thực tế.

---

## 2. Ba trạng thái, và một trạng thái thứ tư hiện ra từ hai cờ

`VerificationStatus` chỉ có ba giá trị:

| Trạng thái | Nghĩa |
|---|---|
| `UNVERIFIED` | Chưa ai đối chiếu với nguồn nào. |
| `PROVISIONAL` | Đã cài, khớp quy tắc kinh điển, **chưa được ký duyệt**. |
| `VERIFIED` | Đã đối chiếu nguồn đã chốt và có người ký. |

`BLOCKED` trong báo cáo **không phải** một mức tin cậy. Nó là tổ hợp
`implemented = False` **và** `blocked_by` khác rỗng — đọc rõ hơn `UNVERIFIED`
khi thứ đang thiếu là một quyết định chứ không phải công sức.

> **"Đã cài" ≠ "đã kiểm định".** 14 chính tinh đã code đầy đủ và vẫn
> `PROVISIONAL`. Trộn hai khái niệm này chính là cách một lá số chưa ai kiểm
> được đem đi bán như hàng chuẩn.

---

## 3. Ma trận kiểm định

File: `packages/astrology-engine/tests/fixtures/major_stars_matrix.json`

### Ba khối, đừng nhầm

| Khối | Ai điền | Ý nghĩa |
|---|---|---|
| `derived_frame` | engine | Phần khung đã kiểm chứng. Tin được. |
| `engine_candidate_stars` | engine | **Đầu ra hiện tại. KHÔNG phải chân lý.** Đây là thứ đem đi đối chiếu. |
| `expected_*` | **người thẩm định** | Lấy từ nguồn độc lập. `null` = chưa kiểm định. |

`expected_tu_vi`, `expected_stars`, `expected_tuan`, `expected_triet` đều bắt
đầu bằng `null`. **Test coi `null` là chưa kiểm định và bỏ qua**, không bao giờ
coi là đã xác nhận.

### Quy tắc bất di bất dịch

> **Không bao giờ chép `engine_candidate_stars` sang `expected_stars`.**

Có test canh điều này: nếu hai khối trùng khít mà không có
`independently_confirmed: true` kèm tên người thẩm định, test đỏ. Một fixture
chép từ chính engine thì chỉ chứng minh engine bằng chính nó — vô nghĩa.

### Quy trình thẩm định một ca

1. Chốt nguồn chuẩn (Q1, Q2, Q3), ghi vào `source_of_truth`.
2. Dựng lá số **bằng tay hoặc bằng phần mềm của nguồn đã chốt**. Không mở engine ra xem.
3. Điền `expected_tu_vi` và `expected_stars`.
4. Điền `reviewer`, `source`, `verification_status`.
5. So sánh với `engine_candidate_stars`.
   - Khớp → đặt `verified_against_source: true`.
   - Lệch → **ghi vào sổ mâu thuẫn** (`astrology-conventions.md` mục 21).
     Có thể engine sai, cũng có thể nguồn dùng quy ước khác. Đừng sửa engine vội.

---

## 4. Khi reviewer nói "sao X nằm sai cung"

Bật trace để thấy **vì sao** nó được đặt ở đó:

```python
chart = build_chart(birth, stage=EngineStage.PREVIEW, trace=True)
print(TraceLog(...).format())   # hoặc chart.to_dict()["trace"]
```

Mỗi bước ghi: quy tắc nào, đầu vào nào, chính sách nào, mức tin cậy, và đang
chờ câu hỏi mở nào. Trace **mặc định tắt** và không ảnh hưởng kết quả — có test
xác nhận bật trace không làm đổi lá số.

---

## 5. Cổng production

```python
from cosmic_astrology import is_production_ready, validate_convention_profile
```

Một hồ sơ chỉ `production_ready` khi **mọi** quy tắc trong `CRITICAL_RULES`
đều đã chốt, đã cài, và ở mức `VERIFIED`:

`calendar`, `timezone`, `late_zi`, `menh_placement`, `than_placement`, `cuc`,
`palace_order`, `palace_stems`, `tu_vi_placement`, `major_stars`.

Hôm nay hồ sơ chuẩn **không** đạt, vì `late_zi` chưa chốt và `tu_vi_placement`
với `major_stars` mới ở mức `PROVISIONAL`. **Đó là trạng thái đúng**, không phải lỗi.

Cổng này **chưa bật toàn cục** để không chặn việc phát triển. Chế độ dev vẫn
lập được lá số với hồ sơ tạm; cờ `is_authoritative` trong payload và cờ
`provisional` trên từng sao là thứ UI dùng để nói thật với người dùng.

---

## 6. Phiên bản và việc tính lại

Mỗi lá số mang dấu bất biến:

```json
{
  "engine_version": "0.2.0",
  "convention_profile": "COSMIC_SIGNS_STANDARD_V1",
  "convention_version": "2026.09"
}
```

Lưu cả trong `chart_json` **và** thành cột `convention_profile` /
`convention_version` trên bảng `charts`, để truy vấn được "lá số nào lập theo
luật cũ" mà không phải quét JSON toàn bảng.

### Nguyên tắc: không bao giờ tính lại ngầm

```python
from cosmic_astrology.conventions import needs_recalculation
check = needs_recalculation(chart.convention_profile, chart.convention_version, PROFILE)
```

Lá số **không** được tính lại khi đọc. Một bản luận giải người ta đã trả tiền
không được phép đổi dưới chân họ. `needs_recalculation` chỉ trả lời *lá số nào
sẽ ra khác nếu lập lại hôm nay*, để còn **đề nghị** họ lập lại — chứ không áp đặt.

Cột để `NULL` với lá số lập trước khi có tầng quy ước: chúng thật sự không biết
đã dùng luật nào, và ghi đại một tên hồ sơ vào đó là nói dối.

---

## 7. Khi nào được nâng lên `FULL`

Tất cả, không bỏ mục nào:

1. Đóng toàn bộ câu hỏi 🔴 Q1–Q12.
2. Mọi ca trong ma trận có `verified_against_source: true`, kèm reviewer và nguồn.
3. Bảng miếu vượng đắc hãm đủ 168 ô, chép từ nguồn đã chốt.
4. Tứ Hóa, Lộc Tồn và nhóm phụ tinh đã cài và có test.
5. `is_production_ready(profile)` trả `True`.
6. Không còn sao nào mang `provisional: true`.
