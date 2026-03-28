<template>
  <n-tag :bordered="false" :type="tagType" round>
    {{ label }}
  </n-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NTag } from 'naive-ui'

const props = defineProps<{ status: string }>()

const tagType = computed(() => {
  if (['submitted', 'active', 'completed'].includes(props.status)) return 'success'
  if (['corrected', 'warning', 'queued'].includes(props.status)) return 'warning'
  if (['voided', 'withdrawn', 'disabled'].includes(props.status)) return 'error'
  return 'info'
})

const label = computed(() => props.status.split('_').join(' '))
</script>
