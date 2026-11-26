---
status: PROPOSED
raised: 2026-11-26
---
# 6. Boot a nife image whose launch volume is ext4, and read it from Linux

*The slug is this lane's coinage and provisional; calef names things.*

On 2026-11-25 (UTC) the architect ruled that ext4 through `rsext4` replaces RedoxFS, and §34
(RedoxFS is the primary filesystem) records that ruling and
[why RedoxFS cannot stay](../decisions/0034-redoxfs-primary.md#what-replaces-it-and-what-will-not). nife takes `rsext4` from
partsfoundry/rsext4. The fork offers every fix upstream to `rcore-os/tgoskits` first and carries
whatever upstream does not take, for as long as upstream does not take it.

This journey tells that move from a person's side. A person builds a nife image, boots it under
QEMU on aarch64, riscv64 or x86_64, installs a package with `jig`, and shuts it down. Then they
take the image to a Linux machine. `e2fsck -fn` passes on its data partition, and a mount or
`debugfs` lists the files `jig` installed. They need no nife tool on the Linux side.

The story turns on one ruling. §46 (we take what meets our bar) lets a crate that meets its bar
enter any layer, but an architect rules on each dependency, and `rsext4` is the first kernel-side
case. Milestone 190 (ext4, read and write) holds the bar as its done-when. Steps 1 to 5 meet it,
and step 6 asks for the ruling in a pull request of its own. Nothing links `rsext4` into a nife
image before that ruling. Until then `rsext4` stays a host-only test oracle in nife's
`tools/ext4_oracle`.

The volume that changes is the launch store: the writable volume the image boots into, which
takes `jig` installs and holds the installed-programs table under `activation/`. §34 keeps the
root filesystem question apart from this one, and this journey does not answer it. A read-only
measured root over a writable layer remains open there.

| step | milestone | decision | what this step needs |
|---|---|---|---|
| 1 | 190 | | the fork's fixes at the commit nife pins: bugs 1 to 3 and the recovery-flag order, each with a test, every `unsafe` argued and the Kani harnesses passing; nife's oracle pin moves to a fork commit that carries the recovery-flag order |
| 2 | 190 | | the differential oracle passing in CI on aarch64, riscv64 and x86_64, with every image in the corpus |
| 3 | 190 | | fuzzing that runs: the fork's fuzz targets and `ext4_server`'s in nife's rotation, with no open finding |
| 4 | 997 | | the power-cut, torn-write and lying-device sweeps with the negative control, in CI, each bucket counted beside the RedoxFS numbers of milestone 37 (Prove RedoxFS's crash consistency); a nonzero lying-device count goes to the architect with the numbers |
| 5 | 190 | | `ext4_server` as a nife program, reading and writing a Linux-formatted drive under QEMU on each architecture, with `e2fsck -fn` and `borg check` passing afterwards |
| 6 | 190 | 46 | the adoption ruling, asked for in its own pull request carrying `needs-architect`, with each bar condition and the commit or test that meets it |
| 7 | 909 | | basalt composes the bootable image from its packages and boots it under QEMU on all three architectures |
| 8 | 1131 | | the cut-over: the image builder makes an ext4 launch volume, `ext4_server` holds it, and `jig` installs and the `activation/` table land on it |
| 9 | 1131 | | the Linux half: the image's data partition passes `e2fsck -fn`, and a Linux mount lists what `jig` installed |
| 10 | 1133 | | filesystem operations timed on one ext4 volume, through nife and through Linux, on the same machine |
| 11 | 1132 | | RedoxFS leaves the tree, from the inventory of milestone 982 (Retire RedoxFS once a launch store proves itself), with a twin for each helper it still needs |

The steps run in order with two exceptions. Steps 2 and 3 do not wait on each other, and step 7
runs beside steps 1 to 6, since basalt's composition does not depend on the filesystem. Step 8
waits on step 6: nothing puts `rsext4` into an image before the ruling. Step 10 needs a nife
image on ext4, so it follows step 8, and step 11 comes last. Steps 1, 2, 3 and 5 each cite
milestone 190, so `script/journeys` prints one status for four slices. The need text says which
slice each step reads.

Two steps cross repositories. A fix lands in partsfoundry/rsext4 first and nife's pin moves to
the landed commit in a separate pull request (step 1). Step 8 lands in nife, and basalt's pin then
moves to that nife commit.

Step 4 carries a fork that milestone 997 (ext4 through rsext4, under milestone 37's crash injector)
already names. ext4 checksums metadata and not file data,
so a write that the device acknowledges and drops reads back as stale bytes. Whether a nonzero
count there passes is the architect's call, with the numbers in hand. §34 does not decide it.

## What "done" looks like

Every step above at `BUILT`. A person builds a nife image, boots it, installs a package and shuts
it down. They then read its data partition on Linux with stock e2fsprogs and the kernel's own ext4
driver, and nothing reports an error. The same volume gives filesystem numbers on nife and on Linux
that a reader can set side by side. RedoxFS is gone from the tree.
