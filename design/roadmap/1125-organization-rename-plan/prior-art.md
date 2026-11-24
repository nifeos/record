# Prior art

An appendix to [the milestone](../1125-organization-rename-plan.md).

The lane read or measured each entry on 2026-11-24.

| system | what it renamed | how | source |
|---|---|---|---|
| this project | the organization, crickertech to nifeos, on 2026-10-03 | links, `gh` arguments and scripts were changed to the new name; prose that described the past kept the old one; old URLs redirect | the record's [project history](../../tenets/project-history.md) |
| GitHub, organizations | any organization | the old name's repository URLs, git remotes and repository API paths redirect until someone takes the old name; the organization's own profile and API paths do not | GitHub's documentation, "Renaming an organization" |
| GitHub, Actions | a repository or organization that hosts an action or a reusable workflow | a `uses:` line naming the old owner fails, since Actions follows no redirect | GitHub's documentation on renaming a repository, read with the one above |
| GitHub, measured | crickertech, renamed on 2026-10-03 and not claimed since | through the old name: web pages, `git ls-remote`, raw files, release downloads, badges, REST `repos/`, `gh pr list --repo` and GraphQL `repository(owner:)` answer for the new home; REST `orgs/`, GraphQL `organization(login:)` and `gh search --owner` do not | read-only `gh api` and `curl` calls by the lane |
| cargo | a git source whose URL changes | cargo identifies a git source by its URL, so one repository under two URLs is two sources, and a crate under both is two packages | measured: nife's workspace under the rewritten manifests, with the `grant_plan` pin left at a commit that names the old URL, locked `byte_glob`, `grant_contract` and `program_argument_contract` twice |
| crates.io | a team owner | a team owner is written `github:<org>:<team>`, so a published crate owned by a team would need its owner added again under the new name | crates.io's documentation, recalled, not read; no crate here is published |

Where this rename differs. At the first rename the organization held two repositories, nife and
basalt, and the redirect carried nearly everything. Now it holds 40, and 39 of them call one
another: by `uses:`, by git dependency, by qualified record path and by pin. Some of those break
at the rename, and nife's tooling checks others against each other. That is why there is an order, and why the
order puts the shared workflows first and nife last.

An example from the plan: a crate repository's `.github/workflows/ci.yml` writes
`uses: partsfoundry/crate-workflows/.github/workflows/check.yml@<sha>` where it writes
`uses: nifeos/crate-workflows/...` today, and its CI is dead from the rename until that line lands.
