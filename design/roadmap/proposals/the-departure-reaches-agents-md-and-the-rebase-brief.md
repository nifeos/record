---
status: PROPOSED
raised: 2026-11-24
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# The departure reaches `AGENTS.md` and the rebase brief

Raised by the documentation audit of 2026-11-24 (UTC), [the record's departure](../../audit-reports/2026-11-24-the-records-departure.md), findings 7 and 8. Severity medium
for both: one is the file every agent reads first, and the other is a brief a lane follows step by
step.

Reuse: every item edits a file that exists. No new dependency. Item 1 edits nife's `AGENTS.md`,
which a lane does not edit, so it goes to an architect with its pull request.

## The work

1. nife's `AGENTS.md` names where the design record lives. Six of its lines send a reader to
   paths nife no longer holds: `notes/project-metrics.md`, `notes/how-this-is-built.md` and four
   mentions of `design/decisions/`. Each becomes a link into nifeos/record, or a sentence that
   says the decisions are there.
2. nife's `briefs/rebase-onto-main.md` names only the conflicts a nife branch can still meet. Of
   its nine conflict classes, four are about files that left with the record:
   `design/roadmap/README.md` (class 1), `notes/benchmarks*` (class 3), the decisions index and
   `script/decisions --check` (part of class 4) and the milestone blocks with
   `script/roadmap --migrate` (classes 8 and 9). Its closing gate runs `script/roadmap --check`.
   None of those scripts is in nife. The brief keeps the classes that remain (bench files, a
   renamed heading, `AGENTS.md`, shell scripts under `helpers/`) and drops the rest; the record's
   own conflicts, if they need a brief, get one here.
