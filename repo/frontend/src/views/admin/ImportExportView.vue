<template>
  <div class="page-shell">
    <PageHeader eyebrow="IMPORT / EXPORT" title="Field mappings and masked transfers" description="Upload admin imports, generate masked exports, inspect job detail, and retrieve artifacts only through secure expiring download links." />
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
      <n-card class="section-card" title="Imports">
        <n-space vertical>
          <n-select v-model:value="importForm.format" :options="formatOptions" placeholder="Import format" />
          <n-select v-model:value="importForm.scope_type" :options="scopeOptions" placeholder="Import scope" />
          <n-select v-model:value="importForm.mapping_id" :options="mappingOptions" clearable placeholder="Optional field mapping" />
          <input ref="importFileInput" type="file" @change="handleImportFileChange" />
          <n-button type="primary" :loading="importLoading" @click="runImport">Run import</n-button>
          <n-data-table :columns="importColumns" :data="importsRows" :bordered="false" />
        </n-space>
      </n-card>

      <n-card class="section-card" title="Exports">
        <n-space vertical>
          <n-select v-model:value="exportForm.format" :options="formatOptions" placeholder="Export format" />
          <n-select v-model:value="exportForm.scope_type" :options="scopeOptions" placeholder="Export scope" />
          <n-select v-model:value="selectedPolicy" :options="policyOptions" clearable placeholder="Optional masking policy" />
          <n-button type="primary" :loading="exportLoading" @click="runExport">Generate export</n-button>
          <n-data-table :columns="exportColumns" :data="exportsRows" :bordered="false" />
        </n-space>
      </n-card>
    </div>

    <div class="responsive-two">
      <n-card class="section-card" title="Selected import job">
        <div v-if="selectedImportDetail" class="job-detail-grid">
          <div><div class="tiny">Format</div><strong>{{ selectedImportDetail.job.format }}</strong></div>
          <div><div class="tiny">Rows</div><strong>{{ selectedImportDetail.job.row_count }}</strong></div>
          <div><div class="tiny">Succeeded</div><strong>{{ selectedImportDetail.job.success_count }}</strong></div>
          <div><div class="tiny">Failed</div><strong>{{ selectedImportDetail.job.failure_count }}</strong></div>
          <div><div class="tiny">Source file</div><strong>{{ selectedImportDetail.source_file?.display_name || 'Unavailable' }}</strong></div>
          <div><div class="tiny">Checksum</div><strong>{{ selectedImportDetail.job.checksum_sha256 || 'Unavailable' }}</strong></div>
          <n-alert v-if="selectedImportDetail.errors.length" type="warning" title="Import row errors">
            {{ selectedImportDetail.errors.map((item) => `Row ${item.row}: ${item.error}`).join(' | ') }}
          </n-alert>
          <n-data-table v-if="selectedImportDetail.preview_rows.length" :columns="previewColumns(selectedImportDetail.preview_rows)" :data="selectedImportDetail.preview_rows" :bordered="false" />
          <n-button secondary @click="downloadImportSource">Download source with secure link</n-button>
        </div>
        <n-empty v-else description="Select an import job to inspect secure-download detail." />
      </n-card>

      <n-card class="section-card" title="Selected export job">
        <div v-if="selectedExportDetail" class="job-detail-grid">
          <div><div class="tiny">Format</div><strong>{{ selectedExportDetail.job.format }}</strong></div>
          <div><div class="tiny">Scope</div><strong>{{ selectedExportDetail.job.scope_type }}</strong></div>
          <div><div class="tiny">Rows</div><strong>{{ selectedExportDetail.job.row_count }}</strong></div>
          <div><div class="tiny">Checksum</div><strong>{{ selectedExportDetail.job.checksum_sha256 || 'Unavailable' }}</strong></div>
          <div><div class="tiny">Artifact</div><strong>{{ selectedExportDetail.output_file?.display_name || 'Unavailable' }}</strong></div>
          <div><div class="tiny">Generated</div><strong>{{ selectedExportDetail.job.completed_at || selectedExportDetail.job.created_at }}</strong></div>
          <n-data-table v-if="selectedExportDetail.preview_rows.length" :columns="previewColumns(selectedExportDetail.preview_rows)" :data="selectedExportDetail.preview_rows" :bordered="false" />
          <n-button secondary @click="downloadExportArtifact">Download export with secure link</n-button>
        </div>
        <n-empty v-else description="Select an export job to inspect secure-download detail." />
      </n-card>
    </div>

    <n-card class="section-card" title="Current definitions">
      <n-tabs type="line" animated>
        <n-tab-pane name="mappings" tab="Field mappings"><n-data-table :columns="simpleColumns" :data="mappings" :bordered="false" /></n-tab-pane>
        <n-tab-pane name="policies" tab="Masking policies"><n-data-table :columns="simpleColumns" :data="policies" :bordered="false" /></n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue'
import { NAlert, NButton, NCard, NDataTable, NEmpty, NForm, NFormItem, NInput, NSelect, NSpace, NTabPane, NTabs, useMessage } from 'naive-ui'

import { extractApiError } from '@/api/client'
import { deliveriesApi } from '@/api/deliveries'
import { importsExportsApi } from '@/api/importsExports'
import PageHeader from '@/components/common/PageHeader.vue'
import { useAuthStore } from '@/stores/auth'
import type { ExportJobDetail, ExportJobRecord, ImportJobDetail, ImportJobRecord } from '@/types/domain'

const auth = useAuthStore()
const message = useMessage()
const mappings = ref<any[]>([])
const policies = ref<any[]>([])
const importsRows = ref<ImportJobRecord[]>([])
const exportsRows = ref<ExportJobRecord[]>([])
const selectedImportDetail = ref<ImportJobDetail | null>(null)
const selectedExportDetail = ref<ExportJobDetail | null>(null)
const selectedPolicy = ref<string | null>(null)
const importFileInput = ref<HTMLInputElement | null>(null)
const pendingImportFile = ref<File | null>(null)
const importLoading = ref(false)
const exportLoading = ref(false)
const formatOptions = [{ label: 'CSV', value: 'csv' }, { label: 'XLSX', value: 'xlsx' }]
const scopeOptions = [{ label: 'Declarations', value: 'declarations' }, { label: 'Profiles', value: 'profiles' }]
const mappingForm = reactive<any>({ name: '', entity_type: 'declaration', format: 'csv', mapping_json: { package_number: 'Package Number', state: 'State' } })
const policyForm = reactive<any>({ name: '', entity_type: 'declaration', rules_json: { mask_fields: ['participant_id'] }, is_default: false })
const importForm = reactive({ format: 'csv', scope_type: 'declarations', mapping_id: null as string | null })
const exportForm = reactive({ format: 'csv', scope_type: 'declarations' })

const mappingText = computed({
  get: () => JSON.stringify(mappingForm.mapping_json, null, 2),
  set: (value: string) => { try { mappingForm.mapping_json = JSON.parse(value) } catch { /* ignore */ } },
})
const policyText = computed({
  get: () => JSON.stringify(policyForm.rules_json, null, 2),
  set: (value: string) => { try { policyForm.rules_json = JSON.parse(value) } catch { /* ignore */ } },
})
const policyOptions = computed(() => policies.value.map((item) => ({ label: item.name, value: item.id })))
const mappingOptions = computed(() => mappings.value.map((item) => ({ label: item.name, value: item.id })))
const simpleColumns = [{ title: 'Name', key: 'name' }, { title: 'Entity', key: 'entity_type' }]
const importColumns = [
  { title: 'Format', key: 'format' },
  { title: 'Rows', key: 'row_count' },
  { title: 'Succeeded', key: 'success_count' },
  { title: 'Failed', key: 'failure_count' },
  {
    title: 'Action',
    key: 'action',
    render: (row: ImportJobRecord) => h(NButton, { size: 'small', secondary: true, onClick: () => inspectImport(row.id) }, { default: () => 'Inspect' }),
  },
]
const exportColumns = [
  { title: 'Format', key: 'format' },
  { title: 'Scope', key: 'scope_type' },
  { title: 'Rows', key: 'row_count' },
  {
    title: 'Action',
    key: 'action',
    render: (row: ExportJobRecord) => h(NButton, { size: 'small', secondary: true, onClick: () => inspectExport(row.id) }, { default: () => 'Inspect' }),
  },
]

async function load() {
  ;[mappings.value, policies.value, importsRows.value, exportsRows.value] = await Promise.all([
    importsExportsApi.fieldMappings(),
    importsExportsApi.maskingPolicies(),
    importsExportsApi.imports(),
    importsExportsApi.exports(),
  ])
}

function handleImportFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  pendingImportFile.value = input.files?.[0] || null
}

function previewColumns(rows: Array<Record<string, unknown>>) {
  const firstRow = rows[0]
  if (!firstRow) return []
  return Object.keys(firstRow).map((key) => ({
    title: key,
    key,
    render: (row: Record<string, unknown>) => typeof row[key] === 'object' ? JSON.stringify(row[key]) : String(row[key] ?? ''),
  }))
}

async function inspectImport(jobId: string) {
  try {
    selectedImportDetail.value = await importsExportsApi.importDetail(jobId)
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function inspectExport(jobId: string) {
  try {
    selectedExportDetail.value = await importsExportsApi.exportDetail(jobId)
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function downloadByToken(token: string, fallbackName: string) {
  if (!auth.accessToken) return
  const response = await deliveriesApi.downloadByToken(token, auth.accessToken)
  const blob = new Blob([response.data], { type: response.headers['content-type'] || 'application/octet-stream' })
  const href = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = href
  link.download = fallbackName
  link.click()
  URL.revokeObjectURL(href)
}

async function createMapping() {
  try { await importsExportsApi.createFieldMapping(mappingForm); message.success('Mapping saved.'); await load() } catch (error) { message.error(extractApiError(error)) }
}
async function createPolicy() {
  try { await importsExportsApi.createMaskingPolicy(policyForm); message.success('Masking policy saved.'); await load() } catch (error) { message.error(extractApiError(error)) }
}
async function runImport() {
  if (!pendingImportFile.value) {
    message.warning('Choose a CSV or XLSX file first.')
    return
  }
  importLoading.value = true
  try {
    const result = await importsExportsApi.createImport({ ...importForm, upload: pendingImportFile.value })
    if (importFileInput.value) importFileInput.value.value = ''
    pendingImportFile.value = null
    message.success('Import created successfully.')
    await load()
    await inspectImport(result.id)
  } catch (error) {
    message.error(extractApiError(error))
  } finally {
    importLoading.value = false
  }
}
async function runExport() {
  exportLoading.value = true
  try {
    const result = await importsExportsApi.createExport({ format: exportForm.format, scope_type: exportForm.scope_type, masking_policy_id: selectedPolicy.value })
    message.success('Export created successfully.')
    await load()
    await inspectExport(result.id)
  } catch (error) {
    message.error(extractApiError(error))
  } finally {
    exportLoading.value = false
  }
}

async function downloadImportSource() {
  if (!selectedImportDetail.value?.job.id) return
  try {
    const link = await importsExportsApi.createImportDownloadLink(selectedImportDetail.value.job.id)
    await downloadByToken(link.token, selectedImportDetail.value.source_file?.display_name || 'import-source')
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function downloadExportArtifact() {
  if (!selectedExportDetail.value?.job.id) return
  try {
    const link = await importsExportsApi.createExportDownloadLink(selectedExportDetail.value.job.id)
    await downloadByToken(link.token, selectedExportDetail.value.output_file?.display_name || 'export-artifact')
  } catch (error) {
    message.error(extractApiError(error))
  }
}

onMounted(() => load().catch((error) => message.error(extractApiError(error))))
</script>

<style scoped>
.job-detail-grid {
  display: grid;
  gap: 14px;
}
</style>
