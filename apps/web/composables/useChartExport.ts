import { domToBlob } from 'modern-screenshot'
import { CANONICAL_CHART_HEIGHT, CANONICAL_CHART_WIDTH } from '~/utils/tuvi-chart'

/**
 * PNG export of the canonical chart.
 *
 * Always captures the fixed 1400 × 1750 canvas — never whatever squashed layout
 * the screen happens to show — then multiplies pixel density.
 */

export interface ChartExportOptions {
  /** Pixel density multiplier; 2 gives 2800 × 3500. */
  scale?: number
  fileSlug?: string
  /** Pass a fixed date for reproducible file names. */
  date?: Date
}

const pad = (value: number) => String(value).padStart(2, '0')

/** "Nguyễn Thị Minh Anh" → "nguyen-thi-minh-anh". đ has no decomposition, so it is mapped by hand. */
export function slugifyVietnamese(value: string): string {
  const slug = value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return slug || 'la-so'
}

export function chartExportFileName(subject: string, date: Date): string {
  const day = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
  return `la-so-tu-vi-${slugifyVietnamese(subject)}-${day}.png`
}

export async function renderChartPng(node: HTMLElement, scale = 2): Promise<Blob> {
  // Capture before the web fonts settle and the image falls back to a system font,
  // which is exactly where Vietnamese diacritics break.
  if (typeof document !== 'undefined' && document.fonts) await document.fonts.ready
  return domToBlob(node, {
    width: CANONICAL_CHART_WIDTH,
    height: CANONICAL_CHART_HEIGHT,
    scale,
    type: 'image/png',
    backgroundColor: '#fbf7ee',
    // The canvas may sit inside a transformed pan/zoom stage; capture it flat.
    style: { transform: 'none', margin: '0' },
  })
}

function downloadBlob(blob: Blob, fileName: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  link.rel = 'noopener'
  document.body.appendChild(link)
  link.click()
  link.remove()
  // Give the browser a moment to start the download before the URL goes away.
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export function useChartExport() {
  const exporting = ref(false)

  async function exportPng(
    node: HTMLElement,
    options: ChartExportOptions = {},
  ): Promise<{ blob: Blob; fileName: string } | null> {
    exporting.value = true
    try {
      const blob = await renderChartPng(node, options.scale ?? 2)
      const fileName = chartExportFileName(options.fileSlug ?? 'la-so', options.date ?? new Date())
      downloadBlob(blob, fileName)
      return { blob, fileName }
    } catch (caught: unknown) {
      if (import.meta.dev) console.error('[useChartExport]', caught)
      return null
    } finally {
      exporting.value = false
    }
  }

  return { exporting, exportPng }
}
