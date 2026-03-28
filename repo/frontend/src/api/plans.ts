import api, { unwrap } from '@/api/client'
import type { PlanRecord, VersionRecord } from '@/types/domain'

export const plansApi = {
  list() {
    return unwrap<PlanRecord[]>(api.get('/plans'))
  },
  create(payload: Record<string, unknown>) {
    return unwrap<PlanRecord>(api.post('/plans', payload))
  },
  update(planId: string, payload: Record<string, unknown>) {
    return unwrap<PlanRecord>(api.put(`/plans/${planId}`, payload))
  },
  get(planId: string) {
    return unwrap<PlanRecord>(api.get(`/plans/${planId}`))
  },
  versions(planId: string) {
    return unwrap<VersionRecord[]>(api.get(`/plans/${planId}/versions`))
  },
  version(versionId: string) {
    return unwrap<VersionRecord>(api.get(`/plans/versions/${versionId}`))
  },
}
