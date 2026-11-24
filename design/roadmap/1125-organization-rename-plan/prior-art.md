# Prior art

An appendix to [the milestone](../1125-organization-rename-plan.md).

The lane read or measured each entry on 2026-11-24.

| system | what moved | how | source |
|---|---|---|---|
| this project | the organization, crickertech to nifeos, on 2026-10-03 | links, `gh` arguments and scripts were changed to the new name; prose that described the past kept the old one; old URLs redirect | the record's [project history](../../tenets/project-history.md) |
| GitHub, repository transfer | one repository to another owner | issues, pull requests, the wiki, stars, watchers, webhooks, secrets and deploy keys move with it; links and git redirect until the old name is reused; a repository with more than 100 Actions uses in the week before has its old name retired | GitHub's documentation, "Transferring a repository" |
| GitHub, the REST API | the same | `POST /repos/{owner}/{repo}/transfer` with `new_owner`, an optional `new_name` and `team_ids`; it answers 202 and finishes later | GitHub's REST documentation, "Transfer a repository" |
| GitHub, Actions | a repository that hosts a reusable workflow | Actions follows no redirect for an action or a reusable workflow, so a caller's `uses:` line fails at the old name; `secrets: inherit` is documented within one organization or enterprise, and a caller in another organization passes named secrets | GitHub's documentation, "Reusing workflow configurations" |
| GitHub, Actions settings | a repository whose allowed actions are `selected` | actions and reusable workflows of its own organization are allowed; any other needs a pattern of the form `OWNER/REPO/PATH@ref`, with wildcards | GitHub's documentation, "Managing GitHub Actions settings for a repository" |
| release-please-action | the action's repository, moved between organizations | callers that named the old owner failed with "Unable to resolve action" until they changed the line; users reported that callers pinned to a commit kept working, which the lane did not test | googleapis/release-please-action issue 980 |
| cargo | a git source whose URL changes | cargo identifies a git source by its URL, so one repository under two URLs is two sources, and a crate under both is two packages | measured: nife's workspace with the rewritten manifests and the `grant_plan` pin left at a commit that names the old URL locked `byte_glob`, `grant_contract` and `program_argument_contract` twice |

Where this move differs. At the first rename the organization held two repositories, and the
redirect carried nearly everything. Now 33 repositories leave and six stay, and the 33 call one
shared workflow repository by `uses:`, which no redirect carries. So the callers move first, still
calling the old name, and the shared repository moves last.

An example from the plan: a crate repository's `.github/workflows/ci.yml` writes
`uses: partsfoundry/crate-workflows/.github/workflows/check.yml@<sha>` where it writes
`uses: nifeos/crate-workflows/...` today. Its CI fails from the transfer of crate-workflows until
that line lands.
