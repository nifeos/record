---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: 1173
decision_dependencies: none
machine_requirements: a VisionFive 2 with a jumper from header pin 19 to pin 21
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1175. SPI on radon's header: the PL022 controller, looped back

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. On that date calef asked for a
milestone for every part of the VisionFive 2 that nife has not yet exercised on the board, and
this is one of them.

## What is unexercised

The JH7110's general SPI controllers. nife has no SPI driver, and the header's SPI pins have never
moved a bit. The QSPI controller that holds the boot firmware is a different block, and milestone
1178 (writing radon's QSPI flash) covers it.

## The hardware, from primary sources

- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), section 2.9.1: seven SPI interfaces,
  master or slave, an eight-entry FIFO of 16-bit frames each way, and DMA for both FIFOs.
- Mainline Linux `jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`): `spi0: spi@10060000`,
  compatible `arm,pl022` and `arm,primecell`, interrupt 38, clocked by `JH7110_SYSCLK_SPI0_APB`.
  The VisionFive 2 tree turns it on and puts its transmit, receive, clock and chip-select lines on
  GPIO 52, 53, 48 and 49.
- The VisionFive 2 datasheet (v1.53, VisionFive2-DSEN-001), table 5-1: those GPIOs are header pins
  19 (MOSI), 21 (MISO), 23 (SCLK) and 24 (CE0).

## What it needs

- A PL022 crate: clock divider, frame format, chip select and polled FIFO transfers. The PL022 is
  Arm's PrimeCell synchronous serial port, so the register map comes from Arm's manual for it,
  checked against the Linux and U-Boot drivers below. This lane did not read that manual.
- SPI0's clock and reset, and its four pins through milestone 1173 (general-purpose I/O on radon's
  40-pin header).
- A person, to fit one jumper from pin 19 to pin 21 with the board powered off.
- DMA is not part of the block. Polled transfers prove the controller, and the AXI DMA engine
  arrives with milestone 1172 (audio on radon), which states its trust in memory.

## Done when

On radon, with pin 19 jumpered to pin 21, a program sends 4,096 bytes of a known pattern through
SPI0 at three clock rates and reads the same bytes back at each. With the jumper removed, the read
returns a constant byte, which shows that the loop passes through the wire. The log goes under
nife's `bench/radon-<date>/`.

## Prior art

- Linux mainline: `drivers/spi/spi-pl022.c`, with `spidev` for user space.
- U-Boot: `drivers/spi/pl022_spi.c`, a polled driver of a few hundred lines, nearer the size nife
  wants.
- OpenBSD has no PL022 driver under `sys/dev/fdt` at `e70d4a7ea910`.
- Where nife differs: a program holds SPI0 and its four pins by grant. Linux's `spidev` hands a
  whole bus to whoever can open the device file.

Reuse: milestone 1173's pin crate. A search of the roadmap for `SPI`, `PL022` and `spidev` found the
SPI flash in milestone 218 (every boot of the VisionFive 2 needs a human typing four commands into
U-Boot), and no general SPI driver.

## Index row

The JH7110's PL022 SPI controller has never moved a bit under nife. A small polled crate sends a
pattern out of the header's MOSI pin and reads it back through a jumper to MISO, at three clock
rates.
