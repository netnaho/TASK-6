<template>
  <div class="page-shell">
    <PageHeader eyebrow="ADMINISTRATOR DASHBOARD" title="Compliance operations overview" description="Monitor account controls, audit activity, import-export tooling, and operational configuration for this offline compliance deployment." />
    <section class="metric-grid">
      <MetricCard label="Users" :value="users.length" hint="Accounts across all roles" />
      <MetricCard label="Audit entries" :value="auditLogs.length" hint="Immutable critical events" />
      <MetricCard label="Disabled accounts" :value="disabledCount" hint="Access suspended by admins" />
      <MetricCard label="Config items" :value="settings.length" hint="Local runtime controls" />
    </section>
    <div class="responsive-two">
      <n-card class="section-card" title="Recent audit events">
        <n-timeline>
          <n-timeline-item v-for="item in auditLogs.slice(0, 6)" :key="item.id" :title="item.action_type" :content="`${item.entity_type} ${item.entity_id}`" :time="new Date(item.occurred_at).toLocaleString()" />
        </n-timeline>
      </n-card>
      <n-card class="section-card" title="Operational posture">
        <n-list>
          <n-list-item v-for="item in settings" :key="item.id">{{ item.key }}: {{ item.value_json?.value }}</n-list-item>
        </n-list>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { NCard, NList, NListItem, NTimeline, NTimelineItem, useMessage } from 'naive-ui'

import { adminApi } from '@/api/admin'
import { extractApiError } from '@/api/client'
import MetricCard from '@/components/common/MetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'

const message = useMessage()
const users = ref<any[]>([])
const auditLogs = ref<any[]>([])
const settings = ref<any[]>([])
const disabledCount = computed(() => users.value.filter((item) => item.status === 'disabled' || !item.is_active).length)

onMounted(async () => {
  try {
    ;[users.value, auditLogs.value, settings.value] = await Promise.all([adminApi.users(), adminApi.audit(), adminApi.settings()])
  } catch (error) {
    message.error(extractApiError(error))
  }
})
</script>
