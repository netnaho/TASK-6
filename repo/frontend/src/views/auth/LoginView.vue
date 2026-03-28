<template>
  <n-card class="section-card auth-card" title="Sign in">
    <p class="muted">Use your offline username and password. Session refresh stays local to this deployment.</p>
    <n-alert v-if="error" type="error" :title="error" style="margin-bottom: 16px" />
    <n-form :model="form" label-placement="top" @submit.prevent="submit">
      <n-form-item label="Username"><n-input v-model:value="form.username" placeholder="participant_demo" /></n-form-item>
      <n-form-item label="Password"><n-input v-model:value="form.password" type="password" show-password-on="click" /></n-form-item>
      <template v-if="captcha?.challenge_token">
        <n-alert type="info" style="margin-bottom: 16px" :title="captcha.prompt" />
        <n-form-item label="CAPTCHA answer"><n-input v-model:value="form.captcha_answer" /></n-form-item>
      </template>
      <n-button attr-type="submit" type="primary" block :loading="loading">Sign in</n-button>
    </n-form>
    <div style="margin-top:16px;" class="muted">
      Need an account? <router-link to="/register">Register locally</router-link>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NForm, NFormItem, NInput, useMessage } from 'naive-ui'

import { authApi } from '@/api/auth'
import { extractApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const message = useMessage()
const loading = ref(false)
const error = ref('')
const captcha = ref<{ prompt: string; challenge_token: string } | null>(null)
const form = reactive({ username: '', password: '', captcha_answer: '' })

authApi.captcha().then((data) => {
  if (data.challenge_token) captcha.value = { prompt: data.prompt, challenge_token: data.challenge_token }
}).catch(() => undefined)

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login({ ...form, captcha_challenge_token: captcha.value?.challenge_token })
    message.success('Welcome back.')
    await router.push(auth.role === 'participant' ? '/app/participant/dashboard' : auth.role === 'reviewer' ? '/app/reviewer/dashboard' : '/app/admin/dashboard')
  } catch (err) {
    error.value = extractApiError(err)
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
