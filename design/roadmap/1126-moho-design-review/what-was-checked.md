# What the review checked, and how

An appendix to [the milestone](../1126-moho-design-review.md).

## The trees read

- `nifeos/moho_abi` at `1ac97ce486e18623a8d022b8c1f33bc1f73f3196`, the head of its
  `prepare-0.1.0-pre.1` branch. It differs from that repository's `main` (`364f59c9`) only in the
  version string of `Cargo.toml` and `Cargo.lock`. The review read every file under `src/` whole except
  the two test files, and also `README.md`, `CHANGELOG.md` and the head of
  `pinned-at-version-1.txt`.
- `nifeos/nife` at `b89e42872f2181f2651acd3e9e836a42318d071b`, and again at `main`, `f04f8b4c9`.
  Between the two, one line changed in the files named below, a comment in
  `kernel/src/capability_object.rs`, and an independent pass confirmed each claim at `f04f8b4c9`. The kernel pins `moho_abi` at `c8d556ec`, the repository's root commit.
- `nifeos/record` at `f62bc01d2`, the base of this lane.

## What the review read in nife, and what each reading settled

- `kernel/src/system_call.rs`, the functions `dispatch` and `invoke`. The kernel picks the method
  table by the object the slot holds and then matches the method number, so method 0 means a
  different operation on each object (finding 2). `invoke` passes each object only the argument
  words its methods name, and nothing reads the others (finding 3). An unknown method answers
  `BadMethod`.
- `kernel/src/arch/x86_64/exceptions.rs`, `TrapFrame::arg` and `TrapFrame::set_arg`. Word 0
  returns in `rdi`, as the crate's table says, and never in `rax` (finding 14).
- `kernel/src/system_call/rendezvous.rs`, `rendezvous_receive_capability` and
  `rendezvous_send_capability`, and `rendezvous_receive`. A receive that answers `Gone` returns
  before it writes words 1 to 4. The receive writes the sender's word into word 0 with no status
  beside it (finding 1), and the delegation converts the rights word with `as u32` (finding 3).
- `kernel/src/sched/rendezvous.rs`, the collect arm of
  `inter_process_communication_receive_capability` and `strand_reply_caller`. A Reply that does
  not fit the server's table leaves the caller parked, and only a teardown frees it (finding 6).
- `kernel/src/system_call/object_methods.rs`, `process_invoke`, `reboot_invoke` and
  `rendezvous_survey`'s caller. None of them reads an argument word its doc comment marks unused.
- `crates/system_initializer/src/image_request.rs`, `serves_declared_abi`, and
  `interfaces_note::InterfaceList::check_served` in `partsfoundry/interfaces_note`. The progenitor
  compares the program's declared version with its own build-time copy of `ABI_VERSION`, by
  equality, and a program with no note passes (finding 5).
- `kernel/src/capability_object.rs`, the two compile-time assertions on the rights masks.

## What the review read in the record

The decisions, each read whole unless the last section says otherwise:

- §10 (process model: capability-based, microkernel) and §15 (the native ABI).
- §12 (call/reply IPC: a one-shot reply capability), §245 (a `CALL` server tells a Reply from a
  delegation) and §246 (a plain `RECEIVE` never takes a capability).
- §13 (capability revocation and untyped reclamation) and §16 (object revocation) with its five
  amendments.
- §119 (splitting `OutOfMemory`'s three causes is declined for want of a customer), which
  finding 4 reopens.
- §101 (notification objects) and §230 (badged endpoint capabilities).
- §124 (ratify the x86_64 system call ABI) and §276 (the thread system calls as built).
- §323 (the binary interface, and the names of the layers).
- §325 (the services' wire error vocabulary) and §326 (the names and numbers of the services'
  wire error codes).

The review also read `design/naming.md`, and `notes/crate-reviews/moho-abi.md` for the ratified
names, and `notes/address-wait.md` for its `BUGS`. It read milestone 1075 (`abi`: what an outside
maintainer would fix before the move) with its five appendices, so that no item here repeats one
of its twenty-one.

## What the outside sources are

Three research agents fetched the comparators' own documents on 2026-11-25 (UTC) and returned
each fact with its address and, where the page allowed, a short quotation.
[The prior-art appendix](prior-art.md) lists every source and marks the claims no fetch
confirmed.

## What the review did not do

- The review built and ran nothing. No test, no kernel boot and no QEMU session backs a finding. Each
  claim about kernel behavior comes from reading the functions named above.
- The user-mode runtime (`crates/user_mode_runtime`) and the `std` port were not read beyond a
  search for callers. A finding that says what a wrapper would do describes the crate's contract,
  not the runtime's present code.
- The riscv64 and aarch64 trap entries were not read. The register table for those two is the
  crate's own.
- The review took §269 (how threads share a process), §223 (the process view is the supervision
  domain) and §255 (each socket is its own capability) by heading and by search, not whole.
