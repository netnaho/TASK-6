<template>
  <div class="page-shell">
    <PageHeader eyebrow="REVIEW WORKSPACE" :title="reviewContext?.package.package_number || 'Reviewer package detail'" description="Inspect the submitted profile, linked plan, package history, delivery controls, and correction state before issuing structured review feedback." />
    <div class="responsive-two">
      <n-card class="section-card" title="Package context">
        <div v-if="reviewContext" class="detail-grid">
          <div>
            <div class="tiny">State</div>
            <strong>{{ reviewContext.package.state }}</strong>
          </div>
          <div>
            <div class="tiny">Review due</div>
            <strong>{{ formatTimestamp(reviewContext.package.review_due_at) }}</strong>
          </div>
          <div>
            <div class="tiny">Plan version</div>
            <strong>{{ latestVersion?.plan_version_id || 'Unavailable' }}</strong>
          </div>
          <div>
            <div class="tiny">Profile version</div>
            <strong>{{ latestVersion?.profile_version_id || 'Unavailable' }}</strong>
          </div>
        </div>
        <n-timeline style="margin-top: 18px;">
          <n-timeline-item v-for="item in reviewContext?.history.state_history || []" :key="item.id" :title="item.to_state" :content="item.reason_text || item.reason_code || 'State change recorded'" :time="formatTimestamp(item.changed_at)" />
        </n-timeline>
      </n-card>

      <DeliveryWorkspacePanel v-if="reviewContext" :package-id="reviewContext.package.id" can-publish @updated="load" />
    </div>

    <div class="responsive-two">
      <n-card class="section-card" title="Submitted profile snapshot">
        <div v-if="reviewContext?.profile_version" class="snapshot-grid">
          <div><div class="tiny">Version</div><strong>{{ reviewContext.profile_version.version_number }}</strong></div>
          <div><div class="tiny">Captured</div><strong>{{ formatTimestamp(reviewContext.profile_version.created_at) }}</strong></div>
          <pre class="snapshot-block">{{ formatJson(reviewContext.profile_version.snapshot_json) }}</pre>
        </div>
        <n-alert v-else type="warning" title="Profile snapshot unavailable">The package does not have a submitted profile snapshot.</n-alert>
      </n-card>

      <n-card class="section-card" title="Submitted plan snapshot">
        <div v-if="reviewContext?.plan_version" class="snapshot-grid">
          <div><div class="tiny">Version</div><strong>{{ reviewContext.plan_version.version_number }}</strong></div>
          <div><div class="tiny">Captured</div><strong>{{ formatTimestamp(reviewContext.plan_version.created_at) }}</strong></div>
          <pre class="snapshot-block">{{ formatJson(reviewContext.plan_version.snapshot_json) }}</pre>
        </div>
        <n-alert v-else type="warning" title="Plan snapshot unavailable">The package does not have a submitted plan snapshot.</n-alert>
      </n-card>
    </div>

    <div class="responsive-two">
      <n-card class="section-card" title="Linked package history">
        <VersionTimeline :items="reviewContext?.history.versions || []" />
      </n-card>

      <n-card class="section-card" title="Correction history">
        <n-timeline>
          <n-timeline-item v-for="item in corrections" :key="item.id" :title="item.status" :content="item.overall_message" :time="formatTimestamp(item.requested_at)" />
        </n-timeline>
      </n-card>
    </div>

    <WhatChangedPanel v-if="reviewContext?.history.versions?.[0]" :items="reviewContext.history.versions[0].change_summary_json" />

    <div class="responsive-two">
      <n-card class="section-card" title="Correction request">
        <n-form :model="form" label-placement="top">
          <n-form-item label="Overall message"><n-input v-model:value="form.overall_message" type="textarea" :autosize="{ minRows: 4 }" /></n-form-item>
          <n-form-item label="Sections JSON"><n-input v-model:value="sectionsText" type="textarea" :autosize="{ minRows: 8 }" /></n-form-item>
        </n-form>
        <div style="display:flex; gap:12px;">
          <n-button type="warning" :loading="loading" @click="submitCorrection">Request correction</n-button>
          <n-button secondary @click="completeReview">Mark review complete</n-button>
        </div>
      </n-card>

      <n-card class="section-card" title="Current reviewer guidance">
        <n-alert type="info" title="Review context">
          Use the linked version timeline and delivery controls before closing the review. Secure links can be issued either for the participant or for your own verification session from the delivery workspace.
        </n-alert>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NAlert, NButton, NCard, NForm, NFormItem, NInput, NTimeline, NTimelineItem, useMessage } from 'naive-ui'

import { reviewsApi } from '@/api/reviews'
import { extractApiError } from '@/api/client'
import DeliveryWorkspacePanel from '@/components/deliveries/DeliveryWorkspacePanel.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import VersionTimeline from '@/components/history/VersionTimeline.vue'
import WhatChangedPanel from '@/components/history/WhatChangedPanel.vue'
import type { ReviewContext } from '@/types/domain'

const route = useRoute()
const message = useMessage()
const loading = ref(false)
const reviewContext = ref<ReviewContext | null>(null)
const corrections = ref<any[]>([])
const form = reactive({ overall_message: '', sections_json: [{ section: 'plan', issue: '', required_action: '' }], response_due_hours: 72 })
const latestVersion = computed(() => reviewContext.value?.history?.versions?.[0] || null)

const sectionsText = computed({
  get: () => JSON.stringify(form.sections_json, null, 2),
  set: (value: string) => {
    try { form.sections_json = JSON.parse(value) } catch { /* no-op */ }
  },
})

async function load() {
  const packageId = String(route.params.packageId)
  reviewContext.value = await reviewsApi.context(packageId)
  corrections.value = reviewContext.value.corrections
}

function formatJson(value: unknown) {
  return JSON.stringify(value, null, 2)
}

function formatTimestamp(value?: string | null) {
  if (!value) return 'Not scheduled'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function submitCorrection() {
  loading.value = true
  try {
    await reviewsApi.requestCorrection(String(route.params.packageId), form)
    message.success('Correction issued.')
    await load()
  } catch (error) {
    message.error(extractApiError(error))
  } finally {
    loading.value = false
  }
}

async function completeReview() {
  try {
    await reviewsApi.complete(String(route.params.packageId), { note: 'Review completed in UI' })
    message.success('Review marked complete.')
  } catch (error) {
    message.error(extractApiError(error))
  }
}

onMounted(() => load().catch((error) => message.error(extractApiError(error))))
</script>

<style scoped>
.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.snapshot-grid {
  display: grid;
  gap: 12px;
}

.snapshot-block {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  border-radius: 16px;
  padding: 16px;
  background: var(--surface-strong);
  border: 1px solid var(--line-soft);
}
</style>
