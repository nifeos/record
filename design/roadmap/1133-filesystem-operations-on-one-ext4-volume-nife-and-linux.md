---
status: NOT-STARTED
raised: 2026-11-26
milestone_dependencies: 1131
decision_dependencies: none
machine_requirements: none
specific_machine: none
needs_person: no
---
# 1133. Filesystem operations on one ext4 volume, through nife and through Linux

*(The number, the title and the slug are provisional.)*

Raised 2026-11-26 (UTC) by lane `lane/journey-6-ext4-root-filesystem`, writing journey 6 (boot a
nife image whose launch volume is ext4, and read it from Linux). §34 (RedoxFS is the primary
filesystem) gives one reason for the move: no benchmark can compare RedoxFS with Linux on
filesystem operations. Once nife runs on ext4, one volume can serve both systems. No block owned
that comparison, so this one does.

## What it measures

Milestone 38 (filesystem throughput) compared RedoxFS through nife's server with ext4 on Linux.
That compared two filesystems as well as two systems. Here the volume is the same, so the
difference is nife's.

1. One ext4 image, made once and copied fresh for each run.
2. The same workload through `ext4_server` on nife and through the kernel's ext4 driver on Linux,
   each as a guest on the same host at the same virtualization tier.
3. Sequential and random reads and writes, as milestone 38 measured, plus the metadata operations
   it did not: create, stat, list a directory, rename, unlink, and `fsync`.
4. A note records each number beside Linux's, with the method, the host and the tier.

The workload tool is open. fio's file engines fit once milestone 833 (the same storage benchmark on
nife and Linux) ports fio. Milestone 38's instrument fits now. Milestone 833 measures the raw block
device and leaves the filesystem out; this block measures above it.

Reuse: milestone 38's `fs_throughput` instrument and its Linux comparison in `bench/host/`. fio
after milestone 833's port.

## Done when

The workload runs on nife and on Linux against copies of one ext4 volume on aarch64, riscv64 and
x86_64 under QEMU. A note records every operation's numbers side by side. The same comparison on
silicon waits until the ext4 launch store runs there, and it is not part of this block.

## Index row

The first filesystem comparison in which nife and Linux read and write the same volume, so a
difference in the numbers belongs to nife rather than to the filesystem.
