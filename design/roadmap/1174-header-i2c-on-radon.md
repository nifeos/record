---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: 1173
decision_dependencies: none
machine_requirements: a VisionFive 2 with one I2C device wired to header pins 3 and 5
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1174. I2C on radon's header: the DesignWare crate on a second controller

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. Milestone 1166 (an eMMC module in
radon's socket) says why.

## What is unexercised

nife drives one I2C controller, I2C5, and only to reach the power management chip: milestone 592
(radon's cold reboot dies in OpenSBI's PMIC write, and the kernel sets that write up) is where it
started. The header's I2C bus, on I2C0, has never carried a transfer. nife's crate
`designware_inter_integrated_circuit` says in its BUGS that one controller has run it.

## The hardware, from primary sources

- The VisionFive 2 datasheet (v1.53, VisionFive2-DSEN-001), table 5-1: header pin 3 is GPIO 58
  (I2C SDA) and pin 5 is GPIO 57 (I2C SCL).
- The 40-Pin GPIO Header User Guide (v1.3, VisionFive2-UGEN-001) names that bus `i2c0` in its
  pin table.
- Mainline Linux `jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`): `i2c0: i2c@10030000`,
  `snps,designware-i2c`, clocked by `JH7110_SYSCLK_I2C0_APB`. Mainline's VisionFive 2 tree
  (`jh7110-common.dtsi`) runs it at 100 kHz on GPIO 57 and GPIO 58.
- The other buses this board wires out, I2C2 to the DSI connector and I2C6 on GPIO 16 and 17,
  belong to milestones 1170 (a MIPI DSI panel on radon) and 1171 (a MIPI CSI camera on radon).

## What it needs

- I2C0's clock and reset, and its two pins in the system pin controller, which milestone 1173
  (general-purpose I/O on radon's 40-pin header) gives a crate for.
- One I2C device with a register it answers with a known value, for example a small EEPROM or a
  temperature sensor's identity register. A person wires it to pins 1 (3.3 V), 3, 5 and 6 (ground)
  with the board powered off. The block names no part.
- A user-space owner for the bus. The kernel's copy for I2C5 stays where it is; the header bus
  belongs to a program with a grant for I2C0's register page and its two pins.

## Done when

On radon, with a device on the header bus, a program reads its identity register through I2C0
and gets the value its datasheet gives, then writes and reads back one byte where the device has
a writable register. An address with no device returns a refusal within the crate's bound, not a
hang. The log goes under nife's `bench/radon-<date>/`, and the crate's BUGS line counts two
controllers.

## Prior art

- Linux mainline: `drivers/i2c/busses/i2c-designware-platdrv.c` and its core, with interrupts and
  fast mode, and `i2c-dev` for user space.
- OpenBSD: `sys/dev/fdt/dwiic_fdt.c` attaches the same controller, and `iic(4)` children attach
  from the device tree.
- Where nife differs: the crate polls each transfer and bounds every wait, as the crate already does
  for I2C5. A program holds one bus by grant, not every bus on the machine.

Reuse: the crate `designware_inter_integrated_circuit` as it stands, and milestone 1173's pin
crate. A search of the roadmap for `I2C0` and `header` found no other block that drives this bus.

## Index row

The header's I2C bus has never carried a transfer under nife. The DesignWare I2C crate, so far run
only on I2C5 for the power chip, reads and writes a device on I2C0 and refuses an empty address
within its bound.
