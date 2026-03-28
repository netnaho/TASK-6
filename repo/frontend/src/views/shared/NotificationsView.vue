<template>
  <div class="page-shell">
    <PageHeader eyebrow="IN-APP MESSAGING" title="Notification center" description="Track status changes, deadlines, mentions, and mandatory compliance alerts without missing critical actions.">
      <template #actions>
        <n-button secondary @click="markAll">Mark all read</n-button>
      </template>
    </PageHeader>

    <div class="responsive-two">
      <n-card class="section-card" title="Notifications">
        <n-space vertical>
          <n-alert v-for="item in notifications.items" :key="item.id" :type="item.type === 'mandatory_compliance_alert' ? 'error' : item.severity === 'warning' ? 'warning' : 'info'" :title="item.title">
            <div class="muted">{{ item.message }}</div>
            <div style="display:flex; justify-content:space-between; margin-top:8px; gap:12px; align-items:center;">
              <span class="tiny">{{ new Date(item.created_at).toLocaleString() }}</span>
              <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                <router-link v-if="item.link_path" :to="item.link_path" class="notification-link">
                  View details ->
                </router-link>
                <n-button text type="primary" @click="markOne(item.id)">{{ item.is_read ? 'Read' : 'Mark read' }}</n-button>
              </div>
            </div>
          </n-alert>
        </n-space>
      </n-card>

      <n-card class="section-card" title="Mute non-critical alerts">
        <p class="muted">Mandatory compliance alerts remain enforced and always visible.</p>
        <n-switch v-model:value="prefs.status_changes_enabled">Status changes</n-switch>
        <div style="height:12px" />
        <n-switch v-model:value="prefs.mentions_enabled">Mentions</n-switch>
        <div style="height:12px" />
        <n-switch v-model:value="prefs.review_requests_enabled">Review requests</n-switch>
        <div style="height:12px" />
        <n-switch v-model:value="prefs.deadline_warnings_enabled">Deadline warnings</n-switch>
        <div style="height:20px" />
        <n-button type="primary" @click="savePrefs">Save preferences</n-button>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { NAlert, NButton, NCard, NSpace, NSwitch, useMessage } from 'naive-ui'

import PageHeader from '@/components/common/PageHeader.vue'
import { useNotificationsStore } from '@/stores/notifications'
import { usePreferencesStore } from '@/stores/preferences'
import { extractApiError } from '@/api/client'

const message = useMessage()
const notifications = useNotificationsStore()
const preferences = usePreferencesStore()
const prefs = preferences.notificationPreferences

onMounted(() => {
  notifications.fetchAll().catch((error) => message.error(extractApiError(error)))
  preferences.loadNotificationPreferences().catch(() => undefined)
})

async function markOne(id: string) {
  try {
    await notifications.markRead(id)
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function markAll() {
  try {
    await notifications.markAllRead()
    message.success('All notifications marked read.')
  } catch (error) {
    message.error(extractApiError(error))
  }
}

async function savePrefs() {
  try {
    await preferences.saveNotificationPreferences()
    message.success('Preferences saved.')
  } catch (error) {
    message.error(extractApiError(error))
  }
}
</script>

<style scoped>
.notification-link {
  color: var(--accent);
  font-weight: 500;
}
</style>
