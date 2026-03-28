import api, { unwrap } from '@/api/client'
import type { DeclarationRecord, VersionRecord } from '@/types/domain'

export const declarationsApi = {
  list() {
    return unwrap<DeclarationRecord[]>(api.get('/declarations'))
  },
  create(payload: Record<string, unknown>) {
    return unwrap<DeclarationRecord>(api.post('/declarations', payload))
  },
  get(packageId: string) {
    return unwrap<DeclarationRecord>(api.get(`/declarations/${packageId}`))
  },
  history(packageId: string) {
    return unwrap<{ versions: VersionRecord[]; state_history: unknown[] }>(api.get(`/declarations/${packageId}/history`))
  },
  corrections(packageId: string) {
    return unwrap<any[]>(api.get(`/declarations/${packageId}/corrections`))
  },
  submit(packageId: string, payload: Record<string, unknown> = {}) {
    return unwrap<DeclarationRecord>(api.post(`/declarations/${packageId}/submit`, payload))
  },
  withdraw(packageId: string, payload: Record<string, unknown> = {}) {
    return unwrap<DeclarationRecord>(api.post(`/declarations/${packageId}/withdraw`, payload))
  },
  reopen(packageId: string, payload: Record<string, unknown> = {}) {
    return unwrap<DeclarationRecord>(api.post(`/declarations/${packageId}/reopen`, payload))
  },
  void(packageId: string, payload: Record<string, unknown>) {
    return unwrap<DeclarationRecord>(api.post(`/declarations/${packageId}/void`, payload))
  },
  acknowledge(packageId: string, correctionId: string, payload: Record<string, unknown> = {}) {
    return unwrap(api.post(`/declarations/${packageId}/corrections/${correctionId}/acknowledge`, payload))
  },
  resubmit(packageId: string, correctionId: string, payload: Record<string, unknown> = {}) {
    return unwrap(api.post(`/declarations/${packageId}/corrections/${correctionId}/resubmit`, payload))
  },
}
