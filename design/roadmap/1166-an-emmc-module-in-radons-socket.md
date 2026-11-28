---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: 53
decision_dependencies: none
machine_requirements: a VisionFive 2 with an eMMC module in its socket
specific_machine: radon (its eMMC socket is empty; a module is on order)
needs_person: yes
---
# 1166. An eMMC module in radon's socket: the 8-bit bus and the faster modes

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. On that date calef asked for a
milestone for every part of the VisionFive 2 that nife has not yet exercised on the board, and
this is one of them.

## What is unexercised

The JH7110 has two DesignWare mobile storage controllers. Milestone 53 (the board's own
peripherals: network and storage on real silicon) drives the second, the microSD slot at
`0x1602_0000`, through both the polled path and the IDMAC. The first, at `0x1601_0000`, serves the
board's eMMC socket, and on radon it answers `NoCard(NoResponse(1))`, because the socket holds no
module (nife's `bench/radon-2026-11-17/README.md`). So nothing has run the 8-bit bus, the eMMC
command set or the faster modes.

A 16 GB plug-in eMMC 5.1 module, of the kind Radxa's Rock 4 boards take, went on order on
2026-11-28. The bench run waits for its delivery. Whether that module fits and works in the
VisionFive 2's socket remains unverified: the VisionFive 2 datasheet promises only an
"industry-common pinout".

## The hardware, from primary sources

- Mainline Linux `arch/riscv/boot/dts/starfive/jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`):
  `mmc0: mmc@16010000`, the same `starfive,jh7110-mmc` block as the microSD slot's `mmc1`.
- Mainline `jh7110-common.dtsi` at the same revision: `bus-width = <8>`, `max-frequency` 100 MHz,
  an assigned clock of 50 MHz, `mmc-hs200-1_8v` and `mmc-ddr-1_8v`, `non-removable`, a reset on
  GPIO 62, and `vqmmc-supply = <&emmc_vdd>`, a regulator of the AXP15060 PMIC on I2C5.
- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), section 2.2.4: eMMC 5.0 and SD 3.0, with
  4-bit and 8-bit data widths.
- The VisionFive 2 datasheet (v1.53, VisionFive2-DSEN-001): a "high speed eMMC socket for eMMC
  modules", and eMMC as one of the four boot modes.

## What it needs

- The module, fitted by a person with the board powered off.
- The eMMC half of the card protocol in `designware_mobile_storage`: `SEND_OP_COND` instead of the
  SD sequence, the extended CSD read, and the bus-width and timing switches.
- 1.8 V signalling for HS200 and DDR, which means asking the PMIC for the `emmc_vdd` rail first.
  The kernel's AXP15060 path on I2C5 already talks to that PMIC.
- DMA confinement. The JH7110 has no IOMMU (its datasheet lists none, and `notes/iommu.md` says the
  same), so the IDMAC can reach any physical address. The microSD path's answer carries over: one
  region the kernel grants, a descriptor chain built inside it, and the engine stopped before every
  return. This block reuses that answer and does not reopen it.
- Nothing that writes the module's boot partitions. The board's boot mode switches select eMMC
  boot only when a person sets them, and this block leaves them on their current setting.

## Done when

On radon, with the module fitted, the storage bench of milestone 53 runs against slot 0. It prints
the module's CID and extended CSD, reads 8 MiB on a 4-bit bus and then on an 8-bit bus, and
reports each rate. The scratch write test then passes on the module's user area through the IDMAC.
HS200 at 1.8 V then runs, if the module and the board's rail allow it, with its rate measured
against the 8-bit bus. The log goes under nife's `bench/radon-<date>/`.

## Prior art

- Linux drives the socket through `dw_mmc` and its StarFive glue `dw_mmc-starfive.c`, with the
  generic eMMC core in `drivers/mmc/core/mmc.c`, which switches bus width and timing through
  `SWITCH` commands on the extended CSD.
- OpenBSD drives the same controller through `sys/dev/fdt/dwmmc.c`, with the card protocols in
  `sys/dev/sdmmc`.
- Where nife differs: the driver runs at EL0 behind `file_system_contract::blk`, and the kernel
  grants it one DMA region, where Linux trusts its driver with all of memory.

Reuse: `designware_mobile_storage` (partsfoundry), the storage bench and the EL0 block server of
milestone 53, and the kernel's PMIC path. A search of the roadmap for `eMMC` found only milestone
53's line saying the socket is empty.

## Follow-on

- **Outstanding.** The module's delivery, then a person fitting it.
- **Outstanding.** Whether this module's pinout matches the VisionFive 2's socket. The datasheet
  does not name a compatible module.

## Index row

radon's eMMC socket, the first of the JH7110's two DesignWare storage controllers, holds no module,
so the 8-bit bus and the faster modes have never run. A module is on order. The microSD driver gains
the eMMC protocol and the bench reads and writes the module through the IDMAC.
