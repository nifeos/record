# The JH7110's M.2 root port at the bench: a runbook for a person

*Name: provisional, minted 2026-11-19 (UTC) by lane lane/163-jh7110-pcie-kernel-wiring.*

This page takes a VisionFive 2 with an NVMe drive in its M.2 slot from a fresh build to a judged
log. It holds the bench steps of milestone 163 (the JH7110's PCIe root complex), "Steps that need
the board". [jh7110-pci-express.md](jh7110-pci-express.md) explains what the bring-up does, and
[visionfive2.md](visionfive2.md) covers booting the board at all. One boot answers most of the
questions here. Checks 7 and 8 take a second boot, step 3.

## Before anything else

- Read the off-tree bench instructions first, as
  [the bench runbook](bench-runbook.md#before-touching-any-machine) says, and follow their warnings
  over anything here.
- Power off before you touch the M.2 slot. Seat the drive and fit its screw with the board
  unpowered. The slot takes an M-key 2230, 2242, 2260 or 2280 drive.
- Nothing on this page writes the drive. The first boot reads the drive's configuration space and
  nothing else. The second boot (step 3) sends the drive reads only, through a window whose
  capability the NVMe server refuses every write on. Still, use a drive whose contents you can
  lose, because a fault in a new driver is exactly what this run looks for.

## What the run needs

| what | how to confirm |
|---|---|
| A board that already boots nife over the network | [visionfive2.md](visionfive2.md), "The bench runbook": a boot prints `nife: payload came from net` and `nife on RISC-V (rv64, S-mode, Sv39)` |
| The serial console attached before power | `script/board-console` logs every byte to a file ([board-console.md](board-console.md)) |
| A build of the commit under test | `git log -1` in your checkout names it; record the hash in the results table |
| An NVMe drive in the M.2 slot | seen, with the board off |

## Running it hands-free

The run needs nobody at the firmware prompt and one power-on in all. Three pieces make that so:

- **The card.** `script/board-image --tftp --server <host> --card <mounted card>` writes the card
  once. Its `boot.scr.uimg` asks the TFTP host for the served script first, and boots the card's
  own kernel and archive only when the network gives nothing. The served script names the build,
  so the card stays the same between builds. Write the card's own pair from a build that does not
  restart the board, so that a failed fetch cannot start a loop. `script/board-image` runs `cargo
  xtask card-check` on the card after the copy, and it must print `SEALED`.
- **The first boot restarts the board itself.** A `script/board-image --tftp --soak --reboot`
  build runs the bring-up, prints every line in step 2, starts the soak (`soak-test: started`),
  and about 125 seconds later asks the board's power controller to reset it, through the PMIC
  route ([board-reboot.md](board-reboot.md)), before the firmware's own reset
([soak.md](soak.md#the-rebooting-soak-on-radon-which-is-milestone-249s-experiment)). The served set is
  swapped for step 3's while the first one soaks, so the board comes back as the drive-reading
  boot. If the swap cannot be made in time,
  `script/board-console --stop` sends the one byte that disarms the reset.
- **The console decides when each boot is done.** `script/board-console --until soak` exits 0 on
  the first boot's `soak-test: started`. A second watch, started straight after, catches the reset
  lines and step 3's boot. That boot prints no stage word, so the watch is `--until none`, as in
  step 3, and runs ten minutes rather than five because it starts during the soak. Exit 1 is a
  failure the board announced, 2 a board that went quiet, 3 a stage not reached in time
  ([board-console.md](board-console.md)). A watch that ends 2 or 3 is a hang, and the one remedy is
  to cut and restore the board's power; the card then boots whatever the host serves. The second
  watch ends 0 whether step 3's boot halted or hung after its tour line, so its log decides checks
  7 and 8.

This board has reset through the route when a person typed `reboot` at the shell. No bench log
yet holds the rebooting soak's own call of it, so record which line the first boot printed last.
A reset is not a power cycle, so a run with no power cycle between the boots leaves check 9
UNRUN.

## Step 1: check that the tree names the port

The kernel brings up port 1 only from its node in the tree U-Boot hands over. It has no constant
fallback, because a guessed window is how a write lands on the wrong device. So the first question
is what that tree says, and the kernel prints it before anything else in the bring-up. Nobody types
at the firmware prompt. The boot in step 2 prints one line for every `pcie@` node in the
tree, then the port's verdict:

```
  jh7110 pcie: tree: 2 pcie@ node(s)
  jh7110 pcie: tree node 0: compatible "starfive,jh7110-pcie", reg <0x9 0x40000000 0x0 0x1000000 0x0 0x2b000000 0x0 0x100000>, reg-names "cfg","apb", linux,pci-domain <0x0>, status "disabled"
  jh7110 pcie: tree node 1: compatible "starfive,jh7110-pcie", reg <0x9 0xc0000000 0x0 0x1000000 0x0 0x2c000000 0x0 0x100000>, reg-names "cfg","apb", linux,pci-domain <0x1>, status absent
```

The example is mainline's shape; the order of the names and of the windows in `reg` may differ.
Port 1 is the node whose `reg` holds the window at `0x2c000000` (`0x0 0x2c000000`). A property the
node lacks prints `absent`, and an absent `status` means `"okay"`. Record, for that node:

- `compatible`: `"starfive,jh7110-pcie"`.
- `reg-names`: the kernel needs `"apb"` and `"cfg"`. Mainline's tree uses those names.
- `reg`: the `apb` window at `0x2c000000` and the `cfg` window at `0x9c0000000`, in the order
  `reg-names` gives.
- `linux,pci-domain`: `<0x1>`.
- `status`: `"okay"` or absent.

When the kernel accepts the node, the next line carries the two facts the tree lines leave out
(step 2's first example line). The 32-bit window comes from `ranges` and should start at
`0x38000000`. The reset pin comes from `perst-gpios` and should be 28.

If the tree names the controller under other `reg-names` (StarFive's own kernel tree has used
`"reg", "config"`), or has no `linux,pci-domain` of 1, the kernel prints `port One stays off` right
after the tree lines and goes no further. The tree lines are the record of what the tree says
instead. That answers the first board question in milestone 163, and the next change is in
`machine_discovery::jh7110::pci_express`, not at the bench. A build older than the tree lines
prints none of them; read the node at the U-Boot prompt then (`fdt addr ${fdtcontroladdr}`, `fdt
list /soc`, `fdt print` on the node).

## Step 2: boot and read the lines

Boot the build. Every line the bring-up prints starts with `  jh7110 pcie:`. They appear after the
memory map and before the IOMMU lines. After step 1's tree lines, a good boot looks like this
(addresses from mainline's tree; counts vary):

```
  jh7110 pcie: port One: bridge 0x2c000000, cfg 0x9c0000000, 32-bit memory 0x38000000+0x8000000, PERST# pin Some(28)
  jh7110 pcie: SYS clocks: 1 turned on, 1 of 1 reset(s) released, 0 step(s) rejected
  jh7110 pcie: STG clocks: 3 turned on, 6 of 6 reset(s) released, 0 step(s) rejected
  jh7110 pcie: link up after 2 read(s), status 0x00000020, 3 window(s) translated
  jh7110 pcie: root port forwards: bus numbers 0x00010100, memory base and limit 0x3ff03800
  jh7110 pcie: the walk over 2 bus(es):
                00:00.0 1556:xxxx class 060400 bridge to buses 01..=01
                01:00.0 vvvv:dddd class 010802
                2 function(s) over 2 bus(es) of the 2 described; mapping 2048 KiB of config space
```

A clock line may end in ` (already up)`: firmware had left that domain running, and the bring-up
found nothing to do. The link status word needs bit 5 (`DATA_LINK_ACTIVE`) set; other bits may
differ. Later, the machine summary carries the window the bring-up recorded:

```
  pcie             : ecam 0x00000009c0000000..0x9c0200000, bar window 0x38000000..0x40000000
```

A port that stayed off prints `pcie             : none (this machine describes no host bridge)`
there instead.

The NVMe path does not run on this boot. The kernel starts the NVMe server for a client only: the
disk tree at `/disk`, which starts only beside a file service, or the file service itself, which
takes an NVMe disk only on a machine that booted from one. A network boot of this board has
neither, so no `non_volatile_memory_express` or `disk tree` line appears and `/disk/nvme0` does not
exist. Step 3 reads the drive instead.

## Step 3: boot again and read the drive

The second boot is a bench boot: a kernel built with the `disk_read_bench` feature, which starts
the NVMe server with the boot thread as its only client, reads the drive and halts. It never starts
the progenitor, so there is no prompt. [bench-boots.md](bench-boots.md#disk_read_bench-an-nvme-drive-read-through-the-disk-trees-window)
says what each of its lines prints. Build it and power-cycle the board:

```
script/board-image --tftp --extra-features disk_read_bench
script/board-console --until none --for 5m --log target/board/disk-read-bench.log
```

The console has no stage word for this boot, so it watches for the whole five minutes; the boot
halts long before that, after `disk-read-bench: done, halting.`

The console's exit code does not judge this boot. The boot prints its stage lines before the bench
starts, so a boot that hangs later still exits 0 when the five minutes run out. Only the
`disk-read-bench:` lines decide checks 7 and 8, and a log with no verdict line is a FAIL.

The bring-up lines of step 2 print again, and then every line starts `disk-read-bench:`. A good
boot ends like this, where `<...>` stands for what the drive and the build give:

```
disk-read-bench: controller nvme 01:00.0 (rid 0x0100), DMA unconfined: no iommu is translating on this machine
disk-read-bench: namespace  <bytes> bytes, <lba>-byte lbas, blocks_per <n>
disk-read-bench: size       GET_SIZE_BYTES through the window answers <bytes>: agrees
disk-read-bench: landing    blocks 0..16 read twice over 0xaa then 0x55: sha256 <digest>.. both times
disk-read-bench: read       256 x 65536 B (blocks 0..4096) in <us> us = <rate> B/s (<ns> ns per read)
disk-read-bench: verdict READ-AT-RATE: read <rate> B/s over 256 reads of 65536 B, EL0 driver, nothing written; DMA unconfined: no iommu is translating on this machine
disk-read-bench: done, halting.
```

Expect `DMA unconfined` here: the kernel programs no IOMMU on this board, and with none nife
trusts the driver, as §86 (whether an NVMe driver can leave the kernel) rules. Record the line as it reads. The figure
is one 64 KiB read in flight at a time from a debug or release build, as its header line says, so
it is the driver's figure and not the drive's.

To bring the board back to a normal boot, build again without the feature (`script/board-image
--tftp`) and power-cycle.

## Step 4: judge the log

Fill one row per check. A check that did not run is UNRUN, never PASS.

| # | check | pass when | result |
|---|---|---|---|
| 0 | commit under test | recorded | |
| 1 | tree node (step 1) | port 1's tree line shows `reg-names` `apb`, `cfg`, `linux,pci-domain` `<0x1>` and `status` `okay` or absent; the `port One:` line shows PERST# pin 28 | |
| 2 | clocks | both clock lines show `0 step(s) rejected` and every reset released | |
| 3 | no refused access | no `fell outside the mapped pages` line | |
| 4 | link | `link up` | |
| 5 | root port | `00:00.0` class `060400`, `bridge to buses 01..=01` | |
| 6 | drive | `01:00.0` class `010802`, and no other `01:` line | |
| 7 | NVMe (step 3) | `controller nvme 01:00.0`, a `namespace` line, and `size ... agrees` | |
| 8 | reads (step 3) | `landing ... both times` and `verdict READ-AT-RATE`; a `SKIPPED` or `FAILED` verdict, or no verdict line, is a FAIL | |
| 9 | after a power cycle | checks 2 to 6 from a boot without the feature, then 7 and 8 from step 3, again | |

## What a failure looks like

| line | most likely cause, in order |
|---|---|
| no `jh7110 pcie:` line at all | the build predates the bring-up; or the kernel did not take the machine for a JH7110 (no clock-and-reset node and no TRNG) |
| `port One stays off: ...` | the reason is the tree's: the tree lines above it (step 1) say what it holds instead |
| `bring-up stopped: ClocksAndResets` | a clock gate or reset did not take. The two clock lines above it say which domain. A reset that never releases usually means a clock it needs is still off. |
| `bring-up stopped: Window(n)` | a window in the tree is not a power of two of at least 4 KiB. Record the `reg` and `ranges` |
| `link down after 10 reads` | no drive, a drive not seated, or a drive that did not train. Reseat it with the board off and try a second drive before suspecting the sequence. Record the status word. |
| a trap or a hang right after `link up` | a configuration read faulted. See "Unsupported requests" below |
| `01:01.0`, `01:02.0` and so on, all the same device | the root port does not filter device numbers on bus 1. See "Aliased devices" below |
| `verdict SKIPPED: no NVMe controller on the bus` | the walk found no class `010802` function: check 6 says why |
| `verdict SKIPPED: the namespace's lba size gives no blocks_per in 1..=8` | the drive is formatted with a block size the server does not take. The `lba size` line above it gives the size. Record it. |
| `controller ... failed bring-up: ...` or `the server did not come up: ...` | the root complex worked and the NVMe driver refused the drive. That belongs to the NVMe path, not this milestone. Record the reason. |
| `landing ... DIFFERS` | two reads of the same blocks returned different bytes, so the data did not land where the CPU reads it. See "DMA coherence" below |
| no line after `controller nvme` | the admin queue never completed. See "DMA coherence" below |

## What only the board can answer

These are the bring-up's open questions, each one recorded in the crate's or the note's `BUGS`.
The run above answers each one, so record what it shows:

- **Unsupported requests.** The walk reads every device number on bus 1. On a PC an absent device
  reads as all ones. Whether this bridge does the same, or raises a bus error the kernel takes as
  a fault, is unknown. A hang or trap after `link up` that names an address inside
  `0x9c0100000..0x9c0200000` is this.
- **Aliased devices.** A downstream port should answer configuration requests on its secondary bus
  for device 0 only. Linux enforces this in software (`only_one_child`), and `pci.rs` does not.
  Duplicates of `01:00.0` mean this bridge answers every device number, and the next change is to
  limit the walk.
- **DMA coherence.** The Ethernet controller's DMA is measured coherent on this board
  ([designware-ethernet.md](designware-ethernet.md)). The PCI Express master sits on another port
  of the interconnect, and nothing has measured it. Step 3's boot is a first test of it. The admin
  queue's submission and completion rings are DMA, so an identify that times out or returns a zero
  size with the link up points here first. The `landing` line fails when a read's data does not
  reach the CPU. A byte-for-byte comparison of the drive's data against another machine's reading
  needs a dump tool the board image does not carry yet. The `landing` digest covers the first
  64 KiB, so another machine's `sha256sum` of that range sits beside it.
- **The `PCIE_SLV_MAIN` clock.** The STG generator has one, and neither plan turns it on; it stays
  as firmware left it. A link that trains with an endpoint that never answers points here.
- **Who else writes the GPIO page.** The bring-up writes PERST# in the SYS GPIO controller's
  output registers. Nothing else in the kernel writes that page today. If a later server does,
  the two need one owner.

## Record the result

Commit the console log under `bench/radon-<date>/` (UTC) beside the filled table, in a pull request
that ticks the matching items under "Steps that need the board" in
`design/roadmap/0163-jh7110-pcie-root-complex.md`. A FAIL is a result: record it the same way,
with the line that showed it.
