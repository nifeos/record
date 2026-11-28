---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: 1175
decision_dependencies: none
machine_requirements: a VisionFive 2, a person at it, and a host on its console UART
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1178. Writing radon's QSPI flash, and the recovery path proven first

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. Milestone 1166 (an eMMC module in
radon's socket) says why.

## What is unexercised

nife has never read or written radon's QSPI NOR flash. U-Boot reads it at every power-on, and
nife's kernel arrives after it. Milestone 218 (every boot of the VisionFive 2 needs a human typing
four commands into U-Boot) refused to repair the U-Boot environment in that flash. It called the
repair the least reversible thing on its list, because this project owns one VisionFive 2. That
refusal stands. This block plans a reader first, and any write only after a ruling.

## Why a write is dangerous

The flash holds the board's boot firmware: the JH7110 datasheet (v1.63, JH7110-DSEN-001) lists it
as "QSPI Flash (For SPL + OpenSBI + U-Boot)". In the factory boot mode the boot ROM loads the SPL
from it, and the board has no second copy. A write to the wrong offset, an erase cut short by a
power loss, or a driver bug that sends the wrong command leaves radon unable to boot from flash.
Then every bench run on radon stops until a person recovers it. The block that broke the flash
cannot repair it: with no firmware, nife does not start.

The recovery path, from StarFive's VisionFive 2 Quick Start Guide (v1.73), section 4.3:

1. A person powers the board off and sets the boot-mode switches (RGPIO_1, RGPIO_0) to 1, 1,
   which selects UART mode.
2. A host on the console UART at 115,200 baud sees the boot ROM print `C` repeatedly. It sends
   StarFive's recovery binary (`jh7110-recovery-<Version>.bin`, from `starfive-tech/Tools`) by
   XMODEM.
3. The recovery program's option 0 writes the SPL (`u-boot-spl.bin.normal.out`) and option 2
   writes U-Boot (`visionfive2_fw_payload.img`).
4. The person powers off and sets the switches back to 0, 0, flash mode.

That path writes StarFive's published images, not the bytes the flash held before. It restores a
working board, not radon's exact firmware. Booting from microSD in mode 0, 1 is a second route,
unproven on radon (`notes/visionfive2.md`, "Boot-mode switches").

## The hardware, from primary sources

- Mainline Linux `jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`): `qspi: spi@13010000`,
  compatible `starfive,jh7110-qspi` and `cdns,qspi-nor`, with a 4 MiB memory-mapped window at
  `0x2100_0000`, interrupt 25, and three clocks.
- Mainline's VisionFive 2 tree (`jh7110-common.dtsi`): one `jedec,spi-nor` device at 100 MHz with
  three fixed partitions: `spl` from 0 to `0xf_0000`, `uboot-env` of 64 KiB at `0xf_0000`, and
  `uboot` of 15 MiB at `0x10_0000`, 16 MiB in all.
- The JH7110 datasheet, section 2.2.3: master mode, up to 100 Mbps, 1, 2 or 4 data lines, two chip
  selects, and execute-in-place and boot modes.
- Unverified: the flash part's maker, size and erase-sector size. The partitions imply at least
  16 MiB, and the part's own JEDEC identity answers the rest, which is the reader's first output.

## What it needs

- A Cadence QSPI crate for reads: the controller's indirect read and the JEDEC identity and SFDP
  commands. It holds the controller by grant, as milestone 1175 (SPI on radon's header: the PL022
  controller, looped back) does.
- A ruling from calef before any write. A write to this flash fails in a way that no commit
  reverts, and only a person at the board can undo it.
- For any write: a person at radon, a host on the console with the recovery binary and both
  images in hand, and a full read of the flash saved off the board beforehand.

## Done when

The reader counts as done when, on radon, nife reads the flash's JEDEC identity and all 16 MiB,
twice, and both reads hash the same. A Linux boot on the same board reads `/dev/mtd0` to
`/dev/mtd2`, and those bytes match nife's. The log and hashes go under nife's `bench/radon-<date>/`.

The writer counts as done only after the ruling, and only in the `uboot-env` partition. U-Boot
already rejects that partition's contents for a bad CRC, as milestone 218 records. nife erases its
64 KiB, writes a pattern, reads the pattern back, then writes the saved bytes back and confirms they
hash as before. radon then cold-boots from flash with its usual console. A person stands at the
board with the recovery path ready for the whole run.

## Prior art

- Linux mainline: `drivers/spi/spi-cadence-quadspi.c` under the `spi-mem` layer, with `spi-nor`
  and `mtd` above it. User space writes the flash with `flashcp`, the QSG's section 3.8.1 route.
- U-Boot: `drivers/spi/cadence_qspi.c` with the `sf probe`, `sf update` commands the QSG gives
  for the same job.
- Where nife differs: the reader comes first and stands alone, and the writer touches only the one
  partition the board can lose. A ruling gates it, as milestone 218 gated the environment repair.

Reuse: milestone 1175's controller grant. A search of the roadmap for `QSPI`, `SPI flash` and
`uboot-env` found only milestone 218's refusal.

## Index row

nife has never read or written radon's boot flash. A Cadence QSPI reader comes first and checks
its bytes against Linux's. A write, limited to the U-Boot environment and restored, waits on a
ruling, with UART recovery proven ready before it.
