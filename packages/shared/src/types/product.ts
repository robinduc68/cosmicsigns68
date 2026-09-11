/**
 * Mirror of `GET /api/v1/products`.
 *
 * Prices are **not** declared anywhere in this repo's frontend — they live in
 * the `products` table so an operator can change them without a deploy
 * (business.md, nguyên tắc bất biến #4). This file describes their shape only.
 */
export interface Product {
  id: string
  code: string
  name: string
  description: string
  /** Whole đồng. Never a float — money must not round. */
  price_amount: number
  /** ISO 4217, e.g. `VND`. Comes from the row, never assumed. */
  currency: string
  /** Entitlement codes granted on purchase; may be wider than `code`. */
  entitlements: string[]
  is_featured: boolean
  sort_order: number
}
