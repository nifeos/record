---
status: PROPOSED
raised: 2026-11-25
---

# 328. A recipe may change with no person when checks stand in for its review

*(The section number and title are provisional until the merge lands them. Every key, check and
workflow name below is provisional until ruled.)*

Raised 2026-11-25 (UTC) by the maintainer. It proposes an amendment to clause 1 of §195 (a reviewed
recipe vouches for a package, and the owner may overrule it). It is a file of its own because the
amendment is not ruled, and a decided file states only what is in force (§298, a document states
what is in force now). On a yes, §195 gains an amendment that states the new clause 1 and points
here, and this file becomes DECIDED. On a no, this file records the refusal and §195 is unchanged.

The survey reads `nifeos/basalt@9b9e4b842` and the nife commit it pins, `nifeos/nife@6bed50566`.
The prior art was read on 2026-11-25 (UTC).

## Background

basalt is nife's distribution. Each program it ships has a recipe, one file in `recipes/`, that
names the upstream source by its SHA-256, any patch basalt applies by its SHA-256, the license, and
the SHA-256 of the package it builds for each architecture. §195's clause 1 says this digest
"lives in a version-controlled recipe, changed by human review". So every new upstream release
waits for a person to open, read and merge a recipe change.

That is the slow part today. `recipes/ripgrep.toml` pins ripgrep 14.1.1 (crates.io, 2024-09-09).
crates.io lists four releases after it: 15.0.0 (2025-10-16), 15.1.0 (2025-10-22), 15.2.0
(2026-07-15) and 16.0.0 (2026-11-22). Nobody has had the time to move it, and nothing would move it
without a person.

## Is the premise true

Partly, and the part that is not true is the precedent.

- **A digest already changes with no person.** basalt's `pin-bump` workflow moves the nife pin
  daily and rewrites every recipe's `[package_digest]` lines in the same pull request. It arms
  auto-merge on itself when the diff touches only `pins.toml` and those lines, and the required
  checks are the review: nife's system test on three architectures, two byte-identical package
  builds, the `jig` installs and two composed image boots. This was approved 2026-10-21 (UTC), and
  the workflow's header records it. So clause 1 already holds only for the upstream source digest
  (`sha256`) and patch digests, not for package digests.
- **The endowment is basalt's, not upstream's.** A program on nife is endowed from the manifest
  note inside its executable, and the digest covers the note, so changing what a program asks for
  changes its digest (`crates/capability_manifest_note`). ripgrep is unmodified crates.io source,
  so it cannot carry a note of its own. basalt's build links the note `cargo xtask foreign-note`
  writes, which is `program_table::UNVOUCHED_STD_MANIFEST` and nothing else: a `std` program that
  hears its words and reads what they name, read-only, with no network, entropy or domain. So an
  upstream release cannot widen ripgrep's endowment by itself. Only a change on basalt's or nife's
  side can.
- **The machine does not ask.** §220 (signed builds and scoped key trust) refuses an install whose
  manifest exceeds the source's ceiling, and basalt's default trust line has the ceiling
  `domain entropy network` (§195's amendment of 2026-10-10). So a basalt package that newly asks for
  the network installs with no question to the owner. The recipe review is the only place a person
  sees it.

## The proposal: option A

Clause 1 becomes: a package's digest lives in a version-controlled recipe, changed by review, and
the review is a person's or the checks below. The machine still trusts the recipes of the sources
it was given. In order:

1. **A bot opens the pull request.** When an upstream publishes a release, a scheduled workflow in
   basalt opens a recipe pull request with the new source and its SHA-256, read from the upstream's
   own index (for a crate, the `cksum` crates.io's index carries, as the recipe already says), and
   the package digests the build writes. One pull request per recipe, replaced by a newer release.
2. **It merges with no person when all of these hold:**
   - the package builds from source, and two independent builds give the same bytes (the existing
     `reproduce` job);
   - the boot tests pass (the existing `install` and `composed` jobs);
   - every patch basalt carries still applies, unchanged (the existing patch check, run against
     the new upstream);
   - the declared license is unchanged: the upstream's own license field equals the recipe's
     `license`, and the recipe's `license_files` all exist (new: a comparison);
   - the endowment is unchanged or narrower: the manifest note decoded from each new package's
     bytes is equal to, or a subset of, the note in the package the index serves today (new: a
     decode and a comparison, of the built bytes and not of any recipe key, so a widening from any
     route is seen).
3. **A person reviews only when** the endowment widens, the license changes, or a patch no longer
   applies. The bot leaves the pull request open, says which check held it, and adds the label that
   asks a person. Any other check failing leaves a red pull request, as a red pin bump does today.
4. **Publishing is unchanged.** A merge to basalt `main` already publishes the index and the
   packages (`packages.yml`, the `publish` job). This adds no new path to the index.
5. **On the owner's machine nothing changes by default.** The owner decides whether and when a
   machine updates (§250's amendment of 2026-10-07, the owner chooses the source and the moment),
   so scheduled updating is a setting the owner turns on, per source, which is clause 2's shape.
   Undoing an update is one line, `jig rollback`, which points the installed programs one generation
   back (§208, installing a package is granting it, and the installed programs are versioned).
6. **An optional hold.** A source may set a number of days a new upstream release must age before
   its pull request may merge. It is a setting per source, not a fixed number. For basalt it is the
   maintainer's to set and change, as a two-way door.

A recipe can also opt out, as Homebrew's `no_autobump!` does, with a reason in the recipe. That is
how a recipe stays at a version a measurement depends on.

## What this does not catch

Say it plainly: **a compromised upstream release that asks for no new endowment passes every
check.** That is the xz case. The xz 5.6.0 and 5.6.1 release tarballs carried a backdoor, part of
which was only in the tarball and not in git (Freund, oss-security, 2024-03-29). The tags are dated
2024-02-24 and 2024-03-09, so the releases were public 34 and 20 days before the disclosure. A crate
is the same kind of object: an archive the publisher uploads, which need not match the repository.
Every check above would pass on such a release: it builds, it reproduces, it boots, its patches
apply, its license and endowment are the same.

Two things bound it, and neither is a review.

- **Confinement bounds what it can reach** to what the previous version was already granted. A
  compromised `rg` holds a read-only view of what its words name and nothing else. It cannot open a
  socket, because it holds no network capability, so it cannot send what it reads anywhere. On a
  system where a program inherits its user's authority, the same release could. That is the
  difference nife's design buys, and the endowment check is what keeps it from eroding one release
  at a time.
- **The hold is the only time-based defense.** It helps only if somebody else finds the problem
  inside the hold. A week would not have caught xz. A hold of 35 days would have, and would also
  delay every fix by 35 days.

It also does not catch a new transitive dependency in the upstream's lockfile. The bot's pull
request lists the lockfile diff, and nothing holds on it.

## A worked example: ripgrep 14.1.1 to 15.0.0

Checked against the crates on 2026-11-25 (UTC); the bot does not exist yet, so this is what it would
do.

1. ripgrep 15.0.0 is on crates.io with SHA-256 `db22b6e9...f946`, the value crates.io's index
   carries. With a hold of 7 days set on basalt, the pull request could merge no earlier than
   2025-10-23. The bot opens a pull request changing `version` to `15.0.0` and
   `sha256` to the new digest.
2. 15.0.0's `Cargo.lock` takes `ignore` 0.4.24, not 0.4.23. So the bot rewrites the `[[patch]]`
   entry's `version` and `sha256` for `ignore` 0.4.24 and leaves `file` and `file_sha256`
   unchanged. `patches/ripgrep-ignore-walk.patch` applies to `ignore` 0.4.24 with `patch -p1
   --dry-run` and no rejected hunk.
3. The license field in 15.0.0's `Cargo.toml` is `Unlicense OR MIT`, the recipe's value. The license
   check passes.
4. The note in the new `bin/rg` is the same `UNVOUCHED_STD_MANIFEST` note, because basalt links it.
   The endowment check passes.
5. The two builds compare equal, `jig` installs it, the composed images boot, and the pull request
   merges and publishes with no person. An owner who turned scheduled updating on gets it at their
   next update; anyone else gets it with `jig install`. Either can undo it with `jig rollback`.

**If 15.0.0 suddenly asked for the network.** There are two cases, and different things stop each.

- If the upstream code starts opening sockets, the package still carries basalt's note, which grants
  no network, so the endowment check passes and the program runs without the capability. Its
  network calls fail at run time. If that breaks a search, the `install` job's `rg` line fails and
  the pull request is red. If it does not break a search, the release merges, confined. Nothing in
  the chain reads the code.
- If somebody changes the note so that `rg` asks for the network (a change to the foreign note, or a
  recipe that carries its own manifest), the new package's note has `network` set where the served
  one does not. The endowment check holds the pull request for a person. Without that check, nothing
  would: basalt's trust line's ceiling already covers `network`, so the machine would install it
  without asking.

## The prior art, read 2026-11-25 (UTC)

| System | Who opens the change | What merges it | Time gate | Permissions decide review |
|---|---|---|---|---|
| Homebrew `homebrew-core` | `autobump.yml`, every 3 hours | the `automerge` workflow, only once a person has approved | none | no |
| nixpkgs | `@r-ryantm` | a package maintainer asks the merge bot | none | no |
| Debian testing | the uploader, to unstable | the migration, automatically | 2, 5 or 10 days | no |
| Renovate | the bot | `automerge` on green, optionally | `minimumReleaseAge` | no |
| Dependabot | the bot | a person, or a separate auto-merge rule | `cooldown` | no |
| Flathub | `flatpak-external-data-checker` | a person, or automerge by exception | none | no |
| Android | the developer | the store, automatically | none | at run time only, for dangerous permissions |
| Chrome extensions | the developer | the store, automatically | none | yes: a new warning disables it until the user accepts |

- **Homebrew.** `docs.brew.sh/Autobump`: "every 3 hours, a GitHub Action opens a new pull request to
  upgrade them to the latest version, if needed", for every formula unless it carries
  `no_autobump!` with a reason. The merge is not automatic: `homebrew-core`'s
  `.github/workflows/automerge.yml` merges only when `reviewDecision == "APPROVED"`, CI is complete
  and the pull request is mergeable, and `automerge-triggers.yml` runs on an approving review. So
  the bot saves the typing and a person still approves each bump. Where nife differs: option A drops
  the approval when the checks hold. Example: the bump of a formula's `url` and `sha256` that the
  bot opens, merged by the workflow after a maintainer approves it.
- **nixpkgs, `@r-ryantm`.** The bot "updates Nixpkgs by making PRs that bump a package to the latest
  version" (`nixpkgs-update` docs, `r-ryantm.md`). Its checks run each binary "with various flags to
  see if they have a zero exit code and output the new version number", search the output for the
  version, and report CVEs resolved and introduced (`details.md`). nixpkgs' `ci/README.md` says the
  merge bot merges a pull request opened by `@r-ryantm` under `pkgs/by-name/` when a maintainer of
  every touched package asks with `@NixOS/nixpkgs-merge-bot merge`. So a person still decides each
  merge; the README counts roughly 20 maintainers for every committer. Where nife differs: nixpkgs
  has no permission manifest to diff, so a person is the only check on what a package may do.
  Example: an r-ryantm pull request for a `pkgs/by-name` package, merged on its maintainer's
  comment.
- **Debian testing.** `debian.org/devel/testing`: a package migrates from unstable when it "must have
  been in unstable for 10, 5 or 2 days, depending on the urgency of the upload", is built on every
  architecture it was built for before, has no release-critical bugs the testing version lacks, and
  breaks nothing in testing. No person approves a migration. Where nife differs: Debian's gate is
  age plus bug reports from people running unstable, a population basalt does not have, so basalt's
  hold buys less than Debian's. Example: a normal-urgency upload reaches testing after 5 days with
  no RC bug filed. Freund found the xz backdoor on Debian sid machines.
- **Renovate.** `minimumReleaseAge` "requires Renovate to wait for a specified amount of time before
  suggesting a dependency update", per version, and with `automerge` it creates pull requests at
  once and automerges them only once the age has passed. Its documented example is 3 days for npm,
  because npm packages less than 72 hours old can be unpublished. Renovate "only automerges branches
  which are up-to-date and green". Where nife differs: the hold in option A is the same mechanism,
  set per source rather than per package rule. Example:
  `{"matchDatasources": ["npm"], "minimumReleaseAge": "3 days"}`.
- **Dependabot.** The `cooldown` option delays version updates by `default-days` (3 when omitted)
  or by `semver-major-days`, `semver-minor-days` and `semver-patch-days`, with `include` and
  `exclude` lists, and never delays security updates. Example: `cooldown: {default-days: 7}`.
  Where nife differs: no difference in kind; basalt's own `dependabot.yml` sets none today.
- **Flathub.** An app adds `x-checker-data` to a source to receive update pull requests, and "by
  default, the tool opens a PR whenever a source has an update". It automerges only its pull requests
  for broken source URLs; automerging every one of its pull requests "requires a Flathub exception".
  Example: a source with `x-checker-data: {type: github, repo: example/app, tag-pattern:
  '^v([0-9.]+)$'}`. Where nife differs: a Flatpak declares its sandbox permissions in the manifest
  the pull request edits, yet the checker's README does not mention them, and Flathub's review of a permission change was not
  read.
- **Android.** Install-time permissions are "automatically granted when your app is installed", and
  `INTERNET` is one of them: "Protection level: normal" (`Manifest.permission`). Runtime, or
  dangerous, permissions are asked for at run time. So an update that newly adds `INTERNET` installs
  with no question. Where nife differs: nife has no normal tier; the network is a capability the
  progenitor grants from the note. Today a basalt package widening to `network` is in the same
  position as an Android app adding `INTERNET`, which is why the endowment check sits in basalt.
- **Chrome extensions.** If an update adds a permission with a new warning, "the extension will be
  disabled until the user accepts the new permission" (`developer.chrome.com`, permission warnings).
  That is a review decided from a permission diff, placed at the user rather than the store. Where
  nife differs: option A places it at the distribution. Placing it at the owner too is option E.

What the table shows: everyone automates opening the change; most still have a person merge it;
the systems that merge with no person (Debian, Renovate on request) gate on age and tests; and the
only systems that decide review from a permission diff are the two with a permission manifest, and
they put the decision at the user.

## Options

| | What it is | Why it loses, or wins |
|---|---|---|
| **A. Checks stand in for review; a person only on a widening, a license change or a failed patch** | the proposal above | Recommended. It puts the person where nife's design says the risk is, in what a program may reach. |
| B. Keep clause 1 | every recipe change waits for a person | ripgrep is four releases behind under it today. A person reading a 15.0.0 diff of an upstream's tens of thousands of lines does not catch xz either, so the review is mostly a rubber stamp on the checks A runs anyway. |
| C. Automate the pull request, people merge (nixpkgs, Homebrew) | A's step 1 and the checks, with a person on every merge | Better than B and the common practice. It loses because, with no one to read the upstream's code, the person adds a click and not a check, and the click is what is missing today. |
| D. Automate fully, endowment widening included | A without step 3's widening trigger | A widening is the one change confinement cannot bound, and basalt's ceiling would not stop it on the machine. This removes the only person who would see it. |
| E. A, plus the owner's consent on a widening at install (Chrome) | jig refuses or asks when an update's note is wider than the installed one's | Not refused, and not part of this ruling: it changes §208's and §220's install rule, which A does not touch. It is worth its own proposal. |

**The recommendation is A.** It is not about effort: B is the cheapest to build, since it builds
nothing. The test of §92's tenet (would we still choose it if both cost the same) gives A again,
because A's person is spent on the one change nothing else bounds.

## What it costs

Not measured; estimated from the existing jobs. The build, reproduce, install, composed and patch
checks exist. New: a scheduled job that reads each upstream's index and opens the pull request (the
`pin-bump` workflow is the template); the license comparison; the endowment comparison, which
decodes the note with `capability_manifest_note::decode` against the package the index serves; and
the hold, a status check that stays pending until the release's age passes, as Renovate's
`renovate/stability-days` does. Each is a basalt change and goes through basalt's queue.

## Reversibility, and who has acted on it

Checked 2026-11-25 (UTC): `nifeos/basalt` has no forks and no stars, and its pull requests are by
calef, `nife-smelter[bot]` and Dependabot only. No other source stands up a recipe under clause 1,
and `pin-bump.yml` records that basalt has no customers yet. So nobody outside has acted on
clause 1, and the rule itself is reversible: turning the bot off restores it.

What is not reversible is each release the bot merges. A merge publishes, and a package an owner has
installed has run on their machine; `jig rollback` removes it from the installed programs and does
not undo what it did while it ran. That cost is bounded by the endowment, which is the reason the
endowment check is the one that keeps a person.

## What is blocked, and what happens on a no

Blocked until ruled: the basalt bot and the two new checks. Nothing else waits. On a no, clause 1
stands, recipes keep waiting for a person, and option C is still open as a basalt change, since it
keeps a person on every merge.
