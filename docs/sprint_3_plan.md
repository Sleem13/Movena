# Sprint 3 Plan

## Goal

Improve the existing Squat Analyzer MVP’s reliability, testability, safety, and clinical defensibility before model training or exercise expansion.

## Scope

- Audit and curate custom squat fixtures for rule validation.
- Centralize and document transparent rule thresholds.
- Harden multipart video validation, size limits, temporary-file cleanup, and error contracts.
- Add automated endpoint and React UI tests.
- Stabilize API and medical-safety documentation.

## Non-goals

No model training, new exercises, authentication, database, production deployment, diagnostic claims, or architectural redesign.

## Deliverables

- Dataset audit and curated rule-validation split.
- Reviewable threshold configuration and physiotherapy review notes.
- Stable success/error schemas and hardened upload endpoint.
- Backend upload tests and frontend Vitest/Testing Library tests.
- API contract, QA checklist, README commands, and safety wording.

## Acceptance Criteria

- Every requested audit, split, threshold, API, plan, and checklist artifact exists.
- Unlabeled videos are excluded from official rule validation.
- Thresholds are imported from one configuration module rather than embedded in analysis logic.
- Missing, unsupported, mismatched MIME, empty, oversized, unreadable, and no-pose uploads return clean JSON.
- Temporary uploads are deleted after success and failure.
- Backend and frontend automated suites pass, the frontend production build passes, and a real Sprint 2 fixture still returns a successful report.
- No prohibited scope is added.

## Risks

- Tiny, imbalanced, non-independent data limits any threshold conclusion.
- Folder labels may not be expert ground truth.
- 2D angle and valgus proxies are view-dependent.
- MIME headers can be spoofed; decoding remains the content validity check.
- In-memory video processing can still be CPU-intensive below the size limit.
- Composite movement scores may imply more clinical precision than validated.

## Test Plan

1. Run dataset structure and metadata preparation checks.
2. Run all Python tests, including threshold and upload-contract tests.
3. Run frontend unit/component tests and production build.
4. Start FastAPI and test health, bad uploads, and the real correct-squat fixture.
5. Confirm error envelopes, cleanup, response fields, limitations, and disclaimer.
6. Review generated split counts and documentation links.
