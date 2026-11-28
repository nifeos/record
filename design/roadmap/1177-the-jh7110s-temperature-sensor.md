---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: none
decision_dependencies: none
machine_requirements: JH7110 silicon
specific_machine: radon (the only JH7110 board this project has)
needs_person: no
---
# 1177. The JH7110's temperature sensor, read and acted on

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. On that date calef asked for a
milestone for every part of the VisionFive 2 that nife has not yet exercised on the board, and
this is one of them.

## What is unexercised

nife has never read the JH7110's die temperature. Nothing in nife watches it, so a long soak on
radon runs with no record of how hot the chip ran and no limit on it. Milestone 225 (run the soak
on radon, argon and xenon) reads the power chip's latched interrupt status, which includes a die
temperature warning from the power chip itself, not the SoC's sensor.

## The hardware, from primary sources

- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), section 2.9.6: a 12-bit sensor, within
  3 degrees Celsius untrimmed from -40 to 100, within 1.0 degree trimmed from 0 to 70, and within
  1.25 degrees trimmed from -40 to 125.
- Mainline Linux `jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`): `temperature-sensor@120e0000`,
  compatible `starfive,jh7110-temp`, with a `sense` and a `bus` clock and reset. StarFive's vendor
  tree names the same block `tmon@120e0000`, interrupt 81.
- The VisionFive 2 datasheet (v1.53, VisionFive2-DSEN-001), section 5.14: the recommended ambient
  range is 0 to 50 degrees Celsius, and the "internal governor" lowers CPU speed and voltage so that
  the CPU never exceeds 85 degrees. The datasheet does not say which software runs that governor; by
  every sign it is Linux's frequency scaling. nife scales no frequency, so under nife nothing holds
  the chip under 85 degrees.

## What it needs

- A crate for the sensor: its clocks and resets, its enable and its conversion read, with the
  raw-to-Celsius formula from the Linux driver below. The datasheet read here gives no formula.
- A place for the reading: the kernel's statistics page, or a small program that holds the
  sensor's register page by grant and prints it on the console.
- A rule for what nife does at a limit. The block proposes one, for example stopping a soak's
  load at 85 degrees and logging why, and the record holds it as provisional.

## Done when

On radon, nife prints the die temperature once a second. Read at the same idle state under Linux
(`/sys/class/hwmon`) and under nife, within one minute of each other, the two readings agree
within 2 degrees. Under a four-hart load the reading rises, and a soak that reaches the limit
stops its load and logs the temperature. The logs go under nife's `bench/radon-<date>/`.

## Prior art

- Linux mainline: `drivers/hwmon/sfctemp.c`, which serves both the JH7100 and JH7110 sensors
  through `hwmon`.
- OpenBSD: `sys/arch/riscv64/dev/stftemp.c` at `e70d4a7ea910`, a sensor for `sysctl hw.sensors`.
  FreeBSD has `sys/riscv/starfive/jh7110_temp.c` at `056925e30639`.
- Where nife differs: the reading has a consumer. A soak on radon records its temperature beside
  its results and stops before the chip passes the limit the board's own documentation sets.

Reuse: the JH7110 clock and reset crates, and milestone 225's soak report. A search of the roadmap
for `temperature`, `thermal` and `sfctemp` found milestone 225's PMIC status and no SoC sensor
driver.

## Index row

nife has never read the JH7110's die temperature, and no governor holds the chip under its 85
degree limit. A small crate reads the sensor, agrees with Linux within 2 degrees, and stops a
soak's load at the limit.
