# Data Model And Relationships

## Core entities

### `users`
- identity: `id`, `username`, `email_optional`, `full_name`, `role`, `status`, `is_active`, `force_password_change`
- auth state: `password_hash`, `failed_login_attempts`, `locked_until`, `last_login_at`, `captcha_required`
- admin metadata: `disabled_reason`, `created_by`, `updated_by`, timestamps
- relationships:
  - one-to-many `password_history`
  - one-to-many `refresh_tokens`
  - one-to-one `notification_preferences`
  - one-to-many `participant_profiles`
  - one-to-many `nutrition_plans`
  - one-to-many `declaration_packages` as participant owner
  - one-to-many `review_assignments` as reviewer
  - one-to-many `audit_logs` as actor

### `password_history`
- `id`, `user_id`, `password_hash`, `created_at`
- stores last 5 hashes for reuse prevention

### `refresh_tokens`
- `id`, `user_id`, `token_hash`, `expires_at`, `revoked_at`, `rotated_from_id`, `issued_at`, `last_used_at`, `user_agent`
- one active family per session, rotated on refresh

### `notification_preferences`
- `id`, `user_id`
- booleans for mutable non-critical categories: `status_changes_enabled`, `mentions_enabled`, `review_requests_enabled`, `deadline_warnings_enabled`
- mandatory alerts are not disable-able and are omitted from preferences toggles

### `participant_profiles`
- identity: `id`, `user_id`, `profile_status`, timestamps
- structured health fields: demographics, medical flags, allergies, medications, dietary restrictions, activity baseline, anthropometrics, wellness risks
- sensitive fields stored encrypted: diagnoses notes, medications detail, allergy detail, pregnancy detail, clinician notes, sensitive free-text
- version pointer: `current_version_id`
- relationships:
  - one-to-many `participant_profile_versions`
  - one-to-many `declaration_packages`

### `participant_profile_versions`
- `id`, `profile_id`, `version_number`, `snapshot_json`, `change_summary_json`, `created_by`, `created_at`
- append-only snapshots used for history and diff views

### `nutrition_plans`
- `id`, `participant_id`, `profile_id`, `title`, `duration_weeks`, `goal_category`, `status`, `current_version_id`, timestamps
- relationships:
  - one-to-many `nutrition_plan_versions`
  - one-to-many `declaration_packages`

### `nutrition_plan_versions`
- `id`, `plan_id`, `version_number`, `summary`, `phase_count`, `snapshot_json`, `change_summary_json`, `created_by`, `created_at`
- append-only plan versions

### `plan_phases`
- stored within version snapshot or normalized child table if query demand warrants it; chosen design: normalized children linked to version
- fields: `id`, `plan_version_id`, `phase_number`, `week_start`, `week_end`, `objective`, `calorie_target`, `macro_targets_json`, `habits_json`, `success_metrics_json`

### `declaration_packages`
- `id`, `package_number`, `participant_id`, `profile_id`, `plan_id`, `current_plan_version_id`, `current_profile_version_id`
- lifecycle: `state` in `draft|submitted|withdrawn|corrected|voided`
- workflow: `submitted_at`, `withdrawn_at`, `voided_at`, `accepted_at`, `review_due_at`, `current_review_assignment_id`
- relationships:
  - one-to-many `declaration_state_history`
  - one-to-many `correction_requests`
  - one-to-many `package_versions`
  - one-to-many `delivery_files`
  - one-to-many `download_tokens`
  - one-to-many `acceptance_confirmations`

### `package_versions`
- `id`, `package_id`, `version_number`, `state`, `profile_version_id`, `plan_version_id`, `snapshot_json`, `change_summary_json`, `created_by`, `created_at`
- captures relevant record versions per package state milestone

### `declaration_state_history`
- `id`, `package_id`, `from_state`, `to_state`, `reason_code`, `reason_text`, `changed_by`, `changed_at`
- append-only canonical lifecycle record

### `review_assignments`
- `id`, `package_id`, `reviewer_id`, `assigned_at`, `review_due_at`, `priority`, `status`
- status examples: `queued`, `in_review`, `completed`, `reassigned`, `cancelled`

### `correction_requests`
- `id`, `package_id`, `review_assignment_id`, `requested_by`, `requested_at`, `response_due_at`, `status`
- structured feedback: `sections_json`, `overall_message`, `participant_acknowledged_at`, `participant_resubmitted_at`
- statuses: `open`, `acknowledged`, `resubmitted`, `closed`

### `delivery_files`
- `id`, `package_id`, `file_type`, `display_name`, `storage_path`, `mime_type`, `checksum_sha256`, `size_bytes`, `version_label`, `is_final`, `created_by`, `created_at`
- file types: `final_plan_pdf`, `supporting_raw_export`, `revision_note`, `import_source`, `acceptance_receipt`

### `download_tokens`
- `id`, `package_id`, `delivery_file_id`, `issued_to_user_id`, `token_hash`, `expires_at`, `revoked_at`, `used_at`, `issued_by`, `purpose`
- used for expiring links and permission revalidation

### `acceptance_confirmations`
- `id`, `package_id`, `confirmed_by`, `confirmed_at`, `confirmation_note`, `accepted_delivery_version`

### `notifications`
- `id`, `user_id`, `type`, `severity`, `title`, `message`, `link_path`, `is_read`, `is_muted_snapshot`, `created_at`, `expires_at`
- types include `status_change`, `mention`, `review_request`, `deadline_warning`, `mandatory_compliance_alert`
- severity examples: `info`, `warning`, `critical`

### `mentions`
- `id`, `notification_id`, `source_type`, `source_id`, `mentioned_by`, `mentioned_user_id`

### `import_jobs`
- `id`, `created_by`, `format`, `source_file_id`, `mapping_id`, `status`, `row_count`, `success_count`, `failure_count`, `checksum_sha256`, `started_at`, `completed_at`, `error_report_path`

### `export_jobs`
- `id`, `created_by`, `format`, `scope_type`, `masking_policy_id`, `status`, `row_count`, `checksum_sha256`, `output_file_id`, `started_at`, `completed_at`

### `field_mappings`
- `id`, `name`, `entity_type`, `format`, `mapping_json`, `is_active`, `created_by`, timestamps
- admin-defined import/export field mapping rules

### `masking_policies`
- `id`, `name`, `entity_type`, `rules_json`, `is_default`, `created_by`, timestamps
- example rules: redact diagnoses free-text, partial mask birth date, mask phone/email, aggregate metrics

### `audit_logs`
- `id`, `occurred_at`, `actor_user_id`, `action_type`, `entity_type`, `entity_id`, `ip_address`, `request_id`, `metadata_json`, `previous_hash`, `entry_hash`
- append-only immutable chain with hash-linking for tamper evidence

### `scheduler_job_runs`
- `id`, `job_name`, `started_at`, `finished_at`, `status`, `details_json`

### `system_settings`
- `id`, `key`, `value_json`, `updated_by`, `updated_at`
- includes local captcha toggle, download expiry defaults, notification retention, queue SLA defaults

## Relationship summary

- one `user` may own one `participant_profile` and many `nutrition_plans`
- one `participant_profile` has many profile versions
- one `nutrition_plan` has many plan versions; each plan version has many phases
- one `declaration_package` references current profile and plan versions and has many version snapshots, state changes, corrections, deliveries, tokens, and acceptance confirmations
- one `review_assignment` belongs to one package and one reviewer
- one `correction_request` belongs to one package and one review assignment
- one `delivery_file` may have many download tokens
- one `audit_log` records each critical action with tamper-evident chaining

## Versioning strategy

- profile updates create a new `participant_profile_versions` row
- plan changes create a new `nutrition_plan_versions` row and phase rows
- package submission, correction, withdrawal, and void operations create new `package_versions` rows capturing relevant linked version ids and change summary
- change summary JSON stores field-level diff labels, human-readable text, actor, and timestamp for the UI "What changed" panel
