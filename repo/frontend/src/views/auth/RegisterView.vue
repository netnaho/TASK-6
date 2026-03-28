<template>
  <n-card class="section-card auth-card" title="Local participant registration">
    <n-form :model="form" label-placement="top" @submit.prevent="submit">
      <n-form-item label="Full name"><n-input v-model:value="form.full_name" /></n-form-item>
      <n-form-item label="Username"><n-input v-model:value="form.username" /></n-form-item>
      <n-form-item label="Optional email"><n-input v-model:value="form.email_optional" /></n-form-item>
      <n-form-item label="Password"><n-input v-model:value="form.password" type="password" show-password-on="click" /></n-form-item>
      <n-button attr-type="submit" type="primary" block :loading="loading">Create account</n-button>
    </n-form>
    <div style="margin-top:16px;" class="muted">Already registered? <router-link to="/login">Sign in</router-link></div>
  </n-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NCard, NForm, NFormItem, NInput, useMessage } from 'naive-ui'

import { authApi } from '@/api/auth'
import { extractApiError } from '@/api/client'

const router = useRouter()
const message = useMessage()
const loading = ref(false)
const form = reactive({ full_name: '', username: '', email_optional: '', password: '' })

async function submit() {
  loading.value = true
  try {
    await authApi.register(form)
    message.success('Registration complete. Sign in next.')
    await router.push('/login')
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
