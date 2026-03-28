<template>
  <div class="page-shell">
    <PageHeader eyebrow="SYSTEM SETTINGS" title="Local runtime controls" description="Adjust offline CAPTCHA, secure link expiry, notification retention, and review SLA defaults for this local deployment." />
    <n-card class="section-card" title="Settings">
      <n-form :model="form" label-placement="top">
        <div class="responsive-two">
          <n-form-item label="Enable local CAPTCHA"><n-switch v-model:value="form.enable_local_captcha" /></n-form-item>
          <n-form-item label="Default download expiry (hours)"><n-input-number v-model:value="form.default_download_expiry_hours" style="width:100%" /></n-form-item>
        </div>
        <div class="responsive-two">
          <n-form-item label="Notification retention days"><n-input-number v-model:value="form.notifications_retention_days" style="width:100%" /></n-form-item>
          <n-form-item label="Review due hours"><n-input-number v-model:value="form.review_due_hours" style="width:100%" /></n-form-item>
        </div>
        <n-button type="primary" @click="save">Save settings</n-button>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { NButton, NCard, NForm, NFormItem, NInputNumber, NSwitch, useMessage } from 'naive-ui'

import { adminApi } from '@/api/admin'
import { extractApiError } from '@/api/client'
import PageHeader from '@/components/common/PageHeader.vue'

const message = useMessage()
const form = reactive<any>({ enable_local_captcha: true, default_download_expiry_hours: 72, notifications_retention_days: 90, review_due_hours: 72 })

onMounted(async () => {
  try {
    const settings = await adminApi.settings()
    settings.forEach((item: any) => {
      if (item.key in form) form[item.key] = item.value_json?.value
    })
  } catch (error) {
    message.error(extractApiError(error))
  }
})

async function save() {
  try {
    await adminApi.updateSettings(form)
    message.success('Settings updated.')
  } catch (error) {
    message.error(extractApiError(error))
  }
}
</script>
