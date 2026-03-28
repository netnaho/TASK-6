<template>
  <div class="empty-state section-card">
    <h3>{{ title }}</h3>
    <p class="muted">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; description: string }>()
</script>

<style scoped>
.empty-state {
  padding: 26px;
  text-align: center;
}

h3 {
  margin: 0 0 8px;
}
</style>
