<template>
  <div style="display:flex; gap:12px; flex-wrap: wrap;">
    <n-button v-if="role === 'participant' && status === 'draft'" type="primary" @click="$emit('submit')">Submit package</n-button>
    <n-button v-if="role === 'participant' && status === 'submitted'" secondary @click="$emit('withdraw')">Withdraw</n-button>
    <n-button v-if="role === 'participant' && status === 'withdrawn'" secondary @click="$emit('reopen')">Reopen draft</n-button>
    <n-button v-if="role === 'participant' && status === 'corrected'" type="warning" @click="$emit('resubmit')">Resubmit correction</n-button>
    <n-button v-if="role === 'administrator' && status !== 'voided'" type="error" @click="$emit('void')">Void declaration</n-button>
  </div>
</template>

<script setup lang="ts">
import { NButton } from 'naive-ui'

defineProps<{ status: string; role: string }>()
defineEmits<{ submit: []; withdraw: []; reopen: []; resubmit: []; void: [] }>()
</script>
