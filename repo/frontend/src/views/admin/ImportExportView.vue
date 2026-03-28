<template>
  <div class="page-shell">
    <PageHeader eyebrow="IMPORT / EXPORT" title="Field mappings and masked exports" description="Manage admin-defined mappings, export masking policies, and generate real CSV or XLSX extracts against live backend data." />
    <div class="responsive-two">
      <n-card class="section-card" title="Create field mapping">
        <n-form :model="mappingForm" label-placement="top">
          <n-form-item label="Name"><n-input v-model:value="mappingForm.name" /></n-form-item>
          <div class="responsive-two">
            <n-form-item label="Entity type"><n-input v-model:value="mappingForm.entity_type" /></n-form-item>
            <n-form-item label="Format"><n-select v-model:value="mappingForm.format" :options="formatOptions" /></n-form-item>
          </div>
          <n-form-item label="Mapping JSON"><n-input v-model:value="mappingText" type="textarea" :autosize="{ minRows: 6 }" /></n-form-item>
          <n-button type="primary" @click="createMapping">Save mapping</n-button>
        </n-form>
      </n-card>

      <n-card class="section-card" title="Create masking policy">
        <n-form :model="policyForm" label-placement="top">
          <n-form-item label="Name"><n-input v-model:value="policyForm.name" /></n-form-item>
          <n-form-item label="Entity type"><n-input v-model:value="policyForm.entity_type" /></n-form-item>
          <n-form-item label="Rules JSON"><n-input v-model:value="policyText" type="textarea" :autosize="{ minRows: 6 }" /></n-form-item>
          <n-button type="primary" @click="createPolicy">Save policy</n-button>
        </n-form>
      </n-card>
    </div>

    <div class="responsive-two">
      <n-card class="section-card" title="Exports">
        <n-space vertical>
          <n-select v-model:value="selectedPolicy" :options="policyOptions" clearable placeholder="Optional masking policy" />
          <n-button type="primary" @click="runExport">Export declarations</n-button>
          <n-data-table :columns="exportColumns" :data="exportsRows" :bordered="false" />
        </n-space>
      </n-card>

      <n-card class="section-card" title="Current definitions">
        <n-tabs type="line" animated>
          <n-tab-pane name="mappings" tab="Field mappings"><n-data-table :columns="simpleColumns" :data="mappings" :bordered="false" /></n-tab-pane>
          <n-tab-pane name="policies" tab="Masking policies"><n-data-table :columns="simpleColumns" :data="policies" :bordered="false" /></n-tab-pane>
        </n-tabs>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { NButton, NCard, NDataTable, NForm, NFormItem, NInput, NSelect, NSpace, NTabPane, NTabs, useMessage } from 'naive-ui'

import { extractApiError } from '@/api/client'
import { importsExportsApi } from '@/api/importsExports'
import PageHeader from '@/components/common/PageHeader.vue'

const message = useMessage()
const mappings = ref<any[]>([])
const policies = ref<any[]>([])
const exportsRows = ref<any[]>([])
const selectedPolicy = ref<string | null>(null)
const formatOptions = [{ label: 'CSV', value: 'csv' }, { label: 'XLSX', value: 'xlsx' }]
const mappingForm = reactive<any>({ name: '', entity_type: 'declaration', format: 'csv', mapping_json: { package_number: 'Package Number', state: 'State' } })
const policyForm = reactive<any>({ name: '', entity_type: 'declaration', rules_json: { mask_fields: ['participant_id'] }, is_default: false })

const mappingText = computed({
  get: () => JSON.stringify(mappingForm.mapping_json, null, 2),
  set: (value: string) => { try { mappingForm.mapping_json = JSON.parse(value) } catch { /* ignore */ } },
})
const policyText = computed({
  get: () => JSON.stringify(policyForm.rules_json, null, 2),
  set: (value: string) => { try { policyForm.rules_json = JSON.parse(value) } catch { /* ignore */ } },
})
const policyOptions = computed(() => policies.value.map((item) => ({ label: item.name, value: item.id })))
const simpleColumns = [{ title: 'Name', key: 'name' }, { title: 'Entity', key: 'entity_type' }]
const exportColumns = [{ title: 'Format', key: 'job.format' }, { title: 'Path', key: 'storage_path' }]

async function load() {
  ;[mappings.value, policies.value, exportsRows.value] = await Promise.all([
    importsExportsApi.fieldMappings(),
    importsExportsApi.maskingPolicies(),
    importsExportsApi.exports(),
  ])
}

async function createMapping() {
  try { await importsExportsApi.createFieldMapping(mappingForm); message.success('Mapping saved.'); await load() } catch (error) { message.error(extractApiError(error)) }
}
async function createPolicy() {
  try { await importsExportsApi.createMaskingPolicy(policyForm); message.success('Masking policy saved.'); await load() } catch (error) { message.error(extractApiError(error)) }
}
async function runExport() {
  try {
    const result = await importsExportsApi.createExport({ format: 'csv', scope_type: 'declarations', masking_policy_id: selectedPolicy.value })
    exportsRows.value = [result, ...exportsRows.value]
    message.success('Export created successfully.')
  } catch (error) {
    message.error(extractApiError(error))
  }
}

onMounted(() => load().catch((error) => message.error(extractApiError(error))))
</script>
