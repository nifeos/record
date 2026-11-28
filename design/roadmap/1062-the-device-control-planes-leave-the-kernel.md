---
status: PARTIAL
raised: 2026-11-10
milestone_dependencies: 811
decision_dependencies: 4, 23, 86, 130, 251, 320
machine_requirements: none
specific_machine: none
needs_person: yes
---
# 1062. The device control planes leave the kernel

*(The number, title and slug are provisional.)*

Reuse: the shape is the tree's own. Milestone 242 (xHCI) already splits a device this way, and
milestone 811 (the boot services leave the kernel) supplies the grants. No outside code fits a
capability split of nife's own kernel, so this lane searched only the tree.

The kernel holds only what must run at EL1 plus what a confinement argument needs (§4 (kernel
shape)), and confinement means an IOMMU (§86 (whether an NVMe driver can leave the kernel)). A
device's control plane is neither. On a machine with an IOMMU the IOMMU confines the device; on a
machine without one nife trusts the driver wherever its control plane runs. So each control plane
the kernel carries today moves to a userspace process, and the kernel keeps only the confinement:
it binds the device's requester id to its DMA region and grants the device's pages.

Ruled 2026-11-10 (UTC). The order follows the dependencies, and each step is one pull request.

- Step 1 waits for milestone 811 (the boot services leave the kernel)'s step 6.
- Step 2 waits on no other work: §320 (the JH7110 clock and reset wire) states its wire.
- Steps 3 and 5 wait for step 2's server.
- Milestone 1064 (PCI enumeration leaves the kernel) follows this milestone and milestone 1068
  (the kernel turns interrupt remapping on where an IOMMU offers it).

## The work, in order

1. e1000e to the xHCI shape, after milestone 811 (the boot services leave the kernel)'s step 6.
   The kernel confines the controller and grants all of BAR0 and the DMA run to a userspace control
   process. That process keeps BAR0's pages 0 and 5 (reset, MAC address, PHY, filters) and grants
   the queue pages to `net_stack`, the shape milestone 242 (xHCI) has for USB. `kernel/src/e1000e.rs` goes,
   and the kernel stops linking `crates/e1000e`. Waiting for 811's step 6 keeps the starter and the
   control plane from moving twice. Ruled 2026-11-28 (UTC). The userspace control process reports
   link asynchronously, as FreeBSD em does, and DHCP waits on that report rather than on a fixed
   deadline.
2. The JH7110 clock and reset server. A userspace server holds the shared clock and reset
   window, which serves USB, PCIe, DMA, the security block and Ethernet. It answers the
   device-level verbs of §320 (the JH7110 clock and reset wire): the badge is the device, and a
   client brings up, reads and rates its own device's clocks and resets and never touches
   another's. No verb turns a device off. The verbs live in a contract crate both sides depend on
   (§311 (a contract is code, not prose)), at interface id 24. The names ship provisional.
   `kernel/src/drivers/jh7110_clock_and_reset.rs` shrinks to what the kernel's own
   JH7110 watchdog (milestone 593 (a wedged kernel resets itself)) needs to turn its clock on, and
   the entropy and Ethernet bring-ups ask the server instead.
   SD/MMC starters and step 5's PMIC route ask it too.
3. The DesignWare GMAC control plane. Its clocks and resets come up through step 2's bring-up
   verb, and a userspace control process holds the channel and MAC pages.
   `kernel/src/designware_ethernet.rs` goes, and `kernel/Cargo.toml` stops naming the crate.
   radon proves it.
4. The NVMe admin plane, as §86 states it: a userspace admin process holds BAR0 and the admin
   queues and grants the data-path driver its doorbell page and I/O queues. The admin half of
   `kernel/src/non_volatile_memory_express.rs` goes. The split keeps §86's option 4 addable.
   Built: #3427.
5. The JH7110 PMIC route, as §251 (restarting the machine is a kernel object the progenitor
   hands out) states it. `components/src/power_management_chip_route.rs` holds the I2C5
   controller's page as a `DeviceFrame` and writes the AXP15060, after its starter brings I2C5 up
   through the step 2 server (§320 (the JH7110 clock and reset wire)). `reboot` calls it, then
   `REBOOT`; the route bounds its wait. The kernel holds no I2C master. radon proves it.
6. The x86 CMOS read, as §130 (how the userspace clock service reads the x86 CMOS RTC) states
   it: the clock service holds a `PortRange` over ports 0x70 and 0x71 and reads the CMOS itself.
   `clock_contract::rtc::CMOS` names the two ports the service reads, and the kernel reads no CMOS.
   Built: #3426.
7. A virtio driver starts with a mediated or a direct grant (§23 (multi-queue DMA confinement)),
   as [its appendix](1062-the-device-control-planes-leave-the-kernel/step-7-virtio-grant.md)
   designs it. Ruled 2026-11-10 (UTC). The appendix lists its four pull requests.

Every new program, process, crate and verb ships with a provisional name.

## Done when

1. None of the files that steps 1, 3, 5 and 6 remove exists, the kernel's clock and reset driver
   serves only its watchdog, and `kernel/Cargo.toml` names neither `e1000e` nor
   `designware_ethernet`.
2. The existing gates for each device pass on every architecture it runs on, with no test weakened.
   That means the e1000e, NVMe and virtio gates under QEMU, the clock tests on `x86_64` with a wall
   clock, and radon's Ethernet and reboot bench boots.
3. `reboot` on radon resets the board through the userspace route. Without it, radon's
   firmware hangs on `REBOOT`'s SBI SRST.
4. `script/fastpath-footprint` reports no change: none of these paths is hot.
5. A virtio-pci driver runs on either grant, each starter grants as the default above states, and
   CI runs the direct and the mediated path on all three architectures.

## Follow-on

- **Done.** Step 4 in #3427 (nifeos/nife@7e45d7269).
- **Done.** Step 6 in #3426 (nifeos/nife@cc48e8b34).
- **Outstanding.** Step 1: `kernel/src/e1000e.rs` exists, and 811 is NOT-STARTED.
- **Done.** Step 2 in #3475: `components/src/jh7110_clock_and_reset.rs`.
- **Done.** Step 3: radon booted it on 2026-11-17 UTC (main `cfe18db337`, `LEASED-AND-MEASURED`, `coherence : Coherent`) and `PROVEN_ON_SILICON` is `true`.
- **Done.** Step 5 in #3499: `components/src/power_management_chip_route.rs`.
- **Outstanding.** A timeout on `reboot`'s call to the route waits on a timed call.
- **Outstanding.** Step 7: the measurement; "Cost and effort" still reads not measured.
- **Outstanding.** An escape test that drives a direct driver (a ring outside its region, a
  declined `VIRTIO_F_ACCESS_PLATFORM`); the mediated
  `the_iommu_faults_a_dma_that_escapes_the_domain` covers that fault today.

## Index row

The kernel still carries the control planes of e1000e, the GMAC, NVMe, the JH7110's clock and
reset block and its PMIC, and reads the x86 CMOS itself. None of that must run at EL1, and none of
it confines DMA, which is the IOMMU's job. This moves each one to a userspace process and takes about 1,500 kernel lines and
two driver crates out of the trusted base. The virtio validator stays for a device granted
mediated, and a starter may grant a virtio-pci device's registers directly behind the IOMMU.
