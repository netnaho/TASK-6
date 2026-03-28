import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { notificationsApi } from '@/api/notifications'
import type { NotificationItem } from '@/types/domain'

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref<NotificationItem[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      items.value = await notificationsApi.list()
    } finally {
      loading.value = false
    }
  }

  async function markRead(notificationId: string) {
    await notificationsApi.markRead(notificationId)
    const target = items.value.find((item) => item.id === notificationId)
    if (target) target.is_read = true
  }

  async function markAllRead() {
    await notificationsApi.markAllRead()
    items.value = items.value.map((item) => ({ ...item, is_read: true }))
  }

  const unreadCount = computed(() => items.value.filter((item) => !item.is_read).length)

  return { items, loading, unreadCount, fetchAll, markRead, markAllRead }
})
