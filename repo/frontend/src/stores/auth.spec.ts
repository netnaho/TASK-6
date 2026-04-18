import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { authApi } from '@/api/auth'
import router from '@/router'

import { useAuthStore } from './auth'

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    window.localStorage.clear()
  })

  it('starts unauthenticated when there is no persisted session', () => {
    const store = useAuthStore()
    expect(store.accessToken).toBe('')
    expect(store.refreshToken).toBe('')
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.role).toBeNull()
  })

  it('login persists tokens, sets the session user, and exposes the role', async () => {
    const loginSpy = vi.spyOn(authApi, 'login').mockResolvedValue({
      access_token: 'access-token-xyz',
      refresh_token: 'refresh-token-xyz',
      token_type: 'bearer',
      access_expires_in_minutes: 30,
      refresh_expires_in_days: 7,
      force_password_change: false,
    })
    const meSpy = vi.spyOn(authApi, 'me').mockResolvedValue({
      id: 'user-1',
      username: 'participant_demo',
      role: 'participant',
      force_password_change: false,
    })

    const store = useAuthStore()
    await store.login({ username: 'participant_demo', password: 'Participant#2026' })

    expect(loginSpy).toHaveBeenCalledWith({ username: 'participant_demo', password: 'Participant#2026' })
    expect(meSpy).toHaveBeenCalled()
    expect(store.accessToken).toBe('access-token-xyz')
    expect(store.refreshToken).toBe('refresh-token-xyz')
    expect(store.isAuthenticated).toBe(true)
    expect(store.role).toBe('participant')
    expect(window.localStorage.getItem('nutrideclare_access_token')).toBe('access-token-xyz')
    expect(window.localStorage.getItem('nutrideclare_refresh_token')).toBe('refresh-token-xyz')
  })

  it('login propagates the API error and keeps the store unauthenticated', async () => {
    vi.spyOn(authApi, 'login').mockRejectedValue(new Error('Invalid credentials'))
    const store = useAuthStore()

    await expect(store.login({ username: 'bad', password: 'bad' })).rejects.toThrow('Invalid credentials')
    expect(store.isAuthenticated).toBe(false)
    expect(store.accessToken).toBe('')
  })

  it('logout clears the session even when the backend call rejects', async () => {
    const store = useAuthStore()
    store.accessToken = 'still-here'
    store.refreshToken = 'stale-refresh'
    store.user = {
      id: 'user-1',
      username: 'participant_demo',
      role: 'participant',
      force_password_change: false,
    }

    vi.spyOn(authApi, 'logout').mockRejectedValue(new Error('server unavailable'))
    const replaceSpy = vi.spyOn(router, 'replace').mockResolvedValue(undefined as any)

    await expect(store.logout()).rejects.toThrow('server unavailable')

    expect(store.accessToken).toBe('')
    expect(store.refreshToken).toBe('')
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(replaceSpy).toHaveBeenCalledWith('/login')
  })

  it('logout completes cleanly when the backend call succeeds', async () => {
    const store = useAuthStore()
    store.accessToken = 'still-here'
    store.refreshToken = 'fresh-refresh'
    store.user = {
      id: 'user-1',
      username: 'participant_demo',
      role: 'participant',
      force_password_change: false,
    }

    const logoutSpy = vi.spyOn(authApi, 'logout').mockResolvedValue(undefined as any)
    const replaceSpy = vi.spyOn(router, 'replace').mockResolvedValue(undefined as any)

    await expect(store.logout()).resolves.toBeUndefined()

    expect(logoutSpy).toHaveBeenCalledWith('fresh-refresh')
    expect(replaceSpy).toHaveBeenCalledWith('/login')
    expect(store.accessToken).toBe('')
    expect(store.user).toBeNull()
  })

  it('clearSession wipes tokens, session user, and persisted storage', () => {
    const store = useAuthStore()
    store.accessToken = 'persisted'
    store.refreshToken = 'persisted-refresh'
    store.user = {
      id: 'user-1',
      username: 'participant_demo',
      role: 'participant',
      force_password_change: false,
    }
    store.clearSession()

    expect(store.accessToken).toBe('')
    expect(store.refreshToken).toBe('')
    expect(store.user).toBeNull()
    expect(window.localStorage.getItem('nutrideclare_access_token')).toBe('')
  })
})
