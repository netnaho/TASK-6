from enum import StrEnum


class Role(StrEnum):
    PARTICIPANT = "participant"
    REVIEWER = "reviewer"
    ADMINISTRATOR = "administrator"


class UserStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


class ProfileStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class DeclarationState(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    WITHDRAWN = "withdrawn"
    CORRECTED = "corrected"
    VOIDED = "voided"


class ReviewAssignmentStatus(StrEnum):
    QUEUED = "queued"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    REASSIGNED = "reassigned"
    CANCELLED = "cancelled"


class CorrectionStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESUBMITTED = "resubmitted"
    CLOSED = "closed"


class DeliveryFileType(StrEnum):
    FINAL_PLAN_PDF = "final_plan_pdf"
    SUPPORTING_RAW_EXPORT = "supporting_raw_export"
    REVISION_NOTE = "revision_note"
    IMPORT_SOURCE = "import_source"
    ACCEPTANCE_RECEIPT = "acceptance_receipt"
    BULK_PACKAGE = "bulk_package"


class NotificationType(StrEnum):
    STATUS_CHANGE = "status_change"
    MENTION = "mention"
    REVIEW_REQUEST = "review_request"
    DEADLINE_WARNING = "deadline_warning"
    MANDATORY_COMPLIANCE_ALERT = "mandatory_compliance_alert"


class NotificationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ImportExportFormat(StrEnum):
    CSV = "csv"
    XLSX = "xlsx"


class EntityType(StrEnum):
    PROFILE = "profile"
    PLAN = "plan"
    DECLARATION = "declaration"


class ExportScopeType(StrEnum):
    DECLARATIONS = "declarations"


class JobRunStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
