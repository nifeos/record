---
status: DECIDED
raised: 2026-11-25
decided: 2026-11-25
ratified_by: calef
---

# 328. A recipe may change with no person when checks stand in for its review

*(The section number is provisional until the merge lands it. Every key, check and workflow name
below is provisional, and so is basalt's 7-day hold.)*

Ruled 2026-11-25 (UTC) by calef on nifeos/record#41: option A. It amends clause 1 of §195 (a
reviewed recipe vouches for a package, and the owner may overrule it), whose amendment of
2026-11-25 states the new clause and points here. This file holds the rule's detail and its reasons.

The survey reads `nifeos/basalt@9b9e4b842` and the nife commit it pins, `nifeos/nife@6bed50566`.
The prior art, read on 2026-11-25 (UTC), follows the rule.

## Background

basalt is nife's distribution. Each program it ships has a recipe, one file in `recipes/`. It
names the upstream source and each patch basalt applies by SHA-256, the license, and the SHA-256 of
the package it builds for each architecture. §195's clause 1 says this digest lives
in a recipe "changed by human review". So every new upstream release waits for a person to open,
read and merge a recipe change.

That is the slow part today. `recipes/ripgrep.toml` pins ripgrep 14.1.1 (crates.io, 2024-09-09).
crates.io lists four releases after it: 15.0.0 (2025-10-16), 15.1.0 (2025-10-22), 15.2.0
(2026-07-15) and 16.0.0 (2026-11-22). Nothing moves a recipe without a person, and no person has.

## Is the premise true

Partly, and the part that is not true is the precedent.

- A digest already changes with no person. basalt's `pin-bump` workflow moves the nife pin daily
  and rewrites every recipe's `[package_digest]` lines in the same pull request. It arms auto-merge
  on itself when the diff touches only `pins.toml` and those lines. Its required checks are the
  review: nife's system test on three architectures, two byte-identical package builds, the `jig`
  installs and two composed image boots. The architect approved this on 2026-10-21 (UTC), and the
  workflow's header records it. So clause 1 holds today only for the upstream and patch digests.
- The endowment is basalt's, not upstream's. The progenitor endows a program from the manifest note
  inside its executable, and the digest covers the note, so a program that asks for more has a new
  digest (`crates/capability_manifest_note`). ripgrep is unmodified crates.io source and carries no
  note of its own. basalt's build links the one `cargo xtask foreign-note` writes, which is
  `program_table::UNVOUCHED_STD_MANIFEST`: a `std` program that hears its words and reads what they
  name, read-only, with no network, entropy or domain. So an upstream release cannot widen ripgrep's
  endowment by itself. Only a change on basalt's or nife's side can.
- The machine does not ask. §220 (signed builds, and trusting a key is scoped) refuses an install
  whose manifest exceeds the source's ceiling. basalt's default trust line has the ceiling
  `domain entropy network` (§195's amendment of 2026-10-10). So a basalt package that newly asks
  for the network installs with no question to the owner. The recipe review is the only place a
  person sees it.

## The rule

Clause 1 of §195 reads: a package's digest lives in a version-controlled recipe that a review changes,
and the review is a person's or the checks below. The machine still trusts the recipes of the
sources it was given.

1. A bot opens the pull request. When an upstream publishes a release, a scheduled basalt workflow
   opens a recipe pull request with the new source and the package digests the build writes. It
   reads the source's SHA-256 from the upstream's own index (for a crate, the `cksum` in crates.io's
   index). A newer release replaces the open pull request for that recipe.
2. It merges with no person when all of these hold:
   - the package builds from source, and two independent builds give the same bytes (the existing
     `reproduce` job);
   - the boot tests pass (the existing `install` and `composed` jobs);
   - every patch basalt carries still applies to the new upstream, with the patch file untouched;
   - the declared license stays the same: the upstream's own license field equals the recipe's
     `license`, and each of its `license_files` exists (new: a comparison);
   - the endowment stays the same or narrows: the note decoded from each new package's bytes equals
     the served package's note or grants a subset of it (new: a decode and a comparison). It reads the built bytes and not a recipe key, so it sees a widening from any
     route.
3. A person reviews only when the endowment widens, the license changes, or a patch no longer
   applies. The bot leaves the pull request open, names the check that held it, and adds the label
   that asks a person. Any other failing check leaves a red pull request, as a red pin bump does.
4. Publishing stays as it is. A merge to basalt `main` already publishes the index and the packages
   (`packages.yml`, the `publish` job). This adds no path to the index.
5. On the owner's machine nothing changes by default. The owner decides whether and when a machine
   updates (§250 (an image names its distribution's package index)'s amendment of 2026-10-07).
   Scheduled updating is a setting the owner turns on per source, which is clause 2's shape.
   `jig rollback` undoes an update in one line by pointing the installed programs one generation
   back (§208 (installing a package is granting it, and the installed programs are versioned)).
6. An optional hold. A source may set a number of days a new upstream release must age before its
   pull request may merge. It is a setting per source, not a fixed number. basalt's value is 7
   days, provisional: the maintainer sets and changes it, as a two-way door.

A recipe may also opt out with a reason, as Homebrew's `no_autobump!` does.

## What this does not catch

**A compromised upstream release that asks for no new endowment passes every check.** That is the
xz case. The xz 5.6.0 and 5.6.1 release tarballs carried a backdoor, and part of it lived only in
the tarball and not in git (Andres Freund, oss-security, 2024-03-29). The tags carry the dates
2024-02-24 and 2024-03-09, so the releases sat in public for 34 and 20 days before the disclosure.
A crate is the same kind of object: an archive the publisher uploads, which need not match the
repository. Such a release builds, reproduces, boots, takes its patches, and keeps its license and
endowment.

Two things bound it, and neither is a review.

- Confinement bounds what it can reach to what the previous version already held. A compromised `rg`
  holds a read-only view of what its words name and nothing else. It holds no network capability,
  so it cannot send what it reads anywhere. Where a program inherits its user's authority, the same
  release could. The endowment check keeps that bound from eroding one release at a time.
- The hold is the only defense that works by time. It helps only if somebody else finds the problem
  inside the hold. A week would not have caught xz. A hold of 35 days would have, and would also
  delay every fix by 35 days.

Nor does it catch a new transitive dependency in the upstream's lockfile; the pull request lists
the lockfile diff, and nothing holds on it.

## A worked example: ripgrep 14.1.1 to 15.0.0

Checked against the crates on 2026-11-25 (UTC), with basalt's 7-day hold. The bot is not built
yet, so this is what it will do.

1. crates.io's index gives ripgrep 15.0.0 the SHA-256 `db22b6e9...f946`. With the hold, its pull
   request could merge no earlier than 2025-10-23. The bot changes `version` to `15.0.0` and
   `sha256` to the new digest.
2. 15.0.0's `Cargo.lock` takes `ignore` 0.4.24, not 0.4.23. The bot rewrites the `[[patch]]` entry's
   `version` and `sha256` for 0.4.24 and leaves `file` and `file_sha256` alone.
   `patches/ripgrep-ignore-walk.patch` applies to `ignore` 0.4.24 under `patch -p1 --dry-run` with
   no rejected hunk.
3. 15.0.0's `Cargo.toml` says `Unlicense OR MIT`, the recipe's value. The license check passes.
4. The new `bin/rg` carries the same `UNVOUCHED_STD_MANIFEST` note, because basalt links it. The
   endowment check passes.
5. The two builds compare equal, `jig` installs it and the composed images boot. The pull request
   merges and publishes with no person. An owner with scheduled updating on gets it at the next
   update, anyone else with `jig install`, and either can undo it with `jig rollback`.

**If 15.0.0 suddenly asked for the network**, two different things stop the two ways it could.

- If the upstream code starts opening sockets, the package still carries basalt's note, which grants
  no network. The endowment check passes and the program runs without the capability, so its network
  calls fail at run time. If that breaks a search, the `install` job's `rg` line fails and the pull
  request goes red. If it does not, the release merges, confined. Nothing in the chain reads the code.
- Suppose somebody changes the note so that `rg` asks for the network, through the foreign note or
  a recipe that carries its own manifest. Then the new note sets `network` and the served one does
  not.
  The endowment check holds the pull request for a person. Without that check nothing would hold it,
  since basalt's ceiling already covers `network` and the machine would install it without asking.

## The prior art, read 2026-11-25 (UTC)

| System | Who opens the change | What merges it | Time gate | A permission diff decides review |
|---|---|---|---|---|
| Homebrew `homebrew-core` | `autobump.yml`, every 3 hours | the `automerge` workflow, after a person approves | none | no |
| nixpkgs | `@r-ryantm` | the merge bot, when a package maintainer asks | none | no |
| Debian testing | the uploader, to unstable | the migration, automatically | 2, 5 or 10 days | no |
| Renovate | the bot | `automerge` on green, if set | `minimumReleaseAge` | no |
| Dependabot | the bot | a person, or a separate auto-merge rule | `cooldown` | no |
| Flathub | `flatpak-external-data-checker` | a person, or automerge by exception | none | no |
| Android | the developer | the store, automatically | none | only at run time, for dangerous permissions |
| Chrome extensions | the developer | the store, automatically | none | yes, at the user |

- Homebrew. "Every 3 hours, a GitHub Action opens a new pull request to upgrade them to the latest
  version" for every formula without a `no_autobump!` and its reason (`docs.brew.sh/Autobump`).
  The merge needs a person: `homebrew-core`'s `automerge.yml` merges only when `reviewDecision ==
  "APPROVED"`, CI has finished and GitHub reports the pull request mergeable. Example: a bump of a
  formula's `url` and `sha256`, merged by the workflow once a maintainer approves. Where nife
  differs: option A drops the approval when the checks hold.
- nixpkgs. `@r-ryantm` makes pull requests "that bump a package to the latest version". Its checks
  run each binary with several flags for a zero exit and the new version number, and report CVEs
  resolved and introduced (`nixpkgs-update`, `details.md`). The merge bot merges an `@r-ryantm` pull
  request under `pkgs/by-name/` when a maintainer of every touched package comments
  `@NixOS/nixpkgs-merge-bot merge` (`ci/README.md`). Example: a `pkgs/by-name` bump merged on its
  maintainer's comment. Where nife differs: nixpkgs has no permission manifest to diff, so a person
  is the only check on what a package may do.
- Debian testing. A package migrates from unstable once it has "been in unstable for 10, 5 or 2
  days, depending on the urgency of the upload". It also needs current builds on every architecture
  it had before, no release-critical bug the testing version lacks, and no breakage in testing
  (`debian.org/devel/testing`). No person approves a migration. Example: a normal-urgency upload
  reaches testing after 5 days with no RC bug filed. Where nife differs: Debian's age gate works
  because people run unstable and file bugs, a population basalt does not have, so basalt's hold
  buys less. Freund found the xz backdoor on Debian sid machines.
- Renovate. `minimumReleaseAge` makes Renovate "wait for a specified amount of time before
  suggesting a dependency update", per version. With `automerge` it opens the pull request at once
  and merges it only after the age passes, and it "only automerges branches which are up-to-date and
  green". Example: `{"matchDatasources": ["npm"], "minimumReleaseAge": "3 days"}`, since npm lets a
  publisher unpublish a package for 72 hours. Where nife differs: option A's hold is the same
  mechanism, set per source.
- Dependabot. `cooldown` delays version updates by `default-days` (3 when omitted) or per semver
  level, with `include` and `exclude` lists, and never delays security updates. Example:
  `cooldown: {default-days: 7}`. Where nife differs: not in kind; basalt's `dependabot.yml` sets
  none today.
- Flathub. A source with `x-checker-data` gets update pull requests: "by default, the tool opens a PR
  whenever a source has an update". It automerges only its pull requests that fix a broken source
  URL, and merging all of them "requires a Flathub exception". Example: `x-checker-data: {type:
  github, repo: example/app, tag-pattern: '^v([0-9.]+)$'}`. Where nife differs: a Flatpak's sandbox
  permissions sit in the manifest the pull request edits, and the checker's README does not mention
  them. Flathub's own review of a permission change went unread here.
- Android. The system grants install-time permissions when the user installs an app, and `INTERNET`
  is one: "Protection level: normal" (`Manifest.permission`). It asks for dangerous permissions only
  at run time. So an update that newly adds `INTERNET` installs with no question. Example: any app
  update that adds network access. Where nife differs: nife has no normal tier; the network is a
  capability the progenitor grants from the note. Today a basalt package that widens to `network`
  stands where an Android app adding `INTERNET` stands, which is why the endowment check sits in
  basalt.
- Chrome extensions. When an update adds a permission with a new warning, "the extension will be
  disabled until the user accepts the new permission" (`developer.chrome.com`, permission warnings).
  That is a review decided from a permission diff, placed at the user. Example: an update that adds
  a host permission for every site. Where nife differs: option A places the review at the
  distribution. Placing it at the owner as well is option E.

Every system automates opening the change, and most still have a person merge it. Those that merge
with no person gate on age and tests. Only the two with a permission manifest decide review from its
diff, and both decide at the user.

## Options

| | What it is | Why it wins or loses |
|---|---|---|
| **A. Checks stand in for review** | the rule above; a person only on a widening, a license change or a failed patch | Chosen. It spends the person where nife's design puts the risk, in what a program may reach. |
| B. Keep clause 1 | every recipe change waits for a person | ripgrep sits four releases behind under it today. A person reading an upstream's whole diff would not catch xz either, so the review mostly repeats A's checks by hand. |
| C. The bot opens, people merge (nixpkgs, Homebrew) | A's step 1 and its checks, with a person on every merge | Better than B and the common practice. It loses because, with nobody reading the upstream's code, the person adds a click and not a check, and the click is what is missing today. |
| D. Automate fully, widening included | A without the widening trigger in step 3 | A widening is the one change confinement cannot bound, and basalt's ceiling would not stop it on the machine. This removes the only person who would see it. |
| E. A, plus the owner's consent on a widening (Chrome) | `jig` refuses or asks when an update's note grants more than the installed one's | Not refused, and not part of this ruling. It changes the install rule of §208 and §220, which A leaves alone, and deserves its own proposal. |

**A was chosen.** It is not about effort: B costs the least to build, since it builds
nothing. Would A still win if both cost the same? Yes, because A spends its person on the one
change nothing else bounds.

## What it costs

Estimated, not measured. The build, reproduce, install, composed and patch checks exist. Four
pieces are new, each a basalt change through basalt's queue:

- a scheduled job that reads each upstream's index and opens the pull request, on `pin-bump`'s
  template;
- the license comparison;
- the endowment comparison, which runs `capability_manifest_note::decode` on both packages;
- the hold, a status check that stays pending until the release has aged, like Renovate's
  `renovate/stability-days`.

## Reversibility, and who has acted on it

Checked 2026-11-25 (UTC): `nifeos/basalt` has no forks and no stars. Its pull requests come from
calef, `nife-smelter[bot]` and Dependabot only. No other source stands up a recipe under clause 1,
and `pin-bump.yml` notes that basalt has no customers yet. So nobody outside has acted on clause 1,
and the rule itself is reversible: turning the bot off restores it.

Each release the bot merges is not reversible. A merge publishes, and a package an owner installs
runs on that owner's machine. `jig rollback` takes it out of the installed programs and does not undo
what it did while it ran. The endowment bounds that cost, which is why the endowment check is the
one that keeps a person.

## What it unblocks

The basalt bot, the license and endowment checks, and the hold, each a basalt change through
basalt's queue. Until they land, recipe changes still wait for a person, because nothing yet stands
in for one.
