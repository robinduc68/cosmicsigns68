<script setup lang="ts">
import type { ConnectionViewModel } from '~/types/chart-view-model'

defineProps<{ connections: ConnectionViewModel[] }>()
</script>

<template>
  <!-- Tam phương tứ chính supplied by the engine; drawn behind the centre text.
       Colour is set through `style`, because var() is unreliable in SVG
       presentation attributes and the exporter reads computed styles. -->
  <svg
    class="tuvi-center__lines"
    viewBox="0 0 100 100"
    preserveAspectRatio="none"
    aria-hidden="true"
    focusable="false"
  >
    <line
      v-for="(connection, index) in connections"
      :key="index"
      :x1="connection.x1"
      :y1="connection.y1"
      :x2="connection.x2"
      :y2="connection.y2"
      :style="{
        stroke:
          connection.type === 'OPPOSITE' ? 'var(--chart-line-opposite)' : 'var(--chart-line-trine)',
      }"
      stroke-width="1.5"
      vector-effect="non-scaling-stroke"
      :data-connection="connection.type"
    />
  </svg>
</template>
