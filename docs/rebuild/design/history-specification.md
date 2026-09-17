# Saved analysis history

Active analysis work is recovered from the owner-scoped replacement lifecycle list
when the independent analysis screen is reopened. Only queued or running jobs are
restored; terminal records remain in history. Recovery resumes polling without
requiring the original video to be selected again.

Progress opens a newest-first history with twenty records per page. A status
selector shows all outcomes, successful analyses, rejected inputs or errors.
Changing the filter returns to the first page. Older/newer buttons use logical
layout order, wrap on small screens and have at least 48-point touch targets.
An explicit refresh reloads the current page; paging uses the existing live
offset API, not a frozen snapshot.

Each record shows the localized exercise name, localized timestamp, outcome and
available repetitions. Rejected/error records never display successful counts.
A real zero remains zero; null/non-finite values remain unavailable. The full
record opens on selection. Unknown historical statuses use a neutral label.
Do not average different exercises or infer clinical improvement from this list.

Show loading and retry states inside the list, leaving filters and the newer-page
control reachable after an offline failure. An empty filtered result explains
that no records match; an empty history points to independent analysis. If a live
page becomes empty after records change, newer-page navigation still works.
There is no optimistic deletion or local persistence of health records.

Use white/dark surfaces, blue controls and existing typography. Status is text,
not color alone. Arabic mirrors navigation and localizes dates/numbers. Native
rows grow for 200% text scaling; web rows and controls wrap without overflow.
Contracts retain the legacy list/detail schema and object-level authorization.
