<script setup lang="ts">
import { computed, h, onMounted, reactive, ref } from 'vue'
import { NAlert, NButton, NCard, NCheckbox, NCheckboxGroup, NDataTable, NForm, NFormItem, NSelect, type DataTableColumns, useMessage } from 'naive-ui'

import { extractApiError } from '@/api/client'
import { deliveriesApi } from '@/api/deliveries'
import DownloadLinkPanel from '@/components/deliveries/DownloadLinkPanel.vue'
import { useAuthStore } from '@/stores/auth'
import type { DeliveryFileRecord } from '@/types/domain'

const props = withDefaults(defineProps<{
  packageId: string
  canPublish?: boolean
  canAccept?: boolean
  accepted?: boolean
}>(), {
  canPublish: false,
  canAccept: false,
  accepted: false,
})

const emit = defineEmits<{
  updated: []
  accepted: []
}>()

const auth = useAuthStore()
const message = useMessage()
const fileInput = ref<HTMLInputElement | null>(null)
const deliveries = ref<DeliveryFileRecord[]>([])
const selectedFileId = ref('')
const pendingUpload = ref<File | null>(null)
const uploadLoading = ref(false)
const linkLoading = ref(false)
const bulkLoading = ref(false)
const linkExpired = ref(false)
const downloadToken = ref('')
const downloadExpiresAt = ref('')
const currentLinkDownloadAllowed = ref(false)
const downloadFilename = ref('nutrideclare-download')

const uploadForm = reactive({
  fileType: 'revision_note',
  isFinal: false,
  allowedRoles: ['participant', 'reviewer', 'administrator'],
  linkRecipient: 'participant',
})

const fileTypeOptions = [
  { label: 'Revision Note', value: 'revision_note' },
  { label: 'Final Plan PDF', value: 'final_plan_pdf' },
  { label: 'Supporting Export', value: 'supporting_raw_export' },
]

const linkRecipientOptions = [
  { label: 'Package participant', value: 'participant' },
  { label: 'My account', value: 'self' },
]

const roleOptions = [
  { label: 'Participant', value: 'participant' },
  { label: 'Reviewer', value: 'reviewer' },
  { label: 'Administrator', value: 'administrator' },
]

const selectedFile = computed(() => deliveries.value.find((item) => item.id === selectedFileId.value) || deliveries.value[0] || null)
const canAcceptCurrentLink = computed(() => props.canAccept && currentLinkDownloadAllowed.value)
const linkRecipientHint = computed(() => {
  if (!props.canPublish) return 'Use a secure link or bulk bundle to download the visible files.'
  return uploadForm.linkRecipient === 'participant'
    ? 'This token is issued to the package participant and is meant to be shared, not downloaded by your current session.'
    : 'This token is issued to your current account for verification or internal download.'
})

const columns: DataTableColumns<DeliveryFileRecord> = [
  { title: 'Artifact', key: 'display_name' },
  { title: 'Type', key: 'file_type' },
  {
    title: 'Audience',
    key: 'allowed_roles',
    render: (row) => row.allowed_roles.join(', '),
  },
  {
    title: 'Final',
    key: 'is_final',
    render: (row) => row.is_final ? 'Yes' : 'No',
  },
  {
    title: 'Created',
    key: 'created_at',
    render: (row) => formatTimestamp(row.created_at),
  },
  {
    title: 'Action',
    key: 'action',
    render: (row) => h(NButton, {
      size: 'small',
      secondary: selectedFileId.value !== row.id,
      type: selectedFileId.value === row.id ? 'primary' : 'default',
      onClick: () => { selectedFileId.value = row.id },
    }, { default: () => selectedFileId.value === row.id ? 'Selected' : 'Select' }),
  },
]

function formatTimestamp(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  pendingUpload.value = input.files?.[0] || null
}

async function load() {
  deliveries.value = await deliveriesApi.list(props.packageId)
  if (!deliveries.value.length) {
    selectedFileId.value = ''
    return
  }
  if (!deliveries.value.some((item) => item.id === selectedFileId.value)) {
    selectedFileId.value = deliveries.value[0].id
  }
}

async function uploadSelectedFile() {
  if (!pendingUpload.value) {
    message.warning('Choose a file to publish first.')
    return
  }
  uploadLoading.value = true
  try {
    const file = await deliveriesApi.uploadFile(props.packageId, {
      upload: pendingUpload.value,
      file_type: uploadForm.fileType,
      is_final: uploadForm.isFinal,
      allowed_roles: uploadForm.allowedRoles,
    })
    selectedFileId.value = file.id
    pendingUpload.value = null
    if (fileInput.value) fileInput.value.value = ''
    message.success('Delivery artifact published.')
    await load()
    emit('updated')
  } catch (error) {
    message.error(extractApiError(error))
  } finally {
    uploadLoading.value = false
  }
}

async function generateLink() {
  if (!selectedFile.value) {
    message.warning('Select a delivery artifact first.')
    return
  }
  linkLoading.value = true
  try {
    const payload = await deliveriesApi.createLink(props.packageId, {
      delivery_file_id: selectedFile.value.id,
      issued_to_user_id: uploadForm.linkRecipient === 'self' ? auth.user?.id : undefined,
    })
    downloadToken.value = payload.token
    downloadExpiresAt.value = payload.expires_at
    currentLinkDownloadAllowed.value = uploadForm.linkRecipient === 'self'
    downloadFilename.value = selectedFile.value.display_name
    linkExpired.value = false
    message.success('Secure link created.')
  } catch (error) {
    linkExpired.value = true
    message.error(extractApiError(error))
  } finally {
    linkLoading.value = false
  }
}

async function generateBulkLink() {
  bulkLoading.value = true
  try {
    const payload = await deliveriesApi.bulkDownload(props.packageId)
    downloadToken.value = payload.token
    downloadExpiresAt.value = payload.expires_at
    currentLinkDownloadAllowed.value = true
    downloadFilename.value = 'nutrideclare-bulk-package.zip'
    linkExpired.value = false
    message.success('Bulk download bundle is ready.')
  } catch (error) {
    message.error(extractApiError(error))
  } finally {
    bulkLoading.value = false
  }
}

async function downloadArtifact() {
  if (!downloadToken.value || !auth.accessToken) return
  try {
    const response = await deliveriesApi.downloadByToken(downloadToken.value, auth.accessToken)
    const blob = new Blob([response.data], { type: response.headers['content-type'] || 'application/octet-stream' })
    const href = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = href
    link.download = downloadFilename.value
    link.click()
    URL.revokeObjectURL(href)
  } catch (error) {
    linkExpired.value = true
    message.error(extractApiError(error))
  }
}

async function acceptDelivery() {
  try {
    await deliveriesApi.accept(props.packageId, { confirmation_note: 'Accepted in participant portal', accepted_delivery_version: 'current' })
    message.success('Delivery accepted.')
    emit('accepted')
  } catch (error) {
    message.error(extractApiError(error))
  }
}

onMounted(() => {
  load().catch((error) => message.error(extractApiError(error)))
})
</script>

<template>
  <div class="page-shell">
    <n-card class="section-card" title="Delivery artifacts">
      <div class="workspace-toolbar">
        <div class="tiny">
          {{ selectedFile ? `Selected artifact: ${selectedFile.display_name}` : 'No delivery artifacts published yet.' }}
        </div>
        <div class="toolbar-actions">
          <n-button secondary @click="load">Refresh</n-button>
          <n-button secondary :loading="bulkLoading" :disabled="!deliveries.length" @click="generateBulkLink">Download all</n-button>
        </div>
      </div>

      <n-data-table :columns="columns" :data="deliveries" :bordered="false" />

      <div v-if="canPublish" class="upload-grid">
        <n-alert type="info" title="Publishing controls">
          Reviewers and administrators can upload artifacts, restrict them by role, and issue secure links for either the participant or the current operator.
        </n-alert>

        <n-form :model="uploadForm" label-placement="top">
          <div class="responsive-two">
            <n-form-item label="Artifact type">
              <n-select v-model:value="uploadForm.fileType" :options="fileTypeOptions" />
            </n-form-item>
            <n-form-item label="Secure link target">
              <n-select v-model:value="uploadForm.linkRecipient" :options="linkRecipientOptions" />
            </n-form-item>
          </div>

          <n-form-item label="Allowed roles">
            <n-checkbox-group v-model:value="uploadForm.allowedRoles">
              <div class="role-grid">
                <n-checkbox v-for="option in roleOptions" :key="option.value" :value="option.value" :label="option.label" />
              </div>
            </n-checkbox-group>
          </n-form-item>

          <n-form-item label="Artifact file">
            <input ref="fileInput" type="file" @change="handleFileChange" />
          </n-form-item>

          <n-form-item>
            <n-checkbox v-model:checked="uploadForm.isFinal" label="Mark as final delivery artifact" />
          </n-form-item>

          <div class="toolbar-actions">
            <n-button type="primary" :loading="uploadLoading" @click="uploadSelectedFile">Publish artifact</n-button>
            <n-button secondary :disabled="!selectedFile" :loading="linkLoading" @click="generateLink">Generate secure link</n-button>
          </div>
        </n-form>
      </div>
    </n-card>

    <n-alert type="default" class="section-card" :title="props.canPublish ? 'Secure link behavior' : 'Participant access'">
      {{ linkRecipientHint }}
    </n-alert>

    <DownloadLinkPanel
      :token="downloadToken"
      :loading="linkLoading"
      :expired="linkExpired"
      :expires-at="downloadExpiresAt"
      :accepted="props.accepted"
      :allow-create="false"
      :allow-download="currentLinkDownloadAllowed"
      :allow-accept="canAcceptCurrentLink"
      @download="downloadArtifact"
      @accept="acceptDelivery"
    />
  </div>
</template>

<style scoped>
.workspace-toolbar,
.toolbar-actions,
.role-grid,
.upload-grid {
  display: grid;
  gap: 12px;
}

.workspace-toolbar {
  margin-bottom: 16px;
}

.toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.role-grid {
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
}

.upload-grid {
  margin-top: 18px;
}
</style>
