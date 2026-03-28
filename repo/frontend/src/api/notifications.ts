import api, { unwrap } from '@/api/client'
import type { NotificationItem } from '@/types/domain'

export const notificationsApi = {
  list() {
    return unwrap<NotificationItem[]>(api.get('/notifications'))
  },
  markRead(notificationId: string) {
    return unwrap(api.post(`/notifications/${notificationId}/read`))
  },
  markAllRead() {
    return unwrap(api.post('/notifications/read-all'))
  },
  updatePreferences(payload: Record<string, unknown>) {
    return unwrap(api.patch('/notifications/preferences', payload))
  },
  preferences() {
    return unwrap<Record<string, unknown>>(api.get('/notifications/preferences'))
  },
  mandatoryAlerts() {
    return unwrap<NotificationItem[]>(api.get('/notifications/mandatory-alerts'))
  },
}
