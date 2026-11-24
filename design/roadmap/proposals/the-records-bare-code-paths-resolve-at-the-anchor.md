---
status: PROPOSED
raised: 2026-11-24
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# The record's bare code paths resolve at the anchor

Raised by the documentation audit of 2026-11-24 (UTC), [the record's departure](../../audit-reports/2026-11-24-the-records-departure.md), finding 10. Severity low for any one
page and medium for the class: a reader following one of these paths finds nothing at any commit.

Reuse: `helpers/qualified_paths.py`, which resolves `partsfoundry/<repo>:<path>` at basalt's pin, and
`helpers/nife_tree.py`, which already fetches nife's tree. No new dependency.

## The problem

§201 (one roadmap until a citation has to cross) says a bare code path in a record written before
the move means that path at the anchor, the last nife commit before the record left, which nife's
`packages/moved.toml` names. Nothing checks that such a path existed at the anchor. A count over
`notes/` finds 259 bare code paths in 167 notes that do not exist at the anchor either: crates that
took a new name or left before the move (`crates/moho_abi`, `crates/grant_plan`, `crates/slots`),
programs renamed (`components/src/swish.rs`) and helpers removed. Some matches are other projects'
paths (Linux's `kernel/printk/`) or paths quoted in a dated run log, so the true count is lower.
`notes/documentation-audit.md`, the procedure this audit follows, is one of them: it cites
`crates/moho_abi/src/lib.rs`, `crates/virtio` and `system_tests/src/user/tests.rs`.

## The work

- A `script/lint` section reads each bare code path in `notes/` and `design/` and fails when it
  is in neither the anchor's tree nor this repository's. It starts as a ratchet with today's sites
  as its baseline, one sorted entry per line, and only falls.
- A path that names another project, or one quoted in a dated log, takes a marker on its line, so
  the exemption is visible where the reader meets it.
- The fixes themselves are ordinary lanes, most of them qualifying the path (`partsfoundry/moho_abi:`,
  `partsfoundry/grant_plan:`) or naming the crate's present home.
