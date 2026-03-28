<template>
  <n-card class="section-card auth-card" title="Change your password">
    <p class="muted">An administrator reset your password. You must create a new password before continuing.</p>
    <n-form :model="form" label-placement="top" @submit.prevent="submit">
      <n-form-item label="New password"><n-input v-model:value="form.new_password" type="password" show-password-on="click" /></n-form-item>
      <n-button attr-type="submit" type="primary" block :loading="loading">Continue securely</n-button>
    </n-form>
  </n-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NCard, NForm, NFormItem, NInput, useMessage } from 'naive-ui'

import { extractApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const message = useMessage()
const form = reactive({ new_password: '' })
const loading = ref(false)

async function submit() {
  loading.value = true
  try {
    await auth.changeForcedPassword(form.new_password)
    message.success('Password updated.')
    await router.push(auth.role === 'participant' ? '/app/participant/dashboard' : auth.role === 'reviewer' ? '/app/reviewer/dashboard' : '/app/admin/dashboard')
  } catch (error) {
    message.error(extractApiError(error))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-card {
  max-width: 560px;
  margin: 0 auto;
}
</style>
