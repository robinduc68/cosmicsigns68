<script setup lang="ts">
import { TabsContent, TabsList, TabsRoot, TabsTrigger } from 'reka-ui'

export interface TabItem {
  value: string
  label: string
  locked?: boolean
}

defineProps<{ items: TabItem[]; ariaLabel?: string }>()
const model = defineModel<string>({ required: true })
</script>

<template>
  <TabsRoot v-model="model" class="w-full">
    <TabsList
      :aria-label="ariaLabel"
      class="-mx-5 flex gap-1 overflow-x-auto px-5 pb-px [scrollbar-width:none] sm:mx-0 sm:px-0 [&::-webkit-scrollbar]:hidden"
    >
      <TabsTrigger
        v-for="item in items"
        :key="item.value"
        :value="item.value"
        class="relative shrink-0 rounded-lg px-3.5 py-2 text-small font-medium whitespace-nowrap text-[var(--text-muted)] transition-colors hover:text-[var(--text)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)] data-[state=active]:bg-[var(--card)] data-[state=active]:text-[var(--text)]"
      >
        {{ item.label }}
        <span
          v-if="item.locked"
          class="ml-1.5 inline-block size-1.5 rounded-full bg-[var(--color-gold-400)] align-middle"
          aria-label="Nội dung chuyên sâu"
        />
      </TabsTrigger>
    </TabsList>
    <TabsContent
      v-for="item in items"
      :key="item.value"
      :value="item.value"
      class="mt-6 focus:outline-none"
    >
      <slot :name="item.value" />
    </TabsContent>
  </TabsRoot>
</template>
