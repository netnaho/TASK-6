<template>
  <article class="metric-card">
    <div class="tiny">{{ label }}</div>
    <div class="value">{{ value }}</div>
    <div class="muted">{{ hint }}</div>
  </article>
</template>

<script setup lang="ts">
defineProps<{ label: string; value: string | number; hint: string }>()
</script>

<style scoped>
.value {
  font-size: 2rem;
  font-weight: 700;
  margin: 8px 0;
}
</style>
