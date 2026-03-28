import api, { unwrap } from '@/api/client'

export const importsExportsApi = {
  imports() {
    return unwrap<any[]>(api.get('/imports'))
  },
  exports() {
    return unwrap<any[]>(api.get('/exports'))
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
    return unwrap(api.post('/exports', payload))
  },
}
