---
status: NOT-STARTED
raised: 2026-10-08
promoted_from: netperf-tcp-rr-on-nife-and-linux
milestone_dependencies: 494, 53, 835, 809, 801
decision_dependencies: 262, 265
machine_requirements: silicon with a NIC nife drives and a peer on the same wire, xenon or radon
specific_machine: none
needs_person: yes
---
# 829. netperf TCP_RR on nife and Linux, request and response latency

*(The title and slug are provisional.)*

Model: milestone 833 (the same storage benchmark on nife and Linux, by porting real fio). Pairs with milestone
828 (iperf3 on nife and Linux); throughput hides per-packet cost and this exposes it.

**In brief.** Port `netperf` and `netserver` and run TCP_RR (and UDP_RR): a one-byte request, a
one-byte response, in a loop. The result is transactions per second, so its inverse is round-trip
latency.

## What it measures

One round trip through the whole path: client, stack, driver, wire, peer and back. With
a one-byte payload there is nothing to amortize, so the number is dominated by fixed cost per
crossing.

## Which fatal risks it informs

Risk 4 (the per-crossing cost): a request and response cross driver, stack and client boundaries
each way; the count is known from the design, so the measured time divides into a cost per
crossing that can be set beside `ipc_rtt_el0`. Risk 6: a confined driver that adds a fixed delay
shows up here at once.

## What nife must supply, as questions

- The same socket surface questions as iperf3. Does netserver's fork-per-connection model need
  `fork`, or can it run with `-D` and one process?
- `TCP_NODELAY`, `SO_RCVBUF` and `getsockopt`: which does the stack implement? Nagle behavior
  changes the answer by an order of magnitude, so it must match on both sides.
- Interrupt or poll in the driver? Record it; it moves the number more than any other setting.

## The Linux comparison

The same netperf version and parameters (`-t TCP_RR -l 30 -- -r 1,1`), same peer and cable,
Linux and nife in turn on the same board, with `netserver` on the peer and CPU affinity recorded.
Linux's interrupt coalescing is set to the same mode as nife's driver, or both modes are reported.

Reuse: netperf is taken and ported.

## What it waits on

The C library,
[milestone 835 (a C library, stage 1)](0835-a-c-library-stage-one-files-clock-and-memory.md), is
built. This program's other needs are below.

A NIC on silicon, as [milestone 828 (iperf3 on nife and Linux)](0828-iperf3-on-nife-and-linux.md)
lists.

Fork. `netserver` forks a child per test by default. nife has no `fork`, so a fork row follows
[milestone 826 (an lmbench subset)](0826-an-lmbench-subset-on-nife-and-linux.md)'s rule. From
memory, `netserver` has a flag that runs tests serially in one process; the port checks the source
before relying on it.

## How it runs continuously

It runs continuously as [milestone 826 (an lmbench subset on nife and Linux)](0826-an-lmbench-subset-on-nife-and-linux.md) does.

## Done when

*§297 (a package `jig` installs) binds this. calef, 2026-10-12 (UTC): "They should all be installed
via jig through basalt."*

netperf must run on nife installed by `jig install` from basalt's package index. basalt builds the
package against the nife commit it pins. The install waits on milestones 809 and 801, as §297 (a
package `jig` installs) lists. No work toward that starts until those milestones land
([the package manager](../../notes/packages/jig.md#a-port-waits-on-the-package-client) holds the rule).

## Index row

netperf TCP_RR round trips through driver, stack and client, a fixed cost per crossing with nothing
to amortize. Waits on a C library and a NIC on silicon; netserver's default fork never runs here.
