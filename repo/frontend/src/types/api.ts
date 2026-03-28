export interface ApiEnvelope<T> {
  success: boolean
  message?: string | null
  data: T
  meta?: Record<string, unknown>
}

export interface ApiErrorItem {
  code: string
  field?: string | null
  detail: string
}

export interface ApiErrorEnvelope {
  success: false
  message: string
  errors: ApiErrorItem[]
}

export type UserRole = 'participant' | 'reviewer' | 'administrator'

export interface SessionUser {
  id: string
  username: string
  role: UserRole
  force_password_change: boolean
}
