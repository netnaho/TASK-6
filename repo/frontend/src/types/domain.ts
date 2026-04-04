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
  profile_version_id?: string | null
  plan_version_id?: string | null
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
  package_id: string | null
  file_type: string
  display_name: string
  mime_type: string
  checksum_sha256: string
  size_bytes: number
  version_label?: string | null
  is_final: boolean
  allowed_roles: string[]
  created_at: string
}

export interface ImportJobRecord {
  id: string
  created_by: string
  format: string
  source_file_id?: string | null
  mapping_id?: string | null
  status: string
  row_count: number
  success_count: number
  failure_count: number
  checksum_sha256?: string | null
  started_at?: string | null
  completed_at?: string | null
  created_at: string
}

export interface ExportJobRecord {
  id: string
  created_by: string
  format: string
  scope_type: string
  masking_policy_id?: string | null
  status: string
  row_count: number
  checksum_sha256?: string | null
  output_file_id?: string | null
  started_at?: string | null
  completed_at?: string | null
  created_at: string
}

export interface ImportJobDetail {
  job: ImportJobRecord
  source_file?: DeliveryFileRecord | null
  errors: Array<{ row: number; error: string; row_data: Record<string, unknown> }>
  preview_rows: Array<Record<string, unknown>>
}

export interface ExportJobDetail {
  job: ExportJobRecord
  output_file?: DeliveryFileRecord | null
  preview_rows: Array<Record<string, unknown>>
}

export interface StateHistoryRecord {
  id: string
  to_state: string
  reason_code?: string | null
  reason_text?: string | null
  changed_at: string
}

export interface ReviewContext {
  package: DeclarationRecord
  history: {
    versions: VersionRecord[]
    state_history: StateHistoryRecord[]
  }
  profile_version?: {
    id: string
    version_number: number
    snapshot_json: Record<string, unknown>
    change_summary_json: Array<{ field: string; summary: string; before?: unknown; after?: unknown }>
    created_at: string
  } | null
  plan_version?: {
    id: string
    version_number: number
    summary?: string | null
    snapshot_json: Record<string, unknown>
    change_summary_json: Array<{ field: string; summary: string; before?: unknown; after?: unknown }>
    created_at: string
  } | null
  corrections: Array<Record<string, any>>
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
