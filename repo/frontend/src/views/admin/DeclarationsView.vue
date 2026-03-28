<template>
  <div class="page-shell">
    <PageHeader eyebrow="DECLARATION GOVERNANCE" title="Admin declaration control" description="Review every package across participants, inspect current state, and open a detail workspace to void packages with documented administrative reasons." />
    <n-card class="section-card">
      <n-data-table :columns="columns" :data="declarations" :bordered="false" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { NCard, NDataTable, type DataTableColumns, useMessage } from 'naive-ui'

import { declarationsApi } from '@/api/declarations'
import { extractApiError } from '@/api/client'
import DeadlineChip from '@/components/common/DeadlineChip.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import type { DeclarationRecord } from '@/types/domain'

const message = useMessage()
const declarations = ref<DeclarationRecord[]>([])

const columns: DataTableColumns<DeclarationRecord> = [
  {
    title: 'Package',
    key: 'package_number',
    render: (row) => h(RouterLink, { to: `/app/admin/declarations/${row.id}` }, { default: () => row.package_number }),
  },
  { title: 'Participant', key: 'participant_id' },
  { title: 'State', key: 'state', render: (row) => h(StatusBadge, { status: row.state }) },
  { title: 'Deadline', key: 'review_due_at', render: (row) => h(DeadlineChip, { value: row.review_due_at }) },
]

async function load() {
  declarations.value = await declarationsApi.list()
}

onMounted(() => load().catch((error) => message.error(extractApiError(error))))
</script>
