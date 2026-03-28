<template>
  <div class="page-shell">
    <PageHeader eyebrow="PARTICIPANT DASHBOARD" title="Your compliance workspace" description="Track your current declaration status, upcoming reviewer deadlines, delivery readiness, and required follow-up actions from one place." />

    <section class="metric-grid">
      <MetricCard label="Plans" :value="plans.length" hint="Nutrition plans in your workspace" />
      <MetricCard label="Declarations" :value="declarations.length" hint="Draft and submitted packages" />
      <MetricCard label="Pending actions" :value="correctedCount" hint="Corrections or acknowledgements needed" />
      <MetricCard label="Unread notices" :value="notifications.unreadCount" hint="Recent workflow changes" />
    </section>

    <div class="responsive-two">
      <n-card class="section-card" title="Current declarations">
        <n-data-table :columns="columns" :data="declarations.slice(0, 5)" :bordered="false" />
      </n-card>

      <n-card class="section-card" title="Mandatory updates">
        <n-list :bordered="false">
          <n-list-item v-for="item in mandatoryAlerts" :key="item.id">
            <div>
              <strong>{{ item.title }}</strong>
              <div class="muted">{{ item.message }}</div>
            </div>
          </n-list-item>
        </n-list>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { NCard, NDataTable, NList, NListItem, useMessage } from 'naive-ui'

import PageHeader from '@/components/common/PageHeader.vue'
import MetricCard from '@/components/common/MetricCard.vue'
import DeadlineChip from '@/components/common/DeadlineChip.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { declarationsApi } from '@/api/declarations'
import { notificationsApi } from '@/api/notifications'
import { plansApi } from '@/api/plans'
import { extractApiError } from '@/api/client'
import { useNotificationsStore } from '@/stores/notifications'

const message = useMessage()
const notifications = useNotificationsStore()
const declarations = ref<any[]>([])
const plans = ref<any[]>([])
const mandatoryAlerts = ref<any[]>([])

const correctedCount = computed(() => declarations.value.filter((item) => item.state === 'corrected').length)

const columns = [
  { title: 'Package', key: 'package_number', render: (row: any) => h(RouterLink, { to: `/app/participant/declarations/${row.id}` }, { default: () => row.package_number }) },
  { title: 'State', key: 'state', render: (row: any) => h(StatusBadge, { status: row.state }) },
  { title: 'Deadline', key: 'review_due_at', render: (row: any) => h(DeadlineChip, { value: row.review_due_at }) },
]

onMounted(async () => {
  try {
    ;[declarations.value, plans.value, mandatoryAlerts.value] = await Promise.all([
      declarationsApi.list(),
      plansApi.list(),
      notificationsApi.mandatoryAlerts(),
    ])
    notifications.fetchAll().catch(() => undefined)
  } catch (error) {
    message.error(extractApiError(error))
  }
})
</script>
