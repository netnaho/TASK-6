import api, { unwrap } from '@/api/client'
import type { ProfileRecord, VersionRecord } from '@/types/domain'

export const profilesApi = {
  getMine() {
    return unwrap<ProfileRecord>(api.get('/profiles/me'))
  },
  save(payload: Record<string, unknown>) {
    return unwrap<ProfileRecord>(api.post('/profiles/me', payload))
  },
  update(payload: Record<string, unknown>) {
    return unwrap<ProfileRecord>(api.put('/profiles/me', payload))
  },
  history() {
    return unwrap<VersionRecord[]>(api.get('/profiles/me/history'))
  },
  version(versionId: string) {
    return unwrap<VersionRecord>(api.get(`/profiles/me/history/${versionId}`))
  },
}
