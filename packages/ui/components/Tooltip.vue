<script setup lang="ts">
import { TooltipArrow, TooltipContent, TooltipPortal, TooltipRoot, TooltipTrigger } from 'reka-ui'

withDefaults(defineProps<{ content: string; side?: 'top' | 'right' | 'bottom' | 'left' }>(), {
  side: 'top',
})
</script>

<template>
  <TooltipRoot :delay-duration="220">
    <TooltipTrigger as-child>
      <slot />
    </TooltipTrigger>
    <TooltipPortal>
      <TooltipContent
        :side="side"
        :side-offset="6"
        class="z-50 max-w-64 rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-2.5 py-1.5 text-caption text-[var(--text-muted)] shadow-lg"
      >
        {{ content }}
        <TooltipArrow class="fill-[var(--bg-elevated)]" :width="10" :height="5" />
      </TooltipContent>
    </TooltipPortal>
  </TooltipRoot>
</template>
