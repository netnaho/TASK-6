import api, { unwrap } from '@/api/client'
import type { AuditLogRecord, UserRecord } from '@/types/domain'

export const adminApi = {
  users() {
    return unwrap<UserRecord[]>(api.get('/admin/users'))
  },
  createUser(payload: Record<string, unknown>) {
    return unwrap<UserRecord>(api.post('/admin/users', payload))
  },
  updateUser(userId: string, payload: Record<string, unknown>) {
    return unwrap<UserRecord>(api.patch(`/admin/users/${userId}`, payload))
  },
  resetPassword(userId: string, payload: Record<string, unknown>) {
    return unwrap(api.post(`/admin/users/${userId}/reset-password`, payload))
  },
  audit() {
    return unwrap<AuditLogRecord[]>(api.get('/audit'))
  },
  settings() {
    return unwrap<any[]>(api.get('/admin/settings'))
  },
  updateSettings(payload: Record<string, unknown>) {
    return unwrap(api.put('/admin/settings', payload))
  },
}
