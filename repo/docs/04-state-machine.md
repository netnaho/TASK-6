# Declaration Lifecycle State Machine

## States
- `draft`
- `submitted`
- `withdrawn`
- `corrected`
- `voided`

## Legal transitions

| From | To | Allowed Actor(s) | Conditions |
|---|---|---|---|
| `draft` | `submitted` | Participant | Profile complete, active plan selected, package passes validation, participant account active |
| `draft` | `voided` | Administrator | Invalid duplicate or administrative cancellation before submission |
| `submitted` | `withdrawn` | Participant | No final acceptance recorded and package not voided |
| `submitted` | `corrected` | Reviewer or Administrator | Structured correction request recorded |
| `submitted` | `voided` | Administrator | Administrative void with mandatory reason |
| `withdrawn` | `draft` | Participant | Reopen withdrawn package before archival window closes |
| `withdrawn` | `voided` | Administrator | Administrative void with mandatory reason |
| `corrected` | `submitted` | Participant | Correction acknowledged and resubmission payload saved |
| `corrected` | `voided` | Administrator | Administrative void with mandatory reason |

## Rejected transitions

- `draft -> corrected`
- `draft -> withdrawn`
- `submitted -> draft`
- `withdrawn -> submitted`
- `corrected -> draft`
- `corrected -> withdrawn`
- `voided -> any`
- self-transition without explicit versioning action

## Workflow notes

- `corrected` means the package is in a participant-action-required state following reviewer feedback
- resubmission moves `corrected -> submitted` and preserves full correction history
- withdrawal is participant-initiated and reversible only to `draft`
- void is terminal and administrative only
- every legal transition writes:
  - `declaration_state_history`
  - `package_versions`
  - immutable `audit_logs`
  - notifications to relevant parties

## Role and state gated actions

### Participant
- `draft`: edit package, edit linked profile/plan, submit, delete local draft attachments if not referenced elsewhere
- `submitted`: view status, withdraw, comment, download permitted artifacts
- `withdrawn`: reopen to draft, inspect history
- `corrected`: acknowledge correction, update linked records, resubmit, inspect prior versions and feedback
- `voided`: view-only history

### Reviewer
- `submitted`: claim assignment, review package, request corrections, upload revision notes, issue mentions, generate review outputs
- `corrected`: view waiting status and prior feedback, no new correction until resubmission
- `withdrawn` or `voided`: view-only if assigned previously

### Administrator
- all states: view and audit
- `draft`, `submitted`, `withdrawn`, `corrected`: void with required reason
- manage deadlines, reassign reviewer, regenerate download link, manage delivery permissions, run import/export, manage users
