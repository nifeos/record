# Working on the design record

This repository holds the design record of the nifeos projects: the decisions in
[design/decisions/](design/decisions/), the roadmap in [design/roadmap/](design/roadmap/), the
journeys, the fatal risks, the audits and the notes. The code it describes lives in
[nifeos/nife](https://github.com/nifeos/nife), and a record path that names code (`script/lint`,
`xtask/src/host.rs`) means that path in nife at the commit basalt's `main` pins.

## The lane skills live in nife

A lane here works by the same rules as a lane in nife, and nife keeps them, once. Read each one at the moment named, from nife's `main`:

- Before any work in a lane, read `nifeos/nife:notes/skills/developer-lane/SKILL.md`. It holds the
  claim, the handoff and where identified work goes.
- Before you brief, gate or merge a lane, read `nifeos/nife:notes/skills/maintainer/SKILL.md`.
- Before you choose between options, recommend one, or hold work for an architect, read
  `nifeos/nife:notes/skills/decisions/SKILL.md`.
- Before you mint or change a name, read `nifeos/nife:notes/skills/naming-authority/SKILL.md`.
- Before you commit or push, read `nifeos/nife:notes/skills/worktree-commits/SKILL.md`. Never use
  git stash, and never rewrite a pushed commit.
- Before you put a question or a report to an architect, read
  `nifeos/nife:notes/skills/working-with-the-architect/SKILL.md`.

nife's `AGENTS.md` holds the rest of the house rules (American spelling, no em-dashes, a document
states the rule in force now), and [design/tenets/](design/tenets/README.md) holds the reasons
behind them. The record's lint enforces the rules that read the record. One rule is the record's
own: each rule or fact has one home, and other files link to it ([the documentation
standard](design/tenets/documentation-standard.md#one-home-for-each-rule-or-fact) states it).

## Claiming a lane

`script/claim` is nife's claim, copied byte for byte together with the three helpers it runs
(`helpers/branch-name-check.sh`, `helpers/smelter-token`, `helpers/stash-block.sh`), until the
fleet repository the tooling ruling names exists (decided provisionally 2026-11-23 UTC). The copy
follows nife's file at the commit basalt's `main` pins, and the `claim_copy` section of
`script/lint` fails when they differ, printing the command that brings them level. A change to the
claim lands in nife first.

Two of its defaults are nife's. Pass `--worktree <dir>` or set `NIFE_WORKTREES`, since the default
root is `nife-worktrees` beside the checkout. And use `--new-work`: `--debt-paydown` opens the
draft with a `debt-paydown` label, which this repository does not have yet. The checks the claim
names in nife (its fleet lint and its pre-push hook) stay in nife.

## Scripts

- `script/lint` runs every gate the record holds itself to, one section at a time, and is what CI
  runs on a pull request and in the merge queue. `script/lint --list` names the sections and
  `script/lint --section <id>` runs one. For the length of a run it links nife's tree at the
  pinned commit into this one (`helpers/nife_tree.py`), so a check that resolves a nife path finds
  it. The header of `script/lint` says how, and why nobody edits through those links.
- `script/roadmap` validates and reports the milestones in design/roadmap/ (`--check`, `--ready`,
  `--outstanding`).
- `script/decisions` validates and indexes the decisions in design/decisions/.
- `script/journeys` reports progress against the journeys in design/journeys/.
- `script/citations` checks that a citation says what it cites and a quotation still says what it
  quoted (`--check`, `--ratchet`, `--moved`).
- `script/fatal-risks` checks that design/fatal-risks/ agrees with the records it cites.
- `script/audits` says when the next audit is due and checks the audit index in
  design/audit-reports/.
- `script/review-status` reads the outside reviews of the crates, one row per crate.
- `script/claim` cuts a lane's branch and worktree and makes the claim (above).

The baselines the ratchets hold the record to are the record's rows of nife's:
`design/passive-baseline.tsv`, `design/module-block-baseline.txt`,
`design/naming-rule-baseline.txt` and `design/removed.tsv`. The record's own is
`design/repeated-sentence-baseline.txt`, the copies the one-home rule found when it took effect.
Each only shrinks.

## Where things go

A change to the record lands here, through this repository's pull requests. A change to code lands
in nife. When a record change waits for a nife change, the record's pull request names the nife
one, and not the other way round. The maintainers keep unit-specific details of their machines
off this tree.
