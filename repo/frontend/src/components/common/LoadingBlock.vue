<template>
  <n-card class="section-card">
    <n-skeleton text :repeat="rows" />
  </n-card>
</template>

<script setup lang="ts">
import { NCard, NSkeleton } from 'naive-ui'

withDefaults(defineProps<{ rows?: number }>(), { rows: 4 })
</script>
