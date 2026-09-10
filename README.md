# Cosmic Signs

Nền tảng lập và luận giải lá số Tử Vi. Người dùng nhập ngày giờ sinh, hệ thống **tự tính**
lá số bằng một engine tất định, sau đó AI chỉ **diễn giải** dữ liệu đã tính.

> Trạng thái: đang xây dựng. Xem [PROGRESS.md](PROGRESS.md) để biết phần nào đã xong.

## Nguyên tắc kiến trúc

Ba lớp tách bạch, không được trộn:

| Lớp | Ở đâu | Tính chất |
| --- | --- | --- |
| **Calculation** | `packages/astrology-engine` | 100% tất định, không I/O, không AI, có test |
| **Interpretation rules** | `apps/api` (sẽ bổ sung) | Logic có cấu trúc, sinh facts + evidence |
| **Language generation** | AI provider (chưa triển khai) | Chỉ viết lời văn từ facts đã có |

AI không bao giờ tự suy ra vị trí sao, Mệnh, Cục, Tuần hay Triệt.

## Cấu trúc

```
apps/
  api/                  FastAPI + SQLAlchemy + Alembic
  web/                  Nuxt 3 + Vue 3 + Tailwind v4
packages/
  astrology-engine/     Python — lịch âm dương, can chi, khung 12 cung
  shared/               TypeScript — types, zod schemas, hằng số dùng chung
  ui/                   Design system, đóng gói dưới dạng Nuxt layer
docs/                   Tài liệu sản phẩm & kỹ thuật
infra/                  Cấu hình hạ tầng
```

## Yêu cầu môi trường

- Node ≥ 20.11 (pnpm qua `corepack`)
- Python ≥ 3.12
- Docker + Docker Compose

Cổng mặc định tránh các cổng thông dụng đã bị chiếm: web `3100`, api `8100`,
postgres `5436`, redis `6382`.

## Bắt đầu

```bash
cp .env.example .env
make setup     # cài dependency, dựng database, chạy migration
make dev       # chạy API (8100) và web (3100) với hot reload
```

Chạy toàn bộ trong Docker:

```bash
make up        # web + api + postgres
make down
```

## Các lệnh thường dùng

```bash
make lint         # eslint + ruff
make typecheck    # vue-tsc + mypy
make test         # pytest (engine + api) + vitest
make migrate      # alembic upgrade head
make migration m="mô tả thay đổi"
```

## Biến môi trường

Xem [.env.example](.env.example). Ứng dụng phải khởi động được khi **mọi** khoá AI và
thanh toán còn trống — các tính năng đó chưa được triển khai.

`CHART_ENGINE_STAGE` điều khiển mức độ hoàn chỉnh của engine:

- `FRAME` — chỉ những phép tính đã kiểm định (lịch, can chi, 12 cung, Mệnh/Thân/Cục, Tuần/Triệt)
- `PREVIEW` — thêm 14 chính tinh, được đánh dấu `provisional` cho tới khi có bộ test đối chiếu

## Tài liệu

- [business.md](business.md) — yêu cầu nghiệp vụ
- [PROGRESS.md](PROGRESS.md) — tiến độ và việc kế tiếp
- `docs/` — tài liệu kiến trúc (đang viết)
