<script setup lang="ts">
import { EARTHLY_BRANCHES } from '@cosmic/shared'
import type { VoidMarkerViewModel } from '~/types/chart-view-model'

const props = defineProps<{ marker: VoidMarkerViewModel }>()

const description = computed(
  () =>
    `${props.marker.label} giữa cung ${EARTHLY_BRANCHES[props.marker.branches[0]]} và ` +
    `${EARTHLY_BRANCHES[props.marker.branches[1]]}`,
)
</script>

<template>
  <!-- Position comes from the engine's flags; the renderer only finds the shared border. -->
  <span
    class="tuvi-void"
    :class="`tuvi-void--${marker.orientation}`"
    :style="{ left: `${marker.x}%`, top: `${marker.y}%` }"
    role="note"
    :aria-label="description"
    :data-void="marker.kinds.join('-')"
  >
    {{ marker.label }}
  </span>
</template>
