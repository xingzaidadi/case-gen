Feature: VCB-like Job API control-plane cases

  @p0 @api @security
  Scenario: TC-JOB-001 Reject missing actor identity when reading Job
    Given Job A exists.
    When Call read Job without actor identity.
    Then HTTP status is 401 or documented auth failure code.

  @p0 @api @security
  Scenario: TC-JOB-002 Reject cross-user Job read
    Given Job B belongs to user B.
    When Call read Job as user A for user B's resource.
    Then HTTP status is 403 and response body does not include B's Job data.
    And Denial is recorded with actor/resource/action/result/request_id when request_id is present.

  @p0 @api @security
  Scenario: TC-JOB-003 Reject cross-user Job close and preserve state
    Given Job B status is RUNNING.
    When Call close Job as user A for user B's resource.
    Then HTTP status is 403.
    And Job B remains RUNNING.
    And Audit contains actor=A, resource=job-b-001, action=close, result=forbidden, request_id=rid-cross-user-001.
    And owner_forbidden metric increments by 1.

  @p0 @api @negative
  Scenario: TC-JOB-004 Reject Job close when scope scene does not match
    Given User A owns Job A.
    When Call close Job with mismatched scene scope.
    Then HTTP status is 403 and mutation is not applied.
    And cross_scene_reject metric increments by 1.

  @p0 @api @boundary
  Scenario: TC-JOB-005 Replay request_id within 5 minute window does not repeat close mutation
    Given User A owns Job A and Job A is RUNNING.
    When Submit close request with request_id=rid-close-001.
    And Replay the same request at 4min59s, 5min, and 5min01s according to product policy.
    Then Within the 5 minute window the mutation is not repeated and documented prior-result behavior is returned.
    And Job A is closed only once.

  @p1 @integration @regression
  Scenario: TC-JOB-006 Concurrent same request_id only applies one close mutation
    Given User A owns Job A and Job A is RUNNING.
    When Send 10 concurrent close requests with the same request_id.
    Then Exactly one mutation is applied; the others return documented idempotent duplicate behavior.
    And idempotent_drop metric increments for duplicate requests.
