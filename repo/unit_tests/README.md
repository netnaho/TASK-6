# Unit Test Plan

Unit tests cover core business rules without requiring full HTTP execution and run against the isolated test configuration defined for `run_tests.sh`.

Mandatory suites:
- password policy
- password history reuse prevention
- account lockout
- token issuance and refresh rotation logic
- declaration lifecycle legal and illegal transitions
- correction workflow rules
- download expiry logic
- notification mute protections for mandatory alerts
- export masking rules
- checksum generation
- version diff summaries
- permission checks
