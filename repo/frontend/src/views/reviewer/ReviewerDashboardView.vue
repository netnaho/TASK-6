<template>
  <div class="page-shell">
    <PageHeader eyebrow="REVIEWER DASHBOARD" title="Review workload overview" description="Watch overdue declarations, identify upcoming review deadlines, and jump into packages that need structured correction feedback or closure." />
    <section class="metric-grid">
      <MetricCard label="Queue size" :value="queue.length" hint="Assigned packages" />
      <MetricCard label="Overdue" :value="overdue" hint="Requires immediate action" />
      <MetricCard label="Due today" :value="dueSoon" hint="Within 24 hours" />
      <MetricCard label="Corrections open" :value="corrected" hint="Awaiting participant response" />
    </section>
    <n-card class="section-card" title="Priority queue">
      <n-data-table :columns="columns" :data="queue" :bordered="false" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { NCard, NDataTable, useMessage } from 'naive-ui'

import { reviewsApi } from '@/api/reviews'
import { extractApiError } from '@/api/client'
import DeadlineChip from '@/components/common/DeadlineChip.vue'
import MetricCard from '@/components/common/MetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const message = useMessage()
const queue = ref<any[]>([])
const overdue = computed(() => queue.value.filter((item) => new Date(item.review_due_at).getTime() < Date.now()).length)
const dueSoon = computed(() => queue.value.filter((item) => (new Date(item.review_due_at).getTime() - Date.now()) / 36e5 < 24 && new Date(item.review_due_at).getTime() > Date.now()).length)
const corrected = computed(() => queue.value.filter((item) => item.status === 'in_review').length)

const columns = [
  { title: 'Package', key: 'package_id', render: (row: any) => h(RouterLink, { to: `/app/reviewer/packages/${row.package_id}` }, { default: () => row.package_id.slice(0, 8) }) },
  { title: 'Status', key: 'status', render: (row: any) => h(StatusBadge, { status: row.status }) },
  { title: 'Deadline', key: 'review_due_at', render: (row: any) => h(DeadlineChip, { value: row.review_due_at }) },
]

onMounted(async () => {
  try { queue.value = await reviewsApi.queue() } catch (error) { message.error(extractApiError(error)) }
})
</script>
