<template>
  <n-card class="section-card" title="Secure downloads">
    <div v-if="expired" class="expired">
      <strong>Link expired</strong>
      <p class="muted">This download link is no longer valid. Generate a new secure link to continue.</p>
    </div>
    <div v-else>
      <p class="muted">Create a time-bound file link for the selected delivery artifact.</p>
      <div style="display:flex; gap: 12px; flex-wrap: wrap;">
        <n-button v-if="allowCreate" type="primary" :loading="loading" @click="$emit('create')">Generate secure link</n-button>
        <n-button v-if="token" secondary @click="$emit('download')">Download</n-button>
        <n-button v-if="token && !accepted" type="success" @click="$emit('accept')">Accept delivery</n-button>
      </div>
      <div v-if="token" style="margin-top: 14px;">
        <n-alert type="success" title="Link ready">
          Download URL token: <code>{{ token }}</code>
          <div v-if="expiresAt" class="tiny" style="margin-top: 8px;">Expires {{ countdownLabel }}</div>
          <div v-if="accepted" class="tiny" style="margin-top: 8px; color: var(--text-strong);">Delivery accepted.</div>
        </n-alert>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NAlert, NButton, NCard } from 'naive-ui'

const props = defineProps<{ token?: string; expired?: boolean; loading?: boolean; expiresAt?: string; accepted?: boolean; allowCreate?: boolean }>()
defineEmits<{ create: []; download: []; accept: [] }>()

const countdownLabel = computed(() => {
  if (!props.expiresAt) return 'soon'
  const remainingMs = new Date(props.expiresAt).getTime() - Date.now()
  if (remainingMs <= 0) return 'now'
  const totalMinutes = Math.floor(remainingMs / 60000)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `in ${hours}h ${minutes}m`
})
</script>

<style scoped>
.expired {
  padding: 4px 0;
}
</style>
