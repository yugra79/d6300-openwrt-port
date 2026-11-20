# Bozza PR upstream — Netgear D6300 (BCM6362)

Aggiornata al 20/11/2026, dopo il bootlog e la ristrutturazione su bcm6362.

---

## PR 1 — openwrt/openwrt

**Titolo:** `bmips: add support for Netgear D6300`

**Descrizione proposta:**

```
Add support for the Netgear D6300, a BCM6362 based VDSL/ADSL router.

Hardware (from the stock firmware analysis and boot log):
- SoC: BCM6362B0 (MIPS 400 MHz, DDR 333 MHz)
- RAM: 128 MB
- NAND: ST NAND512W3A2CN6 (64 MB, 16 KB blocks, 512 B pages)
- Switch: internal BCM6362 + external BCM53125 (5 GbE ports)
- USB: 2x USB 2.0 (EHCI + OHCI)
- 2.4 GHz: BCM435f (b43)
- 5 GHz: BCM4360KMLG mini-PCIe module - NOT supported (no mainline driver)
- LEDs: internet/giga/lan on GPIO 4/5/7/10/26/30
- Serial console: UART0 at 115200 8N1 (J252 header)

The partition layout is derived from the stock firmware boot log:
cferom, rootfs_update, wfi, flag, data. The CFE boots the image from the
"wfi" area (0x1d80000). The MAC address is read from the cferom partition.

Not supported: DSL modem, 5 GHz BCM4360.
```

**Commit (3, già pronti in `port/openwrt/patches/`):**
1. `bmips: add Netgear D6300 device tree`
2. `bmips: bcm6362: add Netgear D6300 image`
3. `bmips: bcm6362: add Netgear D6300 base-files`

**Da fare prima dell'invio:**
- personalizzare `From:`/`Signed-off-by:` con i propri dati
- testare il build e il flash sul dispositivo
- verificare sul device: offset MAC in cferom (0x6a0), layout CFE esatto,
  tasti reset/WPS, funzionamento b43 2.4 GHz
- aggiornare la pagina wiki con i risultati del test

---

## PR 2 — openwrt/bcm63xx-cfe

**Titolo:** `netgear,d6300: add cferam`

**Descrizione proposta:**

```
Add the CFE RAM image for the Netgear D6300.

The cferam has been extracted from the stock firmware image
(D6300-V1.0.0.102_1.0.102.chk, board id 96362ADVN2xh) and is used by the
bmips bcm6362 image recipe (CFE_RAM_FILE := netgear,d6300/cferam.000).

File: netgear,d6300/cferam.000 (the stock JFFS2 names it cferam.000)
- size: 196380 bytes
- md5: 5b996cd5dc353ac451bc380c0e4d0216
- sha256: baefac12a26889f039275e3f4ba8db44c037a01c0d026b2e445118b502837bcd
- CFE version: 1.0.38-112.70 (BCM96362 platform boot code V1.0.9-4.12L.04)
- note: different from the DGND3700 v2 cferam (253680 bytes)
```

---

## Note per la revisione

- La piattaforma è **BCM6362** (confermato da CFE/chip id nel bootlog): il port
  riusa il subtarget bcm6362 e i driver esistenti.
- Il cferam è specifico del D6300 (estratto dallo stock) e va nel repo bcm63xx-cfe.
- Il 5 GHz BCM4360 non ha driver mainline: limitazione dichiarata.
- Il 2.4 GHz usa b43 con le stesse modalità del DGND3700v2.
- Il layout delle partizioni segue quello osservato nel bootlog stock; eventuali
  correzioni dopo il test sul device andranno in un follow-up.
