<template>
  <n-result title="Page not found" status="404" description="This route does not exist in the current workspace.">
    <template #footer><n-button type="primary" @click="$router.push('/login')">Go home</n-button></template>
  </n-result>
</template>

<script setup lang="ts">
import { NButton, NResult } from 'naive-ui'
</script>
