<template>
  <n-timeline>
    <n-timeline-item v-for="item in items" :key="item.id" :title="`Version ${item.version_number}`" :content="item.summary || fallbackText(item)" :time="formatTimestamp(item.created_at)" />
  </n-timeline>
</template>

<script setup lang="ts">
import { NTimeline, NTimelineItem } from 'naive-ui'

import type { VersionRecord } from '@/types/domain'

defineProps<{ items: VersionRecord[] }>()

function fallbackText(item: VersionRecord) {
  return `${item.change_summary_json.length} recorded changes`
}

function formatTimestamp(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  return date.toLocaleString()
}
</script>
