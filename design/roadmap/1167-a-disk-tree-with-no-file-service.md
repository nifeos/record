---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: 163, 834
decision_dependencies: unwritten
machine_requirements: a machine that boots over the network, with an NVMe drive behind a PCIe root complex the kernel brings up
specific_machine: radon (a VisionFive 2 booted over the network, with a drive in its M.2 slot)
needs_person: yes
---
# 1167. A disk tree with no file service: `/disk/nvme0` on a board booted over the network

*(The number, title and slug are provisional.)*

**This milestone needs an architect's ruling before anyone builds it.** It reopens the two
rulings below, and a lane does not reopen a ruling.

## What it would change

A board booted over the network has no file service, since the file service takes an NVMe disk
only on a machine that booted from one. The disk tree at `/disk` starts only beside a file service.
It takes the file service's window 0 as its own, and the shell finds it at a name in the file
service's tree.
So on a VisionFive 2 booted over the network, `/disk/nvme0` never appears, and the run that
milestone 834 (ioping on nife and Linux) plans, `ioping` against `/disk/nvme0/n1`, cannot happen
there.

This milestone would start the disk tree, and the NVMe server under it, with no file service. The
progenitor would hand the shell the disk tree on a machine that has a drive and no file service. A person at the prompt of a board booted over the network could then `cd
/disk/nvme0` and run `ioping` and `ls` against the drive, read-only, as on an installed system.

Milestone 163 (the JH7110's PCIe root complex) does not wait for this. Its runbook,
[`notes/jh7110-pci-express-bench.md`](../../notes/jh7110-pci-express-bench.md), reads the drive with
a bench boot (`disk_read_bench`) that starts the NVMe server with no tree at all, so no ruling
changes. This milestone is the other way to the same reads, and the one that gives a prompt.

## The rulings it would revisit

- §234 (the prompt shows one tree, and other trees are mounted at names in it), ruled 2026-09-26
  (UTC). The disk tree sits at a name in the root. With no file service there is no
  root to mount it in. Either the disk tree becomes the root the prompt shows, which is a second
  meaning for "the one tree", or the boot gains an empty root whose only content is the mount
  `/disk`, which is a new tree no ruling describes. Either is the architect's choice.
- Milestone 834's ruling on nifeos/nife#2371, 2026-10-18 (UTC): the disk tree stays read-only at
  the prompt, and each client has its own window. That ruling placed the disk tree as the
  installed system's second mounted tree, beside a file service. A disk tree with no file service
  is a first tree on a system that is not installed. The read-only rule would stand; whether it is
  still the right shape where the disk tree is the only storage the prompt reaches is the question
  to put.

## What the work would be, once ruled

- The disk tree's start no longer takes the file service's window 0. It takes a window of its own
  from the NVMe server's client windows (`non_volatile_memory_express::CLIENT_WINDOWS`), so it
  starts whether or not a file service does.
- The progenitor grants the disk tree at its slots on any machine with an NVMe controller, and the
  shell mounts it as the architect's ruling says.
- A QEMU case: a riscv64 boot with the suite's NVMe controller and no file service reaches the
  prompt, `ls /disk/nvme0` lists `n1`, and a write gets `EROFS`.

Reuse: the change would take the disk tree (`crates/disk_tree`, `components/src/disk_tree.rs`) and
the NVMe server whole, and move only where the progenitor starts them. Nothing in
the tree or a dependency starts a tree with no root to mount it in.

## Follow-on

- **None.** Nobody has built any of it yet.

## Index row

A drive a person can reach at the prompt of a board booted over the network, read-only, so that
`ioping` runs there as it does on an installed system. It reopens §234 and milestone 834's ruling,
and waits for an architect's ruling on both.
