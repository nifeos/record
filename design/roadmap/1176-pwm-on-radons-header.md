---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: 1173
decision_dependencies: none
machine_requirements: a VisionFive 2 with a jumper from header pin 32 to pin 31
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1176. PWM on radon's header: one channel, measured

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. On that date calef asked for a
milestone for every part of the VisionFive 2 that nife has not yet exercised on the board, and
this is one of them.

## What is unexercised

The JH7110's eight PWM channels. nife has no PWM driver, and the header's two PWM pins have never
carried a waveform. The PWMDAC is a separate audio block and belongs to milestone 1172 (audio on
radon).

## The hardware, from primary sources

- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), section 2.9.10: eight PWM interfaces,
  each a 32-bit counter with single-run and continuous modes, PWM mode, high and low reference and
  capture registers, and an interrupt.
- Mainline Linux `jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`): eight nodes `pwm0` to `pwm7`,
  the first at `pwm@120d0000`, compatible `starfive,jh7110-pwm` and `opencores,pwm-v1`, clocked by
  `JH7110_SYSCLK_PWM_APB`. The VisionFive 2 tree puts channel 0 on GPIO 46 and channel 1 on
  GPIO 59, header pins 32 and 33 in the VisionFive 2 datasheet's table 5-1.
- At that mainline revision `drivers/pwm` has no driver that matches either compatible string;
  only the binding exists. StarFive's vendor tree (`starfive-tech/linux` at `6d6aee034b81`) has one
  node, `ptc: pwm@120d0000`, compatible `starfive,jh7110-pwm`, and its own driver.

## What it needs

- A PWM crate for the counter: period, duty, enable and the output enable, from the datasheet and
  the vendor driver, with the vendor driver's register names checked against the binding's
  OpenCores name.
- The PWM clock and reset, and the two pins through milestone 1173 (general-purpose I/O on radon's
  40-pin header).
- A person, to fit one jumper from pin 32 (PWM channel 0) to pin 31 (GPIO 39) with the board
  powered off.

## Done when

On radon, PWM channel 0 drives pin 32 at 1 kHz with a 25 percent duty cycle. A program reads the
waveform back on GPIO 39 through edge interrupts and timestamps each edge with the timer. The
measured period lies within 1 percent of 1 millisecond and the high time within 1 percent of 250
microseconds, over ten thousand periods. The same check then runs at 75 percent. The log goes under
nife's `bench/radon-<date>/`.

## Prior art

- Linux: no mainline driver at `cbbddb6b08cc`. StarFive's vendor kernel drives the block as
  `starfive,jh7110-pwm` and serves the `pwm` class in sysfs.
- No driver for this block appears in OpenBSD's or FreeBSD's JH7110 support
  (`sys/arch/riscv64/dev` and `sys/riscv/starfive`, read for this block).
- Where nife differs: a program holds one channel and its pin by grant, and the block measures
  its output rather than trusting the register writes.

Reuse: milestone 1173's pin crate and its edge interrupt. A search of the roadmap for `PWM` found
the PWMDAC only in this lane's milestone 1172.

## Index row

The JH7110's PWM channels have never carried a waveform under nife. A small crate drives channel
0 on the header, and a jumper back to a GPIO measures its period and duty cycle within 1 percent.
