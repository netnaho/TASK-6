<template>
  <div class="phase-grid">
    <n-card v-for="(phase, index) in phases" :key="index" class="section-card" :title="`Phase ${phase.phase_number}`">
      <div class="responsive-two">
        <n-form-item label="Week start"><n-input-number v-model:value="phase.week_start" style="width:100%" /></n-form-item>
        <n-form-item label="Week end"><n-input-number v-model:value="phase.week_end" style="width:100%" /></n-form-item>
      </div>
      <n-form-item label="Objective"><n-input v-model:value="phase.objective" type="textarea" :autosize="{ minRows: 3 }" /></n-form-item>
      <div class="responsive-two">
        <n-form-item label="Calorie target"><n-input-number v-model:value="phase.calorie_target" style="width:100%" /></n-form-item>
        <n-form-item label="Macro targets JSON"><n-input v-model:value="macroTexts[index]" type="textarea" :autosize="{ minRows: 3 }" /></n-form-item>
      </div>
      <n-button tertiary type="error" @click="$emit('remove', index)">Remove phase</n-button>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NButton, NCard, NFormItem, NInput, NInputNumber } from 'naive-ui'

const props = defineProps<{ phases: Array<Record<string, any>> }>()
defineEmits<{ remove: [index: number] }>()

const macroTexts = computed(() => props.phases.map((phase) => JSON.stringify(phase.macro_targets_json || {}, null, 2)))
</script>

<style scoped>
.phase-grid {
  display: grid;
  gap: 16px;
}
</style>
