<template>
  <div class="page-shell">
    <PageHeader eyebrow="NUTRITION PLANS" title="Phased goal planning" description="Maintain multi-phase wellness goals, edit active plan versions, and review exactly what changed before every declaration package submission.">
      <template #actions>
        <router-link to="/app/participant/plans/new"><n-button type="primary">New plan</n-button></router-link>
      </template>
    </PageHeader>

    <n-card class="section-card">
      <n-data-table :columns="columns" :data="plans" :bordered="false" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { NButton, NCard, NDataTable, useMessage } from 'naive-ui'

import { plansApi } from '@/api/plans'
import { extractApiError } from '@/api/client'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const message = useMessage()
const plans = ref<any[]>([])

const columns = [
  { title: 'Title', key: 'title', render: (row: any) => h(RouterLink, { to: `/app/participant/plans/${row.id}` }, { default: () => row.title }) },
  { title: 'Duration', key: 'duration_weeks', render: (row: any) => `${row.duration_weeks} weeks` },
  { title: 'Goal', key: 'goal_category' },
  { title: 'Status', key: 'status', render: (row: any) => h(StatusBadge, { status: row.status }) },
]

onMounted(async () => {
  try {
    plans.value = await plansApi.list()
  } catch (error) {
    message.error(extractApiError(error))
  }
})
</script>
