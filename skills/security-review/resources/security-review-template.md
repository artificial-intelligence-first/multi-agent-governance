# Security Review Template

**Change summary:**  
- Feature / component:  
- PR / ticket link:  
- Reviewer(s):  
- Date: %DATE%

## Scope
- Description of change
- Systems/components affected
- Data classified (PII, secrets, regulated?)
- Deployment plan & rollback steps

## Threat modeling (STRIDE)
- Spoofing:
- Tampering:
- Repudiation:
- Information disclosure:
- Denial of service:
- Elevation of privilege:

## Controls assessment
- Authentication updates:
- Authorization / RBAC changes:
- Secrets management:
- Network boundaries:
- Logging & monitoring:
- Dependency changes:

## Findings
| Severity | Description | Mitigation | Owner | Target date |
| --- | --- | --- | --- | --- |

## Risk evaluation
- Residual risk level (Low/Medium/High):
- Approval decision (approve with mitigations / block pending fixes):
- Follow-up actions / reminders:

## Sign-off
- GovernanceSAG reviewer:
- Date:

> Note: Update this template from `skills/security-review/resources/security-review-template.md` when policy changes. Replace `%DATE%` with the review date.
