<script setup lang="ts">
import {
  TooltipArrow,
  TooltipContent,
  TooltipPortal,
  TooltipProvider,
  TooltipRoot,
  TooltipTrigger,
} from 'reka-ui'

/**
 * Self-contained on purpose: the provider lives inside so a tooltip works
 * anywhere without the consuming app having to remember to mount one.
 */
withDefaults(defineProps<{ content: string; side?: 'top' | 'right' | 'bottom' | 'left' }>(), {
  side: 'top',
})
</script>

<template>
  <TooltipProvider :delay-duration="220">
    <TooltipRoot>
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
  </TooltipProvider>
</template>
