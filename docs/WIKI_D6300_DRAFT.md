# Netgear D6300

*Netgear D6300 (N1600 Wireless Dual Band Gigabit DSL Router)*

## Support status

| Feature | Status |
|---|---|
| SoC | BCM6362B0 (BMIPS4350, 2x 400 MHz) |
| RAM | 128 MB |
| NAND | 64 MB (ST NAND512W3A2CN6, 16 KB blocks, 512 B pages) |
| Switch | BCM6362 (internal) + BCM53125 (external), 4x LAN + 1x WAN |
| USB | 2x USB 2.0 |
| 2.4 GHz | BCM435f (b43) - to be verified |
| 5 GHz | BCM4360 mini-PCIe - **not supported** (no mainline driver) |
| DSL | not supported |
| Serial console | UART0, 115200 8N1, J252 pads (pad 2 = GND, pad 3 = TX) |

## Installation

1. Open the case and locate the J252 4-pad header on the main board
   (2 = GND, 3 = TX at 115200 8N1).
2. Connect a 3.3 V USB-TTL adapter (GND -> pad 2, adapter RX -> pad 3).
3. Configure the CFE (boot delay 1 s): interrupt with a key on the console
   (adapter TX -> pad 1 or 4) and use TFTP at 192.168.1.1 / host 192.168.1.100.
4. Flash the OpenWrt image (see the image recipe: kernel + cferam.000 JFFS2
   + UBI rootfs + WFI tag).

## Known limitations

- 5 GHz (BCM4360) unsupported: no mainline driver. A supported mini-PCIe
  card (e.g. Atheros AR9280, ath9k) can replace it for 5 GHz 802.11n.
- DSL modem unsupported.
- 2.4 GHz support depends on b43 for the integrated BCM435f.

## Partition layout (from the stock boot log)

```
cferom          0x0000000 - 0x0004000  (MAC address)
rootfs_update   0x0004000 - 0x1d80000
wfi             0x1d80000 - 0x3afc000  (OpenWrt image)
flag            0x3afc000 - 0x3b00000
data            0x3b00000 - 0x3f00000
```
