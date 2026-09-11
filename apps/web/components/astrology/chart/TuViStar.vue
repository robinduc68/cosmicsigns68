<script setup lang="ts">
import type { StarViewModel } from '~/types/chart-view-model'
import { STRENGTH_LABELS, elementColor } from '~/utils/tuvi-chart'

const props = withDefaults(defineProps<{ star: StarViewModel; major?: boolean }>(), {
  major: false,
})

/**
 * Colour comes only from the element the engine declared; no element, neutral ink.
 * It is applied to the whole label — name, polarity and strength together — because
 * the element belongs to the star, not to one glyph of its name.
 */
const color = computed(() => elementColor(props.star.element))
const strengthTitle = computed(() =>
  props.star.strength ? STRENGTH_LABELS[props.star.strength] : undefined,
)
</script>

<template>
  <span
    class="tuvi-star"
    :class="[
      major ? 'tuvi-star--major' : 'tuvi-star--minor',
      {
        'is-provisional': star.provisional,
        'is-transformation': star.isTransformation,
        'is-annual': star.isAnnual,
      },
    ]"
    :style="{ color }"
    :data-star="star.code"
    :data-element="star.element ?? 'NONE'"
    :aria-label="star.ariaLabel"
    :title="star.ariaLabel"
    ><span v-if="star.polarityPrefix" class="tuvi-star__polarity" aria-hidden="true">{{
      star.polarityPrefix
    }}</span
    >{{ star.name
    }}<template v-if="star.strengthAbbr">
      <abbr class="tuvi-star__strength" :title="strengthTitle">({{ star.strengthAbbr }})</abbr>
    </template><span v-if="star.provisional" class="tuvi-star__mark" aria-hidden="true">*</span
    ><span v-if="star.provisional" class="sr-only"> — vị trí chưa được kiểm định</span>
  </span>
</template>
