import api, { unwrap } from '@/api/client'

export interface LoginPayload {
  username: string
  password: string
  captcha_challenge_token?: string
  captcha_answer?: string
}

export interface TokenPayload {
  access_token: string
  refresh_token: string
  token_type: string
  access_expires_in_minutes: number
  refresh_expires_in_days: number
  force_password_change: boolean
}

export const authApi = {
  register(payload: Record<string, unknown>) {
    return unwrap(api.post('/auth/register', payload))
  },
  login(payload: LoginPayload) {
    return unwrap<TokenPayload>(api.post('/auth/login', payload))
  },
  refresh(refresh_token: string) {
    return unwrap<TokenPayload>(api.post('/auth/refresh', { refresh_token }))
  },
  logout(refresh_token: string) {
    return unwrap(api.post('/auth/logout', { refresh_token }))
  },
  me() {
    return unwrap(api.get('/auth/me'))
  },
  captcha() {
    return unwrap<{ enabled?: boolean; prompt: string; challenge_token: string }>(api.get('/auth/captcha/challenge'))
  },
  changePassword(payload: { current_password: string; new_password: string }) {
    return unwrap(api.post('/auth/change-password', payload))
  },
  completeForcedPasswordChange(payload: { new_password: string }) {
    return unwrap(api.post('/auth/complete-forced-password-change', payload))
  },
}
