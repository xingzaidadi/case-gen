# Mobile Job Control Design

## Requirements

REQ-AUTH-001: Every protected Job API must reject requests without `actor_open_id`.

REQ-RES-001: A user can read only jobs where `owner_open_id` equals their `actor_open_id`.

REQ-SCOPE-001: Mutating Job APIs must reject requests when `scene_type` and `scene_chat_id` do not match the issued scope.

REQ-IDMP-001: Mutating Job APIs must use `request_id` idempotency. Replaying the same `request_id` inside the 5 minute window must not repeat the mutation.

REQ-AUDIT-001: Authorization denials must emit audit evidence with actor, resource, action, result, and request_id.

## Test Data

- User A: `actor_open_id=A`
- User B: `actor_open_id=B`
- Job A: `job_id=job-a-001`, `owner_open_id=A`
- Job B: `job_id=job-b-001`, `owner_open_id=B`

