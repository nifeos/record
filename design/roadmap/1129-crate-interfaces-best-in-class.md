---
status: NOT-STARTED
raised: 2026-11-25
milestone_dependencies: none
decision_dependencies: unwritten
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1129. The combine review: each crate's interface against the best in its space

The number, title and slug are provisional. The branch that wrote this block is
`milestone/1129-crate-interfaces-best-in-class`.

The publishing hold names a review that no block defines. Milestone 1050's Goal holds every
partsfoundry crate back from crates.io until every outside review milestone is delivered "and the
combine review has decided what the crates share", and step 11a of
[the crate move](../../notes/crate-move.md) says the combine review checks each crate's outside
review. A search of the record on 2026-11-25 (UTC) for "combine review" finds those two places and
[1050's prior-art appendix](1050-designware-mobile-storage-outside-review/prior-art.md), which
lists four questions for it, and nothing else. This block is that review.

It is also wider than the hold asks. The outside reviews (milestones 1048 to 1113) set a floor: a
stranger builds, tests and proves the crate from its README, the documents match the code, the
names follow [design/naming.md](../naming.md), and nothing one-way ships that a later release must
take back. They did not ask whether the interface is the best one in its space. This block asks
that of every crate, against the strongest existing crate or system doing the same job, because
the interface bounds the implementation behind it. An interface that forces a copy, an allocation,
a lock or a runtime check caps every later implementation at that cost.

What drives it: the first crates.io publish of each crate, which the hold already waits on. What
it saves: a breaking version for every interface gap found after a stranger depends on the crate,
and a second pass over the same crates to decide what they share.

Reuse: the outside review milestones and their review packages in
[notes/crate-reviews/](../../notes/crate-reviews/), with every name they ratified;
`script/review-status`, which counts each crate's findings; `script/stranger-test`; each crate's
own benchmarks and Kani harnesses; the crates.io API for the demand figures. No new tool.

## Goal

Each crate publishes at 0.1.0 with an interface no comparator beats on an axis that matters to its
users, or with a recorded reason where one does. The crates share one convention wherever they
solve the same problem, decided once. Every one-way door either finding leaves open has a ruling
before the first publish.

## The crates

The scope is the library crates in the partsfoundry organization, 29 of them on 2026-11-25 (UTC),
each with its outside review as the baseline:

| crate | baseline | crate | baseline |
|---|---|---|---|
| `address_space_layout` | 1076 | `file_system_contract` | 1090 |
| `block_roster_contract` | 1059 | `generational_table` | 1048 |
| `boot_ladder` | 1078 | `grant_contract` | 1094, package `grant-contract.md` |
| `byte_glob` | 1092 | `grant_plan` | 1094 |
| `byte_sink_contract` | 1079 | `interfaces_note` | 1096 |
| `capability_table` | 1081 | `intrusive_queue` | 1097 |
| `clock_contract` | 1083 | `jh7110_entropy` | 1049 |
| `counter_frequency_contract` | 1073 | `line_editor` | 1098 |
| `designware_ethernet` | 1074 | `non_volatile_memory_express` | 1058 |
| `designware_mobile_storage` | 1050 | `program_argument_contract` | 1106 |
| `device_tree_blob` | 1085 | `terminal_contract` | 1098, package `terminal-contract.md` |
| `domain_name_system` | 1087 | `universal_serial_bus` | 1111 |
| `e1000e` | 1057 | `entropy_contract` | 1071 |
| `environment_contract` | 1089 | `extensible_host_controller_interface` | 1060 |
| `file_allocation_table` | 1061 | | |

Three are outside it. `file_system_fixture` is test data that never publishes. `rsext4` is a fork
of a published crate: its interface belongs to its upstream, so a finding against it becomes an
upstream submission, which the architect reads in full before it is filed. A crate that moves to
partsfoundry later joins at its move, in its place in the order below.

`grant_contract` and `terminal_contract` split out of the crates that 1094 and 1098 reviewed and
have no outside review milestone of their own. Their reviews here also check the floor the outside
reviews set.

## The baseline, and the release-review rule

The outside reviews and the names they ratified are the starting point, and this block re-raises
neither. One rule reopens a name: a name ratified before a later naming rule is checked against the
rules in force at release ([notes/crate-reviews.md](../../notes/crate-reviews.md)). This review is
that release review, so it lists each such name with a recommended replacement. Every other
ratified name stays, and a finding that would rename one says so as a one-way door, with the
comparator evidence, for the architect.

## Per crate: what the review does

### Choose the comparators by measurement

For each crate the review names its comparators and records, for each one, the version read, total
downloads, downloads in the last 90 days, the count of reverse dependencies, the date it was last
updated, and the date measured (UTC). It takes the numbers from the crates.io API
(`/api/v1/crates/<name>` and `/api/v1/crates/<name>/reverse_dependencies`) on the day the review
runs.

- Up to three Rust crates that solve the problem a stranger would choose this crate for, ranked by
  90-day downloads. A crate that solves a neighboring problem may stand in the table, marked as a
  neighbor, but it does not rank.
- The crates this one should integrate with, measured the same way and listed apart: the traits it
  might implement or accept, such as `embedded-hal`, `embedded-io`, `rand_core`, `smoltcp`'s
  device traits or `core::fmt::Write`.
- Where no Rust comparator in the same problem draws 10,000 downloads in 90 days, the best-known
  system outside Rust that solves it (a C library, an operating system's driver, a specification's
  reference code), read at a named version or commit.

The first measurement, which sets the order below, is in
[the demand appendix](1129-crate-interfaces-best-in-class/demand.md).

### Compare the public interface

The review reads each comparator's documentation and source at the version measured, and compares
the crate on each axis below that applies, saying for each which side is better and why:

1. Misuse made unrepresentable: newtypes, typestate, private fields, sealed traits, and which
   wrong calls the compiler refuses on each side.
2. Errors: one type or several, whether each is an enum a caller can match, whether it implements
   `core::fmt::Display` and `core::error::Error`, and whether a caller can recover the input that
   failed.
3. `no_std` and `alloc`: what works with neither, what each feature adds, and whether a feature
   changes a signature.
4. Borrowing against owning: whether a parse borrows its input, whether a result can outlive it,
   and every copy or allocation the interface forces.
5. Iteration: whether sequences are iterators with the standard adapters, and what they yield.
6. Ecosystem traits: the integration crates above, plus `core::fmt`, `Default`, `From` and
   `TryFrom`, `Hash` and `Ord` where the type is a value.
7. The [Rust API Guidelines checklist](https://rust-lang.github.io/api-guidelines/checklist.html),
   all 54 items, each marked met, not met or not applicable, with the item code.
8. Documentation shape: the crate-level page, an example on every public item a caller starts
   from, a failure section on every fallible function, and what a stranger needs to read before the
   first call, against the comparator's.
9. Measured performance, where the interface shapes it: a benchmark of the crate and its leading
   comparator on the same input and the same machine, with the command, the machine type, both
   numbers and what each includes. A measurement not run is marked not run, never estimated.

### Write the findings

The output for each crate is one proposed roadmap block titled "`<crate>`: the release review's
findings", in the outside reviews' form, so `script/review-status` counts it. Each finding carries
a priority, the evidence (the comparator, its version, the file or item read), the change, the door
and the effort. P0 blocks the crate's 0.1.0 interface and its first publish. P1 lands before the
first release. P2 may follow. The block lists its one-way doors apart, after the findings, each
with a recommendation, so the architect rules them one at a time. It carries a prior-art table of
its comparators with the numbers above, and a section on what the crate does better than each.
Text filed into a crate's own repository never names nife.

Each finding states whether it was verified in the source or inferred. A possible vulnerability
goes to the maintainer alone and stays out of the block.

## Across crates: what they share

Some shapes recur, and the crates share each one or differ on purpose, decided once. A grep of the
29 crates on 2026-11-25 (UTC) shows how far they differ today. Each count is approximate, and the
census in step 1 recounts it.

| shape | today | the question |
|---|---|---|
| Errors | about nine crates implement `core::error::Error`; others return bare enums or `Option` | one convention: an enum per operation or per crate, `Display` and `core::error::Error` always, the input that failed carried or not |
| DMA regions | three traits named `DirectMemoryAccessRegion`, in `designware_ethernet`, `designware_mobile_storage` and `e1000e`, with different offset widths and barrier placement | one trait or two, and whether it lives in its own crate (1050's appendix recommends two for now) |
| Doorbells and tails | two `Tails` traits and two `Hardware` traits | one register-access shape for ring drivers, or each its own |
| Register access | each driver reads and writes through its own trait | a shared shape, against `tock-registers` and `safe-mmio` |
| Byte sinks and sources | `line_editor`'s `Sink`, `file_allocation_table`'s `SectorDevice` and optional `embedded-io-07` feature | which crates implement or accept `embedded-io` and `core::fmt::Write`, and under what feature name |
| Feature names | `simulator`, `peak`, `embedded-io-07` | one naming rule for features, and for a feature that names a dependency's version |
| Contract crates | about a dozen crates hold a page layout or request words | one layout: magic, version, interface identity, the request builder, the decoder and its refusals, in the same places and spellings |
| Simulators | `designware_mobile_storage` ships one as a feature | whether every driver ships its test double, and under one feature name |

Each question becomes one decision, brought once the crates it touches have been reviewed, with
those reviews as its evidence. A crate reviewed before a shared decision gets a finding that follows
it. A shared shape that becomes its own crate is a new name and a new repository, and each is the
architect's call.

## The order

By measured demand: the crates a stranger is most likely to adopt come first, so the reviews that
matter most land soonest and the work runs a few crates at a time. Demand is the 90-day download
count of a crate's leading comparator, from [the demand appendix](1129-crate-interfaces-best-in-class/demand.md).
Crates with no Rust comparator follow, grouped so that one lane sees the crates that should share a
layout.

Each lane reviews three crates, and two lanes run at a time. Each lane is a fresh-context agent the
maintainer launches on the most capable model available. It is never a lane that wrote,
extracted or reviewed the crate before, and it does not read the crate's own lanes' reports. Its
pass is read-only on the crate repositories: no push, no pull request, no issue, no tag.

1. The census, one lane, before any review: every shape in the table above, counted in each crate
   at a named commit, with the command that counted it.
2. Lane A: `byte_glob`, `generational_table`, `domain_name_system`.
3. Lane B: `line_editor`, `intrusive_queue`, `designware_mobile_storage`.
4. Lane C: `file_allocation_table`, `device_tree_blob`, `e1000e`.
5. Lane D: `extensible_host_controller_interface`, `designware_ethernet`,
   `universal_serial_bus`.
6. The first shared decisions, once lanes A to D are done: errors, DMA regions, doorbells and
   tails, register access, byte sinks, feature names and simulators.
7. Lane E: `non_volatile_memory_express`, `jh7110_entropy`, `capability_table`.
8. Lane F: `interfaces_note`, `address_space_layout`, `boot_ladder`.
9. Lane G: `grant_plan`, `grant_contract`, `program_argument_contract`.
10. Lane H: `block_roster_contract`, `byte_sink_contract`, `clock_contract`.
11. Lane I: `counter_frequency_contract`, `entropy_contract`, `environment_contract`.
12. Lane J: `file_system_contract`, `terminal_contract`.
13. The contract-crate layout decision, once lanes F to J are done.

Each lane measures its crates' comparators again on the day it runs. A crate whose demand moved it
past a later lane's crates keeps its place; the order is for scheduling, not a ranking to maintain.

## Gating

Provisional (maintainer, 2026-11-25 UTC):

- It blocks each crate's first crates.io publish, as the hold already does, until that crate's
  block has every P0 finding Done and every one-way door ruled, and every shared decision that
  touches the crate is ruled.
- It blocks each crate's 0.1.0 interface the same way: a crate's tag at 0.1.0 waits for its P0
  findings. Pre-release tags (`0.1.0-pre.N`) do not wait.
- It does not block implementation work behind an unchanged interface: a fix, a proof, a test or a
  speedup that changes no public item lands as before.

## Prior art

How other projects review an interface before they promise it is in
[the prior-art appendix](1129-crate-interfaces-best-in-class/prior-art.md). In short: the Rust
library team's 2017 blitz evaluated sixteen crates against the API Guidelines before their 1.0s,
one crate at a time with a lead and a public write-up; Tokio shipped 0.3 as a 1.0 beta and took
pre-1.0 dependencies out of its public interface; embedded-hal 1.0 removed the traits generic
drivers could not use and gave every error a kind from one fixed set. This block takes the
blitz's shape (a checklist, one crate at a time, findings filed as discrete items), Tokio's rule on
public dependencies, and embedded-hal's error convention as one candidate for the shared decision.
It differs in measuring each crate against named comparators, which none of them did.

## Done when

1. The census exists, with each count and the command and commit that produced it.
2. Each of the 29 crates has a proposed block titled "`<crate>`: the release review's findings",
   and `script/review-status` lists it.
3. Each block names its comparators with version, total and 90-day downloads, reverse
   dependencies, last update and the date measured, and marks the 54 API Guidelines items.
4. Each block either records a measured benchmark against its leading comparator or says why the
   interface does not shape performance, and marks any benchmark it did not run as not run.
5. Each block lists its one-way doors apart, each with a recommendation.
6. Every shared question in the table above has a decision recorded, and each crate it touches has
   a finding that follows it.
7. `script/review-status` shows no open P0 in any of the 29 blocks, and every one-way door they list
   is ruled.

## BUGS

- The demand measure counts downloads of the leading comparator, which measures the space, not the
  crate's chance in it. A crate in a crowded space may rank high and still be adopted less than one
  in an empty space.
- Downloads include continuous integration traffic, so they overstate users. Reverse dependencies
  count published crates only.
- The census counts in the shared-shapes table came from a grep, not a reading, and may be off.
- `rsext4` stays outside the bar, so its interface is the upstream's whatever this review finds.

## Index row

The combine review that the publishing hold names, widened to a best-in-class bar. Each crate's
interface is compared with its strongest comparators, chosen by measured downloads, on the API
Guidelines and the axes that matter, and its findings land as a release review block with one-way
doors apart. The shapes the crates share (errors, DMA regions, register access, feature names,
contract layout) are decided once. Lanes of three crates run in order of measured demand, and the
review blocks each crate's first publish and 0.1.0 interface, provisionally.
