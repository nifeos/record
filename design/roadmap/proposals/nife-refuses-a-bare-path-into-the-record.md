---
status: PROPOSED
raised: 2026-11-24
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# nife refuses a bare path into the record

Raised by the documentation audit of 2026-11-24 (UTC), [the record's departure](../../audit-reports/2026-11-24-the-records-departure.md), findings 1, 5 and 7. Severity medium:
the class produced about 140 broken pointers in nife's front pages, briefs and skills in the week
after the record left, and no gate saw any of them.

Reuse: `packages/moved.toml` in nife, which already lists `design/` and `notes/` as departed and
says where they went, and the markdown-links section of nife's `script/lint`. No new dependency.

## The problem

A bare `design/...` or `notes/...` path in nife reads as a file in nife's checkout. For the design
record that file is no longer there. partsfoundry/nife#4071 turned the ones in `SECURITY.md`,
`README.md`, `CONTRIBUTING.md`, the briefs and the skills into links into partsfoundry/record, by a
one-off script. The same pointers remain in `AGENTS.md` (a lane does not edit it) and inside code
blocks and example output. Nothing stops a new one: a lane copying a sentence from the record
into nife writes the bare form, because that is how the record spells it.

## The work

- A `script/lint` section reads every markdown file and source comment in nife, finds each bare
  path under a directory `packages/moved.toml` lists as departed, and fails when the path is not in
  nife's tree. The message names the qualified form (`partsfoundry/record:<path>`) and the link form.
- The section starts as a ratchet with a baseline of the sites left today, `AGENTS.md`'s six among
  them, so it can land before anyone clears the baseline, and it only falls.
- The section reads code blocks too: an example that tells a reader to open a path should name one that
  opens. A path quoted from a dated log is exempt only by a marker on the same line.
