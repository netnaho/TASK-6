<template>
  <n-tag :bordered="false" :type="tone" round>
    {{ label }}
  </n-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NTag } from 'naive-ui'

const props = defineProps<{ value?: string | null }>()

const date = computed(() => (props.value ? new Date(props.value) : null))
const tone = computed(() => {
  if (!date.value) return 'default'
  const diffHours = (date.value.getTime() - Date.now()) / 36e5
  if (diffHours < 0) return 'error'
  if (diffHours < 24) return 'warning'
  return 'info'
})
const label = computed(() => {
  if (!date.value) return 'No deadline'
  return `Due ${date.value.toLocaleString()}`
})
</script>
