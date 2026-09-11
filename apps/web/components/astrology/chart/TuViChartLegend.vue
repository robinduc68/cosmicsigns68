<script setup lang="ts">
import type { ChartMetaViewModel } from '~/types/chart-view-model'
import { ELEMENT_COLOR_MAP, ELEMENT_ORDER, STRENGTH_LEGEND } from '~/utils/tuvi-chart'

const props = withDefaults(defineProps<{ meta: ChartMetaViewModel; compact?: boolean }>(), {
  compact: false,
})

const offset = computed(() => {
  const hours = props.meta.utcOffsetHours
  if (hours === null) return null
  return `UTC${hours >= 0 ? '+' : '−'}${Math.abs(hours)}`
})
</script>

<template>
  <footer class="tuvi-legend" :class="{ 'tuvi-legend--compact': compact }">
    <div class="tuvi-legend__row">
      <div class="tuvi-legend__group" role="list" aria-label="Độ sáng của sao">
        <span v-for="entry in STRENGTH_LEGEND" :key="entry.key" role="listitem">
          <b class="tuvi-legend__abbr">{{ entry.abbr }}</b>: {{ entry.label }}
        </span>
      </div>
      <div class="tuvi-legend__group" role="list" aria-label="Ngũ hành">
        <span v-for="key in ELEMENT_ORDER" :key="key" role="listitem">
          <i
            class="tuvi-legend__swatch"
            :style="{ background: ELEMENT_COLOR_MAP[key].color }"
            aria-hidden="true"
          />{{ ELEMENT_COLOR_MAP[key].label }}
        </span>
      </div>
    </div>

    <div class="tuvi-legend__row tuvi-legend__meta">
      <span>
        Cosmic Signs Engine {{ meta.engineVersion
        }}<template v-if="meta.conventionProfile">
          · Quy ước {{ meta.conventionProfile
          }}<template v-if="meta.conventionVersion">@{{ meta.conventionVersion }}</template>
        </template>
      </span>
      <span v-if="offset">{{ offset }}</span>
    </div>

    <!-- Inline, !important styles on purpose: a stylesheet or utility class must not
         be able to hide this warning, on screen, in print or in an exported PNG. -->
    <p
      v-if="meta.provisional"
      role="note"
      data-provisional-badge
      style="
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        margin: 0 !important;
        padding: 6px 12px !important;
        background: #8c2a1b !important;
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        text-align: center !important;
      "
    >
      ENGINE PROVISIONAL — NOT FOR CUSTOMER USE
    </p>
  </footer>
</template>
