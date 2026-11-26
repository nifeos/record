---
status: NOT-STARTED
raised: 2026-10-08
promoted_from: iperf3-on-nife-and-linux
milestone_dependencies: 494, 53, 812, 835, 809, 801
decision_dependencies: 262, 265
machine_requirements: silicon with a NIC nife drives and a peer on the same wire, xenon or radon
specific_machine: none
needs_person: yes
---
# 828. iperf3 on nife and Linux, throughput for the network drivers

*(The title and slug are provisional.)*

Model: milestone 833 (the same storage benchmark on nife and Linux, by porting real fio). Starts after a
NIC works on silicon, so it waits on milestones 494 (a driver for the network card a PC actually
has) and 53 (the board's own peripherals).

**In brief.** Run iperf3 as the server on nife and as the client on a peer, TCP and UDP, in both
directions, and do the same with Linux on the board.

## What it measures

Sustained TCP and UDP goodput, retransmits and CPU use over a wired link, single stream and
four parallel streams. It is the network twin of fio for risk 6.

## Which fatal risk it informs

Risk 6 (`6-a-confined-driver-is-too-slow.md`): the NIC driver and the stack are separate servers on
nife. Line rate, or a measured gap to Linux, is the NIC half of the confined-driver verdict that
fio gives for NVMe. A shortfall points at copies across the driver-stack-client boundary, which is
risk 4's currency.

## What nife must supply, as questions

- Does the stack offer a BSD socket surface (milestone 649 (every client of a network stack shares its socket numbers)) that iperf3's
  C code can use, or does the port need a shim? If a shim, it is part of what is measured.
- `select` or `poll`, threads (iperf3 3.16+ is multithreaded) and a timer fine enough for its interval reports?
- Does the stack have window scaling and enough buffer for a gigabit link, or does it cap lower?
- Is the peer a fixed Linux box? Its kernel is recorded too.

## The Linux comparison

The same iperf3 version, same peer, cable, switch, MTU and parameters (`-t 30 -P 1/4`, `-R`, `-u
-b`),
Linux and nife booted on the same board in turn. Link speed is checked first so a 100 Mb
fallback is not read as slowness. Linux's NIC driver and offloads are recorded.

Reuse: iperf3 is taken and ported; no nife-side traffic generator is written.

## What it waits on

The C library, [milestone 835](0835-a-c-library-stage-one-files-clock-and-memory.md) (a C library,
stage 1), is built. This program's other needs are below.

A NIC on silicon, milestones 494 (a driver for the network card a PC actually has) and 53 (the
board's own peripherals).

Threads, for iperf3 3.16 and later, which runs one thread per stream. Threads are
[milestone 812](0812-threads-in-one-address-space.md) (`std::thread::spawn` runs real threads),
built. An older, single-threaded iperf3 would run sooner, but it is not the version the field now
reports, so that choice is written in the row if it is taken.

## How it runs continuously

It runs continuously as [milestone 826](0826-an-lmbench-subset-on-nife-and-linux.md) (an lmbench
subset on nife and Linux) does.

## Done when

*§297 (a package `jig` installs) binds this. calef, 2026-10-12 (UTC): "They should all be installed
via jig through basalt."*

iperf3 must run on nife installed by `jig install` from basalt's package index. basalt builds the
package against the nife commit it pins. The install waits on milestones 809 and 801, as §297 (a
package `jig` installs) lists. No work toward that starts until those milestones are built
([notes/packages.md](../../notes/packages.md#a-port-waits-on-the-package-client) holds the rule).

## Index row

iperf3 throughput through a confined NIC driver and stack, against Linux on the same board and wire:
the network half of risk 6. Waits on a C library, a NIC on silicon and threads.
