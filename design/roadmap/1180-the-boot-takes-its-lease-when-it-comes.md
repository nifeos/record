---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: none
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# 1180. The boot takes its DHCP lease when it comes

*(The number, title and slug are provisional.)*

Ruled 2026-11-28 (UTC). The boot's wait on the DHCP lease is its own milestone, not a step of
milestone 1062 (the device control planes leave the kernel). So it is not held behind milestone
811 (the boot services leave the kernel)'s step 6.

Reuse: none exists. The change is to the progenitor's own boot order, so this lane searched only
the tree. The shape is 1062 step 1's ruling one layer up: DHCP waits on the link report, not on a
deadline, and the boot waits on neither.

## The gap

The progenitor takes `net_stack`'s lease before it builds the terminal. Until a DHCP server
answers, the boot stops short of the prompt. Nothing bounds the wait, on any of the three paths.

- The virtio-net path. `build_net_stack` in `crates/system_initializer/src/children.rs` builds
  `net_stack` and then receives on its report endpoint.
- The kernel-built path. `start_network` in `crates/system_initializer/src/boot_steps.rs` receives
  on `net_stack_report` (slot 30) when the kernel granted a stack. That covers an `e1000e` (the
  82574L, and the I219 since nifeos/nife@0707b99) and radon's GMAC.
- `net_stack` itself. `dhcp_lease` in `components/src/interface_bring_up.rs` loops until smoltcp
  reports `Configured`, with no exit. `server` in `components/src/socket_server.rs` serves no
  socket call until it returns.

So a cabled port with no DHCP server answering holds the boot for ever. A port with no link does
not: the kernel's link wait refuses to start a stack there (`Absent::NoLink`).

## What reads the lease

- `start_domain_name_resolver` (`crates/system_initializer/src/children.rs`) takes the stack and
  the lease's name server. It builds no resolver without a name server.
- `announce_network` prints the lease and the resolver's server. `script/swish-check` reads both
  lines (`xtask/src/swish_check/boot.rs`).
- The spawn service holds the stack endpoint and the resolver's endpoint (`Channels` in
  `crates/system_initializer/src/spawn_loop.rs`). It needs the stack at once and the resolver only
  once one exists.

## The work

1. The progenitor builds `net_stack` and keeps its stack endpoint, then goes on to the terminal and
   the prompt. It does not receive the report there.
2. The spawn service takes the report whenever `net_stack` sends it, on the virtio-net and the
   kernel-built paths alike. Both paths keep one route to the lease, as they share one today. How
   the loop hears the report (a badged copy of its own endpoint in `net_stack`'s report slot, or
   another shape) is the lane's. A shape that adds a system call or a wire is an architect's call.
3. On the report, the spawn service builds the resolver and keeps its endpoint for later jobs. It
   prints the two network lines then, through the terminal endpoint it already keeps.
4. A job spawned before the lease that asks for the network gets the stack endpoint. Its calls
   wait until `net_stack` serves, which is after the lease. A job spawned before the resolver
   exists gets no resolver, as a job does today on a boot that built none.
5. `crates/system_initializer`'s BUGS line ("A boot with a NIC waits for DHCP before the prompt")
   goes, and so does the matching line in `notes/system-initializer/the-boot-order.md`.

No step adds a DHCP deadline. `net_stack` keeps asking, on smoltcp's own retransmit, until a server
answers.

This needs neither milestone 1062 nor milestone 811. 1062 step 1 moves the `e1000e` control plane
out of the kernel; the stack it starts reports its lease to the same place this milestone moves.

## Done when

1. A system test on x86_64 boots with an `e1000e` behind a netdev that answers no DHCP. QEMU's
   `filter-buffer` holding the NIC's frames is one way. The prompt appears, and the boot prints no
   lease line.
2. The same test then lets frames through. `net_stack` takes a lease on its own retransmit, the
   progenitor prints `network stack up; DHCP leased` after the prompt, and a job spawned after that
   resolves a name.
3. Criteria 1 and 2 hold on aarch64 or riscv64 over virtio-net.
4. A job that asks for the network before the lease completes its call once the lease comes.
5. `script/swish-check` passes on every leg, its network lines now read after the prompt.

## A xenon boot

Cabled to a switch with no DHCP server, xenon today prints its kernel network line and stops; the
progenitor never prints its announcements. Once this lands, the same boot reaches `$` with no
lease line. Turning a DHCP server on prints the lease line under the prompt. No exit criterion
needs xenon.

## Follow-on

None yet.

## Index row

A cabled port with no DHCP server answering holds the boot short of its prompt for ever, on every
NIC nife drives. This lets the boot reach the prompt first and take the lease whenever it comes,
with no deadline.
