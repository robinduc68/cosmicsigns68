# Quy ước Tử Vi của Cosmic Signs

Cập nhật: **2026-09-11** · Trạng thái: **BẢN THẢO — chưa được người có chuyên môn ký duyệt**

Tài liệu này chốt **đúng một** bộ quy tắc tính lá số. Mục đích duy nhất của nó là
ngăn việc trộn quy tắc từ nhiều trường phái khác nhau ở các phase sau.

> **Đọc kỹ trước khi dùng.** Tài liệu này do người viết code soạn từ *code hiện có*
> cộng với các quy tắc kinh điển phổ biến. Nó **chưa được một người hành nghề Tử Vi
> thẩm định**. Mọi mục gắn 🔴 hoặc 🟡 đều chưa được phép coi là chân lý.

---

## Ký hiệu trạng thái

| | Nghĩa |
|---|---|
| ✅ **FROZEN** | Đã cài đặt, có test, coi như chốt. Đổi phải có lý do và sửa test. |
| 🟡 **PENDING** | Đã cài đặt (hoặc đã đề xuất) và khớp quy tắc kinh điển, nhưng **chưa đối chiếu với nguồn chuẩn đã chốt**. |
| 🔴 **OPEN** | Chưa quyết. **Chặn** việc viết code cho phần liên quan. |
| ⛔ **BLOCKED** | Phụ thuộc một mục 🔴 khác. |

Quy tắc phụ thuộc trường phái đều ghi rõ `COSMIC_SIGNS_CHOSEN_RULE`,
`ALTERNATIVE_RULE` và lý do chọn.

Quy ước chỉ số dùng xuyên suốt: **địa chi 0 = Tý, 1 = Sửu, … 11 = Hợi**;
**thiên can 0 = Giáp, … 9 = Quý**. Mọi phép cộng đều `mod 12` / `mod 10`.

---

## 0. Nguồn chuẩn 🔴 OPEN — **đây là thứ đang chặn mọi thứ**

**Chưa chốt.** Cosmic Signs hiện **không có** một nguồn chuẩn được chỉ định.

Đây không phải việc viết code mà là một quyết định nghiệp vụ. Cho tới khi có
câu trả lời, mọi sao đều phải mang cờ `provisional` và UI phải nói rõ.

Cần chốt ba thứ:

| Cần chốt | Vì sao quan trọng |
| --- | --- |
| **Q1 — Trường phái** | Nam phái / Bắc phái / biến thể Việt Nam. Quyết định bảng Tứ Hóa, miếu vượng, và vài vị trí phụ tinh. |
| **Q2 — Sách/nguồn đối chiếu cụ thể** | Cần một ấn bản có tên và năm xuất bản để viết test. "Tra trên mạng" không đủ: các trang web mâu thuẫn nhau. |
| **Q3 — Người thẩm định** | Một người đọc được lá số, ký duyệt vào 17 ca trong ma trận kiểm định. Không có người này thì không thể nâng engine lên `FULL`. |

> **Khuyến nghị:** chọn **một** nguồn tiếng Việt in giấy làm chuẩn duy nhất, ghi
> tên ấn bản + năm vào ô "source_of_truth" trong
> `packages/astrology-engine/tests/fixtures/major_stars_matrix.json`. Khi hai
> nguồn mâu thuẫn, nguồn đã chốt thắng — và ghi lại mâu thuẫn vào mục 21 dưới đây.

---

## 1. Chuyển đổi Dương ↔ Âm lịch ✅ FROZEN

**COSMIC_SIGNS_CHOSEN_RULE** — Thuật toán thiên văn theo Meeus
(*Astronomical Algorithms*, 2nd ed., chương 49) cho thời điểm sóc, cộng hiệu chỉnh
ΔT theo Espenak & Meeus, rồi áp luật lịch Việt Nam:

- Tháng 11 âm lịch **luôn chứa đông chí**.
- Năm 13 tháng thì nhuận vào **tháng đầu tiên không chứa trung khí**.
- Ngày âm bắt đầu từ **nửa đêm dân sự địa phương**, không phải UTC.

**ALTERNATIVE_RULE** — Tra bảng lịch vạn niên in sẵn.

**Lý do chọn:** tính được cho mọi năm trong 1900–2100 mà không cần dữ liệu tra
cứu, và kiểm chứng được bằng test. Bản rút gọn của Meeus từng bị thử và **sai tới
~43 phút**, đủ để lệch mùng 1 và làm sai toàn bộ lá số — nên bắt buộc dùng bản đầy đủ.

**Đã kiểm chứng:** 48 test, đối chiếu ngày Tết chính thống 2000–2026 và tháng
nhuận Quý Mão 2023.

**Cài đặt:** `calendar/lunar.py`.

---

## 2. Xử lý múi giờ 🔴 OPEN

**Hiện trạng code (đã sửa 2026-09-11):** offset tra từ **IANA tzdb** tại đúng
thời điểm sinh qua `zoneinfo`, gói `tzdata` được ghim làm dependency. Lá số ghi
lại `timezone_id`, offset, nguồn và cờ `resolved_from_database`.

Con số đáng nhớ: theo tzdb, miền Nam chạy **UTC+8 từ 1960 đến giữa 1975**. Có
**251 ngày** trong khoảng đó mà +7 và +8 cho ra **ngày âm khác nhau** — giả định
cũ sai nguyên một giờ cho cả một thế hệ người còn sống.

Hai câu hỏi dưới đây vẫn mở, và chúng **không** phải cùng một việc với múi giờ:

Có **hai câu hỏi chưa trả lời**, và cả hai đều làm sai lá số nếu trả lời sai:

### Q4 — Giờ dân sự hay giờ mặt trời thật? 🔴

| | |
|---|---|
| **Phương án A (hiện tại)** | Dùng thẳng giờ đồng hồ dân sự. Giờ 14:00 ở Hà Nội và ở Cà Mau đều là giờ Mùi. |
| **Phương án B** | Hiệu chỉnh về giờ mặt trời địa phương theo kinh độ nơi sinh (±4 phút cho mỗi độ kinh tuyến lệch so với 105°Đ), có thể cộng phương trình thời gian. |

Việt Nam trải từ ~102°Đ đến ~110°Đ, tức lệch tới **±20 phút** so với kinh tuyến
chuẩn 105°Đ. Với người sinh gần ranh giới canh giờ, chênh 20 phút là **đổi canh
giờ, đổi cung Mệnh, đổi cả lá số**.

> Chưa chọn. Phương án B đòi phải thu thập kinh độ nơi sinh — hiện `birth_place`
> mới chỉ lưu dạng chữ, chưa có toạ độ.

### Q5 — Nguồn múi giờ lịch sử 🟡 (đã có lời giải kỹ thuật)

Múi giờ hành chính ở Việt Nam **đã thay đổi nhiều lần** trong thế kỷ 20, và miền
Nam từng dùng offset khác miền Bắc trong một số giai đoạn trước 1975. Người sinh
trong các giai đoạn đó mà bị tính bằng UTC+7 sẽ **sai ngày âm** nếu sinh gần nửa đêm.

> **Đã dùng IANA tzdb** làm nguồn, thay vì tự lập bảng. Còn lại là câu hỏi
> nghiệp vụ: tzdb mô tả **múi giờ hành chính**, mà người sinh ở vùng do bên khác
> kiểm soát trong thời chiến có thể đã sống theo giờ khác giờ hành chính trên
> giấy tờ. Cần người am hiểu xác nhận xem có cần xử lý riêng không.

---

## 3. Giờ Tý và ranh giới ngày 🔴 OPEN — *câu hỏi* chưa chốt, nhưng mâu thuẫn code đã gỡ

Giờ Tý kéo dài **23:00–00:59**, tức vắt qua nửa đêm. Chia làm hai nửa:

- **Tý sớm** (早子時) 23:00–23:59 — thuộc ngày dương *trước*
- **Tý muộn** (夜子時) 00:00–00:59 — thuộc ngày dương *sau*

### Q6 — Sinh lúc 23:xx thì tính là ngày nào? 🔴

Đây là tranh luận có thật giữa các trường phái. Trước tháng 9/2026 Cosmic Signs
trả lời **không nhất quán mà không ai chọn điều đó**; đo được bằng thực nghiệm:

Sinh **10/09/1992 lúc 23:00**:

| Đại lượng | Giá trị engine cho ra | Thuộc ngày nào |
|---|---|---|
| Trụ ngày | `Canh Dần` | **11/09** (đã dịch sang ngày sau) |
| Ngày âm dùng để an Tử Vi | `14` | **10/09** (chưa dịch) |

Hai đại lượng đang theo hai quy ước khác nhau trong cùng một lá số. Vì Tử Vi an
theo ngày âm, sai lệch này **dịch Tử Vi đi 3 cung** (Kim tứ cục: ngày 14 → Mùi,
ngày 15 → Thìn).

Nguồn gốc: `pillars_for_birth()` có `day_jd = jd + 1 if hour == 23`, nhưng
`build_chart()` lấy `lunar.day` từ ngày dương gốc, không dịch.

> **Kiến trúc đã sửa (2026-09-11).** Quyết định nay thuộc về `LateZiPolicy` trong
> hồ sơ quy ước. `pillars_for_birth` không còn tự dịch ngày; hồ sơ chuẩn đặt
> `UNRESOLVED` nên engine **từ chối lập lá số sinh lúc 23:xx** kèm thông báo nêu
> tên cả ba phương án. **Câu hỏi Q6 vẫn chưa được trả lời** — cái đã sửa là chỗ
> để câu trả lời, không phải câu trả lời.

**Ba phương án, phải chọn đúng một:**

| | Quy tắc | Hệ quả |
|---|---|---|
| **A** | 23:xx thuộc **ngày hôm sau** cho *mọi* mục đích (cả trụ ngày lẫn ngày âm) | Nhất quán. Phải dịch cả ngày âm. |
| **B** | 23:xx thuộc **ngày hiện tại** cho *mọi* mục đích | Nhất quán. Phải bỏ `+1` ở trụ ngày. |
| **C** | Trụ ngày dịch, ngày âm không dịch (`PILLAR_ONLY_NEXT_DAY`) | Có trường phái theo hướng này. Engine đánh dấu `internally_consistent: false` để sự bất đối xứng luôn hiện ra chứ không nấp đi. |

> **Chưa chọn.** Đây là mục chặn nặng nhất sau Q1: nó đổi vị trí Tử Vi, tức đổi
> cả 14 chính tinh. Ca `TV-B1` trong ma trận kiểm định đang bị đánh dấu CHẶN vì lý do này.

**Ranh giới canh giờ** (đã cài, ✅): `hour_branch_index(h) = ((h + 1) // 2) % 12`.
Tức Tý = 23–00, Sửu = 01–02, Dần = 03–04, … Hợi = 21–22. **Phút bị bỏ qua hoàn
toàn** — hệ quả trực tiếp là Q4 chưa giải thì phút không có ý nghĩa.

---

## 4. Xác định Âm Dương ✅ FROZEN

**COSMIC_SIGNS_CHOSEN_RULE** — Âm/dương lấy theo **thiên can của năm sinh âm lịch**.
Can chỉ số chẵn (Giáp, Bính, Mậu, Canh, Nhâm) là **dương**; lẻ là **âm**.

Kết hợp với giới tính cho ra bốn loại: Dương Nam, Âm Nam, Dương Nữ, Âm Nữ.

**ALTERNATIVE_RULE** — Một số tài liệu mô tả qua **địa chi** năm sinh (Tý, Dần,
Thìn, Ngọ, Thân, Tuất là dương). Trong hệ can chi hợp lệ, hai cách **luôn cho
cùng kết quả** vì can dương chỉ ghép với chi dương. Không phải mâu thuẫn thật.

**Cài đặt:** `Pillar.is_yang`, `Chart.yin_yang`.

---

## 5. An Mệnh ✅ FROZEN

**COSMIC_SIGNS_CHOSEN_RULE** — Khởi từ **cung Dần**, đếm **thuận** tới số tháng
sinh âm lịch, rồi từ đó đếm **nghịch** tới canh giờ sinh.

```
menh_branch = (2 + (tháng_âm − 1) − chi_giờ) mod 12
```

**Về tháng nhuận** 🟡 PENDING — engine hiện dùng **số tháng như đã ghi** (tháng 2
nhuận tính là tháng 2).

> `ALTERNATIVE_RULE`: một số trường phái tính nửa đầu tháng nhuận theo tháng trước
> và nửa sau theo tháng sau; số khác dùng tiết khí thay vì số tháng. **Chưa xác
> nhận.** Ca `TV-L1` trong ma trận tồn tại để kiểm định điểm này.

**Cài đặt:** `builder.build_chart`.

---

## 6. An Thân ✅ FROZEN

**COSMIC_SIGNS_CHOSEN_RULE** — Cùng điểm khởi (cung Dần), nhưng **cả hai lần đếm
đều thuận**.

```
than_branch = (2 + (tháng_âm − 1) + chi_giờ) mod 12
```

Hệ quả kiểm được: Mệnh và Thân **luôn đối xứng qua trục Dần–Thân**, và trùng nhau
khi sinh giờ Tý hoặc giờ Ngọ.

---

## 7. Thân cư ✅ FROZEN

**COSMIC_SIGNS_CHOSEN_RULE** — "Thân cư X" nghĩa là **địa chi của Thân rơi vào
cung tên X** trong 12 cung đã an. Không tính riêng.

Do Mệnh và Thân đối xứng qua trục Dần–Thân, Thân chỉ có thể cư vào **6 cung**:
Mệnh, Phúc Đức, Quan Lộc, Thiên Di, Tài Bạch, Phu Thê. Đây là bất biến kiểm được
bằng test.

---

## 8. Ngũ hành Mệnh (bản mệnh) ✅ FROZEN

**COSMIC_SIGNS_CHOSEN_RULE** — Ngũ hành **nạp âm của trụ năm sinh**.
Ví dụ Nhâm Thân → Kiếm Phong Kim → hành **Kim**.

**Phân biệt rõ với mục 9:** bản mệnh lấy từ **trụ năm**, còn Cục lấy từ **nạp âm
của cung Mệnh**. Hai đại lượng khác nhau, dùng cùng bảng nạp âm 60 hoa giáp nhưng
**đầu vào khác nhau**. Nhầm hai cái này là lỗi kinh điển.

**Cài đặt:** `nap_am_element(trụ_năm)`.

---

## 9. Tính Cục ✅ FROZEN

**COSMIC_SIGNS_CHOSEN_RULE** — Lấy **thiên can + địa chi của cung Mệnh**, tra nạp
âm, được ngũ hành, rồi ánh xạ:

| Ngũ hành cung Mệnh | Cục | Số |
|---|---|---|
| Thủy | Thủy Nhị Cục | 2 |
| Mộc | Mộc Tam Cục | 3 |
| Kim | Kim Tứ Cục | 4 |
| Thổ | Thổ Ngũ Cục | 5 |
| Hỏa | Hỏa Lục Cục | 6 |

Thiên can cung Mệnh có được nhờ ngũ hổ độn (mục 12).

---

## 10. Quan hệ Mệnh – Cục ✅ FROZEN (chỉ là dữ kiện diễn giải)

**COSMIC_SIGNS_CHOSEN_RULE** — So ngũ hành bản mệnh (mục 8) với ngũ hành Cục
(mục 9) theo vòng sinh–khắc, cho ra một trong năm mã:
`TUONG_HOA`, `CUC_SINH_MENH`, `MENH_SINH_CUC`, `CUC_KHAC_MENH`, `MENH_KHAC_CUC`.

Vòng tương sinh: Mộc→Hỏa→Thổ→Kim→Thủy→Mộc.
Vòng tương khắc: Mộc→Thổ→Thủy→Hỏa→Kim→Mộc.

> Đại lượng này **không ảnh hưởng tới việc an sao**. Nó chỉ là dữ kiện cho tầng
> luận giải sau này. Ghi ở đây để không ai dùng nhầm nó vào phép tính.

---

## 11. Thứ tự 12 cung 🟡 PENDING — *đã sửa lỗi 2026-09-11*

**COSMIC_SIGNS_CHOSEN_RULE** — Từ cung Mệnh đi **nghịch chiều kim đồng hồ**
(địa chi giảm dần) theo trình tự kinh điển:

| Bước nghịch | Cung | Bước nghịch | Cung |
|---|---|---|---|
| 0 | Mệnh | 6 | Thiên Di |
| 1 | Huynh Đệ | 7 | Nô Bộc |
| 2 | Phu Thê | 8 | Quan Lộc |
| 3 | Tử Tức | 9 | Điền Trạch |
| 4 | Tài Bạch | 10 | Phúc Đức |
| 5 | Tật Ách | 11 | Phụ Mẫu |

Tương đương: Phụ Mẫu nằm **một cung thuận** từ Mệnh. Engine lưu danh sách theo chiều
thuận (`Mệnh, Phụ Mẫu, Phúc Đức, …, Huynh Đệ`) nên công thức là:

```
branch_cung_thứ_i = (menh_branch + i) mod 12     # i theo PALACE_ORDER (chiều thuận)
```

> ⚠️ **Sự cố 2026-09-11.** Bản trước ghi và cài `(menh_branch − i)` với danh sách chiều
> thuận — tức đặt ngược, sai 10/12 tên cung và sai "Thân cư" trên mọi lá số. Nhãn ✅ FROZEN
> khi đó chỉ dựa trên test sinh ra từ chính engine. Phát hiện khi đối chiếu chéo một lá
> số bên thứ ba; sửa ở engine 0.2.0. Hạ xuống 🟡 cho tới khi người thẩm định xác nhận.

**Quan trọng:** thứ tự này **cố định, không đảo theo giới tính**. Chỉ chiều **đại
vận** (mục 20) mới đổi theo âm dương nam nữ. Đây là chỗ rất dễ nhầm.

---

## 12. Gán thiên can cho cung 🟡 PENDING — *đã sửa lỗi 2026-09-11*

**COSMIC_SIGNS_CHOSEN_RULE** — **Ngũ hổ độn**: thiên can của **cung Dần** do
thiên can năm sinh quyết định, các cung khác suy ra theo địa chi.

| Can năm | Can cung Dần |
|---|---|
| Giáp, Kỷ | Bính |
| Ất, Canh | Mậu |
| Bính, Tân | Canh |
| Đinh, Nhâm | Nhâm |
| Mậu, Quý | Giáp |

```
can_cung_Dần = (can_năm × 2 + 2) mod 10
can_cung(chi) = (can_cung_Dần + ((chi − 2) mod 12)) mod 10
```

Can đi **tới** từ Dần suốt năm âm lịch: Tý là tháng 11 (Dần + 10), Sửu là tháng Chạp
(Dần + 11). Ví dụ năm Nhâm: Nhâm Dần, Quý Mão, … Tân Hợi, **Nhâm Tý, Quý Sửu**.

> ⚠️ **Sự cố 2026-09-11.** Bản trước thiếu `mod 12` bên trong, nên Tý và Sửu bị tính
> lùi (Dần − 2, Dần − 1) — lệch 2 bậc can. Vì Cục lấy từ nạp âm cung Mệnh, **mọi lá số có
> Mệnh ở Tý hoặc Sửu (~17%) bị sai Cục, kéo theo sai Tử Vi và cả 14 chính tinh.** Test cũ
> chỉ kiểm can cung Dần. Sửa ở engine 0.2.0; test mới kiểm đủ 12 cung theo định nghĩa.

---

## 13. An Tử Vi 🟡 PENDING

**COSMIC_SIGNS_CHOSEN_RULE** — Thuật toán cục số kinh điển:

1. Tìm bội số nhỏ nhất của **cục số** lớn hơn hoặc bằng **ngày sinh âm lịch**.
   Gọi `n` là thương, `padding` = bội số đó − ngày âm.
2. Khởi từ **cung Dần**, đếm thuận `n − 1` cung.
3. Nếu `padding` **chẵn** → đi thuận thêm `padding` cung.
   Nếu `padding` **lẻ** → đi nghịch `padding` cung.

**Đã đối chiếu 5 mốc kinh điển mùng 1** (ca `TV-A1`…`TV-A5`), **tất cả đều khớp**:

| Cục | Tử Vi mùng 1 | Engine |
|---|---|---|
| Thủy nhị (2) | Sửu | Sửu ✓ |
| Mộc tam (3) | Thìn | Thìn ✓ |
| Kim tứ (4) | Hợi | Hợi ✓ |
| Thổ ngũ (5) | Ngọ | Ngọ ✓ |
| Hỏa lục (6) | Dậu | Dậu ✓ |

Bất biến phụ cũng khớp: **ngày âm = đúng cục số → Tử Vi ở Dần**.

> Vẫn để 🟡 vì mới kiểm 5 ngày trên tổng 30 ngày × 5 cục = 150 ô. Cần đối chiếu
> **toàn bộ bảng 150 ô** với nguồn đã chốt. Bảng engine sinh ra đã có sẵn, chỉ
> cần người thẩm định soát.

---

## 14. An 14 chính tinh 🟡 PENDING

**COSMIC_SIGNS_CHOSEN_RULE** — Hai chòm, suy từ vị trí Tử Vi.

**Chòm Tử Vi** — đi **nghịch** từ cung Tử Vi:

| Sao | Độ lệch |
|---|---|
| Tử Vi | 0 |
| Thiên Cơ | −1 |
| Thái Dương | −3 |
| Vũ Khúc | −4 |
| Thiên Đồng | −5 |
| Liêm Trinh | −8 |

**Chòm Thiên Phủ** — Thiên Phủ đối xứng với Tử Vi qua **trục Dần–Thân**:

```
thien_phu = (4 − tu_vi) mod 12
```

rồi đi **thuận** từ cung Thiên Phủ:

| Sao | Độ lệch |
|---|---|
| Thiên Phủ | 0 |
| Thái Âm | +1 |
| Tham Lang | +2 |
| Cự Môn | +3 |
| Thiên Tướng | +4 |
| Thiên Lương | +5 |
| Thất Sát | +6 |
| Phá Quân | +10 |

**Bất biến đã kiểm:** Tử Vi và Thiên Phủ **trùng cung khi và chỉ khi** cùng ở Dần
hoặc cùng ở Thân. Ca `TV-C1`…`TV-C4` phủ cả hai trường hợp.

> 🟡 vì chưa có ca nào được người có chuyên môn ký duyệt. Toàn bộ 14 sao hiện
> mang cờ `provisional: true` và engine chỉ chạy ở stage `PREVIEW`.

---

## 15. Tứ Hóa 🟡 PENDING — **đã cài, Q7 vẫn mở**

> **Thay đổi trạng thái, 2026-09-14.** Mục này từng ghi 🔴 *"không được cài cho tới
> khi chốt nguồn"*, với ghi chú *"người viết code không đủ thẩm quyền chọn"* cho hàng
> Canh. **Chủ dự án đã yêu cầu cài ở mức `PROVISIONAL`** và chọn một phương án. Bảng
> dưới đây nay là **luật đang chạy**, không còn là đề xuất.
>
> Chọn một phương án **không phải là trả lời được Q7**. Câu hỏi vẫn mở, `blocked_by`
> vẫn chứa `Q7`, và không hàng nào được `VERIFIED`.

Đây vẫn là mục **phụ thuộc trường phái nặng nhất** trong toàn bộ danh sách.

Cài đặt: `stars/four_transformations.py` · Policy `NAM_PHAI_TABLE_V1` ·
Hồ sơ `COSMIC_SIGNS_NAM_PHAI_V1`.

**Tứ Hóa không phải bốn ngôi sao.** Nó là bốn *trạng thái* gắn vào sao đã an, nên
tổng số sao trên lá số **không đổi theo năm sinh** — 27 sao dù can năm là gì.

Bảng đang chạy:

| Can năm | Hóa Lộc | Hóa Quyền | Hóa Khoa | Hóa Kỵ |
|---|---|---|---|---|
| Giáp | Liêm Trinh | Phá Quân | Vũ Khúc | Thái Dương |
| Ất | Thiên Cơ | Thiên Lương | Tử Vi | Thái Âm |
| Bính | Thiên Đồng | Thiên Cơ | Văn Xương | Liêm Trinh |
| Đinh | Thái Âm | Thiên Đồng | Thiên Cơ | Cự Môn |
| **Mậu** | Tham Lang | Thái Âm | **Hữu Bật ⚠️** | Thiên Cơ |
| Kỷ | Vũ Khúc | Tham Lang | Thiên Lương | Văn Khúc |
| **Canh** | Thái Dương | Vũ Khúc | **Thái Âm ⚠️** | **Thiên Đồng ⚠️** |
| Tân | Cự Môn | Thái Dương | Văn Khúc | Văn Xương |
| **Nhâm** | Thiên Lương | Tử Vi | **Tả Phù ⚠️** | Vũ Khúc |
| Quý | Phá Quân | Cự Môn | Thái Âm | Tham Lang |

### Q7 — Hàng Canh theo phương án nào? 🔴

Đây là điểm bất đồng nổi tiếng nhất của Tứ Hóa. Các biến thể **được ghi nhận** gồm:

- Canh: Dương Lộc, Vũ Quyền, **Thái Âm** Khoa, **Thiên Đồng** Kỵ
- Canh: Dương Lộc, Vũ Quyền, **Thiên Đồng** Khoa, **Thái Âm** Kỵ
- Canh: Dương Lộc, Vũ Quyền, **Thiên Phủ** Khoa, Thiên Đồng Kỵ

**ĐANG CHỌN: phương án 1** — Dương Lộc, Vũ Quyền, **Thái Âm Khoa, Thiên Đồng Kỵ**
(đa số bản Việt). Hằng số `SELECTED_CANH_VARIANT` trong
`stars/four_transformations.py`; cả ba phương án nằm cạnh nhau trong `CANH_VARIANTS`,
nên đổi lại là sửa một hằng số chứ không phải sửa bảng.

> **Phương án 1 và 2 đổi chỗ Khoa với Kỵ.** Chọn nhầm không làm lá số sai một chi
> tiết — nó **lật một cát tinh thành hung tinh** trên mọi lá số sinh năm Canh. Đây là
> lý do Q7 phải ở lại `blocked_by` cho tới khi người thẩm định (Q3) quyết theo nguồn
> đã chốt (Q2).

### Hàng Mậu và Nhâm 🟡

| Hàng | Đang chọn | Cách đọc đối lập |
| --- | --- | --- |
| Mậu — Hóa Khoa | **Hữu Bật** | Thái Dương |
| Nhâm — Hóa Khoa | **Tả Phù** | Thiên Phủ |

### Sao đích

Bảng trỏ tới **15 sao**, tất cả đều đã được engine an: 12 chính tinh cộng Văn Xương,
Văn Khúc, Tả Phù, Hữu Bật. **Không ô nào trong 40 ô bị treo.**

Nếu một ngày bảng trỏ tới sao chưa an, engine **không im lặng bỏ qua**: nó ghi
`Thiếu sao đích của Tứ Hóa: <tên>` ra log, ghi một bước trace *"CHƯA GIẢI ĐƯỢC"*, và
lá số vẫn dùng được.

### Q8 — Hàng Mậu và Nhâm 🔴

Vị trí **Hóa Khoa** của hai hàng này cũng khác nhau giữa các tài liệu (Hữu Bật /
Thái Âm cho Mậu; Tả Phù / Thiên Phủ cho Nhâm). Cần xác nhận.

### Q9 — Tứ Hóa còn dùng ở đâu nữa? 🔴

Ngoài tứ hóa theo **can năm sinh**, nhiều trường phái còn dùng tứ hóa theo **can
cung đại vận** và **can cung lưu niên** (phi tinh tứ hóa). Cần chốt Cosmic Signs
có làm hay không — ảnh hưởng lớn tới thiết kế dữ liệu.

> ⚠️ Bảng trên có nhắc **Văn Xương, Văn Khúc, Tả Phù, Hữu Bật** — đều là phụ tinh
> **chưa được cài**. Không thể cài Tứ Hóa trước khi cài xong nhóm phụ tinh này.

---

## 16. Lộc Tồn 🟡 PENDING

**Chưa cài đặt.** Bảng đề xuất (ổn định giữa các trường phái hơn hẳn Tứ Hóa):

| Can năm | Lộc Tồn |
|---|---|
| Giáp | Dần |
| Ất | Mão |
| Bính | Tỵ |
| Đinh | Ngọ |
| Mậu | Tỵ |
| Kỷ | Ngọ |
| Canh | Thân |
| Tân | Dậu |
| Nhâm | Hợi |
| Quý | Tý |

Bất biến kiểm được: Lộc Tồn **không bao giờ ở Thìn, Tuất, Sửu, Mùi** (tứ mộ).

**Kình Dương / Đà La** đi kèm: Kình Dương cung liền **trước** Lộc Tồn theo chiều
thuận, Đà La cung liền **sau** theo chiều nghịch.

> 🟡 — cần xác nhận theo nguồn đã chốt trước khi cài.

---

## 17. Tuần (Tuần Trung Không Vong) 🟡 PENDING

**COSMIC_SIGNS_CHOSEN_RULE** — Xác định theo **trụ năm sinh**. Mỗi tuần giáp gồm
10 trụ, phủ 10 địa chi; **hai địa chi còn lại** là Tuần không.

```
vị_trí = index của trụ năm trong vòng 60
chi_đầu_tuần = (chi_năm − vị_trí mod 10) mod 12
tuần_không = (chi_đầu_tuần + 10, chi_đầu_tuần + 11)
```

Ví dụ kiểm được: năm Nhâm Thân 1992 → Tuần tại **Tuất, Hợi**.

**Cài đặt:** `_tuan_branches`. Đã có test.

> 🟡 vì chưa đối chiếu nguồn chuẩn, dù quy tắc này ổn định.

---

## 18. Triệt (Triệt Lộ Không Vong) 🟡 PENDING

**COSMIC_SIGNS_CHOSEN_RULE** — Tra theo **thiên can năm sinh**, phủ **hai địa chi
liền nhau**:

| Can năm | Triệt |
|---|---|
| Giáp, Kỷ | Thân – Dậu |
| Ất, Canh | Ngọ – Mùi |
| Bính, Tân | Thìn – Tỵ |
| Đinh, Nhâm | Dần – Mão |
| Mậu, Quý | Tý – Sửu |

**ALTERNATIVE_RULE** 🔴 **Q10** — Một số tài liệu cho rằng Triệt **không phủ đều
hai cung**: cung trước "bị triệt nặng", cung sau nhẹ hơn (hoặc ngược lại). Engine
hiện coi **hai cung như nhau** (`has_triet: bool`).

> Nếu nguồn đã chốt phân biệt mức độ, kiểu dữ liệu phải đổi từ `bool` sang thang
> độ. Cần xác nhận **trước khi** tầng luận giải đọc trường này.

---

## 19. Bảng Miếu / Vượng / Đắc / Bình / Hãm 🔴 OPEN — **tuyệt đối không bịa**

**Cơ chế đã cài. Bảng vẫn RỖNG. Hai việc khác nhau.**

> **Cập nhật 2026-09-14.** Toàn bộ đường ống đã dựng xong: tra cứu `star_id + địa chi`,
> gắn `star.strength`, hiển thị dạng `THÁI ÂM (M)`, chú giải M/V/Đ/B/H. **Nhưng
> 168 ô vẫn trống**, nên mọi độ sáng là `null` và lá số render tên sao trơn.
>
> Đây là trạng thái đúng. Điều kiện tiên quyết — *một bảng Nam phái đã được chọn* —
> chưa thỏa, và nguyên tắc "không có giá trị đáng tin thì để `null`, không bịa" được
> áp dụng đúng như nó được viết ra.

Bảng này gồm **14 sao × 12 địa chi = 168 ô**. Nó **khác nhau đáng kể** giữa các
trường phái, và không có cách nào suy ra bằng công thức — phải chép từ nguồn.

> **Đây là mục dễ bịa nhất và hại nhất nếu bịa.** Một bảng miếu vượng sai trông
> vẫn "hợp lý" với người không rành, nhưng người có nền Tử Vi (persona P3 trong
> `business.md`) sẽ phát hiện ngay và mất hết uy tín.
>
> Người viết code **không cung cấp bảng đề xuất** cho mục này. Phải do người thẩm
> định (Q3) chép từ nguồn đã chốt (Q2).

**Kiểu dữ liệu đã sẵn sàng:** `StarStrength = MIEU | VUONG | DAC | BINH | HAM`,
trường `Star.strength` đang luôn `null`.

### Cách điền bảng

Bảng nằm ở **file dữ liệu riêng**, không nằm trong code, vì người điền nó là người
thẩm định chứ không phải người viết code:

```
packages/astrology-engine/src/cosmic_astrology/stars/data/nam_phai_star_strength_v1.json
```

1. Điền `source_title`, `source_page`, `verified_by`.
2. Thêm từng sao vào `entries`. **Một sao đã vào bảng thì phải đủ 12 địa chi.**
3. `make astrology-star-strength-report` để xem còn thiếu ô nào.
4. Khi đủ, đổi `implemented=True` ở binding `star_strength` trong `conventions/nam_phai.py`.

**Điền đủ KHÔNG tự động thành `VERIFIED`.** Nâng nhãn là việc của quy trình thẩm định.

### Bất biến đã cưỡng chế trong code

Engine **từ chối nạp** bảng sai thay vì lặng lẽ bỏ qua — một ô gõ sai chính tả sẽ
biến thành "chưa biết" mà không ai phát hiện:

| Lỗi | Engine làm gì |
| --- | --- |
| Sao có 11/12 địa chi | **Từ chối nạp**, nêu tên địa chi còn thiếu |
| Địa chi sai chính tả (`Tuat`) | **Từ chối nạp** |
| Độ sáng không hợp lệ (`MIEUU`, `mieu`) | **Từ chối nạp**, liệt kê giá trị hợp lệ |

> **Ô thiếu nghĩa là "chưa biết", KHÔNG phải "bình hòa".** Hai thứ đó khác nhau và
> không được lẫn — đó là lý do bảng điền nửa vời bị từ chối thay vì được chấp nhận.

---

## 20. Đại vận: chiều và tuổi khởi 🟡/🔴

### Chiều đi 🟡 PENDING (đã cài phần xác định)

**COSMIC_SIGNS_CHOSEN_RULE** —

| Loại | Chiều |
|---|---|
| Dương Nam | **Thuận** (chiều kim đồng hồ) |
| Âm Nữ | **Thuận** |
| Âm Nam | **Nghịch** |
| Dương Nữ | **Nghịch** |

Engine đã tính sẵn cờ `yin_yang.is_thuan_ly` = `(năm_dương == là_nam)`.

### Tuổi khởi vận 🟡 PENDING

**COSMIC_SIGNS_CHOSEN_RULE (đề xuất)** — Đại vận thứ nhất khởi tại **cung Mệnh**,
bắt đầu ở tuổi bằng **cục số**, mỗi vận 10 năm.
Ví dụ Kim tứ cục → vận 1 là 4–13 tuổi, vận 2 là 14–23 tuổi…

### Q11 — Tuổi ta hay tuổi tây? 🔴

Chưa chốt "tuổi" ở đây là **tuổi mụ (tuổi ta)** hay tuổi tròn. Lệch một tuổi là
lệch ranh giới mọi đại vận.

### Q12 — Tiểu vận và lưu niên 🔴

Chưa chốt quy tắc an tiểu vận, và cách xác định cung lưu niên theo địa chi năm xem.

---

## 23. Ngũ hành riêng của từng sao 🟡 PENDING

Dùng để **tô màu chữ** trong lá số, không tham gia một phép tính nào. Đây vẫn là dữ
liệu tử vi, nên chịu đúng kỷ luật như mọi mục khác: không có nguồn thì không có giá trị.

**COSMIC_SIGNS_CHOSEN_RULE:** ghi nhận ngũ hành + âm/dương cho **12/14 chính tinh**,
ở những chỗ các bản đọc trùng nhau. Hai sao còn lại để **trống**.

| Sao | Hành | Âm/Dương |
| --- | --- | --- |
| Tử Vi | Thổ | Âm |
| Thiên Cơ | Mộc | Âm |
| Thái Dương | Hỏa | Dương |
| Vũ Khúc | Kim | Âm |
| Thiên Đồng | Thủy | Dương |
| Liêm Trinh | Kim | Âm |
| Thiên Phủ | Thổ | Dương |
| Thái Âm | Thủy | Âm |
| **Tham Lang** | *(trống)* | *(trống)* |
| **Cự Môn** | *(trống)* | *(trống)* |
| Thiên Tướng | Thủy | Dương |
| Thiên Lương | Thổ | Dương |
| Thất Sát | Kim | Dương |
| Phá Quân | Thủy | Âm |

**ALTERNATIVE_RULE — đúng hai chỗ đang mâu thuẫn:**

- **Tham Lang**: sách cổ ghi *"âm thủy, hóa khí là mộc"* — **hai hành trong cùng một
  câu**. Không có đáp án đơn trị để tô một màu, nên để trống.
- **Cự Môn**: Thổ (đa số bản Hoa) / Thủy (một số bản Việt) / Kim (thiểu số).

Hai sao nhỏ hơn cũng có biến thể, đã ghi lại nhưng vẫn chọn giá trị đa số:
**Liêm Trinh** (một số bản Việt ghi Hỏa) và **Thiên Lương** (một số bản suy từ chữ 梁
là rường gỗ mà ghi Mộc).

**Lý do chọn:** để trống cả 14 sao thì lá số không còn thông tin ngũ hành nào, còn bịa
2 sao để đủ màu thì đặt một khẳng định không nguồn lên lá số của khách. Cách thứ ba —
ghi phần đồng thuận, để trống phần mâu thuẫn, và **nói rõ chỗ trống** — giữ được cả hai.

**Trạng thái:** `PROVISIONAL`, chặn bởi Q1/Q2/Q3 — giống hệt `major_stars`. Không sao
nào là `VERIFIED` khi `sources.json` còn chưa chốt nguồn chuẩn.

**Bất biến đã cài:** ngũ hành và âm/dương phải **cùng có hoặc cùng thiếu** (chúng đến
từ cùng một câu trong sách); để trống thì **buộc** phải liệt kê ≥ 2 cách đọc đang mâu
thuẫn — một ô trống lặng lẽ bị `StarMetadata` từ chối ngay lúc khởi tạo.

**Nơi cài:** `packages/astrology-engine/src/cosmic_astrology/stars/catalog.py` — catalog
sao tập trung. Luật an sao chỉ mang **id**; tên, hành, âm/dương, category đều tra ở đây.

**Mức kiểm định theo từng sao**, không phải một nhãn chung: sao có giá trị thì
`PROVISIONAL`, sao để trống thì `UNVERIFIED`. Cả 14 mục đều mang provenance ghi rõ
*chưa chọn ấn bản chuẩn*, nên `has_citation` = false trên toàn bộ catalog. Code chặn
việc nâng lên `VERIFIED` nếu provenance chưa có đủ trích dẫn **và** người ký duyệt —
sửa tay file này không nâng được nhãn.

**Độ phủ:** `make astrology-star-metadata-report`.

---

## 24. Vòng Tràng Sinh 🟡 PENDING

Mười hai chặng, đặt trên **địa chi** (không phải trên tên cung):

Tràng Sinh → Mộc Dục → Quan Đới → Lâm Quan → Đế Vượng → Suy → Bệnh → Tử → Mộ →
Tuyệt → Thai → Dưỡng.

### 24.1 Địa chi khởi 🟡

**COSMIC_SIGNS_CHOSEN_RULE** — `CUC_ELEMENT_THO_WITH_THUY`:

| Ngũ hành Cục | Tràng Sinh tại |
| --- | --- |
| Kim | Tỵ |
| Mộc | Hợi |
| Thủy | Thân |
| Hỏa | Dần |
| **Thổ** | **Thân** (theo Thủy) |

**ALTERNATIVE_RULE** — `CUC_ELEMENT_THO_WITH_HOA`: Thổ khởi ở **Dần** (theo Hỏa).

Bốn hành đầu đọc giống nhau ở mọi sách. **Thổ thì không.** Hai cách đọc lệch nhau
6 cung, tức đảo ngược nửa vòng, trên **mọi lá Thổ Ngũ Cục**. Đây không phải chi tiết
nhỏ, nên cả hai bảng đều nằm trong code (`cycles/trang_sinh.py`) để so được bằng mắt
chứ không phải một câu trong tài liệu.

**Lý do chọn:** đa số bản tiếng Việt xếp Thổ theo Thủy. Chưa có ấn bản nào được chốt
(Q1/Q2/Q3), nên đây là cách đọc đa số, **không** phải trích dẫn.

### 24.2 Chiều 🟡

**COSMIC_SIGNS_CHOSEN_RULE** — `YANG_MALE_YIN_FEMALE_FORWARD`: dương nam và âm nữ đi
**thuận**, âm nam và dương nữ đi **nghịch** — cùng luật với đại vận.

**ALTERNATIVE_RULE** — `CUC_POLARITY`: chiều lấy theo âm dương của **Cục**, không theo
người xem. Hai cách cho kết quả khác nhau trên **một nửa số lá số**.

---

## 25. Đại vận 🟡 PENDING

### 25.1 Chiều 🟡

`YANG_MALE_YIN_FEMALE_FORWARD` — dương nam / âm nữ thuận, âm nam / dương nữ nghịch.

> **Chỉ đường đi của đại vận đổi chiều. Tên 12 cung thì KHÔNG.**
>
> Đây đúng là chỗ đã sinh ra lỗi lật gương tên cung ở engine 0.1.0 (mục 11). Vì vậy
> `cycles/major_cycle.py` làm việc trên **chỉ số địa chi**, và mọi cung vẫn giữ nguyên
> tên do `PALACE_ORDER` quyết định, bất kể đại vận đi chiều nào.

### 25.2 Tuổi khởi và dãy đại vận 🟡

`CUC_NUMBER` — đại vận 1 khởi tại **cung Mệnh**, ở tuổi **bằng số Cục**; mỗi cung
**10 năm**; đi tiếp theo chiều đã chọn.

Ví dụ Mộc Tam Cục, Mệnh tại Tuất, âm nữ (thuận):
Tuất 3–12 → Hợi 13–22 → Tý 23–32 → … → Dậu 113–122.

**Con số thì các sách thống nhất.** Cái chưa chốt là **"tuổi" nghĩa là gì** — tuổi ta
hay tuổi tròn, tức câu hỏi mở **Q11**. Điều đó **không đổi một con số nào ở trên**,
nhưng nó chặn việc quy tuổi ra năm dương lịch — nên **lưu niên vẫn chưa mở**.

### 25.3 Trạng thái

Cả bốn quy tắc (`trang_sinh_start`, `trang_sinh_direction`, `major_cycle_direction`,
`major_cycle_start_age`) đều `PROVISIONAL`. Fixture kỳ vọng ở
`packages/astrology-engine/tests/fixtures/cycles.json`, **suy từ bảng quy tắc trên**,
không chép từ đầu ra engine. Không được tự nâng lên `VERIFIED`.

---

## 26. Phụ tinh nhóm 1 🟡 PENDING — **Nam phái**

Hồ sơ `COSMIC_SIGNS_NAM_PHAI_V1` là nơi duy nhất chọn các luật dưới đây. Hồ sơ
`COSMIC_SIGNS_STANDARD_V1` **không** chọn: nó không nêu trường phái, nên không có cơ
sở để an nhóm này, và lá số lập theo nó đơn giản là không có phụ tinh.

> **Đã nêu trường phái, chưa chốt ấn bản.** Q1 coi như đã trả lời là *Nam phái*, nhưng
> Q2 (ấn bản cụ thể) và Q3 (người thẩm định) thì chưa. Vì vậy cả 8 luật ở mức
> `PROVISIONAL`, và mọi giá trị dưới đây là **cách đọc thông dụng**, không phải trích
> dẫn. Cài đặt nằm gọn trong `stars/placement.py` để đổi một luật chỉ phải sửa một hàm.

| Luật | Sao | Cách an |
| --- | --- | --- |
| `van_xuong_van_khuc` | Văn Xương, Văn Khúc | Xương khởi **Tuất** đếm nghịch theo giờ sinh; Khúc khởi **Thìn** đếm thuận |
| `ta_phu_huu_bat` | Tả Phù, Hữu Bật | Tả khởi **Thìn** đếm thuận, Hữu khởi **Tuất** đếm nghịch, từ tháng Giêng âm |
| `thien_khoi_thien_viet` | Thiên Khôi, Thiên Việt | Bảng theo can năm (xem dưới) |
| `loc_ton` | Lộc Tồn | Cung lâm quan của can năm |
| `kinh_duong_da_la` | Kình Dương, Đà La | "Tiền Kình hậu Đà" — kẹp hai bên Lộc Tồn |
| `dao_hoa` | Đào Hoa | Tam hợp chi năm |
| `hong_loan_thien_hy` | Hồng Loan, Thiên Hỷ | Hồng Loan khởi **Mão** năm Tý đếm nghịch; Thiên Hỷ đối cung |
| `thien_ma` | Thiên Mã | Tam hợp chi năm (dịch mã) |

### Bảng theo thiên can năm sinh

Đọc từ câu quyết *"Giáp Mậu Canh ngưu dương · Ất Kỷ thử hầu hương · Bính Đinh trư kê
vị · Nhâm Quý thỏ xà tàng · Lục Tân phùng mã hổ"*.

| Can | Lộc Tồn | Kình | Đà | Khôi | Việt |
| --- | --- | --- | --- | --- | --- |
| Giáp | Dần | Mão | Sửu | Sửu | Mùi |
| Ất | Mão | Thìn | Dần | Tý | Thân |
| Bính | Tỵ | Ngọ | Thìn | Hợi | Dậu |
| Đinh | Ngọ | Mùi | Tỵ | Hợi | Dậu |
| Mậu | Tỵ | Ngọ | Thìn | Sửu | Mùi |
| Kỷ | Ngọ | Mùi | Tỵ | Tý | Thân |
| Canh | Thân | Dậu | Mùi | **Sửu** | **Mùi** |
| Tân | Dậu | Tuất | Thân | Ngọ | Dần |
| Nhâm | Hợi | Tý | Tuất | Mão | Tỵ |
| Quý | Tý | Sửu | Hợi | Mão | Tỵ |

**ALTERNATIVE_RULE:** can **Canh** là chỗ các trường phái hay khác nhau — một số bản
tách Canh ra khỏi nhóm Giáp/Mậu. Bản này xếp Canh cùng nhóm theo câu quyết.

### Tam hợp chi năm

| Chi năm | Đào Hoa | Thiên Mã |
| --- | --- | --- |
| Thân Tý Thìn | Dậu | Dần |
| Dần Ngọ Tuất | Mão | Thân |
| Tỵ Dậu Sửu | Ngọ | Hợi |
| Hợi Mão Mùi | Tý | Tỵ |

### Bất biến kiểm được (không cần nguồn ngoài)

Bốn hệ quả sau suy thẳng từ các luật trên, nên chúng bắt được lỗi bảng mà không cần
chờ ai ký duyệt:

1. **Văn Xương và Văn Khúc đồng cung tại Mùi (giờ Mão) và Sửu (giờ Dậu).** Hai sao
   này **không** đối cung nhau — chúng đối xứng qua trục Thìn–Tuất.
2. **Đào Hoa luôn ở tứ chính** (Tý Ngọ Mão Dậu).
3. **Thiên Mã luôn ở tứ sinh** (Dần Thân Tỵ Hợi).
4. **Kình Dương và Đà La luôn kẹp Lộc Tồn**, và Lộc Tồn không bao giờ vào tứ mộ.

### Ngũ hành

11/13 sao có ngũ hành. Hai sao để trống vì các sách chia hai hướng rõ rệt:

- **Hữu Bật** — Thổ (đi theo Tả Phù, phần lớn bản Việt) / Thủy (`右弼 屬水`, phần lớn
  bản Hoa). Tả Phù thì thống nhất là Thổ; chỉ Hữu Bật là tranh chấp.
- **Đào Hoa** — Mộc (một số bản Việt) / Thủy (Hàm Trì 咸池 thuộc thủy, phần lớn bản Hoa).

---

## 27. Phụ tinh nhóm 2 🟡 PENDING — **Nam phái**

24 sao, 12 luật, tất cả trong `COSMIC_SIGNS_NAM_PHAI_V1` ở mức `PROVISIONAL`.
Cài đặt: `stars/placement_group2.py`.

| Luật | Sao | Cách an | Phụ thuộc |
| --- | --- | --- | --- |
| `long_tri_phuong_cac` | Long Trì, Phượng Các | Long Trì khởi **Thìn** thuận; Phượng Các khởi **Tuất** nghịch | chi năm |
| `thien_duc_nguyet_duc` | Thiên Đức, Nguyệt Đức | Khởi **Dậu** và **Tỵ**, cùng đếm thuận | chi năm |
| `hoa_cai` | Hoa Cái | Cung mộ của tam hợp chi năm | chi năm |
| `thai_tue_cycle` | Thiếu Dương, Thiếu Âm, Long Đức, Phúc Đức | Vòng Thái Tuế khởi tại chi năm, đi thuận | chi năm |
| `tam_thai_bat_toa` | Tam Thai, Bát Tọa | Từ **Tả Phù** thuận / **Hữu Bật** nghịch tới ngày âm | Tả Phù, Hữu Bật, ngày âm |
| `an_quang_thien_quy` | Ân Quang, Thiên Quý | Từ **Văn Xương** / **Văn Khúc** thuận tới ngày âm, rồi **lùi 1 cung** | Văn Xương, Văn Khúc, ngày âm |
| `thien_tai_thien_tho` | Thiên Tài, Thiên Thọ | Từ **cung Mệnh** / **cung Thân**, đếm thuận theo chi năm | Mệnh, Thân, chi năm |

Sáu sao cuối phụ thuộc vị trí đã an, nên **nhóm 2 bắt buộc chạy sau nhóm 1**. Sao neo
được **đọc lại từ lá số**, không tính lại — chỉ có một chỗ quyết định Tả Phù nằm đâu.

### Bất biến kiểm được

1. **Long Trì và Phượng Các đồng cung tại Mùi (năm Mão) và Sửu (năm Dậu)** — cùng
   dạng đối xứng như Xương/Khúc.
2. **Hoa Cái luôn ở tứ mộ** (Thìn Tuất Sửu Mùi).
3. **Thiên Đức và Nguyệt Đức luôn cách nhau 4 cung.**
4. Offset vòng Thái Tuế: Thiếu Dương +1, Thiếu Âm +3, Long Đức +7, Phúc Đức +9.

### Vòng Thái Tuế — chỉ an 4/12 sao

Vòng có 12 sao. Nhóm này cố ý **chỉ an bốn**; Tang Môn, Bạch Hổ, Quan Phù, Điếu Khách
và các sao còn lại thuộc nhóm sau. `THAI_TUE_CYCLE` trong code liệt kê đủ 12 để offset
đọc được, nhưng builder chỉ lấy bốn.

### Ngũ hành: **0/24**

Toàn bộ nhóm 2 để trống, đánh dấu `NOT_RECORDED` — **khác với `DISPUTED`**:

| Trạng thái | Nghĩa | Việc cần làm |
| --- | --- | --- |
| `DISPUTED` | Các sách ghi khác nhau | Người thẩm định phải **chọn** |
| `NOT_RECORDED` | Chưa tra được từ nguồn nào | Người thẩm định phải **tìm** |

Gộp hai trạng thái này lại là đánh mất thông tin về việc cần làm tiếp, nên code cưỡng
chế: để trống ngũ hành mà không nói rõ lý do thì `StarDefinition` từ chối khởi tạo.

### Phần bổ sung (S4.1) — thêm 9 sao, 5 luật

| Luật | Sao | Cách an | Phụ thuộc |
| --- | --- | --- | --- |
| `thien_quan_thien_phuc` | Thiên Quan, Thiên Phúc | Bảng Quý Nhân theo can năm | can năm |
| `thien_giai_dia_giai` | Thiên Giải, Địa Giải | Khởi **Thân** và **Mùi**, đếm thuận theo tháng âm | tháng âm |
| `thai_phu_phong_cao` | Thai Phụ, Phong Cáo | Khởi **Ngọ** và **Dần**, đếm thuận theo giờ sinh | giờ sinh |
| `quoc_an_duong_phu` | Quốc Ấn, Đường Phù | Cách **Lộc Tồn** 8 và 5 cung, chiều thuận | Lộc Tồn |
| `bac_si_cycle` | Hỷ Thần | Vòng Bác Sĩ từ **Lộc Tồn**, dương nam/âm nữ thuận | Lộc Tồn, âm dương nam nữ |

**Ba bằng chứng nội tại** khiến các bảng này kiểm được mà không cần nguồn ngoài —
hai cách phát biểu độc lập trùng khớp thì khó là trùng hợp:

1. Bảng **Quốc Ấn** theo can năm khớp đúng `Lộc Tồn + 8` ở **cả 10 can**.
2. Bảng **Đường Phù** khớp đúng `Lộc Tồn + 5` ở **cả 10 can**.
3. **Thai Phụ / Phong Cáo**: phát biểu "khởi Ngọ / khởi Dần theo giờ" và phát biểu
   "Văn Khúc ± 2 cung" cho **cùng kết quả ở cả 12 giờ**. Đây là *một* luật với hai
   cách nói, không phải hai luật mâu thuẫn — điều mà lần rà trước đã hiểu nhầm.

Bất biến khác: Thiên Giải luôn đứng liền sau Địa Giải; Thai Phụ và Phong Cáo luôn
cách nhau 4 cung.

**Vòng Bác Sĩ chỉ an 1/12 sao.** Đại Hao, Tiểu Hao, Thanh Long… thuộc nhóm sau.

### Sao trong danh sách nhưng **VẪN CHƯA cài** — 3 sao

| Sao | Lý do | Cần gì để mở |
| --- | --- | --- |
| **Giải Thần** | 🔴 **DISPUTED** — có hai luật ứng viên (theo tam hợp chi năm / theo tháng âm) và dự án chưa có quyết định nào để chọn | Người thẩm định chọn một |
| **Thiên Trù** | Bảng theo can năm không nêu lại được với độ tin cậy đủ, và **không có cấu trúc nội tại nào để đối chiếu** (khác Quốc Ấn / Đường Phù) | Bảng từ ấn bản |
| **Thiên Y** | Luật theo tháng âm không nêu lại được chắc chắn | Luật từ ấn bản |

Hai lý do này **khác nhau** và đừng gộp: Giải Thần là *biết hai đường, không được
chọn bừa*; Thiên Trù và Thiên Y là *không nêu lại được đường nào*.

---

## 28. Sát tinh / bại tinh nhóm 1 🟡 PENDING — **Nam phái**

16 sao. Nhưng **chỉ 6 luật mới**: sáu sao đã thuộc chu kỳ engine đang đi, nên được
**tái dùng** thay vì viết lại — hai nguồn sự thật cho cùng một chu kỳ là lỗi chờ sẵn.

### Tái dùng chu kỳ có sẵn (6 sao, 0 luật mới)

| Sao | Chu kỳ | Offset |
| --- | --- | --- |
| Tang Môn, Quan Phù, Bạch Hổ, Điếu Khách | vòng Thái Tuế (§27) | +2, +4, +8, +10 |
| Tiểu Hao, Đại Hao | vòng Bác Sĩ (§27) | +3, +9 |

### Luật mới (6 luật, 10 sao)

| Luật | Sao | Cách an | Phụ thuộc |
| --- | --- | --- | --- |
| `dia_khong_dia_kiep` | Địa Không, Địa Kiếp | Cùng khởi **Hợi** giờ Tý; Kiếp thuận, Không nghịch | giờ sinh |
| `hoa_tinh_linh_tinh` | Hỏa Tinh, Linh Tinh | Địa chi khởi theo tam hợp chi năm, đếm theo giờ sinh | chi năm + giờ + chiều |
| `kiep_sat` | Kiếp Sát | Cung tuyệt của tam hợp chi năm | chi năm |
| `co_than_qua_tu` | Cô Thần, Quả Tú | Theo **mùa** của chi năm | chi năm |
| `thien_khong` | Thiên Không | Cung liền sau Thái Tuế | chi năm |
| `thien_khoc_thien_hu` | Thiên Khốc, Thiên Hư | Cùng khởi **Ngọ** năm Tý; Khốc nghịch, Hư thuận | chi năm |

### Sáu bất biến kiểm được

1. **Địa Không và Địa Kiếp đồng cung tại Hợi (giờ Tý) và Tỵ (giờ Ngọ).**
2. **Thiên Khốc và Thiên Hư đồng cung tại Ngọ (năm Tý) và Tý (năm Ngọ).**
3. Kiếp Sát luôn ở **tứ sinh**.
4. Cô Thần luôn ở **tứ sinh**, Quả Tú luôn ở **tứ mộ**.
5. Cô Thần và Quả Tú luôn cách nhau **4 cung**.
6. **Thiên Không luôn đồng cung Thiếu Dương** — cả hai ở offset +1 của vòng Thái Tuế.
   Đây là kết quả đúng, không phải trùng lặp cần khử.

> **Địa Không ≠ Thiên Không.** Hai sao khác nhau, khác luật (giờ sinh vs chi năm),
> khác mã (`DIA_KHONG` vs `THIEN_KHONG`). Chúng chỉ chung một chữ.

### Chỗ các bản khác nhau

**Chiều đếm của Hỏa Tinh / Linh Tinh.** Bản này lấy dương nam / âm nữ đi thuận, cùng
luật chiều với đại vận. Một số bản cho cả hai sao **luôn đi thuận**. Ghi trong note của
`hoa_tinh_linh_tinh`.

### Ngũ hành: **2/16**

Chỉ **Hỏa Tinh** (dương hỏa) và **Linh Tinh** (âm hỏa) — hai sao mà chính tên đã nói ra
hành. 14 sao còn lại `NOT_RECORDED`.

> **Màu trên lá số là NGŨ HÀNH, không phải "tốt hay xấu".** Địa Không, Địa Kiếp, Bạch
> Hổ, Tang Môn — những sao đáng sợ nhất — đều vẽ **mực trung tính**, vì chưa tra được
> hành của chúng. Tô đỏ một sát tinh chỉ vì nó là sát tinh sẽ phá vỡ ý nghĩa của toàn
> bộ hệ màu. Ngược lại Hỏa Tinh đỏ vì nó **là** Hỏa, không phải vì nó hung.

---

## 29. Phụ tinh nhóm 3 🟡 PENDING — **Nam phái**

21 sao, nhưng **chỉ 5 luật mới**. Việc lớn nhất của mục này không phải thêm sao —
mà là **gộp hai chu kỳ về một nguồn tính**.

### Gộp chu kỳ: sửa một lỗi cấu trúc đang lớn dần

Trước mục này, **vòng Bác Sĩ được an từ hai chỗ khác nhau** trong builder (Hỷ Thần
ở nhóm 2, Đại/Tiểu Hao ở nhóm sát tinh), và **vòng Thái Tuế từ hai chỗ khác** nữa.
Mỗi lần một nhóm mới xin vài sao của chu kỳ, lại thêm một chỗ gọi.

Đó chính là cách một chu kỳ có hai cách tính rồi lặng lẽ lệch nhau. Nay mỗi chu kỳ
được đi **trọn một lần, ở một chỗ**, và mọi sao chỉ là một offset trong đó.

| Chu kỳ | Neo | Số sao |
| --- | --- | --- |
| Vòng Thái Tuế | chi năm | 12/12 |
| Vòng Bác Sĩ | **Lộc Tồn**, chiều theo âm dương nam nữ | 12/12 |

Việc gộp này làm lộ ra **Thái Tuế** và **Tuế Phá** chưa có trong catalog — engine
cảnh báo thay vì im lặng vẽ mã sao. Hai sao này không nằm trong danh sách yêu cầu
nhưng có trên mọi lá số, nên đã được bổ sung.

### Năm luật mới (8 sao)

| Luật | Sao | Cách an | Phụ thuộc |
| --- | --- | --- | --- |
| `pha_toai` | Phá Toái | Tứ chính → Tỵ, tứ sinh → Sửu, tứ mộ → Dậu | chi năm |
| `thien_hinh_thien_dieu` | Thiên Hình, Thiên Diêu | Khởi **Dậu** và **Sửu**, thuận theo tháng âm | tháng âm |
| `thien_la_dia_vong` | Thiên La, Địa Võng | **Cố định** tại Thìn và Tuất | — |
| `thien_thuong_thien_su` | Thiên Thương, Thiên Sứ | Tại **cung Nô Bộc** và **cung Tật Ách** | vị trí cung |
| `dau_quan` | Đẩu Quân | Từ Thái Tuế nghịch tới tháng, rồi thuận tới giờ | chi năm + tháng + giờ |

**Thiên La / Địa Võng là hằng số, không phải hàm** — để không ai tưởng chúng phụ
thuộc ngày sinh.

**Thiên Thương / Thiên Sứ gắn vào *cung*, nhưng engine vẫn trả về *địa chi***. Cung
nào nằm ở địa chi nào là việc engine đã biết; frontend tuyệt đối không được tự suy.

### Ba bất biến kiểm được

1. **Phá Toái luôn nằm trong tam hợp Tỵ–Dậu–Sửu** — cả ba nhánh của bảng.
2. **Thiên Hình và Thiên Diêu luôn cách nhau 8 cung.**
3. Thiên La luôn ở Thìn, Địa Võng luôn ở Tuất.

### Quan Phù ≠ Quan Phủ

Hai sao khác nhau, thuộc hai chu kỳ khác nhau:

| Sao | Chu kỳ | Mã |
| --- | --- | --- |
| **Quan Phù** 官符 | vòng Thái Tuế, +4 | `QUAN_PHU_TT` |
| **Quan Phủ** 官府 | vòng Bác Sĩ, +11 | `QUAN_PHU_BS` |

### Sao trong danh sách nhưng **CHƯA cài**

**Lưu Hà** — bảng theo can năm. Người viết code nêu lại được một bảng nhưng phát
hiện **một chỗ bất quy tắc** trong đó (cặp Canh/Tân phá vỡ quy luật của bốn cặp
trước), và **không có cấu trúc nội tại nào để đối chiếu** như Quốc Ấn hay Đường Phù.
Đó là dấu hiệu bảng có thể đã nhớ sai, nên không cài. Cần bảng từ ấn bản đã chốt.

### Ngũ hành: **0/21**

Toàn bộ `NOT_RECORDED`.

---

## 30. Lưu niên 🟡 PENDING — **Nam phái**

Dữ liệu của **một năm xem**, tách hoàn toàn khỏi lá số gốc.

> **Nguyên tắc kiến trúc:** lưu niên **không được nướng vào `chart_json` đã lưu**.
> Một lá số đã lưu không mang sẵn một năm xem nào; lưu niên tính theo yêu cầu qua
> `GET /charts/{id}/annual?year=…`. Nhờ vậy đổi năm xem **không có đường nào** chạm
> tới sao bản mệnh — không phải vì cẩn thận, mà vì kiến trúc không cho phép.

### Tái dùng bảng của lá số gốc

Phần lớn luật lưu **dùng đúng bảng bản mệnh**, chỉ thay can/chi năm sinh bằng can/chi
năm xem. Chép lại bảng là tạo nguồn sự thật thứ hai, nên `annual.py` gọi thẳng vào
`stars.placement` và `stars.placement_malefic`.

| Lưu tinh | Dùng lại bảng | Đầu vào |
| --- | --- | --- |
| L.Lộc Tồn, L.Kình Dương, L.Đà La | `place_loc_ton` + kẹp hai bên | can năm xem |
| L.Thiên Khôi, L.Thiên Việt | bảng Quý Nhân theo can | can năm xem |
| L.Thiên Mã, L.Đào Hoa, L.Hồng Loan, L.Thiên Hỷ | tam hợp chi năm | chi năm xem |
| L.Thiên Khốc, L.Thiên Hư | cặp đối xứng qua Ngọ | chi năm xem |
| L.Thái Tuế, L.Tang Môn, L.Quan Phù, L.Bạch Hổ, L.Điếu Khách | **vòng Thái Tuế** | chi năm xem |
| L.Hóa Lộc/Quyền/Khoa/Kỵ | bảng Tứ Hóa Nam phái | can năm xem |

### Luật thật sự mới: `luu_van_xuong_van_khuc`

Đây là chỗ duy nhất lưu niên **khác họ luật** với bản mệnh. Văn Xương / Văn Khúc bản
mệnh an theo **giờ sinh**; bản lưu an theo **thiên can năm xem**:

- **Lưu Văn Xương** = Lộc Tồn(can năm xem) **+ 3** cung
- **Lưu Văn Khúc** = đối xứng qua trục Sửu–Mùi, tức tổng hai vị trí luôn ≡ 2 (mod 12)

Hai quan hệ này đúng ở **cả 10 can**, nên bảng kiểm được mà không cần nguồn ngoài.

### 12 cung lưu niên

Cung Mệnh lưu rơi vào địa chi của **năm xem**, rồi dùng **đúng `PALACE_ORDER`** của lá
số gốc. Trình tự 12 cung là một, không có bản "lưu niên" riêng.

Footer mỗi cung: `ĐV.<số>` · `<Tràng Sinh>` · `LN.<cung lưu>`.

### Tuổi xem — Q11 vẫn mở

Engine đưa **cả hai** con số và **không chọn hộ**:

| Trường | Ví dụ (sinh 2001, xem 2026) |
| --- | --- |
| `age_tuoi_ta` | 26 |
| `age_completed` | 25 |
| `age_convention` | **`null`** — chưa chốt quy ước dùng cách nào (Q11) |

Giao diện hiển thị *"26 tuổi ta · 25 tuổi tròn"* thay vì chọn một cái rồi trình bày
như thể đó là câu trả lời.

### Tách bản mệnh và lưu niên

Lưu tinh là **instance riêng**, không sửa `Star` bản mệnh. Lưu hóa gắn vào sao bản
mệnh qua một trường **riêng** (`annualTransformations`), nên một ngôi sao có thể mang
**cả hóa bản mệnh lẫn hóa năm xem** cùng lúc — ví dụ `Văn Xương [Kỵ] [L.Khoa]`.

### Màu

Lưu tinh dùng **ngũ hành của sao gốc** (`base_star_id`), không khai báo lại. Là lưu
tinh **không làm đổi hành** của một ngôi sao. Trạng thái lưu niên thể hiện bằng tiền
tố `L.` và chữ nghiêng — **không** bằng một màu riêng.

---

## 21. Sổ mâu thuẫn giữa các nguồn

Khi phát hiện hai nguồn mâu thuẫn, **ghi vào đây** thay vì âm thầm chọn một bên.

| # | Mục | Mâu thuẫn | Trạng thái |
|---|---|---|---|
| 1 | §15 Tứ Hóa | Hàng **Canh**: Khoa/Kỵ có ít nhất 3 biến thể được ghi nhận | 🔴 chờ Q7 |
| 2 | §15 Tứ Hóa | Hàng **Mậu** và **Nhâm**: vị trí Hóa Khoa khác nhau giữa các tài liệu | 🔴 chờ Q8 |
| 3 | §3 Giờ Tý | Sinh 23:xx thuộc ngày nào — **code hiện tại tự mâu thuẫn** | 🔴 chờ Q6 |
| 4 | §18 Triệt | Hai cung bị triệt đều nhau hay khác mức | 🔴 chờ Q10 |
| 5 | §5 An Mệnh | Cách xử lý tháng nhuận khi đếm tháng | 🔴 chờ xác nhận |
| 6 | §2 Múi giờ | Giờ dân sự vs giờ mặt trời thật | 🔴 chờ Q4 |
| 7 | §11 Thứ tự cung | Engine đặt tên cung ngược chiều so với trình tự kinh điển và lá số đối chiếu chéo | ✅ lỗi engine, đã sửa 0.2.0; có fixture vàng `PALACE_ORDER_MENH_TUAT` + test đủ 12 vị trí Mệnh; lá số lưu bằng 0.1.0 bị gắn cờ cần lập lại |
| 8 | §12 Can cung | Engine tính can Tý/Sửu lùi thay vì tới; lá số đối chiếu chéo cho Canh Tý / Tân Sửu | ✅ lỗi engine, đã sửa 0.2.0 |
| 9 | §23 Ngũ hành sao | Tham Lang ghi "âm thủy hóa khí mộc"; Cự Môn ghi Thổ/Thủy/Kim tùy trường phái | 🟡 để trống 2 sao, vẽ mực trung tính; 12/14 sao có giá trị PROVISIONAL |
| 10 | §24 Tràng Sinh | Thổ cục khởi ở Thân (theo Thủy) hay Dần (theo Hỏa); chiều theo âm dương nam nữ hay theo âm dương Cục | 🟡 chọn cách đọc đa số, ghi cả hai vào policy |
| 11 | §26 Phụ tinh 1 | Hữu Bật ghi Thổ hay Thủy; Đào Hoa ghi Mộc hay Thủy; can Canh trong bảng Khôi/Việt | 🟡 để trống 2 sao; Canh xếp cùng nhóm Giáp/Mậu, ghi rõ cách đọc đối lập |
| 12 | §15 Tứ Hóa | Hàng Canh có 3 biến thể, hai trong số đó đảo Khoa↔Kỵ; hàng Mậu và Nhâm khác nhau ở Hóa Khoa | 🟡 đã chọn phương án 1 cho Canh, Hữu Bật cho Mậu, Tả Phù cho Nhâm — đều PROVISIONAL, Q7 vẫn mở |
| 13 | §27 Phụ tinh 2 | Ân Quang/Thiên Quý: bước "lùi 1 cung" có bản ghi khác; Thiên Đức/Nguyệt Đức một số bản an theo tháng âm | 🟡 chọn cách đọc thông dụng, ghi rõ trong note của từng luật |
| 14 | §28 Sát tinh 1 | Chiều đếm Hỏa Tinh / Linh Tinh: theo âm dương nam nữ hay luôn thuận | 🟡 chọn theo âm dương nam nữ, ghi cách đọc đối lập trong note |
| 15 | §29 Phụ tinh 3 | Lưu Hà: bảng theo can năm có chỗ bất quy tắc, không đối chiếu được | 🔴 chưa cài — cần bảng từ ấn bản |
| 16 | §30 Lưu niên | Tuổi xem là tuổi ta hay tuổi tròn (Q11) | 🟡 engine đưa CẢ HAI, `age_convention` = null cho tới khi chốt |

---

## 22. Nguyên tắc khi gặp điều chưa biết

1. **Không bịa quy tắc để code chạy được.** Thiếu quy tắc thì để trống và gắn cờ.
2. **Không trộn nguồn.** Một mục lấy từ một nguồn, không ghép nửa nọ nửa kia.
3. **Mọi thứ chưa kiểm định phải mang `provisional: true`** và UI phải nói rõ.
4. **Engine chỉ được lên stage `FULL`** khi toàn bộ mục 🔴 đã đóng và ma trận
   kiểm định đã được ký duyệt.
5. **Dữ liệu tử vi chưa biết phải là `null`** — không `"Unknown"`, không `"N/A"`,
   không sao giữ chỗ, không độ sáng đoán. Renderer quyết định hiển thị gì khi
   thiếu; domain và API thì không được bù. Chi tiết và danh sách field ở
   `chart-data-contract.md` mục 0.
