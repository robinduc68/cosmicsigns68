<script setup lang="ts">
const props = defineProps<{ state: string }>()

/** Mismatch must stand out; everything else stays quiet so it can. */
const variant = computed(() => {
  switch (props.state) {
    case 'VERIFIED':
      return 'success' as const
    case 'DISAGREEMENT':
      return 'danger' as const
    case 'BLOCKED':
      return 'gold' as const
    case 'IN_REVIEW':
      return 'accent' as const
    default:
      return 'neutral' as const
  }
})

const LABELS: Record<string, string> = {
  PENDING: 'Chờ thẩm định',
  IN_REVIEW: 'Đang thẩm định',
  VERIFIED: 'Đã kiểm định',
  DISAGREEMENT: 'Bất đồng',
  BLOCKED: 'Bị chặn',
}
</script>

<template>
  <CsBadge :variant="variant">{{ LABELS[state] ?? state }}</CsBadge>
</template>
