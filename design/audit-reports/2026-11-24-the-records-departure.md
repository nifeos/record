# Documentation audit, 2026-11-24: the record's departure

**Kind:** documentation. **Lens:** the record's departure from nife, read from both sides: every
pointer in nife's front pages, briefs, skills and kept notes to a `design/` or `notes/` path that now
lives only in nifeos/record, and every claim the record's front pages make about where a tool or a
file lives, with each one checked against the tree it names. **Findings:** fixed 5, minted 6,
accepted 1.

The finding to carry off is that the search a newcomer is told to use no longer reaches the design
record, and nothing else does. nife's `script/apropos` exists because strangers could not find the
network note or any decision; since the record left, it indexes only nife's own notes and module
headers, and this repository has no search of its own. nifeos/nife#4071 makes nife's pages say so.
A search over the record is minted as [a search that reaches the design
record](../roadmap/proposals/a-search-that-reaches-the-design-record.md).

## Why this lens

`script/audits` on `main` reported documentation DUE on milestones built 510 to 542 (+32, fires at
10). The security audit run the same day takes the graphical drivers' parsers; this sweep reads the
documents.

The window's largest change was not a milestone. The design record left nife under milestone 1018 (the
design record moves to `nifeos/record` and is published as a website), and nife removed `design/` and
most of `notes/` in one series. Every pointer nife's pages held into those directories went dead
that day, and the record's own pages kept describing tools that stayed behind. `script/audits
--worklist` cannot see this: it reads only this repository's history, so a move in nife's tree
leaves no trace in it, and the procedure's own `BUGS` already says a moved document ranks low.

### The two judgment questions, answered

Has a subsystem been rewritten inside its existing crate since the last sweep? **No crate was
rewritten in place.** The window's heaviest churn in nife is crates leaving for their own
repositories: `grant_plan` (8,596 changed lines, all removals), then `kernel/src`, `components/src`,
`filesystem_contract` and `device_tree_blob`. A crate that leaves is the departure's own class, and
finding 10 counts what it left behind in the notes.

Has a decision superseded a plan that a note still prescribes? **One.** §201 (one roadmap until a
citation has to cross) section 4 says a bare code path in a record written before the move means
that path at the anchor, the last nife commit before the record left. Nothing checks that such a
path existed there, and 259 do not (finding 10).

## How it was read

The scope was chosen from nife's history, not from the worklist. A first-parent diff of nife from
`343c64e95` (the last `main` commit before the previous documentation audit) to `main` listed every
path that changed. Each note here was scored by how many of the nife paths it cites changed and by
how many it cites that no longer exist, and the departure's own commits were read whole.

- nife's `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `AGENTS.md`, every brief under `briefs/`
  and every skill under `notes/skills/`: each bare `design/` or `notes/` path checked against nife's
  tree and this one. There were 139.
- nife's `script/apropos` and `script/catch-up`, run on nife's `main`, and the comment in
  `xtask/src/manual.rs` that describes what the search covers.
- The gate lists in nife's briefs, each command checked against nife's `script/`.
- This repository's `design/audit-reports/README.md`, `notes/documentation-audit.md` and the two
  open proposals the previous documentation audit minted, against the tree as it is now.
- Every bare code path in this repository's `notes/`, checked against nife's tree at the anchor
  that nife's `packages/moved.toml` names.

`script/audits --worklist` was then rechecked as nifeos/record#8 rebuilds it, reading nife's paths
at basalt's pin. Its list grows from 119 documents to 1,635, and its top entries are pages whose
cited nife code moved: `scripts.md` and `helpers-class-3.md` under milestone 902 (nife's tooling,
sorted by who needs it, before any of it moves), `consumers.md` under milestone 1027 (leaving the
central program table), `notes/lint-sections-generic-or-nife-only/nife-only.md`, milestone 902's
own block, milestone 407 (one definition of the numbers a kernel test and its program agree on),
two crate reviews and milestone 287 (`script/bootstrap` installs a working QEMU on Linux). This
sweep covers them only through finding 10, which counts their dead bare paths as a class. It read none of them sentence by sentence, and it
leaves the top of that list to the next documentation audit. Milestone 287 cites
`script/apropos`, whose claims finding 2 corrects in nife.

## Findings

### 1. FIXED: `SECURITY.md` and `README.md` sent a reader to files nife does not hold

`SECURITY.md` named 40 record paths as bare paths: the confinement claims, the audit reports, the
fatal risks. In a nife checkout none of them opens. `README.md`'s metrics chart linked
`notes/project-metrics.md`, which is gone. Three sentences also described the record as part of
nife's tree. Each path is now a link into nifeos/record, in nifeos/nife#4071. Severity medium:
`SECURITY.md` is the page a reporter reads.

### 2. FIXED: nife's pages promised a search over every decision

`CONTRIBUTING.md` said `script/apropos` searches "every note, decision and roadmap block" and gave
`script/apropos socket` as finding `notes/net.md` and the socket decisions. The script's own header
said the same, and a comment in `xtask/src/manual.rs` said the record is "searched there". Run on
nife's `main`, the socket search returns 16 crates and programs and no note or decision, and the
record has no search. All three now say what the search reaches, with an example that works, in
nifeos/nife#4071. Severity medium.

### 3. MINTED: nothing searches the design record

The pages finding 2 corrected now say the truth, and the truth is a gap: the decisions, the
milestone blocks and most notes are reachable only by browsing nifeos/record on GitHub. Severity
medium. Minted as [a search that reaches the design
record](../roadmap/proposals/a-search-that-reaches-the-design-record.md).

### 4. FIXED: two briefs gated a lane on a script nife no longer has

`briefs/gate-a-lane.md`, `briefs/gate-in-ci.md` and `briefs/README.md` told a lane to run
`script/roadmap --check` before pushing. The script left with the roadmap. A lane following the
brief stops on "not found". The gates are three now, in nifeos/nife#4071. Severity medium.

### 5. FIXED: bare record paths across `CONTRIBUTING.md`, the briefs and a skill

Beyond `SECURITY.md`, about 50 more bare record paths in `CONTRIBUTING.md` and eleven briefs became
links into nifeos/record, in nifeos/nife#4071: 88 links in all with finding 1. Left as they were:
paths inside code blocks and example output, spans holding a placeholder
(`design/decisions/<NNNN>-*.md`), and the decisions skill's description, whose length the skills
table checks. Severity low each, medium together. The class is minted under finding 6's gate.

### 6. MINTED: no gate refuses a bare path into the record

Every pointer in findings 1, 4 and 5 was written before the move and none was caught after it,
because nothing in nife's `script/lint` knows that `design/` and `notes/` left, although nife's
`packages/moved.toml` says so. Severity medium. Minted as [nife refuses a bare path into the
record](../roadmap/proposals/nife-refuses-a-bare-path-into-the-record.md), a ratchet that starts at
the sites left today.

### 7. MINTED: `AGENTS.md` names six paths nife does not hold

nife's `AGENTS.md`, which every agent reads first, sends a reader to `notes/project-metrics.md`,
`notes/how-this-is-built.md` and four times to `design/decisions/`. A lane does not edit it.
Severity medium. Minted as item 1 of [the departure reaches `AGENTS.md` and the rebase
brief](../roadmap/proposals/the-departure-reaches-agents-md-and-the-rebase-brief.md), for an
architect.

### 8. MINTED: the rebase brief resolves conflicts in files that left

Four of `briefs/rebase-onto-main.md`'s nine conflict classes are about files under `design/` or
`notes/benchmarks*`, and its steps run `script/decisions --check`, `script/roadmap --migrate` and
`script/roadmap --check`, none of which is in nife. Severity medium: a lane follows a brief step by
step. Minted as item 2 of the same proposal.

### 9. MINTED: the README's `script/catch-up` exits 1

The previous documentation audit found `script/catch-up` reporting no milestone changes with
exit 0. It now refuses rather than report zero, and since the roadmap left nife it refuses on
every run: it exits 1 before printing the merged pull requests and commits, the half
that never needed the roadmap. nife's README still offers it in the Try it block. Severity high for
the newcomer path. The open proposal, [`script/catch-up` reads the milestone
blocks](../roadmap/proposals/catch-up-reads-the-milestone-blocks.md), is rewritten to the present
problem: read the milestone half from this repository, and print the rest without it.

### 10. MINTED: 259 bare code paths in the notes resolve at no commit

§201 section 4 anchors a bare code path in an older record at the last nife commit before the move.
Checked against that tree, 259 bare code paths in 167 of this repository's 1,150 notes do not exist:
crates renamed or extracted before the move (`crates/moho_abi`, `crates/grant_plan`,
`crates/slots`), programs renamed and helpers removed. Some matches are other projects' paths or
quoted logs, so the true count is lower. `notes/documentation-audit.md`, the procedure this audit
follows, cites three. Severity low each, medium for the class. Minted as [the record's bare code
paths resolve at the
anchor](../roadmap/proposals/the-records-bare-code-paths-resolve-at-the-anchor.md).

### 11. FIXED: the audit README counted and edited in nife's tree

[`README.md`](README.md) said the ABI count is the surface of `crates/moho_abi`, which left nife.
`script/audits` reads `moho_abi` at the revision nife's `Cargo.lock` pins, and counts components and
external packages in nife's tree at basalt's pin. Its step 4 said `SECURITY.md` is part of the
audit's diff, but `SECURITY.md` is nife's, so that work goes in a nife pull request that the
report's waits on. Both sentences say so now, in this pull request. Severity low.

### 12. ACCEPTED: `SECURITY.md`'s audit count fails nife's lint when the pin moves

nife's `SECURITY.md` carries the number of security audits on the record, and nife's lint checks
it against this index at basalt's pin. When the pin moves past a commit that adds a security audit,
every nife pull request fails lint until one lane updates the number. That happened this week, when
the pin took in the graphical drivers' audit. It stays: the count is never wrong on `main` without
a red check saying so, and the fix is one line.

## What was deliberately not examined

- The notes behind the window's crate extractions, read crate by crate. Finding 10 counts their
  dead paths; the crate repositories' own documents are each crate's review.
- nife's own kept notes (`notes/` in nife) beyond their pointers into the record.
- The top of the rebuilt worklist (nifeos/record#8), read page by page. The next documentation
  audit starts there.
- ABI constants against their crate. The count did not move (99 to 99).
- The website the record is published as. It is not built yet.
- Fuzz findings and advisories.

## What wants a lane of its own

- [A search that reaches the design
  record](../roadmap/proposals/a-search-that-reaches-the-design-record.md), finding 3.
- [nife refuses a bare path into the
  record](../roadmap/proposals/nife-refuses-a-bare-path-into-the-record.md), finding 6.
- [The departure reaches `AGENTS.md` and the rebase
  brief](../roadmap/proposals/the-departure-reaches-agents-md-and-the-rebase-brief.md), findings 7
  and 8. Its `AGENTS.md` item needs an architect.
- [`script/catch-up` reads the milestone
  blocks](../roadmap/proposals/catch-up-reads-the-milestone-blocks.md), finding 9, rewritten.
- [The record's bare code paths resolve at the
  anchor](../roadmap/proposals/the-records-bare-code-paths-resolve-at-the-anchor.md), finding 10.
