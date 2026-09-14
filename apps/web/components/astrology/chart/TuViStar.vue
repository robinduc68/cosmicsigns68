<script setup lang="ts">
import type { StarViewModel } from '~/types/chart-view-model'
import { STRENGTH_LABELS, elementClass } from '~/utils/tuvi-chart'

const props = withDefaults(defineProps<{ star: StarViewModel; major?: boolean }>(), {
  major: false,
})

/**
 * Colour is chosen by a semantic class keyed on the element the engine declared;
 * no element means the neutral class. The class covers the whole label — polarity,
 * name and strength together — because the element belongs to the star, not to one
 * glyph of its name. The star's name is never an input to this.
 */
const elementSelector = computed(() => elementClass(props.star.element))
const strengthTitle = computed(() =>
  props.star.strength ? STRENGTH_LABELS[props.star.strength] : undefined,
)
</script>

<template>
  <span
    class="tuvi-star"
    :class="[
      major ? 'tuvi-star--major' : 'tuvi-star--minor',
      elementSelector,
      {
        'is-provisional': star.provisional,
        'is-transformation': star.isTransformation,
        'is-annual': star.isAnnual,
      },
    ]"
    :data-star="star.code"
    :data-element="star.element ?? 'NONE'"
    :data-category="star.category"
    :aria-label="star.ariaLabel"
    :title="star.ariaLabel"
    ><span v-if="star.polarityPrefix" class="tuvi-star__polarity" aria-hidden="true">{{
      star.polarityPrefix
    }}</span
    >{{ star.name
    }}<template v-if="star.strengthAbbr">
      <abbr class="tuvi-star__strength" :title="strengthTitle">({{ star.strengthAbbr }})</abbr>
    </template
    ><!-- Tứ Hóa: dấu vuông, cố ý khác ngoặc tròn của độ sáng. Nó KHÔNG đổi màu sao —
         màu thuộc về ngũ hành, hóa là một thông tin khác.
    --><span
      v-for="hoa in star.transformations"
      :key="hoa.code"
      class="tuvi-star__hoa"
      :data-transformation="hoa.code"
      :title="hoa.fullLabel"
      >[{{ hoa.label }}]</span
    ><span v-if="star.provisional" class="tuvi-star__mark" aria-hidden="true">*</span
    ><span v-if="star.provisional" class="sr-only"> — vị trí chưa được kiểm định</span>
  </span>
</template>
