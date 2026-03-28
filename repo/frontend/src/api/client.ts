import axios from 'axios'

import type { ApiEnvelope, ApiErrorEnvelope } from '@/types/api'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

let accessToken = ''
let onUnauthorized: (() => Promise<void>) | null = null

export function setAccessToken(token: string) {
  accessToken = token
}

export function setUnauthorizedHandler(handler: () => Promise<void>) {
  onUnauthorized = handler
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && onUnauthorized) {
      await onUnauthorized()
    }
    return Promise.reject(error)
  },
)

export async function unwrap<T>(request: Promise<{ data: ApiEnvelope<T> }>): Promise<T> {
  const response = await request
  return response.data.data
}

export function extractApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const payload = error.response?.data as ApiErrorEnvelope | undefined
    return payload?.errors?.[0]?.detail || payload?.message || error.message
  }
  return 'An unexpected error occurred.'
}

export default api
