---
status: NOT-STARTED
raised: 2026-11-26
milestone_dependencies: 190, 997, 990, 909
decision_dependencies: 34, 244
machine_requirements: none
specific_machine: none
needs_person: no
---
# 1131. ext4 becomes the launch store, and Linux reads the image

*(The number, the title and the slug are provisional.)*

Raised 2026-11-26 (UTC) by lane `lane/journey-6-ext4-root-filesystem`, writing journey 6 (boot a
nife image whose launch volume is ext4, and read it from Linux). §34 (RedoxFS is the primary
filesystem) rules that ext4 through `rsext4` replaces RedoxFS on adoption. It names the cut-over as
a milestone of its own and leaves its order open. No block owned it, so this one does.

## What it does

On adoption, one ext4 server takes over the launch store on aarch64, riscv64 and x86_64. The launch
store is the writable volume the image boots into. It takes `jig` installs and holds the
installed-programs table under `activation/`.

1. The image builder makes the launch volume as ext4. `cargo xtask base-image` makes a RedoxFS
   volume today, with `redoxfs_host mkfs` and `import`. It gains an ext4 twin that formats the
   volume and imports the launch tree. The tool is open: the host's `mke2fs -d`, or `rsext4` on the
   host. Either way, `e2fsck -fn` judges the result.
2. `ext4_server` holds the volume at boot, where `redoxfs_server` holds it now. The boot path
   attaches the data partition and hands it to the ext4 server.
3. `jig` installs onto the ext4 volume, and the installed-programs table of milestone 990 (the base
   image's first installed-programs table) lives under `activation/` on it.
4. basalt's composed image carries the ext4 launch volume. The change lands in nife first, and
   basalt's pin then moves to the landed commit in a pull request of its own.
5. Linux reads the image. CI copies the data partition out of a booted image and runs `e2fsck -fn`
   on it. A Linux mount or `debugfs` then lists the files `jig` installed, with their sizes and
   contents.

## What it waits on

- The adoption ruling of milestone 190 (ext4, read and write), under §46 (we take what meets our
  bar). Nothing in this block links `rsext4` into a nife image before that ruling.
- Milestone 997 (ext4 through rsext4, under milestone 37's crash injector), whose sweeps are part
  of 190's bar.
- Milestone 990's item 2, which attaches the launch volume and reads generation 1 at boot. It is
  outstanding for RedoxFS too.
- Milestone 909 (basalt composes the bootable image from its packages), for item 4.

## Questions for the architect

- §244 (the installed disk has four partitions) names partition 1 as "nife data, RedoxFS". The
  type GUID of §45 does not change, but the row's format does. That edit is the architect's.
- §34 leaves open whether the extended-attribute layer carries over to ext4 or gives way to ext4's
  own extended attributes. `fs_proto` hides where an attribute lives, so either answer works here.
- §34 leaves open whether the cut-over and RedoxFS's removal happen in one step or two. This block
  takes two, provisionally: milestone 1132 (RedoxFS leaves the tree) follows it.

Existing RedoxFS volumes are not converted. nife has no installs, so a machine takes a new image.
That choice is provisional and easy to revisit.

Reuse: `rsext4` from partsfoundry/rsext4 behind nife's `ext4_server`, as milestone 190 builds it.
e2fsprogs on the host as the oracle, under §136 (a mature foreign implementation earns its place as
an oracle). The base-image builder, the boot check and basalt's composed job, extended rather than
replaced. A search of nifeos/nife `xtask/` and basalt's workflows found no ext4 image path.

## Done when

Under QEMU on aarch64, riscv64 and x86_64, basalt's gate boots an image whose launch volume is
ext4 and reaches the swish prompt. `jig` installs a package onto it, and the next boot reads the
installed-programs table from it. CI then runs `e2fsck -fn` on the image's data partition with no
error and lists the installed files from Linux.

## BUGS

- The two RedoxFS crash-check helpers in `xtask/src/disk.rs` have no ext4 twin. Milestone 1132
  needs one before RedoxFS can leave.

## Index row

The launch store moves from RedoxFS to ext4 on all three architectures, and Linux reads the image a
nife machine wrote with stock tools.
