<template>
  <div class="page-shell">
    <PageHeader eyebrow="IMMUTABLE AUDIT" title="Audit trail explorer" description="Review critical action history with actor, entity, and tamper-evident hash values for offline compliance verification." />
    <n-card class="section-card">
      <n-data-table :columns="columns" :data="rows" :bordered="false" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NCard, NDataTable, useMessage } from 'naive-ui'

import { adminApi } from '@/api/admin'
import { extractApiError } from '@/api/client'
import PageHeader from '@/components/common/PageHeader.vue'

const message = useMessage()
const rows = ref<any[]>([])
const columns = [
  { title: 'Time', key: 'occurred_at', render: (row: any) => new Date(row.occurred_at).toLocaleString() },
  { title: 'Action', key: 'action_type' },
  { title: 'Entity', key: 'entity_type' },
  { title: 'Entity ID', key: 'entity_id' },
  { title: 'Hash', key: 'entry_hash', ellipsis: { tooltip: true } },
]

onMounted(async () => {
  try { rows.value = await adminApi.audit() } catch (error) { message.error(extractApiError(error)) }
})
</script>
