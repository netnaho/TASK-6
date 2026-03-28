<template>
  <div class="page-shell">
    <PageHeader eyebrow="GUIDED PROFILE" title="Health profile" description="Capture structured health context with sensitive notes protected at rest and full version tracking for every material change." />
    <div class="responsive-two">
      <ProfileWizardForm v-model:model-value="form" :saving="saving" @submit="save" />
      <div class="page-shell">
        <VersionTimeline :items="history" />
        <WhatChangedPanel v-if="selectedVersion" :items="selectedVersion.change_summary_json" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useMessage } from 'naive-ui'

import { profilesApi } from '@/api/profiles'
import { extractApiError } from '@/api/client'
import PageHeader from '@/components/common/PageHeader.vue'
import ProfileWizardForm from '@/components/forms/ProfileWizardForm.vue'
import VersionTimeline from '@/components/history/VersionTimeline.vue'
import WhatChangedPanel from '@/components/history/WhatChangedPanel.vue'

const message = useMessage()
const saving = ref(false)
const history = ref<any[]>([])
const selectedVersion = ref<any | null>(null)
const form = reactive<any>({
  profile_status: 'in_progress',
  demographics_json: {},
  medical_flags_json: {},
  activity_json: {},
  anthropometrics_json: {},
  sensitive: {},
})

async function load() {
  try {
    const profile = await profilesApi.getMine().catch(() => null)
    if (profile) Object.assign(form, profile)
    history.value = await profilesApi.history()
    selectedVersion.value = history.value[0] || null
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function save() {
  saving.value = true
  try {
    await profilesApi.update(form)
    message.success('Profile saved with new version.')
    await load()
  } catch (error) {
    message.error(extractApiError(error))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
