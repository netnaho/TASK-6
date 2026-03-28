<template>
  <div class="page-shell">
    <PageHeader eyebrow="PLAN BUILDER" :title="isEdit ? 'Edit nutrition plan' : 'Create nutrition plan'" description="Build a 12-week style phased program with measurable objectives, calorie targets, macro guidance, and versioned plan history." />
    <div class="responsive-two">
      <n-card class="section-card" title="Plan details">
        <n-form :model="form" label-placement="top">
          <div class="responsive-two">
            <n-form-item label="Title"><n-input v-model:value="form.title" /></n-form-item>
            <n-form-item label="Goal category"><n-input v-model:value="form.goal_category" /></n-form-item>
          </div>
          <div class="responsive-two">
            <n-form-item label="Duration weeks"><n-input-number v-model:value="form.duration_weeks" style="width:100%" /></n-form-item>
            <n-form-item label="Summary"><n-input v-model:value="form.summary" /></n-form-item>
          </div>
        </n-form>
        <n-button tertiary @click="addPhase">Add phase</n-button>
        <div style="height: 12px" />
        <PlanPhaseEditor :phases="form.phases" @remove="removePhase" />
        <div style="height: 16px" />
        <n-button type="primary" :loading="saving" @click="savePlan">{{ isEdit ? 'Save new version' : 'Create plan' }}</n-button>
      </n-card>

      <div class="page-shell">
        <VersionTimeline :items="versions" />
        <WhatChangedPanel v-if="versions[0]" :items="versions[0].change_summary_json" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NCard, NForm, NFormItem, NInput, NInputNumber, useMessage } from 'naive-ui'

import { plansApi } from '@/api/plans'
import { extractApiError } from '@/api/client'
import PageHeader from '@/components/common/PageHeader.vue'
import WhatChangedPanel from '@/components/history/WhatChangedPanel.vue'
import VersionTimeline from '@/components/history/VersionTimeline.vue'
import PlanPhaseEditor from '@/components/plans/PlanPhaseEditor.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const saving = ref(false)
const versions = ref<any[]>([])
const isEdit = computed(() => Boolean(route.params.planId))
const form = reactive<any>({ title: '', duration_weeks: 12, goal_category: '', summary: '', phases: [] })

function addPhase() {
  form.phases.push({ phase_number: form.phases.length + 1, week_start: 1, week_end: 4, objective: '', calorie_target: null, macro_targets_json: {}, habits_json: [], success_metrics_json: [] })
}

function removePhase(index: number) {
  form.phases.splice(index, 1)
}

async function load() {
  if (!isEdit.value) {
    if (!form.phases.length) addPhase()
    return
  }
  try {
    const plan = await plansApi.get(String(route.params.planId))
    Object.assign(form, plan)
    versions.value = await plansApi.versions(String(route.params.planId))
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function savePlan() {
  saving.value = true
  try {
    const response = isEdit.value ? await plansApi.update(String(route.params.planId), form) : await plansApi.create(form)
    message.success(isEdit.value ? 'Plan version saved.' : 'Plan created.')
    await router.push(`/app/participant/plans/${response.id}`)
  } catch (error) {
    message.error(extractApiError(error))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
