<template>
  <n-card class="section-card" title="What changed">
    <div v-if="items.length" class="change-list">
      <div v-for="change in items" :key="change.field" class="change-row">
        <div>
          <strong>{{ change.field }}</strong>
          <div class="tiny">{{ change.summary }}</div>
        </div>
        <div class="change-values">
          <div>
            <div class="tiny">Before</div>
            <span>{{ stringify(change.before) }}</span>
          </div>
          <div>
            <div class="tiny">After</div>
            <span>{{ stringify(change.after) }}</span>
          </div>
        </div>
      </div>
    </div>
    <n-empty v-else description="No tracked changes for this version." />
  </n-card>
</template>

<script setup lang="ts">
import { NCard, NEmpty } from 'naive-ui'

defineProps<{ items: Array<{ field: string; summary: string; before?: unknown; after?: unknown }> }>()

function stringify(value: unknown) {
  if (value == null || value === '') return 'None'
  return typeof value === 'object' ? JSON.stringify(value) : String(value)
}
</script>

<style scoped>
.change-list {
  display: grid;
  gap: 14px;
}

.change-row {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 16px;
  padding: 16px;
  border-radius: 18px;
  background: var(--surface-strong);
  border: 1px solid var(--line-soft);
}

.change-values {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

@media (max-width: 720px) {
  .change-row,
  .change-values {
    grid-template-columns: 1fr;
  }
}
</style>
