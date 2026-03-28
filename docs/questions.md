# Required Document Description: Business Logic Questions Log

## State transition for "withdrawn" declarations
**Question:** The prompt mentions status states such as "draft, submitted, withdrawn, corrected, and voided", and that "a voided record cannot be corrected", but it does not specify what actions are allowed from a "withdrawn" state.
**My Understanding:** A withdrawn declaration should revert to a "draft" state to allow the participant to make necessary changes before re-submitting.
**Solution:** Implement state machine logic where transitioning to "withdrawn" allows a subsequent transition back to "draft" or directly to "submitted".

## Review deadline assignment
**Question:** Reviewers work from a queue highlighting "upcoming deadlines", but there's no specification on how these deadlines (e.g., "review due by 04/15/2026 5:00 PM") are calculated or assigned.
**My Understanding:** There should be a standard Service Level Agreement (SLA), such as 5 business days, triggered from the moment a participant submits a declaration.
**Solution:** Add a system configuration for review SLA in days/hours and calculate a deadline timestamp automatically upon the "submitted" status transition.

## Client acceptance confirmation
**Question:** For delivery and asset distribution, the prompt states it "requires client acceptance confirmation," but doesn't detail who acts as the "client" in this context.
**My Understanding:** In this workplace wellness program setting, the "client" consuming the final nutritional plan is the Participant (employee).
**Solution:** Implement an "Accept Delivery" action/button for the Participant role on the delivery package UI, securely logging the timestamp and user ID of the acceptance.

## Participant registration approval flow
**Question:** The prompt states "Participants can register and sign in locally", but there is no mention if their registration requires Administrator or Reviewer approval before gaining full access.
**My Understanding:** To maintain a secure environment, self-registered accounts should require admin activation or be validated against an internal employee roster.
**Solution:** Implement a "Pending Approval" state for newly registered participant accounts that require Administrator verification before login or full submission capabilities are granted.

## Reviewer queue assignment mechanism
**Question:** The prompt mentions "Reviewers work from a queue", but doesn't specify if cases are automatically assigned to specific reviewers or if Reviewers pick from a common pool.
**My Understanding:** A common pool where Reviewers manually claim "submitted" cases prevents bottlenecks if a specific Reviewer is unavailable.
**Solution:** Create a shared queue for Reviewers with a "Claim Case" action, assigning the specific declaration ID to the claiming Reviewer's direct workload.

## Account lockout resolution
**Question:** The prompt specifies "account lockout for 15 minutes after 5 failed attempts." Does a locked account automatically unlock after 15 minutes, or can an Administrator manually unlock it sooner?
**My Understanding:** While it should automatically unlock after 15 minutes as stated, Administrators should also have the capability to unlock accounts manually to provide immediate support.
**Solution:** Implement an automated validation at login to clear lockouts > 15 minutes old, and add an "Unlock Account" override button in the Admin account management panel.

## "Draft" versioning history triggers
**Question:** Participants can view "prior versions with clear 'what changed' summaries." Does this versioning apply to every incremental save of a "draft" or only upon state transitions?
**My Understanding:** Creating a new version on every single autosave of a draft could bloat the database. Versions should be snapshotted only upon significant actions.
**Solution:** Create an immutable version record in the database only when a declaration is "submitted", "corrected", "withdrawn", or transitions between major phases.

## Data Export masking policy definition
**Question:** The prompt mentions "exports can be masked by policy," but does not clarify who defines these policies or if they are dynamic.
**My Understanding:** Administrators need the ability to configure distinct export profiles that define which fields are masked/hidden for different compliance scenarios.
**Solution:** Create a "Data Export Policies" management interface for Administrators to toggle fields as visible, masked, or hidden, and apply the selected policy during the offline export generation.
