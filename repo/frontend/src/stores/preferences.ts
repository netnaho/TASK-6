import { ref } from 'vue'
import { defineStore } from 'pinia'

import { notificationsApi } from '@/api/notifications'

export const usePreferencesStore = defineStore('preferences', () => {
  const notificationPreferences = ref({
    status_changes_enabled: true,
    mentions_enabled: true,
    review_requests_enabled: true,
    deadline_warnings_enabled: true,
  })

  async function loadNotificationPreferences() {
    const response = await notificationsApi.preferences()
    notificationPreferences.value = {
      status_changes_enabled: Boolean(response.status_changes_enabled),
      mentions_enabled: Boolean(response.mentions_enabled),
      review_requests_enabled: Boolean(response.review_requests_enabled),
      deadline_warnings_enabled: Boolean(response.deadline_warnings_enabled),
    }
  }

  async function saveNotificationPreferences() {
    await notificationsApi.updatePreferences(notificationPreferences.value)
  }

  return { notificationPreferences, loadNotificationPreferences, saveNotificationPreferences }
})
