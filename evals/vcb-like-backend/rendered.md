# VCB-like Job API control-plane cases

> Mode: security-control

## Assumptions

- Actor identity is injected by middleware before controller execution.
- Audit and idempotency services are implemented outside the sample controller.

## Coverage Map

| Source/Test Point | Priority | Status | Cases |
| --- | --- | --- | --- |
| REQ-AUTH-001 | P0 | covered | TC-JOB-001 |
| REQ-RES-001 | P0 | covered | TC-JOB-002, TC-JOB-003 |
| REQ-SCOPE-001 | P0 | covered | TC-JOB-004 |
| REQ-IDMP-001 | P0 | covered | TC-JOB-005, TC-JOB-006 |
| REQ-AUDIT-001 | P1 | covered | TC-JOB-003 |
| TP-E2E-001 |  | covered | TC-JOB-002, TC-JOB-003 |
| TP-API-001 |  | covered | TC-JOB-001 |
| TP-API-002 |  | covered | TC-JOB-005, TC-JOB-006 |

## Cases

| ID | Priority | Level | Type | Title | Traceability | Expected |
| --- | --- | --- | --- | --- | --- | --- |
| TC-JOB-001 | P0 | api | security | Reject missing actor identity when reading Job | REQ-AUTH-001, CODE:input-controller.java:JobController.getJob, RULE:VCB-AUTH-01, RISK-001, TP-API-001 | HTTP status is 401 or documented auth failure code. [response] |
| TC-JOB-002 | P0 | api | security | Reject cross-user Job read | REQ-RES-001, CODE:input-controller.java:JobController.getJob, RULE:VCB-RES-01, RISK-001, TP-E2E-001 | HTTP status is 403 and response body does not include B's Job data. [response]<br>Denial is recorded with actor/resource/action/result/request_id when request_id is present. [log] |
| TC-JOB-003 | P0 | api | security | Reject cross-user Job close and preserve state | REQ-RES-001, REQ-AUDIT-001, CODE:input-controller.java:JobController.closeJob, RULE:VCB-RES-02, RULE:VCB-AUDIT-01, RISK-001, TP-E2E-001 | HTTP status is 403. [response]<br>Job B remains RUNNING. [db]<br>Audit contains actor=A, resource=job-b-001, action=close, result=forbidden, request_id=rid-cross-user-001. [log]<br>owner_forbidden metric increments by 1. [metric] |
| TC-JOB-004 | P0 | api | negative | Reject Job close when scope scene does not match | REQ-SCOPE-001, CODE:input-controller.java:CloseRequest, RULE:VCB-SCOPE-01, RISK-001 | HTTP status is 403 and mutation is not applied. [response]<br>cross_scene_reject metric increments by 1. [metric] |
| TC-JOB-005 | P0 | api | boundary | Replay request_id within 5 minute window does not repeat close mutation | REQ-IDMP-001, CODE:input-controller.java:CloseRequest.requestId, RULE:VCB-IDMP-01, RISK-001, TP-API-002 | Within the 5 minute window the mutation is not repeated and documented prior-result behavior is returned. [response]<br>Job A is closed only once. [db] |
| TC-JOB-006 | P1 | integration | regression | Concurrent same request_id only applies one close mutation | REQ-IDMP-001, CODE:input-controller.java:JobController.closeJob, RULE:VCB-IDMP-02, RISK-001, TP-API-002 | Exactly one mutation is applied; the others return documented idempotent duplicate behavior. [db]<br>idempotent_drop metric increments for duplicate requests. [metric] |

## Open Questions

| ID | Question | Impact | Owner |
| --- | --- | --- | --- |
| Q-001 | What is the documented status code for missing actor identity: 401 or 403? | affects_p1 | product |

## Quality Gates

| Gate | Status |
| --- | --- |
| p0_sources_covered | True |
| no_happy_path_only | True |
| all_cases_have_traceability | True |
| all_cases_have_observable_expected | True |
| boundary_cases_have_concrete_values | True |
| state_cases_include_invalid_transitions | True |
| security_cases_include_negative_authorization | True |
| e2e_layer_cross_check_complete | True |
