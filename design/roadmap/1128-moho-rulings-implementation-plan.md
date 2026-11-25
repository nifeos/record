---
status: NOT-STARTED
raised: 2026-11-25
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1128. The Moho review's rulings: the order in which they land

The Moho design review, the draft
[nifeos/record#36](https://github.com/nifeos/record/pull/36), ruled every one-way finding on
2026-11-25 (UTC), and the maintainer ruled findings 7, 8, 13, 14 and 15 provisionally the same
day. This block is the plan that lands those rulings in `nifeos/moho_abi`, nife and
basalt. It changes no code. The branch is `milestone/1128-moho-rulings-implementation-plan`, and
the number is provisional.

What drives it: the first publish of `moho_abi`, and the measurement block that the draft
[nifeos/record#37](https://github.com/nifeos/record/pull/37) proposes, which starts once the P0
fixes land. What it saves: one version
change per ruling, and a queue that breaks on a half-moved interface.

Reuse: `cargo xtask std-src` (it copies `moho_abi` into the `std` overlay verbatim), the moho_abi
test that pins every number, `script/bench --check`, `script/fastpath-footprint`, the Kani prove
shards, basalt's `pin-bump.yml`, and the checklist in
[design/naming/rename-what-moves.md](../naming/rename-what-moves.md). One new tool: the generator
of step 1.

## Goal

Every ruling of the review is in force in `moho_abi` and in nife, and basalt pins a nife commit
that carries it. The interface's version moves once for the whole set, from 1 to the pair 2.0.
Each commit on each `main` builds and boots on all three architectures.
The plan publishes no number.

## The rulings, grouped by what they touch

| group | rulings | touches |
|---|---|---|
| The method table | 13 (provisional), 14 (provisional) | `moho_abi` only; no number changes |
| The names | 16, except the order of the map arguments | every caller; no number changes |
| The table crate | the table-size ruling's storage, 9's right | `partsfoundry/capability_table` |
| The version pair | 5 | `moho_abi`, `partsfoundry/interfaces_note`, the start check |
| Numbers and refusals | 2, 3, 4, 11, 16's map argument order | the kernel's dispatch, every refusal a caller tests |
| The message | 1, 10, 6's receive slot, 11's reply-with-capability number | the trap's registers, the IPC fastpath, the `std` port |
| Slots and rights | 6, the table-size ruling, 9, 12, 4's retype defect | process creation, every capability-installing method |
| Additions after 2.0 | 7, 8, 15 (all provisional) | new numbers behind the `unstable` feature |

Findings 17, 18 and 19 are two-way and unruled, and this plan does not schedule them.

## The census

The lane measured it at `nifeos/nife@6bed50566`, `nifeos/moho_abi@1e99eed` and
`partsfoundry/capability_table@968a16f`. The full count, with the commands, is in
[the census appendix](1128-moho-rulings-implementation-plan/census.md). In short:

- `moho_abi` is about 2,000 lines in 23 modules, with 125 public constants and a pinned list of 116
  lines. No partsfoundry crate depends on it, and basalt names none of its symbols.
- nife pins `moho_abi` by commit in 16 manifests. 212 Rust files outside `user_mode_runtime` name
  `user_mode_runtime`: 86 in components, 85 in fixtures, 22 in crates.
- `user_mode_runtime`'s three trap files hold 1,171 lines. The `std` overlay's `rt.rs` keeps its
  own trap and its own `invoke` in 272 lines, and the overlay has 38 call sites and 29 `Error::`
  references.
- Direct `invoke(` calls outside `user_mode_runtime`: 145 lines in 57 files, 37 of them in
  `system_tests`.
- The kernel names `moho_abi::` 373 times in 46 files and holds 27 Kani proofs.
  `inter_process_communication` holds 16 and `capability_table` 12.

## The order

Effort: S is under half a day for a lane, M a day or two, L more. Each `moho_abi` or partsfoundry
step lands in that repository first, and the nife step after it moves the pin to the landed
commit, cited as `<org>/<repo>@<sha>`. No pin names an unmerged branch.

### Part one: no number changes

The version stays 1 through part one, and the pinned list does not move.

1. The method table, in `moho_abi` (finding 13). One file lists every system call and method:
   its object kind, its number, its argument words with their defined bits, its answer words, its
   refusals and its rights. A generator writes the constants, their doc comments, the typed
   wrappers and the pinned list from it. The lane commits the output as source, not as `build.rs` output,
   because `cargo xtask std-src` copies the crate into `std` file by file. A test regenerates and
   compares, so a hand edit to generated code fails. The table also emits each method's
   defined-bits masks, which step 9 needs. Effort: M. Lands alone, in `moho_abi`.
2. What a program author needs, in `moho_abi` (finding 14). The trap instruction, the clobbered
   registers and how a program starts, per architecture, in the crate's own documentation. It may
   land any time. Effort: S. Lands
   alone.
3. nife adopts the generated wrappers. The pin moves to step 1. `user_mode_runtime`'s hand
   wrappers become the generated ones or call them, with their names kept, so no caller changes.
   The `std` overlay picks up the generated module through `cargo xtask std-src`, and its own trap
   and `invoke` in `rt.rs` give way to the generated ones, so that step 11 changes one trap. Size:
   the 1,171 lines of the three trap files and the 272 of `rt.rs`. Effort: M. Lands alone. Its proof is that `script/bench --check`
   moves no row.
4. The naming pass, in `moho_abi` (finding 16, names only). One pass under the four rules, in
   the table, then regenerated. The order of the map arguments waits for step 9, because it moves
   words. Every new name is provisional. Effort: M. Lands alone.
5. nife takes the new names. One pull request, as a rename, with the `sed` line in its body
   for lanes in flight. The size depends on the list. The names the review named reach `::WAIT` on
   46 lines in 22 files, `::BIND` on 26 in 15, `::MAP` on 93 in 41 and `MAP_` on 399 in 79. Effort:
   M. Lands alone.
6. A table sized at creation, in `partsfoundry/capability_table`. Today the size is a
   const parameter and the free slots are one 64-bit word, so no table can exceed 64 slots. The
   crate learns a size chosen at creation that never shrinks, a free-slot set wider than one word,
   and a sixth right, `REVOKE` (finding 9). The right exists in the crate from this step, and no
   program can hold or ask for it until step 12. Its 12 Kani proofs move to a bounded runtime size.
   Effort: M. Lands alone, in partsfoundry.
7. The kernel moves to that crate. The pin moves to step 6. Every process still gets 64 slots,
   and no capability carries `REVOKE`, so the interface does not change. Effort: S. Lands alone. Its gates are the kernel's Kani proofs
   and `script/bench --check`, since a slot lookup sits on the fastpath.

### Part two: the breaking set, which becomes 2.0

Each step is one `moho_abi` pull request, then one nife pull request that moves the pin and moves
the kernel, `user_mode_runtime`, the `std` overlay, `system_tests` and the fixtures together. The
kernel and every program must agree on the interface, so neither half lands alone in nife. The
version moves once, in step 9, and the steps after it change 2.0 before any publish. The first
open decision asks whether that is acceptable.

8. The version pair, in `partsfoundry/interfaces_note`. Each record in the `INTERFACES` note
   carries one `u32` version today. It learns the pair, in a new descriptor version, and keeps
   reading version 1. Effort: S. Lands alone, in partsfoundry. It may land any time in part one.
9. The version becomes 2.0 (finding 5). `moho_abi` replaces `ABI_VERSION` with the pair: a
   breaking part, which must be equal, and an additions part, which must be at most the kernel's.
   The kernel hands its pair to the first program. The start check in
   `system_initializer` (`serves_declared_abi`) compares by the pair against the kernel's pair, not
   the crate's. The pinned list for version 1 retires, and the one for 2.0 stays open until step
   13. `ABI_VERSION` appears on 22 lines in 16 files. Effort: M.
10. Numbers and refusals (findings 2, 3, 4 and 11, with finding 16's map argument order).
    - Methods take numbers unique across the interface, the object kind in the high bits. A call
      on the wrong kind answers `WrongObject`. The implementing lane assigns the numbers, keeps the
      six that finding 11 rules stable at their assigned values, and shows them in its diff.
    - An undefined argument word, flag or rights bit faults the caller, read from the table's masks.
      `writable` takes 0 or 1.
    - The four new codes arrive, each refusal moves to its code, the words after the status on a
      refusal are zero, and the four reboot codes move into word 1 of the reboot call's answer.
    - Reboot goes behind the off-by-default `unstable` feature, which `user_mode_runtime` enables.
    - Size: the method constants `BADGE` (39 lines, 19 files), `SPLIT` (77, 25),
      `RETYPE_OBJECT` (91, 33), `SLICE` (29, 13) and `CAPABILITY_INSERT` (30, 15) change value,
      not spelling, so their callers recompile and do not change. The refusals callers test do
      change: `Error::NotPermitted` (144 lines, 43 files), `Error::OutOfMemory` (46, 21),
      `Error::WrongObject` (39, 21), `Error::BadPointer` (38, 15), `Error::BadMethod` (30, 13) and
      `reboot::` (13, 10). The probes that call method `0xffff` and expect `-1` break in four
      overlay files and in `user_mode_runtime`, and so does `std`'s file system, which assumes the kernel's codes run
      from -1 to -8.
    - Effort: L.
11. One message shape (findings 1 and 10, finding 6's receive slot, and finding 11's
    reply-with-capability number).
    - Word 0 holds the kernel's status, and every data word moves down one register.
    - A message is the kernel-written information word, the data words and an optional capability.
      Send, call and reply take that shape, and one receive accepts any of them into the slot it
      names. The kernel refuses an occupied slot with a step 10 code.
    - This rewrites the trap's register use, the fastpath (`ipc_send`, `ipc_call_reply`), the
      rendezvous state machine and its 16 proofs, the `std` overlay's own trap, and every raw
      `invoke`.
    - Size: the receive family collapses into one call. `receive` (126 lines, 51 files),
      `receive_capability` (37, 15), `receive_request` (36, 30), `receive_message` (25, 15),
      `call_receiving` (17, 10) and `receive_capability_message` (2, 2) make 243 lines in at most
      123 files. `send`, `call` and `reply` keep their shape for a caller, so their 1,224 lines
      change only where a caller reads a raw word. The 145 direct `invoke(` lines all move by one
      word.
    - Effort: L.
12. Slots and rights (finding 6, the table-size ruling, findings 9 and 12, and finding 4's
    retype defect).
    - Every capability-installing method takes its destination slot and refuses an occupied one
      before it spends anything. That also fixes the retype defect, where `RETYPE` and
      `RETYPE_OBJECT` spend pages before they find the table full.
    - The creator sets a table's size as an argument of process creation and pays for it from its
      own region. `CAPABILITY_TABLE_SLOTS` leaves the interface, and an out-of-range slot answers
      `InvalidArgument`.
    - The start call takes the supervisor's rendezvous slot and the supervised flag, and
      `FAULT_RENDEZVOUS_SLOT` leaves.
    - `REVOKE` becomes the sixth right. `GRANT` no longer revokes, `ALL` includes `REVOKE`, and
      `SPEND_ONLY` does not.
    - Size: `CAPABILITY_TABLE_SLOTS` (40 lines, 23 files), `FAULT_RENDEZVOUS_SLOT` (33, 20),
      `rights::GRANT` (31, 10) and `REVOKE` (63, 28). The installing wrappers have 80 call lines:
      `retype_into_page_frame` 26, `retype_into_kernel_object` 22,
      `thread_control_block_capability_insert` 9, `split_memory_region` 6,
      `retype_page_frame_run` 5, `thread_control_block_configure` 6,
      `thread_control_block_start` 4 and `slice_page_frame` 2. `capability_plan`'s five proofs
      assume a fixed slot bound.
    - Effort: L.
13. 2.0 is whole, in `moho_abi`. The generator writes the pinned list for 2.0 from the table. The test
    that refuses a reused number starts again from 2.0's numbers. The full list of new names goes
    to the release review. Effort: S. Lands alone. A tag is an outward step.
14. basalt follows. basalt names no `moho_abi` symbol, and nife's queue already builds basalt's
    delivered programs from the candidate tree (milestone 1115 (the gate builds basalt's delivered
    programs from the candidate tree)), so basalt needs no source change. Its `pin-bump.yml` pull
    request moves the nife pin to the commit of step 12, citing it as `nifeos/nife@<sha>`. Effort:
    S. Lands alone, in basalt.

### Part three: additions

15. The additions (findings 7, 8 and 15, provisional). Each takes a new number behind
    `unstable` (finding 11), as one `moho_abi` pull request and one nife pull request. Each lands
    alone, in any order, at effort M.
    - Finding 7: a method that copies a capability in place under a rights mask, and a rights mask
      on any message that carries a capability. After step 11 no separate reply-with-capability
      call exists. The mask is an addition because, after step 10, a program that sets the word it
      uses faults, so no 2.0 program sets it.
    - Finding 8: a non-blocking send and a poll. `address_space::WAIT` gains an absolute deadline,
      which ends `std`'s spinning in `Condvar::wait_timeout` and `park_timeout`. Deadlines on
      message passing wait for the speed measurement.
    - Finding 15: a rights query.

## Gates

Every step passes `script/lint` and the repository's own CI. Beyond those:

| step | gates |
|---|---|
| 1, 4, 13 | the regenerate-and-compare test; the pinned-number test; the moho_abi template's naming checks |
| 2 | the moho_abi documentation build |
| 3, 5 | `script/test` on all three architectures; `script/bench --check` with no row moved |
| 6 | the crate's 12 Kani proofs; its loom and mutation selftests |
| 7 | the kernel's Kani proofs; `script/bench --check`; `script/fastpath-footprint` |
| 8 | the crate's tests, including a version 1 note still read |
| 9 to 12 | `script/test` on all three architectures; Kani prove shards for each changed harness; `script/bench --check` and `script/fastpath-footprint`, with a `# why:` line on each saved row; the falsification patches regenerated; `cargo xtask std-src` and `std_exerciser` |
| 14 | basalt's gate, which runs `script/ci-build test` on all three architectures |
| 15 | as 9 to 12, for the methods it adds |

## Risks

- The fastpath. Step 10 puts a kind check and an undefined-bits check on every send and call,
  step 11 writes the information word, and step 12 checks the receive slot. `ipc_send` and
  `ipc_call_reply` live in `.text.hot.*`, and `script/fastpath-footprint` keeps their footprint
  inside a 5% band. x86_64 already runs near that band, so each step must measure it before
  pushing. A step that leaves the band owes a proposal, not a widened band.
- The icount tripwire. `script/bench --check` holds each row within 0.5% and the sum within
  2%. Steps 10 to 12 will likely move `null_system_call`, `ipc_rtt`, `ipc_rtt_el0`,
  `call_reply`, `relay_rtt` and `broker_rtt`, and step 12 `spawn_reap` and `spawn_el0`. Each save
  carries a `# why:` line that names the ruling it pays for.
- Kani harnesses that pin layouts. `capability_table`'s 12 proofs assume one free-slot word,
  `inter_process_communication`'s 16 assume today's message, and `capability_plan`'s five take
  their slot bound from `CAPABILITY_TABLE_SLOTS`. A runtime table size makes a proof's bound an
  assumption the harness states; a bound too small proves less than the old one.
- The `std` port. The overlay copies `moho_abi` verbatim, keeps its own trap and `invoke` in
  `rt.rs`, probes with a method number that every step from 10 on gives a new meaning, and assumes
  the kernel's codes in `fs`. Step 3 retires the overlay's own trap; if it cannot, step 11 changes
  two.
- The falsification patches. 23 in `system_tests`, two in xtask and two in `capability_plan`
  name `moho_abi` or `user_mode_runtime` in their context, and three name the fastpath. A step that
  changes that context regenerates them in the same commit.
- The measurement block's baselines ([nifeos/record#37](https://github.com/nifeos/record/pull/37)). Its items 1 and 4 may start against today's interface. Steps 10
  to 12 move the very rows they measure, so each of its measurements names the nife commit it ran
  on.
- Lanes in flight. A nife lane that names a receive variant, a raw word or a slot constant
  breaks on its merge of `main` after steps 10 to 12. Each step's pull request body gives the
  mechanical change.

## Open decisions

[The open-decisions appendix](1128-moho-rulings-implementation-plan/open-decisions.md) gives each
question the rulings leave open its background, options and recommendation, with the prior art.

Four stay open for calef:

1. What a call with an undefined method number answers. It blocks step 10.
2. Which fault finding 3 raises, and what the supervisor reads. It blocks step 10.
3. How the version pair travels: one word or two. It blocks steps 8 and 9.
4. How the kernel hands its pair to the first program. It blocks step 9.

The maintainer ruled three on 2026-11-25 (UTC), provisionally, and the appendix states each as
the rule in force: 2.0 may change between nife commits until step 13, the table crate bounds a
table's size, and a number moves the additions part when it leaves `unstable`.

## The outward steps

Each needs its own go, as every publish and tag does.

- The 2.0 tag on `moho_abi`, after step 13.
- The release review of every name the set minted (finding 16).
- The publish of `moho_abi` to crates.io.

## Done when

- `moho_abi`'s `main` carries the method table, the version pair at 2.0, and the pinned list for
  2.0, and the version moved once for the set.
- nife's `main` pins that commit, and its kernel, runtime, `std` port, tests and fixtures speak 2.0.
- basalt's `main` pins a nife commit that carries 2.0, and its gate is green.
- Every saved bench row in the set names the ruling it pays for.
- The release review's list holds each provisional name.

## BUGS

- The wrapper counts are upper bounds: `send`, `call` and `reply` also match functions that are not
  the wrappers.
- The census counts lines, not occurrences.
- Effort figures are estimates from the census, not measured lane times.
- The size of step 5 waits on the naming pass's list; the counts above cover only the names the
  review named.

## Index row

The Moho review's rulings land in order. First come the method table, the names and a table sized
at creation, with no number changed. Then the version becomes 2.0 once, and numbers with refusals,
one message shape, and slots with rights land in turn, each as one `moho_abi` and one nife pull
request. Additions follow behind the `unstable` feature, and the tag and the publish each wait for
a separate go.
