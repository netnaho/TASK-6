<template>
  <n-result status="error" title="We hit a loading issue" :description="message">
    <template #footer>
      <n-button type="primary" @click="$emit('retry')">Retry</n-button>
    </template>
  </n-result>
</template>

<script setup lang="ts">
import { NButton, NResult } from 'naive-ui'

defineProps<{ message: string }>()
defineEmits<{ retry: [] }>()
</script>
