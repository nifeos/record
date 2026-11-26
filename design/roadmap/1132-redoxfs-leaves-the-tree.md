---
status: NOT-STARTED
raised: 2026-11-26
milestone_dependencies: 1131
decision_dependencies: 34
machine_requirements: none
specific_machine: none
needs_person: no
---
# 1132. RedoxFS leaves the tree

*(The number, the title and the slug are provisional.)*

Raised 2026-11-26 (UTC) by lane `lane/journey-6-ext4-root-filesystem`, writing journey 6 (boot a
nife image whose launch volume is ext4, and read it from Linux). §34 (RedoxFS is the primary
filesystem) says RedoxFS leaves through a milestone of its own, minted from the inventory of
milestone 982 (Retire RedoxFS once a launch store proves itself). This is that milestone.

## What it removes

Milestone 982 holds the inventory, and this block does not copy it. In short: the vendored RedoxFS
and its patches, `redoxfs_server/`, `tools/redoxfs_host/`, the `redoxfs` package, its fuzz target,
the RedoxFS helpers in `xtask/src/disk.rs`, and the notes and decisions that describe RedoxFS as
current. Each helper either gets an ext4 twin or goes.

The crash harness must get its twin. Milestone 37 (Prove RedoxFS's crash consistency) built the
injector, and milestone 997 (ext4 through rsext4, under milestone 37's crash injector) puts
`rsext4` behind it. The sweeps keep running on ext4 after RedoxFS goes.

The kernel benchmark in `kernel/src/bench/filesystem.rs` runs through `redoxfs_server` today. It
moves to `ext4_server` here, so milestone 38 (filesystem throughput) keeps a live instrument.

## What it waits on

Milestone 1131 (ext4 becomes the launch store), so nothing still boots from RedoxFS. §34 leaves
open whether the cut-over and the removal happen in one step or two. Two steps is provisional.

Reuse: none exists. Removal reuses milestone 982's inventory, and each twin reuses the ext4 side
of milestones 190 and 997.

## Done when

No file in nifeos/nife builds, vendors or tests RedoxFS. The crash sweeps, the filesystem
benchmark and every test that used a RedoxFS fixture run on ext4. The notes and the decisions that
name RedoxFS as current state the present rule.

## Index row

RedoxFS leaves the tree once ext4 holds the launch store, and the crash harness and the benchmark
keep running on ext4.
