import api, { unwrap } from '@/api/client'
import type { AuditLogRecord } from '@/types/domain'

export const auditApi = {
  list() {
    return unwrap<AuditLogRecord[]>(api.get('/audit'))
  },
}
