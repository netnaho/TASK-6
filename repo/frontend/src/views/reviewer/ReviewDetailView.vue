<template>
  <div class="page-shell">
    <PageHeader eyebrow="REVIEW WORKSPACE" title="Reviewer package detail" description="Inspect package status, deadline, and corrections, then issue structured feedback with preserved version and workflow history." />
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

      <n-card class="section-card" title="Correction history">
        <n-timeline>
          <n-timeline-item v-for="item in corrections" :key="item.id" :title="item.status" :content="item.overall_message" :time="new Date(item.requested_at).toLocaleString()" />
        </n-timeline>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, NCard, NForm, NFormItem, NInput, NTimeline, NTimelineItem, useMessage } from 'naive-ui'

import { reviewsApi } from '@/api/reviews'
import { extractApiError } from '@/api/client'
import PageHeader from '@/components/common/PageHeader.vue'

const route = useRoute()
const message = useMessage()
const loading = ref(false)
const corrections = ref<any[]>([])
const form = reactive({ overall_message: '', sections_json: [{ section: 'plan', issue: '', required_action: '' }], response_due_hours: 72 })

const sectionsText = computed({
  get: () => JSON.stringify(form.sections_json, null, 2),
  set: (value: string) => {
    try { form.sections_json = JSON.parse(value) } catch { /* no-op */ }
  },
})

async function load() {
  corrections.value = await reviewsApi.corrections(String(route.params.packageId))
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
