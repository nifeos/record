# The census

An appendix to [the milestone](../1125-organization-rename-plan.md).

`helpers/organization_rename.py census` in nife (added by nifeos/nife#4077), run on 2026-11-24 over
each repository's default branch. It counts lines, not occurrences, and gives each line the first
form it matches, in the order the tool lists its forms. A line in a history path stays, whatever its form: bench logs, `vendor/`, patches, audit
reports, changelogs, and any record marked as history. So does a line that already names
crickertech.

The lane read these commits:

```
address_space_layout@840ddb7
basalt@2ed3305
basalt-backup@1cca64a
block_roster_contract@b239a54
boot_ladder@6f2dfda
byte_glob@519cedb
byte_sink_contract@d46cbe2
capability_table@20e2deb
clock_contract@0aa2107
counter_frequency_contract@7e7bc1b
crate-workflows@abad4c3
crate-workflows-test@fdb2f71
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
nife@231595b
non_volatile_memory_express@3d9080a
program_argument_contract@764e0e5
record@83a0015
rsext4@9a157a7
terminal_contract@4464f90
universal_serial_bus@0fbceff
partsfoundry.org@a5052f1
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

| repository | breaks | tied | redirects | stale | stays | lines |
|---|---|---|---|---|---|---|
| nife | 11 | 3,158 | 1,013 | 35 | 228 | 4,445 |
| record | 38 | 494 | 1,435 | 1,283 | 308 | 3,558 |
| basalt | 5 | 1 | 26 | 7 | 33 | 72 |
| basalt-backup | 0 | 0 | 16 | 0 | 1 | 17 |
| crate-workflows | 26 | 0 | 48 | 5 | 11 | 90 |
| crate-workflows-test | 10 | 0 | 6 | 1 | 2 | 19 |
| fuzz-host | 4 | 0 | 27 | 58 | 4 | 93 |
| partsfoundry.org | 0 | 10 | 11 | 12 | 3 | 36 |
| address_space_layout | 11 | 0 | 7 | 0 | 0 | 18 |
| block_roster_contract | 10 | 0 | 7 | 0 | 0 | 17 |
| boot_ladder | 11 | 0 | 7 | 0 | 0 | 18 |
| byte_glob | 11 | 0 | 7 | 0 | 0 | 18 |
| byte_sink_contract | 11 | 0 | 7 | 0 | 0 | 18 |
| capability_table | 11 | 0 | 7 | 0 | 0 | 18 |
| clock_contract | 11 | 0 | 7 | 0 | 0 | 18 |
| counter_frequency_contract | 11 | 0 | 7 | 0 | 0 | 18 |
| designware_ethernet | 11 | 0 | 7 | 0 | 1 | 19 |
| designware_mobile_storage | 10 | 0 | 9 | 0 | 0 | 19 |
| device_tree_blob | 11 | 0 | 8 | 0 | 0 | 19 |
| domain_name_system | 11 | 0 | 7 | 0 | 0 | 18 |
| e1000e | 10 | 0 | 8 | 0 | 0 | 18 |
| entropy_contract | 11 | 0 | 9 | 0 | 1 | 21 |
| environment_contract | 11 | 0 | 8 | 0 | 0 | 19 |
| extensible_host_controller_interface | 10 | 0 | 8 | 0 | 0 | 18 |
| file_allocation_table | 10 | 0 | 7 | 0 | 0 | 17 |
| file_system_contract | 17 | 0 | 16 | 0 | 0 | 33 |
| generational_table | 10 | 0 | 7 | 0 | 0 | 17 |
| grant_contract | 11 | 0 | 9 | 0 | 0 | 20 |
| grant_plan | 11 | 0 | 13 | 0 | 0 | 24 |
| interfaces_note | 11 | 0 | 8 | 0 | 0 | 19 |
| intrusive_queue | 11 | 0 | 7 | 0 | 0 | 18 |
| jh7110_entropy | 10 | 0 | 7 | 0 | 0 | 17 |
| line_editor | 11 | 0 | 7 | 0 | 0 | 18 |
| moho_abi | 11 | 0 | 7 | 0 | 0 | 18 |
| non_volatile_memory_express | 10 | 0 | 9 | 0 | 0 | 19 |
| program_argument_contract | 11 | 0 | 7 | 0 | 0 | 18 |
| rsext4 | 11 | 0 | 12 | 0 | 2 | 25 |
| terminal_contract | 11 | 0 | 7 | 0 | 0 | 18 |
| universal_serial_bus | 11 | 0 | 7 | 0 | 0 | 18 |
| all 39 | 433 | 3,663 | 2,832 | 1,401 | 594 | 8,923 |

## By form and group

| form | group | lines |
|---|---|---|
| record-path | tied | 3,272 |
| web-link | redirects | 1,984 |
| citation | stale | 1,401 |
| qualified-path | tied | 391 |
| slug-code | redirects | 326 |
| cargo-git | redirects | 325 |
| uses | breaks | 315 |
| word | stays | 220 |
| dns | stays | 146 |
| api-repo | redirects | 121 |
| web-link | stays (history) | 66 |
| record-path | stays (history) | 49 |
| cargo-metadata | redirects | 38 |
| api-org | breaks | 38 |
| raw | redirects | 36 |
| org-literal | breaks | 35 |
| team | breaks | 34 |
| citation | stays (history) | 32 |
| citation | stays (former name) | 23 |
| word | stays (history) | 19 |
| pages | breaks | 11 |
| slug-code | stays (history) | 10 |
| dns | stays (history) | 8 |
| local-path | stays (history) | 7 |
| api-repo | stays (history) | 6 |
| word | stays (former name) | 4 |
| pin | redirects | 2 |
| api-org | stays (history) | 2 |
| local-path | stays | 1 |
| pages | stays (history) | 1 |
