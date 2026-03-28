<template>
  <div class="app-shell">
    <aside class="sidebar section-card" :class="{ open: shell.mobileDrawerOpen }">
      <div class="brand-block">
        <div class="tiny">NUTRIDECLARE</div>
        <h2>Offline Compliance</h2>
        <p class="muted">Premium workflow controls for wellness declarations and delivery governance.</p>
      </div>

      <n-menu :options="menuOptions" :value="activeMenu" @update:value="navigate" />

      <div class="sidebar-footer">
        <n-button quaternary block @click="auth.logout">Sign out</n-button>
      </div>
    </aside>

    <div class="shell-main">
      <header class="shell-header section-card">
        <div class="app-toolbar">
          <div style="display:flex; align-items:center; gap: 12px;">
            <n-button circle secondary @click="shell.toggleDrawer">
              <template #icon>
                <n-icon><MenuOutline /></n-icon>
              </template>
            </n-button>
            <div>
              <div class="tiny">{{ greeting }}</div>
              <strong>{{ pageTitle }}</strong>
            </div>
          </div>

          <div style="display:flex; align-items:center; gap: 12px;">
            <n-badge :value="notifications.unreadCount" :max="99">
              <n-button circle secondary @click="router.push('/app/notifications')">
                <template #icon><n-icon><NotificationsOutline /></n-icon></template>
              </n-button>
            </n-badge>
            <n-avatar round>{{ initials }}</n-avatar>
          </div>
        </div>

        <n-breadcrumb class="shell-breadcrumbs">
          <n-breadcrumb-item v-for="crumb in breadcrumbs" :key="crumb.path" @click="router.push(crumb.path)">
            {{ crumb.label }}
          </n-breadcrumb-item>
        </n-breadcrumb>
      </header>

      <main class="content-area">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MenuOutline, NotificationsOutline } from '@vicons/ionicons5'
import { NAvatar, NBadge, NBreadcrumb, NBreadcrumbItem, NButton, NIcon, NMenu, type MenuOption } from 'naive-ui'

import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { useAppShellStore } from '@/stores/appShell'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const notifications = useNotificationsStore()
const shell = useAppShellStore()

onMounted(() => {
  notifications.fetchAll().catch(() => undefined)
})

const menusByRole: Record<string, MenuOption[]> = {
  participant: [
    { label: 'Dashboard', key: '/app/participant/dashboard' },
    { label: 'Health Profile', key: '/app/participant/profile' },
    { label: 'Nutrition Plans', key: '/app/participant/plans' },
    { label: 'Declarations', key: '/app/participant/declarations' },
    { label: 'Deliveries', key: '/app/participant/deliveries' },
    { label: 'Notifications', key: '/app/notifications' },
  ],
  reviewer: [
    { label: 'Dashboard', key: '/app/reviewer/dashboard' },
    { label: 'Review Queue', key: '/app/reviewer/queue' },
    { label: 'Notifications', key: '/app/notifications' },
  ],
  administrator: [
    { label: 'Dashboard', key: '/app/admin/dashboard' },
    { label: 'Declarations', key: '/app/admin/declarations' },
    { label: 'Users', key: '/app/admin/users' },
    { label: 'Audit Trail', key: '/app/admin/audit' },
    { label: 'Import & Export', key: '/app/admin/imports' },
    { label: 'Settings', key: '/app/admin/settings' },
    { label: 'Notifications', key: '/app/notifications' },
  ],
}

const menuOptions = computed(() => menusByRole[auth.role || 'participant'] || [])
const activeMenu = computed(() => route.path)
const pageTitle = computed(() => String(route.name || 'Workspace').split('-').join(' '))
const initials = computed(() => auth.user?.username.slice(0, 2).toUpperCase() ?? 'NU')
const greeting = computed(() => `${auth.user?.role?.toUpperCase() ?? 'WORKSPACE'} PORTAL`)
const breadcrumbs = computed(() =>
  route.matched
    .filter((item) => item.name && item.name !== 'not-found')
    .map((item) => ({
      label: String(item.name)
        .split('-')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' '),
      path: item.path,
    })),
)

function navigate(key: string) {
  shell.closeDrawer()
  router.push(key)
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
  padding: 20px;
}

.sidebar {
  padding: 24px 18px;
  display: grid;
  align-content: start;
  gap: 24px;
  position: sticky;
  top: 20px;
  height: calc(100vh - 40px);
}

.brand-block h2 {
  margin: 8px 0;
}

.shell-main {
  display: grid;
  gap: 18px;
}

.shell-header {
  padding: 14px 18px;
}

.shell-breadcrumbs {
  margin-top: 8px;
  color: var(--text-soft);
  font-size: 13px;
}

.content-area {
  display: grid;
}

.sidebar-footer {
  margin-top: auto;
}

@media (max-width: 1024px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: fixed;
    inset: 16px auto 16px 16px;
    width: min(320px, calc(100vw - 32px));
    transform: translateX(-115%);
    transition: transform 0.24s ease;
    z-index: 20;
    height: auto;
  }

  .sidebar.open {
    transform: translateX(0);
  }
}
</style>
