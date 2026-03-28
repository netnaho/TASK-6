<template>
  <section class="hero-panel">
    <div class="tiny">{{ eyebrow }}</div>
    <div class="header-line">
      <div>
        <h1>{{ title }}</h1>
        <p>{{ description }}</p>
      </div>
      <div class="actions">
        <slot name="actions" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ eyebrow: string; title: string; description: string }>()
</script>

<style scoped>
h1 {
  margin: 8px 0 10px;
  font-size: clamp(1.8rem, 2.8vw, 2.7rem);
}

p {
  margin: 0;
  max-width: 760px;
  opacity: 0.92;
}

.header-line {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 720px) {
  .header-line {
    flex-direction: column;
  }
}
</style>
