<template>
  <div class="page-shell">
    <PageHeader eyebrow="DECLARATION PACKAGES" title="Declaration lifecycle" description="Create draft packages from current profile and plan versions, then submit, withdraw, or track corrections with full audit-ready history." />
    <n-card class="section-card" title="Create new draft">
      <div class="responsive-three">
        <n-select v-model:value="selectedProfileId" :options="profileOptions" placeholder="Select profile" />
        <n-select v-model:value="selectedPlanId" :options="planOptions" placeholder="Select plan" />
        <n-button type="primary" :disabled="!selectedProfileId || !selectedPlanId" @click="createPackage">Create draft</n-button>
      </div>
    </n-card>
    <n-card class="section-card">
      <n-data-table :columns="columns" :data="declarations" :bordered="false" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { NButton, NCard, NDataTable, NSelect, useMessage } from 'naive-ui'

import { declarationsApi } from '@/api/declarations'
import { plansApi } from '@/api/plans'
import { profilesApi } from '@/api/profiles'
import { extractApiError } from '@/api/client'
import DeadlineChip from '@/components/common/DeadlineChip.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'

const message = useMessage()
const declarations = ref<any[]>([])
const plans = ref<any[]>([])
const selectedProfileId = ref<string | null>(null)
const selectedPlanId = ref<string | null>(null)
const profile = ref<any | null>(null)

const profileOptions = computed(() => profile.value ? [{ label: `Current profile (${profile.value.profile_status})`, value: profile.value.id }] : [])
const planOptions = computed(() => plans.value.map((plan) => ({ label: plan.title, value: plan.id })))

const columns = [
  { title: 'Package', key: 'package_number', render: (row: any) => h(RouterLink, { to: `/app/participant/declarations/${row.id}` }, { default: () => row.package_number }) },
  { title: 'State', key: 'state', render: (row: any) => h(StatusBadge, { status: row.state }) },
  { title: 'Deadline', key: 'review_due_at', render: (row: any) => h(DeadlineChip, { value: row.review_due_at }) },
]

async function load() {
  ;[declarations.value, plans.value] = await Promise.all([declarationsApi.list(), plansApi.list()])
  profile.value = await profilesApi.getMine().catch(() => null)
  selectedProfileId.value = profile.value?.id || null
}

async function createPackage() {
  try {
    const created = await declarationsApi.create({ profile_id: selectedProfileId.value, plan_id: selectedPlanId.value })
    message.success('Declaration draft created.')
    declarations.value.unshift(created)
  } catch (error) {
    message.error(extractApiError(error))
  }
}

onMounted(() => load().catch((error) => message.error(extractApiError(error))))
</script>
