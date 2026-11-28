---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: none
decision_dependencies: none
machine_requirements: a VisionFive 2 with one jumper wire across two header pins
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1173. General-purpose I/O on radon's 40-pin header

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. Milestone 1166 (an eMMC module in
radon's socket) says why.

## What is unexercised

nife has no GPIO driver. Milestone 163 (the JH7110's PCIe root complex) drives its PERST# line by
writing the pin controller's registers directly, and nothing else in nife sets or reads a pin. No
header pin has ever changed state under nife, and no pin has raised an interrupt.

## The hardware, from primary sources

- The VisionFive 2 datasheet (v1.53, VisionFive2-DSEN-001), table 5-1, and the 40-Pin GPIO Header
  User Guide (v1.3, VisionFive2-UGEN-001) give the pins. Pin 3 is GPIO 58 and pin 5 is GPIO 57
  (I2C). Pins 8 and 10 are GPIO 5 and GPIO 6 (the console UART), pins 19, 21, 23 and 24 are GPIO 52,
  53, 48 and 49 (SPI), and pins 32 and 33 are GPIO 46 and GPIO 59 (PWM). The others are
  general-purpose: GPIO 36, 37, 38, 39, 40, 42, 43, 44, 45, 47, 50, 51, 54, 55, 56, 60, 61 and 63.
- The same datasheet, section 4.2: every GPIO pin works at 3.3 V. Section 5.1.2: the multiplexer can
  switch every GPIO to other functions, among them SDIO, audio, SPI, I2C and UART.
- Mainline Linux `jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`): the system pin controller
  `pinctrl@13040000` (`starfive,jh7110-sys-pinctrl`), which owns GPIO 0 to 63, and the always-on
  one at `pinctrl@17020000` (`starfive,jh7110-aon-pinctrl`). Each is a GPIO controller and an
  interrupt controller.

## What it needs

- A GPIO crate for the system pin controller: direction, output value, input value, and the
  output and input multiplexer for a pin, with the pin's edge or level interrupt.
- A contract for a program to hold a pin: which pins a grant names, and the refusal of every
  pin a grant does not name. The console pins, the pins milestone 163 uses and the pins other
  drivers already hold stay out of any grant.
- A person, to fit one jumper between two free header pins with the board powered off. The pins work
  at 3.3 V, and the jumper joins two of them and nothing else.

## Done when

On radon, with a jumper from pin 11 (GPIO 42) to pin 13 (GPIO 43), a program drives GPIO 42 high
and low a thousand times and reads each level back on GPIO 43 without a miss. A rising edge on
GPIO 43 then raises an interrupt that the program receives, counted against the number of edges
it drove. A request for a pin outside its grant refuses. The log goes under nife's
`bench/radon-<date>/`. Milestone 163 then moves its PERST# writes to the same crate.

## Prior art

- Linux mainline: `drivers/pinctrl/starfive/pinctrl-starfive-jh7110.c` and its system and
  always-on halves, serving `gpiolib` and the character device `/dev/gpiochipN`.
- OpenBSD: `sys/arch/riscv64/dev/stfpinctrl.c` drives the same controller as a `gpio(4)`
  controller. FreeBSD has `sys/riscv/starfive/jh7110_gpio.c`.
- Where nife differs: a pin is a capability. A program holds the pins its grant names and no
  others, where Linux's character device grants a whole chip to whoever can open it.

Reuse: the register map milestone 163 already writes. A search of the roadmap for `GPIO`,
`pinctrl` and `header` found milestone 163's PERST# writes and no GPIO driver.

## Index row

nife has no GPIO driver, and no header pin on radon has changed state under it. A crate for the
JH7110's system pin controller drives a pin, reads one back through a jumper, takes an edge
interrupt, and refuses pins outside a program's grant.
