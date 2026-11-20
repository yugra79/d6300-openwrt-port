# PORT REPORT — OpenWrt per Netgear D6300 (BCM6362)
Report consolidato · aggiornato al 20/11/2026

---

## 1. EXECUTIVE SUMMARY

Port OpenWrt del **Netgear D6300** (router VDSL/ADSL "N1600").
Dal bootlog catturato via UART è emerso che la piattaforma è **BCM6362B0**
(CFE "for BCM96362", board id 96362ADVN2xh): il port è quindi un **device
del subtarget `bcm6362` esistente**, non un nuovo subtarget.

| Area | Stato |
|---|---|
| Analisi firmware stock | ✅ completata |
| Bootlog UART (console) | ✅ catturato (J252: pad2=GND, pad3=TX) |
| Sviluppo port (bcm6362) | ✅ completo e verificato offline |
| Test su dispositivo | ⏳ primo flash da provare |
| Pubblicazione upstream | 📄 3 patch + cferam pronti |

---

## 2. HARDWARE (dal bootlog e dalle foto)

| Componente | Dato |
|---|---|
| SoC | **BCM6362B0** — MIPS 400 MHz, DDR 333 MHz, bus 166 MHz |
| RAM | 128 MB |
| NAND | **ST NAND512W3A2CN6** — 64 MB, blocchi **16 KB**, pagine **512 B**, ECC 15/512 |
| Switch | interno BCM6362 + **esterno BCM53125** (5 GbE) |
| Porte | lan1-4 + wan (RGMII tra switch interno ed esterno) |
| USB | 2x USB 2.0 (EHCI + OHCI) |
| WiFi 2.4G | **BCM435f** integrato (b43) |
| WiFi 5G | **BCM4360KMLG** su mini-PCIe (BCM94360, PN T77H390T00) — **non supportata** |
| LED | GPIO 4/5/7/10/26/30 + catena seriale 24 LED su GPIO2/GPIO3 |
| MAC base | c4:04:15:18:35:10 (da cferom) |
| Console | UART0 115200 8N1 |
| Bootloader | CFE 1.0.38-112.70, autoboot 1 s, IP 192.168.1.1 |

---

## 3. DATI DAL BOOTLOG (evidenza)

```
BCM6362 Platform Boot Code V1.0.9-4.12L.04
CFE version 1.0.38-112.70 for BCM96362 (32bit,SP,BE)
NAND flash device: name ST NAND512W3A2CN6, id 0x2076 block 16KB size 65536KB
External switch id = 53125
Chip ID: BCM6362B0, MIPS: 400MHz, DDR: 333MHz, Bus: 166MHz
Board Id (0-9): 96362ADVN2xh
Root: 0x1d80000-0x3afc000 "rootfs"; update 0x4000-0x1d80000; data 0x3b00000-0x3f00000
Kernel cmdline: root=mtd:rootfs ro rootfstype=jffs2 console=ttyS0,115200
```
Log completo: `netgear-d6300/boot_D6300_full.log`.

---

## 4. DELIVERABLE DEL PORT (nuova struttura bcm6362)

### Patch series OpenWrt (3 patch, verificate)
```
0001-bmips-add-netgear-d6300-device-tree.patch
0002-bmips-bcm6362-add-netgear-d6300-image.patch
0003-bmips-bcm6362-add-netgear-d6300-base-files.patch
series
```

### File aggiunti (struttura upstream)
```
target/linux/bmips/dts/bcm6362-netgear-d6300.dts
target/linux/bmips/image/bcm6362.mk                       (device netgear_d6300)
target/linux/bmips/bcm6362/base-files/etc/board.d/01_leds
target/linux/bmips/bcm6362/base-files/etc/board.d/02_network
target/linux/bmips/bcm6362/base-files/lib/upgrade/platform.sh
```
### Repo separato bcm63xx-cfe
```
netgear,d6300/cferam   (196.380 byte, estratto dal firmware stock, sha256 baefac12...)
```

### Ricetta immagine (allineata al DGND3700v2)
```
CHIP_ID := 6362
CFE_RAM_FILE := netgear,d6300/cferam.000
CFE_RAM_JFFS2_NAME := cferam.000
CFE_RAM_JFFS2_PAD := 496k
BLOCKSIZE := 16k
PAGESIZE := 512
CFE_WFI_FLASH_TYPE := 2
CFE_WFI_VERSION := 0x5731
DEVICE_PACKAGES += $(USB2_PACKAGES) $(B43_PACKAGES) kmod-leds-bcm6328 kmod-leds-gpio
```

---

## 5. EVIDENZA DI VERIFICA (suite: 11/11)

| # | Verifica | Esito |
|---|---|---|
| 1 | DTS compilato con dtc 1.8.1 (via pcpp) | ✅ exit 0, DTB 11.764 B |
| 2 | Patch applicate fedelmente ai file upstream | ✅ tutte coincidono |
| 3 | Struttura port completa | ✅ |
| 4 | cferam integro | ✅ 196.380 B |
| 5 | Ricetta con parametri corretti | ✅ 16k/512/496k/type2/0x5731 |
| 6 | base-files con case netgear,d6300 | ✅ |
| 7 | Bootlog con dati chiave | ✅ |
| 8 | Vecchio subtarget bcm6361 archiviato | ✅ |
| 9 | Coerenza partizioni DTS (5, no overlap, 64 MB) | ✅ |
| 10 | Capienza partizione wfi (24 MB liberi per UBI) | ✅ |
| 11 | Immagine cfe.bin simulata (cferam.000+WFI tag) | ✅ |

Comando: `python3 netgear-d6300/run_all_checks.py`

---

## 6. LAVORO RESIDUO

| Attività | Come |
|---|---|
| Build completa | Linux/WSL → `port/build_d6300.sh` (target bmips/bcm6362, device netgear_d6300) |
| Primo flash di test | da CFE via seriale (`flashimage`) o recovery Netgear |
| Verifiche sul device | offset MAC in cferom (0x6a0?), layout CFE esatto, tasti reset/WPS, b43 2.4 GHz |
| Pubblicazione upstream | 3 patch OpenWrt + PR bcm63xx-cfe (cferam) |

### Limitazioni documentate
- 5 GHz BCM4360 non supportato (nessun driver mainline) → possibile upgrade futuro
  con scheda mini-PCIe AR9280 (vedi `ESPERIMENTO_MINI_PCIE_5GHZ.md`)
- DSL non supportato (nessun driver mainline)
- 2.4 GHz BCM435f via b43 (da verificare in build)

---

## 7. INDICE

- `README.md` — indice e manutenzione
- `STATO_RICOSTRUZIONE_BCM6361.md` — tutte le scoperte (30 sezioni)
- `ROADMAP_PORT_D6300.md` — fasi e attività
- `INSTALL_BUILD_D6300.md` — build/installazione
- `TEST_PLAN_D6300.md`, `BOOTLOG_WORKSHEET.md` — piano e foglio test
- `DRIVER_MATRIX.md` — compatibili → driver
- `UPSTREAM_PR_DRAFT.md` — bozza PR (OpenWrt + bcm63xx-cfe)
- `ESPERIMENTO_MINI_PCIE_5GHZ.md` — upgrade 5 GHz
- `WIKI_D6300_DRAFT.md` — bozza pagina wiki
