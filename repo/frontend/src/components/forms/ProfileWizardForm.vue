<template>
  <n-card class="section-card" title="Guided health profile">
    <n-steps :current="currentStep" size="small">
      <n-step title="Demographics" />
      <n-step title="Medical context" />
      <n-step title="Activity" />
      <n-step title="Sensitive notes" />
    </n-steps>

    <div style="height: 20px" />

    <n-form :model="model" label-placement="top">
      <template v-if="currentStep === 1">
        <div class="responsive-two">
          <n-form-item label="Age"><n-input-number v-model:value="model.demographics_json.age" style="width:100%" /></n-form-item>
          <n-form-item label="Gender"><n-input v-model:value="model.demographics_json.gender" /></n-form-item>
        </div>
      </template>

      <template v-else-if="currentStep === 2">
        <div class="responsive-two">
          <n-form-item label="Medical flags JSON"><n-input v-model:value="medicalFlagsText" type="textarea" :autosize="{ minRows: 4 }" /></n-form-item>
          <n-form-item label="Profile status"><n-input v-model:value="model.profile_status" /></n-form-item>
        </div>
      </template>

      <template v-else-if="currentStep === 3">
        <div class="responsive-two">
          <n-form-item label="Activity level"><n-input v-model:value="model.activity_json.activity_level" /></n-form-item>
          <n-form-item label="Anthropometrics JSON"><n-input v-model:value="anthropometricsText" type="textarea" :autosize="{ minRows: 4 }" /></n-form-item>
        </div>
      </template>

      <template v-else>
        <div class="responsive-two">
          <n-form-item label="Allergy detail"><n-input v-model:value="model.sensitive.allergy_detail" type="textarea" :autosize="{ minRows: 4 }" /></n-form-item>
          <n-form-item label="Clinician notes"><n-input v-model:value="model.sensitive.clinician_notes" type="textarea" :autosize="{ minRows: 4 }" /></n-form-item>
        </div>
      </template>
    </n-form>

    <div style="display:flex; justify-content:space-between; margin-top: 18px; gap: 12px;">
      <n-button secondary :disabled="currentStep === 1" @click="currentStep -= 1">Back</n-button>
      <div style="display:flex; gap: 12px;">
        <n-button v-if="currentStep < 4" type="primary" @click="nextStep">Next</n-button>
        <n-button v-else type="primary" :loading="saving" @click="submit">Save profile</n-button>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { NButton, NCard, NForm, NFormItem, NInput, NInputNumber, NStep, NSteps } from 'naive-ui'

const props = defineProps<{ modelValue: Record<string, any>; saving?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, any>]; submit: [] }>()

const currentStep = ref(1)
const model = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const medicalFlagsText = computed({
  get: () => JSON.stringify(model.value.medical_flags_json, null, 2),
  set: (value: string) => {
    try { model.value.medical_flags_json = JSON.parse(value || '{}') } catch { /* no-op */ }
  },
})

const anthropometricsText = computed({
  get: () => JSON.stringify(model.value.anthropometrics_json, null, 2),
  set: (value: string) => {
    try { model.value.anthropometrics_json = JSON.parse(value || '{}') } catch { /* no-op */ }
  },
})

function nextStep() {
  currentStep.value = Math.min(4, currentStep.value + 1)
}

function submit() {
  emit('submit')
}
</script>
