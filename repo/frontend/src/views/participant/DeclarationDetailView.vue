<template>
  <div class="page-shell">
    <PageHeader eyebrow="PACKAGE DETAIL" :title="declaration?.package_number || 'Declaration package'" description="Review current status, permitted lifecycle actions, secure deliveries, and every prior version that contributed to this compliance record." />

    <div v-if="declaration" class="responsive-two">
      <div class="page-shell">
        <n-card class="section-card" title="Current status">
          <div style="display:flex; gap:12px; flex-wrap:wrap; align-items:center; margin-bottom: 16px;">
            <StatusBadge :status="declaration.state" />
            <DeadlineChip :value="declaration.review_due_at" />
          </div>
          <DeclarationStateActions :status="declaration.state" :role="auth.role || 'participant'" @submit="submitPackage" @withdraw="withdrawPackage" @reopen="reopenPackage" @resubmit="resubmitFirstCorrection" @void="prepareVoidAction" />
          <div v-if="showAdminVoidForm" style="display:grid; gap:12px; margin-top:16px;">
            <n-alert type="error" title="Administrative lifecycle control">
              Voiding permanently closes this package for administrative reasons while preserving its audit history.
            </n-alert>
            <n-input v-model:value="voidReason" type="textarea" :autosize="{ minRows: 3 }" placeholder="Document why this package is being voided." />
            <div style="display:flex; gap:12px; flex-wrap:wrap;">
              <n-button type="error" :loading="voiding" :disabled="!voidReason.trim()" @click="voidPackage">Confirm void</n-button>
              <n-button secondary @click="cancelVoidAction">Cancel</n-button>
            </div>
          </div>
        </n-card>

        <n-card class="section-card" title="History timeline">
          <VersionTimeline :items="history.versions || []" />
        </n-card>

        <WhatChangedPanel v-if="history.versions?.[0]" :items="history.versions[0].change_summary_json" />

        <n-card v-if="corrections.length" class="section-card" title="Correction workflow">
          <n-timeline>
            <n-timeline-item v-for="item in corrections" :key="item.id" :title="item.status" :content="item.overall_message" :time="new Date(item.requested_at).toLocaleString()" />
          </n-timeline>
          <div v-if="activeCorrection" style="display:grid; gap:12px; margin-top: 16px;">
            <n-alert type="warning" title="Reviewer feedback">
              {{ activeCorrection.overall_message }}
            </n-alert>
            <n-button v-if="activeCorrection.status === 'open'" type="warning" @click="acknowledgeCorrection">Acknowledge &amp; Edit</n-button>
            <n-input v-if="correctionAcknowledged" v-model:value="resubmissionReason" type="textarea" :autosize="{ minRows: 4 }" placeholder="Describe the corrections you made before resubmitting." />
            <n-button v-if="correctionAcknowledged" type="primary" @click="resubmitCorrection">Resubmit</n-button>
          </div>
        </n-card>
      </div>

      <div class="page-shell">
        <DeliveryWorkspacePanel
          :package-id="declaration.id"
          :can-publish="auth.role === 'administrator'"
          :can-accept="auth.role === 'participant'"
          :accepted="deliveryAccepted"
          @accepted="load"
          @updated="load"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NAlert, NButton, NCard, NInput, NTimeline, NTimelineItem, useMessage } from 'naive-ui'

import { declarationsApi } from '@/api/declarations'
import { extractApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import DeadlineChip from '@/components/common/DeadlineChip.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import DeclarationStateActions from '@/components/declarations/DeclarationStateActions.vue'
import DeliveryWorkspacePanel from '@/components/deliveries/DeliveryWorkspacePanel.vue'
import VersionTimeline from '@/components/history/VersionTimeline.vue'
import WhatChangedPanel from '@/components/history/WhatChangedPanel.vue'

const route = useRoute()
const message = useMessage()
const auth = useAuthStore()
const declaration = ref<any | null>(null)
const history = ref<any>({ versions: [], state_history: [] })
const corrections = ref<any[]>([])
const deliveryAccepted = ref(false)
const correctionAcknowledged = ref(false)
const resubmissionReason = ref('')
const showAdminVoidForm = ref(false)
const voidReason = ref('')
const voiding = ref(false)

const activeCorrection = computed(() => corrections.value.find((item) => ['open', 'acknowledged', 'resubmitted'].includes(item.status)) || corrections.value[0] || null)

async function load() {
  const packageId = String(route.params.packageId)
  declaration.value = await declarationsApi.get(packageId)
  history.value = await declarationsApi.history(packageId)
  corrections.value = await declarationsApi.corrections(packageId).catch(() => [])
  deliveryAccepted.value = Boolean(declaration.value?.accepted_at)
  correctionAcknowledged.value = activeCorrection.value?.status === 'acknowledged'
}

async function submitPackage() {
  try { declaration.value = await declarationsApi.submit(String(route.params.packageId)); message.success('Package submitted.'); await load() } catch (error) { message.error(extractApiError(error)) }
}
async function withdrawPackage() {
  try { declaration.value = await declarationsApi.withdraw(String(route.params.packageId)); message.success('Package withdrawn.'); await load() } catch (error) { message.error(extractApiError(error)) }
}
async function reopenPackage() {
  try { declaration.value = await declarationsApi.reopen(String(route.params.packageId)); message.success('Draft reopened.'); await load() } catch (error) { message.error(extractApiError(error)) }
}
function prepareVoidAction() {
  showAdminVoidForm.value = true
}
function cancelVoidAction() {
  showAdminVoidForm.value = false
  voidReason.value = ''
}
async function voidPackage() {
  voiding.value = true
  try {
    declaration.value = await declarationsApi.void(String(route.params.packageId), { reason_text: voidReason.value })
    message.success('Declaration voided.')
    cancelVoidAction()
    await load()
  } catch (error) {
    message.error(extractApiError(error))
  } finally {
    voiding.value = false
  }
}
async function resubmitFirstCorrection() {
  if (!activeCorrection.value) return message.warning('No correction request is available from this screen.')
  correctionAcknowledged.value = true
}

async function acknowledgeCorrection() {
  if (!activeCorrection.value) return
  try {
    await declarationsApi.acknowledge(String(route.params.packageId), activeCorrection.value.id, {})
    correctionAcknowledged.value = true
    message.success('Correction acknowledged. Update your changes and resubmit when ready.')
    await load()
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function resubmitCorrection() {
  if (!activeCorrection.value) return
  try {
    await declarationsApi.resubmit(String(route.params.packageId), activeCorrection.value.id, { reason_text: resubmissionReason.value })
    correctionAcknowledged.value = false
    resubmissionReason.value = ''
    message.success('Correction resubmitted successfully.')
    await load()
  } catch (error) {
    message.error(extractApiError(error))
  }
}

onMounted(() => load().catch((error) => message.error(extractApiError(error))))
</script>
