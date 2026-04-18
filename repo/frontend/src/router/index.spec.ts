import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import router, { authNavigationGuard } from './index'
import { useAuthStore } from '@/stores/auth'

type GuardResult = ReturnType<typeof authNavigationGuard>

async function runGuard(toPath: string): Promise<Awaited<GuardResult>> {
  const to = router.resolve(toPath)
  const from = router.resolve('/login')
  return (await (authNavigationGuard as any)(to, from, () => undefined)) as Awaited<GuardResult>
}

describe('router configuration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('resolves the login route with the guestOnly meta flag', () => {
    const resolved = router.resolve('/login')
    expect(resolved.name).toBe('login')
    expect(resolved.meta.guestOnly).toBe(true)
  })

  it('marks participant-protected routes with the participant role', () => {
    const resolved = router.resolve('/app/participant/dashboard')
    expect(resolved.name).toBe('participant-dashboard')
    expect(resolved.meta.auth).toBe(true)
    expect(resolved.meta.roles).toContain('participant')
  })

  it('marks reviewer-protected routes with the reviewer role', () => {
    const resolved = router.resolve('/app/reviewer/queue')
    expect(resolved.name).toBe('reviewer-queue')
    expect(resolved.meta.roles).toContain('reviewer')
  })

  it('marks administrator-protected routes with the administrator role', () => {
    const resolved = router.resolve('/app/admin/dashboard')
    expect(resolved.name).toBe('admin-dashboard')
    expect(resolved.meta.roles).toContain('administrator')
  })

  it('falls back to the not-found route for unknown paths', () => {
    const resolved = router.resolve('/definitely-not-a-route')
    expect(resolved.name).toBe('not-found')
  })
})

describe('authNavigationGuard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('redirects an unauthenticated user away from an auth-required route to /login', async () => {
    const store = useAuthStore()
    vi.spyOn(store, 'hydrate').mockResolvedValue(undefined)

    const result = await runGuard('/app/participant/dashboard')
    expect(result).toBe('/login')
  })

  it('allows an unauthenticated user to reach the login screen', async () => {
    const store = useAuthStore()
    vi.spyOn(store, 'hydrate').mockResolvedValue(undefined)

    const result = await runGuard('/login')
    expect(result).toBe(true)
  })

  it('redirects an authenticated participant away from the login screen', async () => {
    const store = useAuthStore()
    vi.spyOn(store, 'hydrate').mockResolvedValue(undefined)
    store.accessToken = 'token-xyz'
    store.user = {
      id: 'user-1',
      username: 'participant_demo',
      role: 'participant',
      force_password_change: false,
    }

    const result = await runGuard('/login')
    expect(result).toBe('/app/participant/dashboard')
  })

  it('redirects a forced-password-change user to the force-password-change screen', async () => {
    const store = useAuthStore()
    vi.spyOn(store, 'hydrate').mockResolvedValue(undefined)
    store.accessToken = 'token-xyz'
    store.user = {
      id: 'user-1',
      username: 'participant_demo',
      role: 'participant',
      force_password_change: true,
    }

    const result = await runGuard('/app/participant/dashboard')
    expect(result).toBe('/force-password-change')
  })

  it('redirects a reviewer away from participant-only routes to /unauthorized', async () => {
    const store = useAuthStore()
    vi.spyOn(store, 'hydrate').mockResolvedValue(undefined)
    store.accessToken = 'token-xyz'
    store.user = {
      id: 'user-2',
      username: 'reviewer_demo',
      role: 'reviewer',
      force_password_change: false,
    }

    const result = await runGuard('/app/participant/dashboard')
    expect(result).toBe('/unauthorized')
  })

  it('allows an administrator to reach their dashboard', async () => {
    const store = useAuthStore()
    vi.spyOn(store, 'hydrate').mockResolvedValue(undefined)
    store.accessToken = 'token-xyz'
    store.user = {
      id: 'user-3',
      username: 'admin_demo',
      role: 'administrator',
      force_password_change: false,
    }

    const result = await runGuard('/app/admin/dashboard')
    expect(result).toBe(true)
  })
})
