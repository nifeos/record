# Prior art for a direct virtio grant

An appendix to [the milestone](../1062-the-device-control-planes-leave-the-kernel.md),
the background to its step 7 design. It sits apart so the milestone stays within §212's 3,000
words.

- nife's xHCI driver (milestone 242) holds its register file less the MSI-X pages, and a DMA region
  the kernel confined first. The kernel refuses to start it unconfined (`Absent::Unconfined` in
  `kernel/src/extensible_host_controller_interface.rs`). The NVMe data-path driver holds BAR0's
  doorbell page (`kernel/src/user/non_volatile_memory_express_service.rs`), and step 4 gives the
  admin process the rest of BAR0. A direct virtio driver has the same shape.
- Genode. The platform driver hands a driver its device's I/O memory, an interrupt service with
  the routing applied, and DMA buffers. On NOVA every DMA goes through the IOMMU, keyed by the
  function's bus, device and function, so the device reaches only its DMA buffers (read: Genode
  Foundations 23.05, "Device drivers").
- Linux VFIO. A userspace driver maps the device's regions at the offsets the device descriptor
  lists and receives interrupts through eventfds (`VFIO_DEVICE_SET_IRQS`). The IOMMU group is the
  unit of isolation, because DMA is the greatest risk a userspace driver poses (read:
  docs.kernel.org, "VFIO"). Userspace drives a virtio-pci function bound to `vfio-pci` exactly
  so.
- DPDK's virtio poll-mode driver binds the function to `vfio-pci`, in VFIO's no-IOMMU mode where a
  machine has no IOMMU, which trusts the driver (read: the DPDK guide, "Virtio"). That it maps the
  modern capabilities and writes the common configuration and the doorbells itself comes from
  memory, not from a reading.

nife differs in two ways. A starter chooses the grant per device when the driver starts, not
once per boot or per binding. And a device the starter will not hand over keeps a mediated path whose
validator has a Kani proof.
