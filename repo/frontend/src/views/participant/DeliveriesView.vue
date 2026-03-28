<template>
  <div class="page-shell">
    <PageHeader eyebrow="DELIVERY CENTER" title="Delivered package outputs" description="Review final plan PDFs, raw exports, revision notes, secure download windows, and confirm acceptance when the case package is ready." />
    <n-card class="section-card">
      <n-data-table :columns="columns" :data="rows" :bordered="false" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { NButton, NCard, NDataTable, useMessage } from 'naive-ui'

import { declarationsApi } from '@/api/declarations'
import { deliveriesApi } from '@/api/deliveries'
import { extractApiError } from '@/api/client'
import PageHeader from '@/components/common/PageHeader.vue'

const message = useMessage()
const rows = ref<any[]>([])
const columns = [
  { title: 'Package', key: 'package_number' },
  { title: 'Artifact count', key: 'delivery_count' },
  { title: 'Acceptance', key: 'accepted_at', render: (row: any) => row.accepted_at ? 'Confirmed' : 'Pending' },
  {
    title: 'Action',
    key: 'actions',
    render: (row: any) => row.accepted_at
      ? h('span', { class: 'muted' }, 'Completed')
      : h(RouterLink, { to: `/app/participant/declarations/${row.id}` }, {
          default: () => h(NButton, { type: 'primary', size: 'small', secondary: true }, { default: () => 'Open package' }),
        }),
  },
]

onMounted(async () => {
  try {
    const declarations = await declarationsApi.list()
    const deliveryGroups = await Promise.all(declarations.map(async (item) => ({ ...item, delivery_count: (await deliveriesApi.list(item.id).catch(() => [])).length })))
    rows.value = deliveryGroups
  } catch (error) {
    message.error(extractApiError(error))
  }
})
</script>
