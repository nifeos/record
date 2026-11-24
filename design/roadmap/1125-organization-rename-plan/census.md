# The census

An appendix to [the milestone](../1125-organization-rename-plan.md).

`helpers/organization_rename.py census --moving` in nife (from nifeos/nife#4090), run on 2026-11-24
over each repository's default branch, with the list of moving repositories that nife's draft adds
as `helpers/partsfoundry_repositories.txt`. It counts lines, not occurrences, and gives each line
the first form it matches. A line in a history path stays, whatever its form: bench logs,
`vendor/`, patches, audit reports, changelogs, and any record marked as history. So does a line
that already names crickertech.

The tool then sorts each line by the repository it names:

- A line that names a moving repository keeps the group of its form.
- A line that names a repository staying in `nifeos` is counted under "not moving".
- A line that names the organization and no repository (an `orgs/` path, a bare citation) is
  counted under "held". In a moving repository the tool treats it as the library's own, and
  rewrites it; in a staying repository it waits for the record's placement.

The lane read these commits:

```
address_space_layout@840ddb7
basalt-backup@6406ec0
basalt@75c7c20
block_roster_contract@b239a54
boot_ladder@6f2dfda
byte_glob@519cedb
byte_sink_contract@d46cbe2
capability_table@20e2deb
clock_contract@0aa2107
counter_frequency_contract@7e7bc1b
crate-workflows-test@fdb2f71
crate-workflows@abad4c3
designware_ethernet@f40ee90
designware_mobile_storage@dcc989d
device_tree_blob@96ad52a
domain_name_system@c809deb
e1000e@794ca56
entropy_contract@5c9f8eb
environment_contract@4778d59
extensible_host_controller_interface@5bc4cf9
file_allocation_table@faaf13f
file_system_contract@7577a7d
fuzz-host@59406b6
generational_table@8328360
grant_contract@d4e9ca2
grant_plan@b8c93c7
interfaces_note@1a75040
intrusive_queue@10d1fa2
jh7110_entropy@2bf731c
line_editor@b43cb31
moho_abi@c8d556e
nife@d23b43d
non_volatile_memory_express@3d9080a
partsfoundry.org@9042f69
program_argument_contract@764e0e5
record@ddb3766
rsext4@33cb5ed
terminal_contract@4464f90
universal_serial_bus@0fbceff
```

The private record of the maintainers' machines is not counted here.

## The forms

| form | what it matches | group |
|---|---|---|
| uses | a `uses:` line naming a workflow or action in the organization | breaks |
| api-org | a REST path under `orgs/<org>`, GraphQL `organization(login:)`, `gh search --owner`, `gh repo list <org>` | breaks |
| team | a team handle, `@<org>/<team>` | breaks |
| org-literal | the organization alone as a value in code: an owner constant, `owner:` to the App token action, cargo-deny's `github = [...]`, the template's settings | breaks |
| pages | `<org>.github.io` and Pages configuration | breaks |
| api-repo | a REST path under `repos/<org>/<repo>` | redirects |
| cargo-git | a cargo git source, in a manifest or a lockfile | redirects |
| cargo-metadata | `repository =` and `homepage =` in a manifest | redirects |
| pin | a repository URL in basalt's `pins.toml` | redirects |
| raw | a raw.githubusercontent.com URL | redirects |
| slug-code | `<org>/<repo>` in code, such as a `--repo` argument | redirects |
| web-link | a github.com URL | redirects |
| record-path | `<org>/record:<path>` | tied |
| qualified-path | `<org>/<repo>:<path>` for another repository | tied |
| citation | `<org>/<repo>#N` or `@<commit>` in prose | stale |
| dns | nifeos.org, basalt.nifeos.org and their subdomains | stays |
| word | the project word | stays |
| local-path | a checkout path on a maintainer's machine | stays |

## By repository

| repository | moves | breaks | tied | redirects | stale | held | stays | not moving | lines |
|---|---|---|---|---|---|---|---|---|---|
| nife | no | 0 | 2 | 411 | 11 | 65 | 228 | 3,727 | 4,444 |
| record | no | 0 | 5 | 184 | 844 | 211 | 308 | 2,000 | 3,552 |
| basalt | no | 0 | 0 | 0 | 0 | 10 | 33 | 29 | 72 |
| basalt-backup | no | 0 | 0 | 0 | 0 | 0 | 1 | 16 | 17 |
| fuzz-host | no | 0 | 0 | 0 | 0 | 5 | 4 | 84 | 93 |
| partsfoundry.org | no | 0 | 0 | 31 | 0 | 13 | 4 | 22 | 70 |
| address_space_layout | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| block_roster_contract | yes | 10 | 0 | 7 | 0 | 0 | 0 | 0 | 17 |
| boot_ladder | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| byte_glob | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| byte_sink_contract | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| capability_table | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| clock_contract | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| counter_frequency_contract | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| crate-workflows | yes | 26 | 0 | 47 | 4 | 0 | 11 | 2 | 90 |
| crate-workflows-test | yes | 10 | 0 | 6 | 1 | 0 | 2 | 0 | 19 |
| designware_ethernet | yes | 11 | 0 | 7 | 0 | 0 | 1 | 0 | 19 |
| designware_mobile_storage | yes | 10 | 0 | 9 | 0 | 0 | 0 | 0 | 19 |
| device_tree_blob | yes | 11 | 0 | 8 | 0 | 0 | 0 | 0 | 19 |
| domain_name_system | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| e1000e | yes | 10 | 0 | 8 | 0 | 0 | 0 | 0 | 18 |
| entropy_contract | yes | 11 | 0 | 9 | 0 | 0 | 1 | 0 | 21 |
| environment_contract | yes | 11 | 0 | 8 | 0 | 0 | 0 | 0 | 19 |
| extensible_host_controller_interface | yes | 10 | 0 | 8 | 0 | 0 | 0 | 0 | 18 |
| file_allocation_table | yes | 10 | 0 | 7 | 0 | 0 | 0 | 0 | 17 |
| file_system_contract | yes | 17 | 0 | 16 | 0 | 0 | 0 | 0 | 33 |
| generational_table | yes | 10 | 0 | 7 | 0 | 0 | 0 | 0 | 17 |
| grant_contract | yes | 11 | 0 | 9 | 0 | 0 | 0 | 0 | 20 |
| grant_plan | yes | 11 | 0 | 13 | 0 | 0 | 0 | 0 | 24 |
| interfaces_note | yes | 11 | 0 | 8 | 0 | 0 | 0 | 0 | 19 |
| intrusive_queue | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| jh7110_entropy | yes | 10 | 0 | 7 | 0 | 0 | 0 | 0 | 17 |
| line_editor | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| moho_abi | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| non_volatile_memory_express | yes | 10 | 0 | 9 | 0 | 0 | 0 | 0 | 19 |
| program_argument_contract | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| rsext4 | yes | 11 | 0 | 12 | 0 | 0 | 2 | 0 | 25 |
| terminal_contract | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| universal_serial_bus | yes | 11 | 0 | 7 | 0 | 0 | 0 | 0 | 18 |
| all 39 | | 375 | 7 | 929 | 860 | 304 | 595 | 5,880 | 8,950 |

## By form and group

Lines counted under "not moving" are left out of this table.

| form | group | lines |
|---|---|---|
| citation | stale | 860 |
| web-link | redirects | 434 |
| cargo-git | redirects | 321 |
| uses | breaks | 314 |
| word | stays | 220 |
| dns | stays | 146 |
| citation | held (organization-wide) | 143 |
| slug-code | redirects | 126 |
| web-link | stays (history) | 66 |
| record-path | stays (history) | 49 |
| cargo-metadata | redirects | 38 |
| api-org | held (organization-wide) | 38 |
| team | breaks | 34 |
| citation | stays (history) | 32 |
| web-link | held (organization-wide) | 30 |
| qualified-path | held (organization-wide) | 28 |
| org-literal | breaks | 27 |
| slug-code | held (organization-wide) | 24 |
| citation | stays (former name) | 23 |
| word | stays (history) | 19 |
| api-repo | held (organization-wide) | 18 |
| pages | held (organization-wide) | 11 |
| slug-code | stays (history) | 10 |
| api-repo | redirects | 10 |
| org-literal | held (organization-wide) | 8 |
| dns | stays (history) | 8 |
| local-path | stays (history) | 7 |
| qualified-path | tied | 7 |
| api-repo | stays (history) | 6 |
| cargo-git | held (organization-wide) | 4 |
| word | stays (former name) | 4 |
| api-org | stays (history) | 2 |
| local-path | stays | 1 |
| pages | stays (history) | 1 |
| web-link | stays (former name) | 1 |
