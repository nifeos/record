---
status: NOT-STARTED
raised: 2026-10-08
promoted_from: stream-on-nife-and-linux
milestone_dependencies: 835, 809, 801
decision_dependencies: 262, 265
machine_requirements: silicon, radon, xenon, later argon
specific_machine: none
needs_person: yes
---
# 832. STREAM on nife and Linux, the memory-bandwidth baseline

*(The title and slug are provisional.)*

Model: milestone 833 (the same storage benchmark on nife and Linux, by porting real fio). It pairs with
`coremark`, the compute control in `notes/benchmarks.md` that must never move.

**In brief.** Port STREAM (one C file) for the Copy, Scale, Add and Triad bandwidth numbers. If nife
and Linux disagree on a memory-bound loop that makes no system calls, the cause is in page mappings,
page size or cache attributes, and nothing a scheduler or IPC change can explain.

## What it measures

Sustained memory bandwidth in MB/s over arrays far larger than cache, single-threaded and, once
threads exist, with one thread per core.

## Which fatal risk it informs

Risk 4 (the per-crossing cost) as a control: any cost per crossing is only believable when the
workload with no crossings matches Linux. A mismatch here would be a mapping or cache-attribute
defect (memory type, huge-page use) that contaminates every other benchmark on the page. It is a
baseline rather than a risk test.

## What nife must supply, as questions

- Does a program get memory with normal cacheable attributes, and in what page size? Linux uses
  transparent huge pages when enabled; record both and run Linux with THP on and off.
- OpenMP is optional; the single-threaded build needs only `malloc` or a static array and a clock.
- A timer of `wtime` quality (microseconds or better). Is one reachable from std on nife?

## The Linux comparison

The same STREAM revision, `STREAM_ARRAY_SIZE` at least 4x the last-level cache, same compiler and
flags (`-O3`, no auto-parallel unless both sides have it), same board, best of ten iterations as the
program reports. Frequency scaling is pinned on Linux, and the clock and governor recorded.

Reuse: stream.c is taken unmodified except the timer shim.

## What it waits on

The C library,
[milestone 835 (a C library, stage 1)](0835-a-c-library-stage-one-files-clock-and-memory.md), is
built. This program's other needs are below.

Threads, for the per-core half only. The single-threaded build needs none; one thread per core waits
on milestone 812 (`std::thread::spawn` runs real threads in one address space).

## How it runs continuously

It runs continuously as
[milestone 826 (an lmbench subset on nife and Linux)](0826-an-lmbench-subset-on-nife-and-linux.md)
does.

## Done when

*§297 (a package `jig` installs) binds this. calef, 2026-10-12 (UTC): "They should all be installed
via jig through basalt."*

STREAM must run on nife installed by `jig install` from basalt's package index. basalt builds the
package against the nife commit it pins. The install waits on milestones 809 and 801, as §297 (a
package `jig` installs) lists. No work toward that starts until those milestones are built
([notes/packages.md](../../notes/packages.md#a-port-waits-on-the-package-client) holds the rule).

## Index row

STREAM, the memory-bandwidth control: if nife and Linux differ on a loop with no system calls, the cause
is mappings or cache attributes. Needs only a C library for the single-threaded run.
