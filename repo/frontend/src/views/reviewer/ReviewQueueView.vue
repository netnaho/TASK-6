<template>
  <div class="page-shell">
    <PageHeader eyebrow="REVIEW QUEUE" title="Assigned declarations" description="Prioritize packages by visible deadline, inspect current state, and open review workspaces for structured correction or closeout actions." />
    <n-card class="section-card">
      <n-data-table :columns="columns" :data="queue" :bordered="false" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { NCard, NDataTable, useMessage } from 'naive-ui'

import { reviewsApi } from '@/api/reviews'
import { extractApiError } from '@/api/client'
import DeadlineChip from '@/components/common/DeadlineChip.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const message = useMessage()
const queue = ref<any[]>([])

const columns = [
  { title: 'Package', key: 'package_id', render: (row: any) => h(RouterLink, { to: `/app/reviewer/packages/${row.package_id}` }, { default: () => row.package_id }) },
  { title: 'Priority', key: 'priority' },
  { title: 'Assignment status', key: 'status', render: (row: any) => h(StatusBadge, { status: row.status }) },
  { title: 'Review due', key: 'review_due_at', render: (row: any) => h(DeadlineChip, { value: row.review_due_at }) },
]

onMounted(async () => {
  try { queue.value = await reviewsApi.queue() } catch (error) { message.error(extractApiError(error)) }
})
</script>
