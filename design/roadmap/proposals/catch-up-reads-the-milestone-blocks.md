---
status: PROPOSED
raised: 2026-11-17
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# `script/catch-up` reads the milestone blocks

Raised by the documentation audit of 2026-11-17 (UTC),
[the newcomer path](../../audit-reports/2026-11-17-the-newcomer-path.md), finding 1. Restated by
the documentation audit of 2026-11-24 (UTC), [the record's
departure](../../audit-reports/2026-11-24-the-records-departure.md), finding 9. Severity: high for
the newcomer path. nife's README offers `script/catch-up` in its Try it block as the way to learn
what changed, and it does not answer.

Reuse: `parse_blocks` in nifeos/nife:script/catch-up, `helpers/roadmap_block.status_and_built`
and this repository's `script/roadmap --index`. No new dependency.

## The problem

`script/catch-up` reads milestone status from `design/roadmap/` in nife's own history. The
roadmap left nife with the rest of the design record. At nife's `main` there is no block to read.
The script says so and exits 1 before it prints anything else. Its message begins
`catch-up: no roadmap at HEAD`.

The refusal is honest. The 2026-11-17 audit found an empty report instead, which was worse. But
the README's command now gives a newcomer nothing. That includes the half that never needed the
roadmap: the merged pull requests and the commits of the window.

## The work

- The milestone half reads the blocks from nifeos/record. It takes a checkout named on the
  command line or found beside nife's. With no record to read, it prints the rest of its report.
  One line says the milestone half needs the record, and it exits 0.
- A window that starts before the move reads its old end from nife's history. It reads the new
  end from the record. It compares numbers and statuses, not sources, so the move does not read
  as every milestone removed.
- A host test runs the script over two fixed windows and checks the counts it prints. One window
  lies inside nife's history alone and one crosses the move.
