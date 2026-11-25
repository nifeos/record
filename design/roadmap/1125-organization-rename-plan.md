---
status: PARTIAL
raised: 2026-11-24
milestone_dependencies: none
decision_dependencies: 323
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1125. The library moves to partsfoundry: the order of the repository transfers

The crate repositories, crate-workflows and crate-workflows-test move from the `nifeos`
organization to the `partsfoundry` organization, one repository transfer at a time. calef ruled the
name Parts Foundry on 2026-11-15 (UTC) and this shape on 2026-11-24 (UTC): `nifeos` keeps its name
and keeps nife, basalt, basalt-backup and fuzz-host. The record and the site repository stay
in `nifeos` too, and where they live is a separate decision. This block plans the transfers: what
each one keeps, the order, what breaks in between, how to undo it, and how to tell that it is
complete. The number, title and slug are provisional. The branch is
`milestone/1125-organization-rename-plan`.

Reuse: nife's rewrite tool `helpers/organization_rename.py`, whose `--moving FILE` mode rewrites
only the repositories a file lists
([nifeos/nife#4090](https://github.com/nifeos/nife/pull/4090)). It measured this block and made
every draft below, and a stale draft is rebuilt by running it again.

## Goal

Every moving repository lives in `partsfoundry`, and every reference to one names `partsfoundry`,
so that nothing depends on a redirect. Each crate repository's CI and release path works there as
it does today. Nothing else moves: nife, basalt, the record and the site keep `nifeos`, and their
links to the crates may keep redirecting until the record's own placement is decided.

## What a transfer keeps

GitHub's page on transferring a repository, read on 2026-11-24, states these:

- Issues, pull requests, the wiki, stars and watchers move with the repository.
- Webhooks, services, secrets and deploy keys "remain associated after the transfer is complete".
- Every link to the old location redirects, git included, until someone creates a repository or a
  fork at the old name.
- Collaborators stay, and the receiving organization's default permissions apply.
- A repository with more than 100 uses of GitHub Actions in the week before its transfer has its
  old owner and name combination retired for good.

The page says nothing of variables, environments, rulesets or teams. The rsext4 trial measured
them:

- Both rulesets stay, with their rules and required checks, but the tags ruleset loses its bypass
  actor, nife-smelter, which is not installed on `partsfoundry`.
- The `crates-io` environment stays with calef as its required reviewer, as do the description,
  homepage, topics, labels, merge settings, the Actions allowlist and the fork approval policy.
- The team named in the transfer call's `team_ids` arrives with the read role, not maintain.
- Secret scanning and its push protection come back off.

`script/apply-settings` restores all of it in one run, and `script/check-settings` then matches.
Two documented rules from the Actions reference shape the order. Actions follows no redirect
for a reusable workflow or an action. A caller may run a reusable workflow from a public repository
in another organization only when its own Actions settings allow it.

## The census

The lane counted every line that names `nifeos` in the 40 repositories it can read, at each one's
default branch on 2026-11-24, and sorted each by whether it names a moving repository. The tables
are in [the census appendix](1125-organization-rename-plan/census.md).

- The 33 moving repositories hold 683 lines to change. 375 of them break at the transfer of
  crate-workflows or at a repository's own transfer: 314 caller `uses:` lines, 34 code owner team
  handles and 27 organization literals (cargo-deny's allowed organization, the settings file's team
  organization).
- nife holds 424 lines that name a moving repository, of which 302 are cargo git sources. All of
  them redirect, so nife builds unchanged through every transfer.
- The record holds 1,033 such lines, and the site repository 31. Both stay unchanged under this
  plan, since their placement is a separate decision.

## Measured setup

Read-only calls on 2026-11-24 found these:

- Every crate repository sets its allowed actions to `selected`, with one pattern,
  `taiki-e/install-action@*`. That allows reusable workflows from its own organization and nothing
  else, so a crate in `partsfoundry` cannot call `nifeos/crate-workflows`. The settings file holds a
  table of values per owner, merged over the shared ones by `helpers/settings_owner.py`
  ([nifeos/crate-workflows#92](https://github.com/nifeos/crate-workflows/pull/92), landed at
  11d6d6b). Its `partsfoundry` row adds the pattern
  `nifeos/crate-workflows/.github/workflows/*@*`, the team organization, the App and the tags
  bypass, so a crate in `nifeos` sees no change and a crate in `partsfoundry` gets these values.
- Callers pass their secrets by name (`SETTINGS_TOKEN`, `NIFE_SMELTER_APP_ID`,
  `NIFE_SMELTER_PRIVATE_KEY`), never through `secrets: inherit`. A named secret comes from the
  caller's own organization, so `partsfoundry` needs all three before the first crate's weekly or
  release run.
- The tags ruleset of each crate exempts one actor: nife-smelter, an App owned by `nifeos`. Its
  release `tag` job mints that App's installation token in the caller's organization. In
  `partsfoundry` the actor is partsfoundry-smelter, an App owned there and installed on every
  repository, whose credentials sit in the same two secret names.
- The crate repositories hold no repository secrets, variables, webhooks or deploy keys. Each has a
  `crates-io` environment whose one rule names calef as reviewer, and the `crate-maintainers` team
  with the maintain role.
- `nifeos` holds no organization rulesets. `partsfoundry` is on the Free plan, which refuses
  organization rulesets, so the repository rulesets carry the rules alone.

## The order

Effort: S is under half a day for a lane. Every step inside a repository is a two-way door,
except the last transfer, which may be one-way (see the risks).

0. Preparation in `partsfoundry`, all of it calef's: the secrets, the team, the App, and the
   Actions settings (the list after the steps). Nothing changes in the crates still in `nifeos`,
   since the owner table applies only after a crate arrives. Effort: S.
1. The trial: calef transfers rsext4 (done). The lane runs `script/apply-settings`,
   measures what survived (the verification list), and runs its `check`, `proofs`, weekly and
   dry-run release workflows, still calling `nifeos/crate-workflows`. Effort: S.
2. The other 29 crate repositories, one transfer at a time, in any order (done). moho_abi stays
   in `nifeos` (provisional), and crate-workflows-test moves with crate-workflows at step 3, since
   its canary adoption mints its token in the organization that owns crate-workflows-test. Each
   crate follows the trial's steps:
   - Before it transfers, it pins crate-workflows at 11d6d6b or later, the first commit that holds
     the owner table. An older pin's weekly settings check reads the shared values alone and
     reports drift in `partsfoundry`.
   - At its own transfer, `script/apply-settings` runs against it, and the first half of its draft
     lands: the names of the repository itself (README badges, code owners, the manifest's
     `repository`, cargo-deny's allowed organization). The `check / standalone` badge check reads
     the current owner, so that draft is red before the transfer and green after it.
   - Its `uses:` lines keep calling `nifeos/crate-workflows`, so it stays green. They are the
     second half of its draft, which waits for step 3.
   Effort: S in all.
3. crate-workflows-test and crate-workflows, last, under their own ask. From this moment every caller's `uses:` line fails until its draft lands.
4. crate-workflows' own draft
   ([nifeos/crate-workflows#91](https://github.com/nifeos/crate-workflows/pull/91)) lands first,
   then each crate's second draft, its `uses:` lines (one per repository, all titled "crate
   transfer"), grant_plan's among the first. Each draft's pull request runs its new `uses:` lines, so it can pass while `main` is
   red. Effort: S.
5. The record amends DECISIONS §305 (git dependencies are allowed on `nifeos/*` only, pinned to a
   landed commit) to name the library's organization.
6. nife's draft ([nifeos/nife#4090](https://github.com/nifeos/nife/pull/4090)) moves its pin of
   `grant_plan` to the merge commit of grant_plan's draft, and lands. It rewrites every cargo
   source together, because one repository under two URLs is two sources to cargo. At its present
   pin, grant_plan's manifest names three crates under `nifeos`. Effort: S.
7. The `partsfoundry` row of the owner table becomes the shared values, its
   `nifeos/crate-workflows` pattern leaves, and `script/apply-settings` runs against every crate.

## Where the transfers stand

Thirty crate repositories live in `partsfoundry`. Besides rsext4, the trial, they are address_space_layout,
block_roster_contract, boot_ladder, byte_glob, byte_sink_contract, capability_table, clock_contract,
counter_frequency_contract, designware_ethernet, designware_mobile_storage, device_tree_blob,
domain_name_system, e1000e, entropy_contract, environment_contract,
extensible_host_controller_interface, file_allocation_table, file_system_contract,
generational_table, grant_contract, grant_plan, interfaces_note, intrusive_queue, jh7110_entropy,
line_editor, non_volatile_memory_express, program_argument_contract, terminal_contract and
universal_serial_bus.

Each lost what the trial lost: the team arrived at read, secret scanning and push protection came
back off, the tags ruleset lost its bypass actor, and the allowlist lacked the
`nifeos/crate-workflows` pattern. `script/apply-settings` restored it, and `script/check-settings`
matches on all thirty. Beyond the trial's list:

- Private vulnerability reporting was off on clock_contract, domain_name_system, device_tree_blob
  and interfaces_note before the move; `script/apply-settings` turned it on.
- The required checks of block_roster_contract, non_volatile_memory_express and
  file_allocation_table differed from the template before the move; `script/apply-settings` set
  the template's list.
- `script/apply-settings` writes the template's description, which still calls the crate "a
  standalone nifeos crate", over a repository's own. The own descriptions of
  block_roster_contract, designware_mobile_storage, e1000e and extensible_host_controller_interface
  came back by hand, and `script/check-settings` does not read the description. The template's
  text needs a follow-up.

Each crate's own-names draft is ready or landed. Its `uses:` draft is held on
[nifeos/crate-workflows#91](https://github.com/nifeos/crate-workflows/pull/91). grant_contract and
grant_plan fetch their git dependencies from `partsfoundry`, so nife's draft can move every cargo
source together without locking one crate twice.

Still in `nifeos`: crate-workflows-test and crate-workflows (step 3), and moho_abi, which stays.

The preparation list for calef:

- Organization secrets `SETTINGS_TOKEN`, `NIFE_SMELTER_APP_ID` and `NIFE_SMELTER_PRIVATE_KEY`,
  granted to each crate as it arrives. If `SETTINGS_TOKEN` is a fine-grained token, it reads one
  owner's repositories, and `partsfoundry` needs a new one. The lane did not check its kind.
- The `crate-maintainers` team. The transfer call's `team_ids` field can then attach it.
- partsfoundry-smelter, owned by `partsfoundry` and installed on all its repositories (done).
- Fork pull request approval stays at all outside contributors in each repository, as the transfer
  keeps the repository's own setting. `partsfoundry`'s organization default asks only first-time
  contributors.

## The window

| what | why | until |
|---|---|---|
| CI of every crate repository and crate-workflows-test | `uses:` follows no redirect | step 4, each repository's own draft |
| a release tag in a transferred crate | the transfer drops the tags ruleset's bypass actor | `script/apply-settings` at that crate's transfer |
| code owner review requests in a transferred crate | `@nifeos/crate-maintainers` names a team in the old organization | step 4 (no rule requires these reviews) |
| the draft board, `gh search prs --owner nifeos --draft` | it lists one organization | a second search with `--owner partsfoundry` |

The window opens at step 3 and closes when the last crate draft lands, about an hour if a lane
merges each as its checks pass. That is an estimate, not a measurement.

## Rollback

A transfer back to `nifeos` undoes steps 1 and 2, one repository at a time, by the same API call.
The crate drafts have not landed by then, so nothing else needs reverting. After step 3 the
rollback of crate-workflows may not exist (see the risks), and the fix goes forward: land the
drafts.

## Verification

- After each crate's transfer and `script/apply-settings`, `script/check-settings` matches and the
  tags ruleset's bypass actor is partsfoundry-smelter.
- Its `check`, `proofs` and weekly runs pass, and the weekly settings check reports no drift.
- A dry-run release starts and its gate runs. A crate with no stranger-test run on record stops at
  that step, as it does in `nifeos`, so rsext4's dry run shows only that the cross-organization
  call starts.
- After step 4, `organization_rename.py census --moving` over every moving repository reports no
  line in the breaks, tied, redirects or stale groups.
- nife's `cargo metadata --locked` passes after step 6, with one source for each first-party crate.

## Prior art

Read, with sources, in [the prior-art appendix](1125-organization-rename-plan/prior-art.md). The
project renamed its organization once, from crickertech on 2026-10-03, and the redirect carried
nearly everything. GitHub documents what a transfer keeps and that Actions follows no redirect.
What differs here is the order: one shared workflow repository is called by every other moving
repository, so it moves last, and a tool counts the references first and rewrites only the moving
names.

## Risks

- The last transfer may be one-way. crate-workflows has far more than 100 Actions uses a week, so
  GitHub retires `nifeos/crate-workflows`. Nobody has measured whether a retired name blocks a
  transfer back.
- A stale draft. A pull request that lands before cutover may add a line naming `nifeos` for a
  moving repository. The tool's `--check` mode finds it, and the lane runs the rewrite again.

## Open decisions

- **None.** The release App is partsfoundry-smelter (provisional), a second App owned by `partsfoundry`, and every other
  step follows the 2026-11-24 ruling.

## Follow-on

- **Outstanding.** The transfer of crate-workflows-test and crate-workflows (step 3), under its own ask, then steps
  4 to 7.
- **Outstanding.** The template's description text, which names `nifeos`, and a description check in
  `script/check-settings`.

## BUGS

- The census counts lines, not occurrences, and sorts each line by the first form it matches.
- Three nife tools name `nifeos` for the organization's secrets, its App and its repository list
  (`script/grant-org-secrets`, `helpers/smelter-token`, `helpers/idle_pull_requests.py`). Each
  needs a `partsfoundry` case for partsfoundry-smelter.

## Index row

The crate repositories, crate-workflows and crate-workflows-test move from nifeos to partsfoundry
by repository transfer, one at a time: rsext4 as a trial, the other crates, then crate-workflows
last, followed by one rewrite draft per repository and one in nife. nife, basalt and the record stay.
