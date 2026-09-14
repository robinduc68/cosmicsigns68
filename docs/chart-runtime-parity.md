# Đối chiếu runtime: dữ liệu lá số qua từng tầng

Đo thật, không suy đoán. Ngày đo **2026-09-14**, commit `d96bec5` (số sao cập nhật sau khi thêm phụ tinh nhóm 1), trên đúng fixture
đang hiển thị mặc định ở trang lá số: **`cross-check-2001`** — Nguyễn Thị Minh Anh,
nữ, 04/03/2001 09:30, `Asia/Ho_Chi_Minh`, stage `PREVIEW`.

```
Engine Domain Chart → API DTO → Frontend DTO → Chart ViewModel → Rendered palace
```

Cách đo:

| Tầng | Cách lấy |
| --- | --- |
| Engine | gọi thẳng `build_chart(...)`, `to_dict()` |
| API DTO | `POST /api/v1/charts` rồi so sâu từng khoá với đầu ra engine |
| Frontend DTO | `apps/web/fixtures/charts/cross-check-2001.preview.json` |
| ViewModel | chạy `mapChartDtoToViewModel` thật, đổ ra JSON |
| Rendered | đọc DOM thật bằng Chrome headless, cả trang demo lẫn `/chart/<id>` |

---

## 0. Kết luận ngắn

**Pipeline không mất một trường nào.** Mọi thứ engine tính ra đều tới được màn hình.

| Chặng | Mất mát |
| --- | --- |
| Engine → API DTO | **0** (so sâu toàn payload, chỉ lệch `generated_at`) |
| API DTO → Frontend DTO | **0** (fixture trùng **byte** với đầu ra engine) |
| Frontend DTO → ViewModel | **0** trên cả 12 cung |
| ViewModel → Rendered | **0** trên cả 12 cung, 14/14 sao |

Lá số trông thưa **không phải vì mất dữ liệu**. Nó thưa vì engine mới an **14 chính
tinh**, chưa an phụ tinh nào. Đây là loại **A — chưa tính**, không phải B/C/D.

---

## 1. Trường mức lá số

| Trường | ENGINE | API | FE DTO | VIEWMODEL | RENDERED |
| --- | --- | --- | --- | --- | --- |
| `schema_version` | YES | YES | YES | YES | — (nội bộ) |
| `identity.*` | YES | YES | YES | YES | — (nội bộ) |
| `birth.*` (12 trường) | YES | YES | YES | YES | YES |
| `lunar_birth.*` | YES | YES | YES | YES | YES |
| `pillars.{year,month,day,hour}` | YES | YES | YES | YES | YES |
| `yin_yang.*` | YES | YES | YES | YES | YES |
| `menh.*` | YES | YES | YES | YES | YES |
| `than.*` | YES | YES | YES | YES | YES |
| `cuc.*` | YES | YES | YES | YES | YES |
| `traditional.chu_menh` | NULL | NULL | NULL | NULL | NO (bỏ dòng) |
| `traditional.chu_than` | NULL | NULL | NULL | NULL | NO (bỏ dòng) |
| `traditional.lai_nhan_cung` | NULL | NULL | NULL | NULL | NO (bỏ dòng) |
| `traditional.can_luong` | NULL | NULL | NULL | NULL | NO (bỏ dòng) |
| `traditional.nam_xem` | NULL | NULL | NULL | NULL | NO (bỏ dòng) |
| `traditional.tuoi_xem` | NULL | NULL | NULL | NULL | NO (bỏ dòng) |
| `four_transformations` | `{}` | `{}` | `{}` | — | NO |
| `major_cycles` (gốc) | `[]` | `[]` | `[]` | — | NO — đại vận nằm trên từng cung |
| `annual_cycles` | `[]` | `[]` | `[]` | — | NO |

Sáu trường `traditional.*` để trống là **đúng chính sách**: chưa tính thì `null`, và
renderer **bỏ hẳn dòng** thay vì in `—`. Bật `showPendingFields` ở màn hình nội bộ mới
thấy chúng.

---

## 2. Trường mức cung — **đo trên cả 12 cung**

Bảng dưới đây đúng cho **từng cung một**, không phải mẫu một cung suy ra cả lá số.

| Trường | ENGINE | API | FE DTO | VIEWMODEL | RENDERED |
| --- | --- | --- | --- | --- | --- |
| tên cung (`name` / `label`) | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | YES |
| thiên can (`stem`) | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | YES |
| địa chi (`branch`) | YES | YES | YES | YES | YES |
| ngũ hành cung (`element`) | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | YES |
| nạp âm (`nap_am`) | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | YES |
| `palace_index` | YES | YES | YES | YES | NO — chỉ dùng để sắp xếp |
| `month_number` | **NULL** | NULL | NULL | NULL | NO (ẩn khi null) |
| `cycles.major_cycle_age_start` | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | **YES** |
| `cycles.major_cycle_age_end` | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | **YES** |
| `cycles.major_cycle_index` | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | **YES** (`ĐV n`) |
| `cycles.major_cycle_direction` | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | **YES** *(đã nối ở đợt này)* |
| `cycles.trang_sinh_stage` | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | **YES** |
| `cycles.major_cycle_target` | **NULL** | NULL | NULL | NULL | NO |
| `cycles.annual_target` | **NULL** | NULL | NULL | NULL | NO |
| `tuan` / `has_tuan` | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | YES |
| `triet` / `has_triet` | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | YES |
| `major_stars` | PROVISIONAL | PROVISIONAL | PROVISIONAL | YES | YES (14/14) |
| `minor_stars` | **rỗng** | rỗng | rỗng | rỗng | — |
| `transformations` | **rỗng** | rỗng | rỗng | rỗng | — |
| `annual_stars` | **rỗng** | rỗng | rỗng | rỗng | — |
| `metadata` | `{}` | `{}` | `{}` | — | NO |

### Số liệu thật, 12/12 cung

| Chi | Cung | ĐV | Tuổi | Chiều | Tràng Sinh | Tuần | Triệt | Sao |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tuất | Mệnh | 1 | 3–12 | FORWARD | Dưỡng | – | – | 1 |
| Hợi | Phụ Mẫu | 2 | 13–22 | FORWARD | Tràng Sinh | – | – | 2 |
| Tý | Phúc Đức | 3 | 23–32 | FORWARD | Mộc Dục | – | – | 1 |
| Sửu | Điền Trạch | 4 | 33–42 | FORWARD | Quan Đới | – | – | 1 |
| Dần | Quan Lộc | 5 | 43–52 | FORWARD | Lâm Quan | – | – | 2 |
| Mão | Nô Bộc | 6 | 53–62 | FORWARD | Đế Vượng | – | – | 2 |
| Thìn | Thiên Di | 7 | 63–72 | FORWARD | Suy | – | ✓ | 1 |
| Tỵ | Tật Ách | 8 | 73–82 | FORWARD | Bệnh | – | ✓ | 0 |
| Ngọ | Tài Bạch | 9 | 83–92 | FORWARD | Tử | – | – | 1 |
| Mùi | Tử Tức | 10 | 93–102 | FORWARD | Mộ | – | – | 2 |
| Thân | Phu Thê | 11 | 103–112 | FORWARD | Tuyệt | ✓ | – | 0 |
| Dậu | Huynh Đệ | 12 | 113–122 | FORWARD | Thai | ✓ | – | 1 |

**Đủ 12/12 cung có cả `trang_sinh_stage` lẫn khoảng tuổi đại vận, và đều đã render.**

---

## 3. Trường mức sao

Số lượng phát ra trên fixture này:

| Nhóm | Engine phát | Render |
| --- | --- | --- |
| Chính tinh | **14** | **14** |
| Phụ tinh | **13** *(nhóm 1, Nam phái)* | **13** |
| Tứ Hóa | **0** | 0 |
| Lưu tinh | **0** | 0 |
| **Tổng** | **27** | **27** |

Mười trường của mỗi sao, đo trên **cả 14 sao**:

| Trường | ENGINE | API | FE DTO | VIEWMODEL | RENDERED |
| --- | --- | --- | --- | --- | --- |
| `id` | YES | YES | YES | YES | YES (`data-star`) |
| `name` | YES | YES | YES | YES | YES |
| `category` | YES | YES | YES | YES | YES (`data-category`) |
| `element` | PROVISIONAL 12/14 | như engine | như engine | YES | YES (class ngũ hành) |
| `polarity` | PROVISIONAL 12/14 | như engine | như engine | YES | YES (tiền tố `+`/`−`) |
| `strength` | **NULL 0/14** | NULL | NULL | NULL | NO (ẩn khi null) |
| `is_annual` | YES | YES | YES | YES | YES (class `is-annual`) |
| `is_transformation` | YES | YES | YES | YES | YES |
| `display_priority` | YES | YES | YES | YES | YES (thứ tự sắp xếp) |
| `verification_status` | YES | YES | YES | YES | YES (dấu `*` + banner) |

**Không sao nào rụng trường nào.**

---

## 4. Vòng Tràng Sinh và Đại vận

| Trường | Engine có? | Đủ 12 cung? | Đã render? |
| --- | --- | --- | --- |
| `trang_sinh_stage` | **CÓ** | 12/12, 12 chặng khác nhau | **CÓ** — giữa footer |
| `major_cycle_age_start` | **CÓ** | 12/12 | **CÓ** — góc phải đầu cung |
| `major_cycle_age_end` | **CÓ** | 12/12 | **CÓ** |
| `major_cycle_direction` | **CÓ** | 12/12 | **CÓ** — thêm ở đợt này |
| `major_cycle_index` | **CÓ** | 12/12 | **CÓ** — `ĐV n`, trái footer |
| `major_cycle_target` | KHÔNG (`null`) | — | — |
| `annual_target` | KHÔNG (`null`) | — | — |

Cả bốn trường đầu ở mức `PROVISIONAL`: chưa chốt ấn bản chuẩn (Q1/Q2/Q3), và hai chỗ
phân kỳ trường phái đang chọn theo cách đọc đa số — xem `astrology-conventions.md` §24.

---

## 5. Metadata màu (fixture đang hiển thị)

- **Chính tinh có ngũ hành: 12/14**
- **Phụ tinh có ngũ hành: 0/0** — engine chưa an phụ tinh

| Sao | Loại | Hành | Âm/Dương | Độ sáng | Cung | Chi |
| --- | --- | --- | --- | --- | --- | --- |
| Thái Âm | MAJOR | THUY | YIN | — | Mệnh | Tuất |
| Liêm Trinh | MAJOR | KIM | YIN | — | Phụ Mẫu | Hợi |
| **Tham Lang** | MAJOR | **—** | **—** | — | Phụ Mẫu | Hợi |
| **Cự Môn** | MAJOR | **—** | **—** | — | Phúc Đức | Tý |
| Thiên Tướng | MAJOR | THUY | YANG | — | Điền Trạch | Sửu |
| Thiên Đồng | MAJOR | THUY | YANG | — | Quan Lộc | Dần |
| Thiên Lương | MAJOR | THO | YANG | — | Quan Lộc | Dần |
| Vũ Khúc | MAJOR | KIM | YIN | — | Nô Bộc | Mão |
| Thất Sát | MAJOR | KIM | YANG | — | Nô Bộc | Mão |
| Thái Dương | MAJOR | HOA | YANG | — | Thiên Di | Thìn |
| Thiên Cơ | MAJOR | MOC | YIN | — | Tài Bạch | Ngọ |
| Tử Vi | MAJOR | THO | YIN | — | Tử Tức | Mùi |
| Phá Quân | MAJOR | THUY | YIN | — | Tử Tức | Mùi |
| Thiên Phủ | MAJOR | THO | YANG | — | Huynh Đệ | Dậu |

Tham Lang và Cự Môn để trống vì các trường phái ghi khác nhau, không phải vì mất dữ
liệu. **Độ sáng trống trên cả 14 sao** — bảng 168 ô chưa cài, và không được bịa.

---

## 6. Footer của cung

Footer là lưới **ba ô cố định** (`1fr auto 1fr`) để nhãn giữa luôn ở chính giữa. Ô
trống là **chỗ giữ nhịp**, không phải giá trị bị mất.

| Ô | Đích | Hiện trạng |
| --- | --- | --- |
| Trái — `ĐV.<target>` | số đại vận | **Đang hiện** `ĐV 1`…`ĐV 12`, lấy từ `major_cycle_index` |
| Giữa — Tràng Sinh | chặng | **Đang hiện** đủ 12 chặng |
| Phải — `LN.<target>` | lưu niên | **Trống** — `annual_target` là `null` |

**Vì sao `LN` trống:** lưu niên chưa cài. Nó cần quy tuổi ra năm dương lịch, mà việc
đó phụ thuộc **Q11** (tuổi ta hay tuổi tròn — hai cách lệch nhau một năm). Không được
bịa. Phụ thuộc engine còn thiếu: *an lưu niên*.

**`major_cycle_target` khác `major_cycle_index`:** `index` là "cung này là đại vận thứ
mấy" (đã có); `target` để dành cho "đang xem đại vận nào" — một khái niệm của giao diện
lưu niên sau này. Nó `null` là đúng, không phải lỗi nối dây.

---

## 7. Đã sửa ở đợt này (chỉ nối dây, không đụng công thức)

1. **`major_cycle_direction` đã tính nhưng không hiện ở đâu.** Thêm dòng "Chiều đại
   vận" ở trung tâm, qua `formatCycleDirection`.
2. **Đại vận và Tràng Sinh không đọc được bằng trình đọc màn hình.** `ĐV 1` và `Dưỡng`
   là hai mẩu chữ trơ; nay mỗi ô có `title` riêng và `aria-label` của cung nói đủ
   "Cung Mệnh, Mậu Tuất, đại vận 3 – 12 tuổi, Tràng Sinh: Dưỡng".

Không đụng: an sao, an cung, Tử Vi, chính tinh, phụ tinh, Tứ Hóa, độ sáng, lưu tinh.
