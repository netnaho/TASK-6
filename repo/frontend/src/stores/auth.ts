import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { authApi } from '@/api/auth'
import { extractApiError, setAccessToken, setUnauthorizedHandler } from '@/api/client'
import type { SessionUser, UserRole } from '@/types/api'
import router from '@/router'

const ACCESS_TOKEN_KEY = 'nutrideclare_access_token'
const REFRESH_TOKEN_KEY = 'nutrideclare_refresh_token'
const SESSION_USER_KEY = 'nutrideclare_session_user'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem(ACCESS_TOKEN_KEY) || '')
  const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) || '')
  const user = ref<SessionUser | null>(JSON.parse(localStorage.getItem(SESSION_USER_KEY) || 'null'))
  const bootstrapping = ref(false)

  function persist() {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken.value)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken.value)
    localStorage.setItem(SESSION_USER_KEY, JSON.stringify(user.value))
    setAccessToken(accessToken.value)
  }

  function clearSession() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    persist()
  }

  async function hydrate() {
    if (!accessToken.value && !refreshToken.value) return
    bootstrapping.value = true
    setAccessToken(accessToken.value)
    try {
      user.value = await authApi.me() as SessionUser
      persist()
    } catch {
      try {
        if (refreshToken.value) {
          const refreshed = await authApi.refresh(refreshToken.value)
          accessToken.value = refreshed.access_token
          refreshToken.value = refreshed.refresh_token
          setAccessToken(accessToken.value)
          user.value = await authApi.me() as SessionUser
          persist()
        }
      } catch {
        clearSession()
      }
    } finally {
      bootstrapping.value = false
    }
  }

  async function login(payload: { username: string; password: string; captcha_challenge_token?: string; captcha_answer?: string }) {
    const tokenPayload = await authApi.login(payload)
    accessToken.value = tokenPayload.access_token
    refreshToken.value = tokenPayload.refresh_token
    setAccessToken(accessToken.value)
    user.value = await authApi.me() as SessionUser
    if (tokenPayload.force_password_change) {
      user.value.force_password_change = true
    }
    persist()
  }

  async function logout() {
    try {
      if (refreshToken.value) await authApi.logout(refreshToken.value)
    } finally {
      clearSession()
      await router.replace('/login')
    }
  }

  async function refreshSession() {
    if (!refreshToken.value) {
      clearSession()
      await router.replace('/login')
      return
    }
    try {
      const tokenPayload = await authApi.refresh(refreshToken.value)
      accessToken.value = tokenPayload.access_token
      refreshToken.value = tokenPayload.refresh_token
      setAccessToken(accessToken.value)
      user.value = await authApi.me() as SessionUser
      persist()
    } catch {
      clearSession()
      await router.replace('/login')
    }
  }

  async function changeForcedPassword(new_password: string) {
    await authApi.completeForcedPasswordChange({ new_password })
    if (user.value) {
      user.value.force_password_change = false
      persist()
    }
  }

  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value))
  const role = computed<UserRole | null>(() => user.value?.role ?? null)

  setUnauthorizedHandler(async () => {
    if (refreshToken.value) {
      try {
        await refreshSession()
      } catch {
        clearSession()
      }
    }
  })
  setAccessToken(accessToken.value)

  return {
    accessToken,
    refreshToken,
    user,
    role,
    bootstrapping,
    isAuthenticated,
    hydrate,
    login,
    logout,
    refreshSession,
    changeForcedPassword,
    clearSession,
  }
})
