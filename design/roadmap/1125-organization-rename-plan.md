---
status: NOT-STARTED
raised: 2026-11-24
milestone_dependencies: 1018
decision_dependencies: 323
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1125. The organization rename: the order in which every repository takes the name partsfoundry

The GitHub organization takes the name `partsfoundry`. calef ruled the name Parts Foundry and the
domain partsfoundry.org on 2026-11-15 (UTC), and the rename itself on 2026-11-24 (UTC). calef renames
the organization in GitHub's settings. This block plans everything around that moment: what each
reference does at the rename, the order in which the rewrite pull requests land, what breaks in
between, how to undo it, and how to tell that the work is complete. The number, title and slug are
provisional. The branch is `milestone/1125-organization-rename-plan`.

Reuse: the rewrite tool `helpers/organization_rename.py` in nife (added by
[nifeos/nife#4077](https://github.com/nifeos/nife/pull/4077)), whose `census` mode measured this
block and whose `rewrite` mode made every draft below. It can be re-run at cutover, because a draft
that has gone stale is rebuilt by running it again on a fresh branch. The precedent is the rename
from crickertech on 2026-10-03, which the record's
[project history](../tenets/project-history.md) describes.

## Goal

Every repository of the organization names `partsfoundry` wherever it names the organization, so
that nothing depends on GitHub's redirect from the old name. The queue runs again within one
working day of the rename, and nothing else changes its name. The kernel stays `nife`. The domains
nifeos.org and basalt.nifeos.org stay. The project word "nifeos" in prose stays.

## What a reference does at the rename

GitHub keeps a redirect from a renamed organization's repositories to their new home until someone
claims the old name. The lane measured what follows that redirect on the crickertech name, which
nobody has claimed since 2026-10-03. The details are in
[the prior-art appendix](1125-organization-rename-plan/prior-art.md).

- **Redirects.** Web pages, `git` fetch and push URLs, raw.githubusercontent.com, release
  downloads, badges, REST paths under `repos/<org>/<repo>`, `gh pr list --repo`, and GraphQL
  `repository(owner:, name:)`. These keep working, so their rewrite is tidying. It can land late.
- **Breaks.** `uses:` lines that call a reusable workflow or an action in the organization
  (GitHub documents that Actions follows no redirect for these). Also REST paths under
  `orgs/<org>`, GraphQL `organization(login:)`, `gh search --owner`, `gh repo list <org>`, team
  handles such as `@<org>/crate-maintainers` in CODEOWNERS, `owner:` given to
  `actions/create-github-app-token`, and any code that compares a repository's `full_name` with a
  literal. These stop at the rename and must land first.
- **Tied.** A qualified record path (`<org>/record:<path>`) and a pinned git source are read by
  nife's own tooling, which compares the organization text with basalt's `pins.toml` and each
  `Cargo.lock`. These move when the files the tooling compares them with move, in one pull request
  where they share a repository and in a fixed order where they do not.
- **Stays.** The DNS names, the wire literals that spell nife, the kernel's name, the project word,
  and history: bench logs, vendored and patched sources, audit reports, changelogs, and any line
  that already names the earlier name crickertech.

## The census

The lane counted every line that names the organization in the 39 repositories it can read (every
public repository and the record), at each one's default branch on 2026-11-24. The full tables are
in [the census appendix](1125-organization-rename-plan/census.md).

| group | lines | what they are |
|---|---|---|
| breaks | 433 | 315 `uses:` lines, 38 organization API paths, 34 team handles, 35 organization literals in code (owner constants, cargo-deny's allowed organization, the template's settings), 11 Pages references |
| tied | 3,663 | 3,272 record paths (`<org>/record:<path>`), most of them in comments, and 391 qualified paths into other repositories, which the citations check resolves against the pins |
| redirects | 2,832 | 1,984 links, 363 cargo git sources and repository metadata, 326 slugs in code, 121 repository API paths, 36 raw URLs, 2 basalt pins |
| stale | 1,401 | slugs in prose, such as `nifeos/nife#123`, which still resolve but would name a former organization |
| stays | 594 | 146 DNS names, 220 uses of the project word, 1 home path, 227 lines of history and former names |

nife holds 4,445 of the lines and the record 3,558. Each of the 31 crate repositories and crate-workflows-test has 17 to 33
lines, of which 10 to 17 break: nine caller `uses:` lines, CODEOWNERS and `deny.toml`. The App,
runner, fuzz host and workspace references that live outside these repositories appear in a
spec the maintainers keep off-tree.

## The order

Effort: S is under half a day for a lane, M a day or two. Every step inside the repositories is a
two-way door. The list after the steps holds what only calef can do.

0. Before the rename: nife's tooling reads both names. `qualified_paths.py`, the architect
   label rules, the externalized-crates lint, the interface declarations check and the site's
   citation resolver accept a citation, a pin or a locked source under either name. The smelter
   token rewrites SSH remotes of both. This is part of the tooling draft, which is the only draft
   that could land before the rename. It lands with the others instead, to keep the window to one
   cause. Effort: S.
1. Freeze. Nobody arms a pull request for the merge queue in any repository. A run already in
   the queue finishes or leaves it. Lanes in flight keep working, and they do not push.
2. calef renames the organization from `nifeos` to `partsfoundry`.
3. calef creates an empty `nifeos` organization as a placeholder, so that nobody else can claim
   the name and end the redirect. It holds no repository. A repository created there under a
   renamed repository's name would end that repository's redirect.
4. crate-workflows ([nifeos/crate-workflows#91](https://github.com/nifeos/crate-workflows/pull/91)).
   The scaffold's callers, the template's settings and its own CODEOWNERS. The crate repositories
   call it by `uses:`, which stops at step 2, so it lands first. A release tag follows the template's
   own release rule, and the callers pin the new commit. Effort: S.
5. The 31 crate repositories and crate-workflows-test, one draft each. Each draft rewrites
   the nine caller `uses:` lines, CODEOWNERS, `deny.toml`, git dependencies and links. Their CI is
   dead from step 2 until each one lands, and nothing else depends on them landing in a particular
   order. Effort: S in all, since each is the same change.
6. fuzz-host ([nifeos/fuzz-host#25](https://github.com/nifeos/fuzz-host/pull/25)). Its token
   and filer tools compare the repository list GitHub returns with `OWNER/REPOSITORY`. GitHub
   returns the new name from step 2, so both refuse until this lands and the host follows `main`.
   Effort: S.
7. The record ([nifeos/record#14](https://github.com/nifeos/record/pull/14)). It lands before
   nife. nife cites milestone 1018 (the design record moves and is published as a website) with a
   gloss that names the record's new home, and the citations check grounds that gloss in the record
   at basalt's record pin. Effort: S.
8. basalt ([nifeos/basalt#98](https://github.com/nifeos/basalt/pull/98)), then basalt's record
   pin bump to the commit of step 7, as its own pull request. basalt-backup and the site repository
   follow in any order. Effort: S.
9. nife, in nine drafts, one per top-level directory group. The tooling draft
   ([nifeos/nife#4077](https://github.com/nifeos/nife/pull/4077)) lands first, since the other
   drafts' lints run its code. The others are #4078 to #4084 and #4086. The rest follow in any order: kernel, crates,
   components, system_tests, xtask, the remaining program directories, the prose, and the Cargo
   files. The Cargo draft holds every `Cargo.toml` and `Cargo.lock`, `deny.toml` and `.cargo/`,
   because one crate under two URLs in one workspace is two sources to cargo. For the same reason
   it also moves nife's pin of `grant_plan` to the commit of that crate's step 5 draft. `grant_plan`
   is the one crate whose own manifest names other first-party git crates: `byte_glob`,
   `grant_contract` and `program_argument_contract`. At its present pin it names them under the
   former organization, and cargo takes each as a second source. The lane measured this: cargo
   rewrote `Cargo.lock` with three duplicate packages. Effort: M, which is mostly queue time.
10. basalt's nife pin moves to the commit of the last nife draft, citing it as
    `partsfoundry/nife@<sha>`. Then the record refreshes its claim copy (`script/claim` and three
    helpers) and the read-advisory selftest from nife at that pin. Effort: S.
11. Outside the repositories. The App installations, the owned runners, the fuzz host, the
    Pages domains and the maintainers' workspace notes, each in the off-tree spec. The two DNS
    records are calef's: the Pages verification record for the new organization, and nothing else,
    since basalt.nifeos.org's CNAME names the domain and not the organization.

Every draft was rebuilt from `main` on 2026-11-24. A draft that has gone stale by cutover is
rebuilt by running `organization_rename.py rewrite` on a fresh branch, not by merging main into it.

## The window

From step 2 to the end of step 9, these stop working.

| what | why | until |
|---|---|---|
| CI of every crate repository and of crate-workflows' selftest | `uses:` follows no redirect | step 4 and that repository's step 5 draft |
| a lane's App token (`helpers/smelter-token`) | it asks for the installation of the organization by name | nife's tooling draft. Until then a lane sets `NIFE_SMELTER_ORG=partsfoundry` |
| the fuzz host's token and filer | the `full_name` comparison | step 6 and the host's next fast-forward |
| the metrics workflow and the record's basalt-record-pin workflow | `owner:` given to the App token action | nife's tooling draft, and step 7 |
| the queue sweep's idle check | `gh repo list nifeos` | nife's tooling draft |
| the draft board, `gh search prs --owner nifeos --draft` | search follows no redirect | the instructions that name it, steps 7 and 9 |
| code owner review requests in the crate repositories | an unknown team | step 5 |

Expected length: one working day, if a lane rebuilds the drafts the day before and merges each as
soon as its checks pass. nife's nine drafts are the long part, because each one is a queue
run. That is an estimate from queue run times, not a measurement.

## The queue meanwhile

nife's merge queue takes nothing between steps 1 and 9 except the nine rename drafts, the tooling
draft first. Each draft's lint runs the tooling draft's code, so before that draft lands a later
one fails its citations and tied-path checks. Heavy gates run on `merge_group` on the owned runners.
Nobody has measured whether those runners keep their registration through the rename, and the
off-tree spec checks it before step 1. If they lose it, the queue runs on hosted runners or waits
until someone registers them again.

## Rollback

Up to step 3, the rollback is to rename the organization back. GitHub keeps the redirect in the
other direction, and no draft has landed. After step 3, calef deletes the placeholder before taking the
name back. After the first draft lands, the rollback is to rename back and revert each
landed draft by `git revert`, in the reverse of the order above. The tooling's two-name reading
means a revert of a later draft never leaves nife's tooling unable to read the other repositories.

## Verification

- `organization_rename.py census` over every repository reports no line in the breaks, tied,
  redirects or stale groups.
- `gh api orgs/partsfoundry` answers, and `gh api orgs/nifeos` answers with the empty placeholder.
- A crate repository's pull request runs `check` and `proofs` from `partsfoundry/crate-workflows`.
- One nife pull request passes the queue on the owned runners.
- `script/claim` in nife mints an App token and pushes, without `NIFE_SMELTER_ORG`.
- `fuzz-token check` on the fuzz host lists exactly `partsfoundry/nife`.
- basalt's Pages site and the record's site build from `partsfoundry/record` at the pin.
- The record's `script/lint` passes with its claim copy level with nife at basalt's pin.
- `gh search prs --owner partsfoundry --draft` lists the board.

## Prior art

Read, with sources, in [the prior-art appendix](1125-organization-rename-plan/prior-art.md). The
project renamed its organization once before, from crickertech on 2026-10-03. Links, `gh`
arguments and scripts took the new name, and the prose of the past kept the old one. GitHub
documents the redirect and its exception for Actions. crates.io names a team owner by organization,
so a published crate owned by a team would need its owner again under the new name. No crate here
has a release on crates.io. At the first rename the organization held two repositories, nife and basalt. Now it
holds 40, which call one another by name. That is why this rename needs an order.

## Risks

- A claimed old name. If anyone takes `nifeos` before step 3, every redirect ends. The
  placeholder in step 3 is the guard, and the gap between steps 2 and 3 should be minutes.
- The placeholder kills a redirect. A repository created in the placeholder under a renamed
  repository's name would end that one's redirect. This applies to `nifeos.github.io` too, should
  one ever exist. The placeholder stays empty.
- Stale drafts. A pull request that lands between now and step 1 may add a line naming the old
  organization. The census at step 9 finds it, and the rewrite is re-run.
- rustfmt. A longer name can push a line past the width, so rustfmt rewraps it. Two lines needed
  that in nife (in `kernel/src/stack.rs` and `xtask/src/basalt.rs`), and the lane moved one IOMMU
  comment by hand to keep a column aligned. A re-run has to repeat the format check.
- Falsification patches whose context lines name the organization must change with the source
  they patch. Five of them sit in another directory than their target, so they move with the
  target's draft.

## Open decisions

None for this plan. calef ruled the rename on 2026-11-24 (UTC), and steps 2 and 3 are his. The two-name
reading in nife's tooling is a two-way door. It goes once no tracked file outside history names
the former organization, in a follow-up the maintainer rules on.

## Follow-on

- **None.**

## BUGS

- The census counts lines, not occurrences, and sorts each line by the first form it matches.
- The tool does not read a regular expression that escapes the slash (`nifeos\/`). The site's
  citation resolver was the one case, and the lane edited it by hand.
- Nobody has measured whether the owned runners, the App installations, the rulesets and the Pages
  domain verification survive the rename. Nor has anyone measured a write through the redirect,
  or cargo's handling of a lockfile source rewritten without a version change.

## Index row

The GitHub organization takes the name partsfoundry. The census sorts 8,923 lines across 39
repositories into those that break at the rename, those tied to a pin or lockfile, those that
redirect and those that stay. One draft per repository, nine in nife, lands in a fixed order:
the shared workflows, the crates, the fuzz host, the record, basalt, then nife.
