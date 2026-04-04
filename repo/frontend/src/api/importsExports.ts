import api, { unwrap } from '@/api/client'
import type { ExportJobDetail, ExportJobRecord, ImportJobDetail, ImportJobRecord } from '@/types/domain'

export const importsExportsApi = {
  imports() {
    return unwrap<ImportJobRecord[]>(api.get('/imports'))
  },
  exports() {
    return unwrap<ExportJobRecord[]>(api.get('/exports'))
  },
  importDetail(jobId: string) {
    return unwrap<ImportJobDetail>(api.get(`/imports/${jobId}`))
  },
  exportDetail(jobId: string) {
    return unwrap<ExportJobDetail>(api.get(`/exports/${jobId}`))
  },
  createImportDownloadLink(jobId: string) {
    return unwrap<{ token: string; expires_at: string; delivery_file_id: string }>(api.get(`/imports/${jobId}/source-download-link`))
  },
  createExportDownloadLink(jobId: string) {
    return unwrap<{ token: string; expires_at: string; delivery_file_id: string }>(api.get(`/exports/${jobId}/download-link`))
  },
  fieldMappings() {
    return unwrap<any[]>(api.get('/admin/field-mappings'))
  },
  createFieldMapping(payload: Record<string, unknown>) {
    return unwrap(api.post('/admin/field-mappings', payload))
  },
  maskingPolicies() {
    return unwrap<any[]>(api.get('/admin/masking-policies'))
  },
  createMaskingPolicy(payload: Record<string, unknown>) {
    return unwrap(api.post('/admin/masking-policies', payload))
  },
  createExport(payload: Record<string, unknown>) {
    return unwrap<ExportJobRecord>(api.post('/exports', payload))
  },
  createImport(payload: { upload: File; format: string; scope_type: string; mapping_id?: string | null }) {
    const formData = new FormData()
    formData.append('upload', payload.upload)
    formData.append('format', payload.format)
    formData.append('scope_type', payload.scope_type)
    if (payload.mapping_id) formData.append('mapping_id', payload.mapping_id)
    return unwrap<ImportJobRecord>(api.post('/imports', formData))
  },
}
