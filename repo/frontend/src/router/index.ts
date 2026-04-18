import { createRouter, createWebHistory, type NavigationGuard, type RouteRecordRaw } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  {
    path: '/',
    component: () => import('@/layouts/AuthLayout.vue'),
    children: [
      { path: 'login', name: 'login', component: () => import('@/views/auth/LoginView.vue'), meta: { guestOnly: true } },
      { path: 'register', name: 'register', component: () => import('@/views/auth/RegisterView.vue'), meta: { guestOnly: true } },
      { path: 'force-password-change', name: 'force-password-change', component: () => import('@/views/auth/ForcePasswordChangeView.vue'), meta: { auth: true } },
      { path: 'unauthorized', name: 'unauthorized', component: () => import('@/views/shared/UnauthorizedView.vue') },
    ],
  },
  {
    path: '/app',
    component: () => import('@/layouts/AppShell.vue'),
    meta: { auth: true },
    children: [
      { path: 'notifications', name: 'notifications', component: () => import('@/views/shared/NotificationsView.vue') },
      { path: 'participant/dashboard', name: 'participant-dashboard', component: () => import('@/views/participant/ParticipantDashboardView.vue'), meta: { roles: ['participant'] } },
      { path: 'participant/profile', name: 'participant-profile', component: () => import('@/views/participant/ProfileWizardView.vue'), meta: { roles: ['participant'] } },
      { path: 'participant/plans', name: 'participant-plans', component: () => import('@/views/participant/PlansView.vue'), meta: { roles: ['participant'] } },
      { path: 'participant/plans/new', name: 'participant-plan-new', component: () => import('@/views/participant/PlanEditorView.vue'), meta: { roles: ['participant'] } },
      { path: 'participant/plans/:planId', name: 'participant-plan-edit', component: () => import('@/views/participant/PlanEditorView.vue'), meta: { roles: ['participant'] } },
      { path: 'participant/declarations', name: 'participant-declarations', component: () => import('@/views/participant/DeclarationsView.vue'), meta: { roles: ['participant'] } },
      { path: 'participant/declarations/:packageId', name: 'participant-declaration-detail', component: () => import('@/views/participant/DeclarationDetailView.vue'), meta: { roles: ['participant'] } },
      { path: 'participant/deliveries', name: 'participant-deliveries', component: () => import('@/views/participant/DeliveriesView.vue'), meta: { roles: ['participant'] } },
      { path: 'reviewer/dashboard', name: 'reviewer-dashboard', component: () => import('@/views/reviewer/ReviewerDashboardView.vue'), meta: { roles: ['reviewer'] } },
      { path: 'reviewer/queue', name: 'reviewer-queue', component: () => import('@/views/reviewer/ReviewQueueView.vue'), meta: { roles: ['reviewer'] } },
      { path: 'reviewer/packages/:packageId', name: 'reviewer-package-detail', component: () => import('@/views/reviewer/ReviewDetailView.vue'), meta: { roles: ['reviewer'] } },
      { path: 'admin/dashboard', name: 'admin-dashboard', component: () => import('@/views/admin/AdminDashboardView.vue'), meta: { roles: ['administrator'] } },
      { path: 'admin/declarations', name: 'admin-declarations', component: () => import('@/views/admin/DeclarationsView.vue'), meta: { roles: ['administrator'] } },
      { path: 'admin/declarations/:packageId', name: 'admin-declaration-detail', component: () => import('@/views/participant/DeclarationDetailView.vue'), meta: { roles: ['administrator'] } },
      { path: 'admin/users', name: 'admin-users', component: () => import('@/views/admin/UserManagementView.vue'), meta: { roles: ['administrator'] } },
      { path: 'admin/audit', name: 'admin-audit', component: () => import('@/views/admin/AuditLogView.vue'), meta: { roles: ['administrator'] } },
      { path: 'admin/imports', name: 'admin-imports', component: () => import('@/views/admin/ImportExportView.vue'), meta: { roles: ['administrator'] } },
      { path: 'admin/settings', name: 'admin-settings', component: () => import('@/views/admin/SettingsView.vue'), meta: { roles: ['administrator'] } },
    ],
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/shared/NotFoundView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export const authNavigationGuard: NavigationGuard = async (to) => {
  const authStore = useAuthStore()
  if (!authStore.user && !authStore.bootstrapping) {
    await authStore.hydrate()
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    if (authStore.user?.force_password_change) return '/force-password-change'
    return authStore.role === 'participant'
      ? '/app/participant/dashboard'
      : authStore.role === 'reviewer'
        ? '/app/reviewer/dashboard'
        : '/app/admin/dashboard'
  }

  if (to.meta.auth && !authStore.isAuthenticated) return '/login'
  if (authStore.user?.force_password_change && to.name !== 'force-password-change') return '/force-password-change'

  const allowedRoles = to.meta.roles as string[] | undefined
  if (allowedRoles && authStore.role && !allowedRoles.includes(authStore.role)) return '/unauthorized'
  return true
}

router.beforeEach(authNavigationGuard)

export default router
