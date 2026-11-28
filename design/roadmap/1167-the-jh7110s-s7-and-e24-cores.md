---
status: NOT-STARTED
raised: 2026-11-28
milestone_dependencies: none
decision_dependencies: none
machine_requirements: JH7110 silicon
specific_machine: radon (the only JH7110 board this project has)
needs_person: yes
---
# 1167. The JH7110's two small cores: the S7 monitor hart and the E24

*(The number, the title and the slug are provisional.)*

Raised 2026-11-28 (UTC) by lane `lane/radon-unexercised-hardware`. On that date calef asked for a
milestone for every part of the VisionFive 2 that nife has not yet exercised on the board, and
this is one of them.

## What is unexercised

nife runs on the four U74 harts and on nothing else. The chip has two more cores.

- The S7, hart 0. nife refuses to start it, by design: the kernel needs supervisor mode and an MMU,
  and the S7 has neither. `notes/visionfive2.md` ("Harts, and what the bench stops found") records
  why, and records that vendor OpenSBI dies when asked to start it.
- The E24, a 32-bit core that no device tree lists among the cpus. Nothing in nife names it.

The open question for each is whether a small program that is not the kernel could use it, and
for what.

## The hardware, from primary sources

- Mainline Linux `jh7110.dtsi` (`torvalds/linux` `cbbddb6b08cc`): `S7_0: cpu@0`, compatible
  `sifive,s7`, `riscv,isa = "rv64imac_zba_zbb"`, no `mmu-type`, `status = "disabled"`. The U74s
  carry `mmu-type = "riscv,sv39"` and `rv64imafdc_zba_zbb`.
- The StarFive JH7110 datasheet (v1.63, JH7110-DSEN-001), section 2.1: the S7 is RV64IMAC with a
  16 KB instruction cache, an 8 KB DTIM and 8-region PMP, fully coherent with the U74s. Its note
  says "S7 is only used for BOOTROM".
- The same datasheet, section 2.1.3: the E24 is RV32IMFC with a 16 KB instruction cache, 4-region
  PMP and a CLIC of up to 127 interrupts.
- StarFive's vendor tree (`starfive-tech/linux` `JH7110_VisionFive2_devel` at `6d6aee034b81`):
  `co_process: e24@0`, compatible `starfive,e24`, with a command window at `0x6e21_0000`, mailbox
  channels to the U74s, and `firmware-name = "e24_elf"`. Mainline has no E24 node.
- Unverified: which privilege modes the S7 implements beyond machine mode. PMP suggests user mode,
  but no source read here says so.

## What it needs

- A firmware question first. OpenSBI owns machine mode on the S7's peers, and the vendor build
  dies starting the S7. A program on the S7 needs either OpenSBI's cooperation or a firmware that
  leaves the S7 alone and lets the kernel release it some other way. Reading how the boot ROM parks
  the S7 is the first step.
- A use. Candidates, none chosen: a watchdog or health monitor that keeps running when the U74s
  wedge, a power sequencer, or a tight real-time loop. The E24's CLIC and mailbox suit an offload
  engine for one device.
- Confinement. Both cores are bus masters with no IOMMU between them and memory. A program on
  either one can reach all of physical memory, as firmware can. The block states that plainly
  and treats any such program as part of the trusted computing base.

## Done when

On radon, nife's kernel on the U74s starts one small program on the S7 or the E24, sends it a
message, and reads a reply that only that core could have produced. The log goes under nife's
`bench/radon-<date>/`. A finding that neither core starts without new firmware also
closes the block, as a recorded refusal with its evidence.

## Prior art

- Linux leaves the S7 disabled in its tree and does not start it. StarFive's vendor kernel drives
  the E24 with an out-of-tree driver (`starfive,e24`) that loads an ELF and talks over the mailbox,
  the shape Linux's `remoteproc` framework gives other auxiliary cores.
- Microchip's PolarFire SoC has the same shape, an RV64IMAC monitor core beside four
  application cores. Its Hart Software Services run in machine mode on that monitor core and boot
  the others. That is from Microchip's public documentation, and this lane did not check it.
- Where nife differs: nife would not run its kernel there. A program on either core is firmware in
  all but name, and the record says so rather than calling it confined.

Reuse: none exists. A search of the roadmap for `S7`, `E24`, `e24` and `monitor core` found only
`notes/visionfive2.md`'s refusal and milestone 239 (radon's device tree does not describe the TRNG)
reading the vendor tree.

## Index row

The JH7110 has an RV64IMAC S7 monitor hart and an RV32 E24 core beside its four U74s, and nife uses
neither. The block finds whether a small program, not the kernel, can run on either, and what it
would do there.
