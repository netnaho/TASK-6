<template>
  <n-result title="Access restricted" status="403" description="Your role does not have access to this area.">
    <template #footer>
      <n-button type="primary" @click="$router.back()">Go back</n-button>
    </template>
  </n-result>
</template>

<script setup lang="ts">
import { NButton, NResult } from 'naive-ui'
</script>
