export interface NotificationItem {
  id: string
  type: string
  severity: string
  title: string
  message: string
  link_path?: string | null
  is_read: boolean
  created_at: string
}

export interface ProfileRecord {
  id: string
  user_id: string
  profile_status: string
  demographics_json: Record<string, unknown>
  medical_flags_json: Record<string, unknown>
  activity_json: Record<string, unknown>
  anthropometrics_json: Record<string, unknown>
  sensitive: Record<string, unknown>
  current_version_id?: string | null
  created_at: string
  updated_at: string
}

export interface PlanPhase {
  phase_number: number
  week_start: number
  week_end: number
  objective: string
  calorie_target?: number | null
  macro_targets_json: Record<string, unknown>
  habits_json: unknown[]
  success_metrics_json: unknown[]
}

export interface PlanRecord {
  id: string
  participant_id: string
  profile_id: string
  title: string
  duration_weeks: number
  goal_category: string
  status: string
  current_version_id?: string | null
  created_at: string
  updated_at: string
}

export interface VersionRecord {
  id: string
  version_number: number
  summary?: string | null
  snapshot_json: Record<string, unknown>
  change_summary_json: Array<{ field: string; summary: string; before?: unknown; after?: unknown }>
  created_at: string
}

export interface DeclarationRecord {
  id: string
  package_number: string
  participant_id: string
  profile_id: string
  plan_id: string
  state: 'draft' | 'submitted' | 'withdrawn' | 'corrected' | 'voided'
  submitted_at?: string | null
  withdrawn_at?: string | null
  voided_at?: string | null
  accepted_at?: string | null
  review_due_at?: string | null
  current_review_assignment_id?: string | null
  created_at: string
  updated_at: string
}

export interface DeliveryFileRecord {
  id: string
  package_id: string
  file_type: string
  display_name: string
  mime_type: string
  checksum_sha256: string
  size_bytes: number
  version_label?: string | null
  is_final: boolean
  created_at: string
}

export interface AuditLogRecord {
  id: string
  occurred_at: string
  actor_user_id?: string | null
  action_type: string
  entity_type: string
  entity_id: string
  metadata_json: Record<string, unknown>
  previous_hash?: string | null
  entry_hash: string
}

export interface UserRecord {
  id: string
  username: string
  full_name: string
  email_optional?: string | null
  role: string
  status: string
  is_active: boolean
  force_password_change: boolean
  created_at: string
}
