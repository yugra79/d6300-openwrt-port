# RICOSTRUZIONE STATO BCM6361 / BMIPS — NETGEAR D6300

> NOTA: il titolo conserva "BCM6361" per continuita' storica del progetto.
> Dal §27 (bootlog, 20/11) la piattaforma reale e' risultata **BCM6362**; il port
> e' stato ristrutturato di conseguenza (vedi §28-30).

Data: 19/11/2026 · Fase: analisi completata, port in costruzione

## 1. HARDWARE (fonte: TechInfoDepot + autopsia 06/11/2026)
| Componente | Dato | Fonte |
|---|---|---|
| SoC | Broadcom **BCM6361** (BMIPS4350, 2x400 MHz) | autopsia |
| RAM | 128 MB | wiki |
| Flash | 128 MB **NAND** | analisi firmware (cferam) |
| Chip NAND | **Micron MT29F1G08AAC** (1 Gbit) | stringa nel cferam del .chk |
| Geometria NAND | **pagina 2 KB, blocco 128 KB, ECC 512B/15** | MT29F1G08AAC + template openwrt |
| Radio 2.4 GHz | integrata (BCM2057, 2x2 b/g/n) | wiki |
| Radio 5 GHz | **BCM4360 su Mini-PCIe** (modulo con CPU propria) | wiki/autopsia |
| Porte | 1 WAN + 4 LAN **GbE** | wiki |
| USB | 2x USB 2.0 | wiki |
| Default IP | 192.168.0.1 | stock |
| Board ID stock | **U12L216T00_NETGEAR** | header .chk |

## 2. FIRMWARE STOCK ANALIZZATO (.chk, 24,72 MB)
File: `D6300-V1.0.0.102_1.0.102.chk`
- md5 `690133d053e7490eff60954e089aa0ae`
- Header Netgear CHK: magic `0x2A23245E`, header_len `0x3A` (58), payload 25.919.508 byte
- board_id: `U12L216T00_NETGEAR`
- checksum campo 0x10 = 0xCF31D07B (uguale al campo 0x20)

**Struttura payload** (analisi `analyze_payload.py`):
```
0x0000  cferam (CFE bootloader, MIPS big-endian)
0x0104  firma "CFE1CFE1" (versione CFE)
0x0098  nome "cferam.000" nel tag cferam
0x1CC0B kernel LZMA (vmlinux.lz)  [candidato, decompressione da rifinire]
0x39609 rootfs JFFS2 (nodi 0x1985)
```
**Stringhe CFE rilevanti** (prova del supporto NAND e del layout):
- "NAND flash device", "NAND_RFS_OFS", "Erase NAND flash", "flashimage"
- "rootfs1 offset=0x..., size=0x..." / "rootfs2 offset=..." → **doppia rootfs**
- "Total Flash size: %dK with %d sectors"
- "ERROR: NAND flash block size %dKB does not work with an image built with %dKB block size"
- "MT29F1G08AAC" (chip NAND) + tabella anche K9F5608U0, NAND01GW3B2CN6, NAND512W3A2CN6
- "vmlinux.lz" → kernel LZMA, esattamente come si aspetta CFE

**Conclusione firmware**: il D6300 usa lo schema NAND Broadcom standard (cferam + kernel LZMA + JFFS2 dual-rootfs). Nessun squashfs/cramfs/UBI nello stock.

## 3. STATO OPENWRT (verificato su master, 19/11/2026)
`target/linux/bmips/Makefile`:
```
SUBTARGETS:=bcm6318 bcm6328 bcm6358 bcm6362 bcm6368 bcm63268
KERNEL_PATCHVER:=6.18
```
- **bcm6361 NON esiste** in bmips.
- **bcm6361 NON è mai esistito** nemmeno nel vecchio target `bcm63xx` (verificato v17.01/v18.06/v19.07: nessun file bcm6361.dtsi / bcm6361.mk / DGND4000).
- Quindi: **non è una "riesumazione"** ma un **nuovo subtarget** da aggiungere, modellato su bcm6362.
- Piattaforma più vicina: **BCM6362** (Netgear DGND3700v2 è il device di riferimento: stesso vendor, stessa generazione, NAND, dual-band con 5G su mini-PCIe).

### Driver disponibili per un SoC 6361 (kernel 6.18 + patch bmips)
| Blocco | Compatible/uso bmips | Driver kernel | Note 6361 |
|---|---|---|---|
| CPU | brcm,bmips4350 | arch/mips/bmips | stesso core del 6362 ✓ |
| Clock | brcm,bcm6362-clocks | clk-bcm63xx | probabile identico (verificare) |
| Reset | brcm,bcm6345-reset | reset-bcm6345 | ✓ |
| IRQ L1/ext | brcm,bcm6345-l1-intc / ext-intc | ✓ (patch 100) | ✓ |
| GPIO | brcm,bcm6362-gpio | gpio-bcm63xx | probabile identico |
| Pinctrl | brcm,bcm6362-pinctrl | pinctrl-bcm6362 | **driver 6361 assente**: usare 6362 o aggiungere patch |
| UART | brcm,bcm6345-uart | serial-bcm63xx | ✓ |
| Watchdog | brcm,bcm7038-wdt | bcm7038_wdt | ✓ |
| NAND | brcm,nand-bcm6368 + brcmnand-v2.2 | brcmnand/bcm6368_nand.c | ✓ (MT29F1G08AAC 2K/128K) |
| Ethernet | brcm,bcm6362-enetsw | patch 500 bmips | probabile identico |
| Switch | brcm,bcm6362-switch (+ b53 se esterno) | dsa b53 | **da verificare**: switch integrato o BCM53125? |
| PCIe | brcm,bcm6328-pcie | pcie-bcm6328 | serve per il 5G BCM4360 |
| USB | brcm,bcm6362-ehci/ohci/usbh-phy | usb-ehci/ohci + phy-bcm63xx-usbh | ✓ |
| LED | brcm,bcm6328-leds | leds-bcm6328 | ✓ |
| RNG | brcm,bcm6368-rng | bcm63xx-rng | ✓ |
| DSL | — | **nessun driver** (come tutti i bmips) | modem DSL NON supportato: usare WAN Ethernet |

## 4. COSA MANCA PER COMPLETARE (dati da reperire SUL DEVICE)
1. **Boot log seriale CFE** (UART, 115200 8N1): board ID, flash geometry, versione WFI, partizioni
2. **`/proc/mtd`** (da shell stock) → mappa partizioni reale (128 MB NAND)
3. GPIO di LED e pulsanti (da dmesg stock o dal CFE)
4. Modello switch: integrato (bcm6362-switch) o esterno BCM53125 (b53)
5. Verifica WFI version (`CFE_WFI_VERSION`) e flash type (`CFE_WFI_FLASH_TYPE`)
6. cferam: estrarre il file `cferam` dal .chk (o dump da /dev/mtd) per CFE_RAM_FILE

## 5. FILE PRODOTTI IN QUESTA FASE
- `analyze_stock.py` / `analyze_payload.py` → analisi .chk e payload
- `stock_payload.bin` → payload estratto (24,72 MB)
- `openwrt_ref/` → file di riferimento bmips (Makefile, bcm6362.mk, bcm6362.dtsi, DGND3700v2 dts, config-6.18)
- `port/openwrt/` → file del port pronti da incollare nel tree OpenWrt
- `port/ROADMAP_PORT_D6300.md` → roadmap completa
- `port/PROPOSTA_UPSTREAM.md` → proposta per la community

## 6. APPROFONDIMENTO JFFS2 (round 8, 19/11/2026)
Il payload del .chk è un **filesystem JFFS2 completo** (rootfs stock) con dentro
**vmlinux.lz** e **cferam.000** come file:
- Formula CRC JFFS2 verificata: hdr_crc = crc32(header[0:8], 0xFFFFFFFF) ^ 0xFFFFFFFF
- Nodi validati (CRC ok): 15.902, dirent 1.572, inode 587 (su 24,7 MB)
- Il JFFS2 contiene la struttura rootfs standard: bin, data, dev, etc, include,
  lib, linuxrc, mnt, opt, proc, sbin, sys, tmp, udev, usr, var
  + **cferam.000** (ino 3) + **vmlinux.lz** (ino 19)
- I file sono compressi (zlib/lzma) nei nodi inode
- Nota: la versione stock del formato inode ha header 68 byte (senza node_crc),
  che ha richiesto un parser dedicato (parse_jffs2_final.py)

**Conseguenza per il port**: il .chk stock NON è un'immagine flash completa ma
il rootfs (con kernel/cferam come file usati dal processo di upgrade Netgear).
L'immagine OpenWrt va quindi scritta via **CFE (serial/tftp flashimage)** oppure
adattando il formato .chk per il sysupgrade — vedi INSTALL_BUILD_D6300.md.

### 6.1 FILE ESTRATTI CON SUCCESSO (round 10)
| File | ino | Dimensione | Note |
|---|---|---|---|
| **cferam.000** | 3 | **196.380 byte** | CFE bootloader: inizia con codice MIPS, contiene `CFE1CFE1`, `Broadcom`, `flashimage`, `NAND_RFS_OFS` |
| **vmlinuz** | 485 | **4.149.763 byte** | kernel LZMA → decompresso 6.487.264 byte |
| **kernel (decompresso)** | - | 6.487.264 byte | **Linux version 2.6.22** (gcc 4.2.3, build 25/10/2014) |
| vmlinux.lz | 19 | 1.500.213 byte | immagine kernel con header CFE (load 0x80010000) |
| busybox, bash, PNG/GIF web UI | vari | - | conferma correttezza estrazione |

### 6.1-BIS COMANDI CFE ESTRATTI DAL CEFRAM DEL D6300
Dal binario `cferam` (196.380 byte) sono state estratte le descrizioni dei comandi:
`flashimage` (flash immagine compressa), `chkw` (scrive un .chk Netgear),
`f` (scrive immagine via tftp), `w` (immagine intera), `e` (erase NAND/nvram),
`d` (dump memoria/registri), `s` (set), `boardid` (board parameters),
`nvram` (erase persistent). Prompt: Board Id, MAC (1-32), Base MAC, PSI size,
Backup PSI, System Log Size, Main Thread, Device Pin, Voice Board Config.
Vedi `TEST_PLAN_D6300.md` §5 per la tabella completa.

### 6.2 PROVENIENZA CFE_RAM_FILE (per la build)
Il file cferam NON sta nel tree OpenWrt: il package `package/kernel/bcm63xx-cfe`
clona il repo **https://github.com/openwrt/bcm63xx-cfe** e lo installa in
`$(STAGING_DIR_IMAGE)/bcm63xx-cfe/`.
- Riferimento: `netgear,dgnd3700-v2/cferam` = 253.680 byte
- **Nostro estratto**: `netgear,d6300/cferam` = **196.380 byte**
- File già collocato in: `port/openwrt/bcm63xx-cfe/netgear,d6300/cferam`
- Per il build locale: copiarlo in
  `staging_dir/target-*/image/bcm63xx-cfe/netgear,d6300/cferam` (dopo il primo
  build del package) oppure usare un package source locale
- Per l'upstream: serve una PR al repo `openwrt/bcm63xx-cfe` che aggiunge la
  cartella `netgear,d6300/` con il file `cferam`

## 7. ANALISI ROOTFS STOCK (round 14, 19/11/2026)
Scoperto che nel JFFS2 stock `compr=6` significa **zlib** (non LZO) -> estrazione
completa riuscita: **979 file, 42,5 MB** in `netgear-d6300/stock_rootfs/`.

### File chiave trovati
| File | Contenuto |
|---|---|
| `board_data` (128 KB) | board ID `U12L216T00_NETGEAR`, MAC **00:14:bf:00:76:54** e **...:55**, SSID default, serial |
| `gpio_test.sh` | **sled_clk_pin=2, sled_data_pin=3, cnt=24**, colori green/amber/red/blue |
| `sbin/acos_service` | gestione LED (`ledup/leddown/ledgreenup/ledredup/ledblueup/ledamberup`), stringa modello **"N1600 Wireless Dual Band Gigabit DSL Router D6300"** |
| `usr/sbin/heartbeat` | `setInternetLedState`, `blink_internet_led`, `/dev/gpio_drv` |
| `bcm6362_map.bin` | mappa board della famiglia 6362 (conferma strategia DTS "6362-compatible") |
| `wl.ko`, `bcm_enet.ko`, `bcmvlan.ko`, `ethswctl` | stack proprietario Broadcom (stock) |
| nvram vars | `lan_hwaddr`, `wan_hwaddr`, `wan_hwaddr2`, `wla_preset_ssid` (2.4G), `wlg_preset_ssid` (5G), `wl0/wl1_wps_config_state` |

### Conseguenze per il port
- Serial LED: parametri **confermati** (gpio2/gpio3, 24 output) -> già nel DTS
- MAC: posizione in flash da verificare (nvmem-cells) — TODO device test
- WiFi: driver Broadcom proprietari (wl.ko) -> 2.4G integrata e 5G BCM4360 NON supportati da OpenWrt mainline
- Switch/VLAN: stock usa bcm_enet+bcmvlan -> OpenWrt usa enetsw/DSA (differenza attesa)


### 7.1 RETE E SWITCH — CONFERMATI DAL NVRAM STOCK (round 15)
Dal file `/etc/nvram` del rootfs (default nvram Netgear):
```
lan_ifname=br0
lan_ifnames=eth0 eth1 eth2 eth3 wl0 eth5
lan_hwaddr=00:14:BF:00:76:54
wan_ifname=eth4
wan_ifnames=atm0
wan_hwaddr=00:14:BF:00:76:55
```
=> **eth0..eth3 = LAN1..4**, **eth4 = WAN**, eth5/wl0 = bridge aggiuntivi.
=> MAC LAN/WAN confermati (già nel board_data).

**Chip switch**: dal rootfs stock risultano **173 occorrenze di "bcm53115"**
(vs 1 di "53125") => il D6300 usa un **BCM53115** (5 porte GbE), NON un BCM53125
come il DGND3700v2. Il DTS è stato corretto a `compatible = "brcm,bcm53115"`.

**Porte switch** (da `/etc/soft_bridge`): porte 0-7 mappate a VLAN bit 0x01..0x80,
**CPU port 8 = 0xFF**. Coerente con b53 (port@8 = CPU).


## 8. MODELLO DI BOOT E PARTIZIONI DEL CFE (round 16)
Stringhe estratte dal cferam del D6300:
```
boot    offset=0x%8.8lx, size=0x%8.8lx
rootfs1 offset=0x%8.8lx, size=0x%8.8lx
rootfs2 offset=0x%8.8lx, size=0x%8.8lx
NAND_RFS_OFS
```
=> modello **Broadcom NAND**: cferam (JFFS2 con cferam.000) + **boot** (kernel)
+ **rootfs1** + **rootfs2** (dual image con fallback: "Booting from previous/latest image").

Altri elementi del CFE:
- **Boot delay (0-9 secondi)** configurabile -> per interrompere il boot
- **Boot image**: 0=latest, 1=previous (dual image)
- Bootline default: `e=192.168.1.1:ffffff00 h=192.168.1.100 ... f=vmlinux i=bcm963xx_fs_kernel`
  (attenzione: IP CFE recovery **192.168.1.1**, diverso dallo stock 192.168.0.1)
- Comandi: `f` (tftp), `flashimage`, `w` (whole image), `chkw` (.chk), `e n/p/a`, `erasenvram`
- Supporto upload via **web CFE** e **NMRP** (Netgear recovery)
- Controllo dimensione blocco: rifiuta immagini con block size diverso (128KB atteso)


## 9. VALIDAZIONE MODELLO JFFS2 vs RICETTA OPENWRT (round 18)
La ricetta OpenWrt `cfe-jffs2-cferam` (target/linux/bmips/image/Makefile) crea
una partizione JFFS2 con questo layout (commento upstream):
```
1) 1-openwrt   (version 0, ino 2)
2) cferam.000  (version 1, ino 3)
```
**Confronto con il firmware stock del D6300** (dirent JFFS2 estratti):
| Voce stock | pino | version | ino | tipo |
|---|---|---|---|---|
| `bin` (primo entry, dummy) | 1 | **0** | **2** | dir |
| `cferam.000` | 1 | **1** | **3** | file |
| `vmlinux.lz` | 1 | 17 | 19 | file |

=> La partizione cferam dello stock **coincide esattamente** con quella generata
da OpenWrt: dummy version 0 ino 2, cferam.000 version 1 ino 3. Questo conferma
che la ricetta `cfe-jffs2-cferam` è corretta per il D6300.

Inoltre il CFE cerca in JFFS2:
- `cferam.000` per il bootloader RAM
- `vmlinux.lz` per il kernel
- errore "A JFFS2 directory entry for %s was not found" se mancano
=> il modello di boot coincide con quello del target bmips (`cfe-jffs2-cferam`
+ `cfe-jffs2-kernel` + rootfs UBI).


## 10. FORMATO .CHK NETGEAR E WFI TAG (round 19)
### Header .chk (da `firmware-utils/src/mkchkimg.c`)
```
offset  campo            stock D6300            mkchkimg
0x00    magic            0x2A23245E             0x2A23245E
0x04    header_len       0x3A (58)              0x39 (57) = 40+strlen(board_id)
0x08    reserved[8]      01 01 00 00 66 01 00 66 region + versione 1.0.0.102_1.0.102
                         (region=1, A=1,B=0,C=0,D=102,E=1,F=0,G=102)  |  mkchkimg: region + 99
0x10    kernel_chksum    checksum Netgear        checksum
0x14    rootfs_chksum    0                       0
0x18    kernel_len       0x018B8014 (25.919.508) dimensione
0x1C    rootfs_len       0                       0
0x20    image_chksum     0xCF31D07B              checksum
0x24    header_chksum    0x41AE0C44              checksum
0x28    board_id         "U12L216T00_NETGEAR"    (senza NUL, mkchkimg)
```
**Checksum Netgear**: somma a 16 bit (c0/c1) — vedi `netgear_checksum_*` in mkchkimg.c.

**Differenze stock vs mkchkimg**: header_len 58 vs 57 (NUL finale) e versione
reale vs 99.99... => un .chk generato con mkchkimg potrebbe NON essere accettato
dal web UI stock (da testare). Il flash via **CFE seriale** resta il metodo sicuro.

### WFI tag (da `scripts/cfe-wfi-tag.py`)
```
u32 crc32 (JAM CRC32: ~crc32 & 0xFFFFFFFF)
u32 version   0x5700 any | 0x5731 NAND con partizione dati 1MB | 0x5732 normal
u32 chipID    0x00006361 = BCM6361 (il nostro)
u32 flashType 1=NOR, 2=NAND 16k, 3=NAND 128k, 4=NAND 256k, ...
u32 flags     0x1 PMC, 0x2 Secure BootROM
```
=> **CFE_WFI_FLASH_TYPE corretto a 3** (NAND 128KB) nella ricetta immagine.


## 11. VALIDAZIONE DTS CON WARNING ESTESI (round 20)
Compilazione con dtc 1.8.1 e warning dtbs_check:
`unit_address_vs_reg, simple_bus_reg, avoid_default_addr_size,
avoid_unnecessary_addr_size, unique_unit_address, interrupt_provider,
interrupts_property, address_cells_is_cell, size_cells_is_cell`

| Target | Exit | Warning |
|---|---|---|
| **Nostro D6300** | 0 | **2** (nandcs, switch — ereditati dalla struttura bcm6362) |
| **Reference upstream DGND3700v2** | 0 | **2** (identici) |

=> Qualità del DTS **equivalente** a quella di un device già accettato upstream.
I 2 warning sono comuni a tutti i device bcm6362 e non bloccanti.

Nota: `interrupt_cells_is_cell` e `compatible_is_string` non esistono in dtc 1.8.1.


## 12. ARTEFATTI DI BUILD GENERATI E VERIFICATI OFFLINE (round 22)
Con `build_artifacts.py` sono stati prodotti e validati i componenti che la build
userà, senza bisogno di toolchain:

### 12.1 WFI tag (port/build_test/wfi_tag.bin, 20 byte)
```
crc32 (JAM) = 0xAA4347C3  (sul payload demo)
version     = 0x00005731  (NAND con partizione dati 1MB)
chipID      = 0x00006361  (BCM6361)
flashType   = 3           (NAND 128k blocks)
flags       = 0
```
Reverse-parse verificato: tutti i campi tornano.

### 12.2 JFFS2 cferam partition (port/build_test/cferam.jffs2)
Generata in Python con layout **standard mkfs.jffs2**:
- root inode (ino 1) + dirent `1-openwrt` (ino 2, version 0) + inode
- dirent `cferam.000` (ino 3, version 1) + inode con i 196.380 byte del CFE
- 52 nodi, 200.084 byte, ogni nodo con hdr_crc/node_crc/data_crc calcolati
**Roundtrip**: parser indipendente ricostruisce il cferam **identico byte-per-byte**
all'originale e conferma le versioni dirent v0/v1 richieste dal CFE.

=> Il layout della partizione cferam che il CFE si aspetta è **pienamente compreso
e riproducibile**; la build OpenWrt userà mkfs.jffs2 con lo stesso layout
(cfe-jffs2-cferam già lo fa: dummy + cferam.000).


## 13. REVIEW RICETTA IMMAGINE (round 23)
Correzioni applicate a `image/bcm6361.mk`:

### 13.1 CFE_RAM_JFFS2_PAD rimosso
Il DGND3700v2 (NAND con blocchi **16k**) usa `CFE_RAM_JFFS2_PAD := 496k`
= 31 blocchi ✓. Il D6300 ha blocchi **128k**: 496k = 3.875 blocchi → NON
allineato, quindi il pad è stato **rimosso**, seguendo il device 128k-NAND
di riferimento upstream (Huawei HG253s v2) che non lo usa.
TODO: se il boot richiede un offset, usare un multiplo di 128k (512k, 640k).

### 13.2 Pacchetti wireless rimossi
`$(B43_PACKAGES)` era improprio: la 2.4 GHz del BCM6361 è integrata con driver
proprietario (`wl.ko`) e la 5 GHz è un BCM4360 su mini-PCIe. Nessuna delle due
è supportata da mainline → rimossi dal recipe (device senza WiFi come altri bmips).

### 13.3 Parametri finali ricetta
| Variabile | Valore | Fonte |
|---|---|---|
| BLOCKSIZE | 128k | MT29F1G08AAC |
| PAGESIZE | 2048 | MT29F1G08AAC |
| SUBPAGESIZE | 512 | MT29F1G08AAC |
| VID_HDR_OFFSET | 2048 | NAND 2KB |
| CFE_RAM_FILE | netgear,d6300/cferam | estratto dal .chk |
| CFE_RAM_JFFS2_NAME | cferam | CFE stock |
| CFE_RAM_JFFS2_PAD | *(nessuno)* | coerenza 128k |
| CFE_WFI_FLASH_TYPE | **3** | cfe-wfi-tag.py |
| CFE_WFI_VERSION | 0x5731 | TODO boot log |
| CHIP_ID | 6361 | → WFI chip 0x6361 |


## 14. MATRICE DRIVER VERIFICATA (round 24)
Ogni compatible del DTS è stato confrontato con i sorgenti reali
(kernel master + file/patch del target bmips). Risultato completo in
DRIVER_MATRIX.md. In sintesi:
- **Tutti** i compatibili hanno un driver o una gestione verificata
- enetsw e pcie-bcm6328 sono forniti dai **file** del target bmips
  (non mainline) — verificato: cm6368-enetsw.c registra rcm,bcm6362-enetsw
- switch interno rcm,bcm6362-switch -> **b53_mmap.c** (DSA)
- switch esterno rcm,bcm53115 -> **b53_mdio.c**
- rcm,bcm6362-gpio-sysctl è un syscon (nessun driver dedicato necessario)
- rcm,wfi gestito dal mtdsplit OpenWrt (CONFIG_MTD_SPLIT_BCM_WFI_FW=y)
- unico punto aperto: rcm,bcm6368-rng (opzionale, non blocca il boot)


## 15. DRIFT CHECK vs MASTER (round 25)
Confrontati i riferimenti usati per il port con OpenWrt master attuale:
| Riferimento | Esito |
|---|---|
| target/linux/bmips/Makefile | IDENTICO (506 byte) |
| dts/bcm6362.dtsi | IDENTICO (13.315 byte) |
| image/bcm6362.mk | IDENTICO (1.177 byte) |
| dts/bcm6362-netgear-dgnd3700-v2.dts | IDENTICO (4.448 byte) |
| bcm6362/config-6.18 | IDENTICO (7.950 byte) |
| bcm6362/target.mk | IDENTICO (199 byte) |

=> **Nessun drift**: il port è basato sullo stato attuale di master e non
richiede aggiornamenti. Script: `drift_check.py` (da rieseguire prima di ogni PR).

Aggiunta anche la **PR separata per il repo bcm63xx-cfe** (cferam) in
`UPSTREAM_PR_DRAFT.md` e la sezione manutenzione nel README.


## 16. HEADER KERNEL E LAYOUT IMMAGINE VERIFICATI (round 26)
### 16.1 Header kernel
`vmlinux.lz` del firmware stock = formato **cfe-bin-header.py**:
```
struct.pack('>III', entry_addr, load_addr, size)
stock: entry=0x80010000  load=0x803575B0  size=1.500.201 (dimensione LZMA)
```
Conferma che l'immagine OpenWrt generata con `cfe-bin-header.py`
(cfe-jffs2-kernel) usa lo stesso header che il CFE del D6300 si aspetta.

### 16.2 Layout immagine (simulato e verificato)
Con `simulate_image_layout.py` (kernel stock come stand-in) è stata prodotta
un'immagine CFE completa e verificata:
```
0x00000000  kernel JFFS2 (con vmlinux.lz + header)     1.500.660 B
0x00000168  dirent "vmlinux.lz" / 0x1BC header kernel
0x00500000  cferam JFFS2 (KERNEL_SIZE = 5 MB)            200.084 B
0x00530D94  WFI tag (crc JAM, chip 0x6361, flash 3)           20 B
0x00530DA8  fine (5,19 MB)
```
Verifiche: magic JFFS2, header kernel (entry 0x80010000), cferam a 5MB,
WFI tag con CRC valido ✓ — mappa in `build_test/LAYOUT_MAP.txt`.
Nella build reale: kernel OpenWrt al posto dello stock e UBI rootfs dopo il cferam.


## 17. CONFIG KERNEL VERIFICATO + SCRIPT DI BUILD (round 27)
### 17.1 Kernel config (bcm6361/config-6.18)
Verificati tutti i simboli necessari per i blocchi del DTS: CPU BMIPS4350, SMP,
irq L1/ext, clock gate, reset, pinctrl 6362/63xx, gpio, UART+console, watchdog,
brcmnand+BCM63XX, UBI/UBIFS, enetsw, b53 mdio+mmap, DSA+tag brcm, mdio mux,
USB+usbh phy, PCIe 6328, mtd split wfi/bcm63xx -> **tutti presenti (=y)**.
Nota: CONFIG_JFFS2_FS **non serve** nel kernel: i JFFS2 di cferam/kernel sono
letti dal **CFE**, non da Linux.

### 17.2 Script di build automatico
`port/build_d6300.sh` esegue su Linux:
1. verifica ambiente (git/make/gcc/python3/...)
2. clona OpenWrt se assente + applica il port (apply_port.sh)
3. seleziona target bmips/bcm6361/netgear_d6300 via .config
4. inserisce il cferam nel sorgente del package bcm63xx-cfe
5. esegue la build (make -jN, 30-60 min)
6. elenca le immagini prodotte + istruzioni per il cferam mancante

Uso: `./build_d6300.sh /percorso/netgear-d6300`



## 18. FORMATO .CHK VERIFICATO BYTE-PER-BYTE (round 28)
Implementato il checksum Netgear (mkchkimg.c) e ricostruito l'header del
firmware stock:
| Campo | Valore stock | Ricostruito | Esito |
|---|---|---|---|
| magic | 0x2A23245E | 0x2A23245E | ✓ |
| header_len | 58 | 58 | ✓ |
| reserved | 0101000066010066 (region 1, v1.0.0.102_1.0.102) | idem | ✓ |
| kernel_chksum | 0xCF31D07B | 0xCF31D07B | **MATCH** |
| image_chksum | 0xCF31D07B | 0xCF31D07B | **MATCH** |
| header_chksum | 0x41AE0C44 | 0x41AE0C44 | **MATCH** |
| kernel_len | 25.919.508 | 25.919.508 | ✓ |
| board_id | U12L216T00_NETGEAR (18 char) | idem | ✓ |

**Header ricostruito BYTE-PER-BYTE IDENTICO allo stock** e payload identico.

### Formula header_chksum (scoperta)
`netgear_checksum(header[0:40] con campo header_chksum azzerato + board_id)`
(dove board_id è SENZA NUL; header_len = 40 + len(board_id) = 58).

### Generatore
`netgear-d6300/make_chk.py` -> `make_chk(payload)` produce un .chk
identico al formato Netgear (board id D6300, region 1, versione
1.0.0.102_1.0.102 come il firmware ufficiale).
Esempio generato: `port/build_test/factory_test.chk` (payload di test).
=> possibile percorso di flash sperimentale da **web UI stock** (da testare).


## 19. MAPPATURA LED CONFERMATA (round 29)
Dal file `/usr/sbin/gpio_test.sh` del firmware stock:
```c
#define INET_FAIL_LED     4
#define INET_ACT_LED      5
#define GIGA_10_LINK_LED  7
#define GIGA_LINK_LED     10
#define LAN_10_LINK_LED   26
#define LAN_LINK_LED      30
```
- **LED diretti via GPIO**: 4 (internet fail), 5 (internet activity),
  7 (giga 10, non pilotato), 10 (giga link), 26 (lan10 link), 30 (lan link)
- **LED seriali** (shift register bit-banged su GPIO2=clk, GPIO3=data):
  **24 posizioni** (loop 1..24); gruppi colore da `led_all_blue()`:
  3,6,7,9,12,13,19,21; da `led_all_red()`: 4,10,11,18,20,23
- Altri GPIO pilotati: 32, 33, 34 (funzione da confermare)
=> DTS aggiornato con i LED diretti confermati; LED seriali restano TODO
   (mappatura indice->funzione da determinare sul device).

## 20. STRUTTURA BASE-FILES CORRETTA (round 29)
Trovata una **incoerenza strutturale**: in OpenWrt i base-files per device
stanno **per-subtarget** (`target/linux/bmips/bcm6362/base-files/...`), non
nella radice del target. Il port è stato ristrutturato:
```
target/linux/bmips/bcm6361/base-files/etc/board.d/01_leds
target/linux/bmips/bcm6361/base-files/etc/board.d/02_network
target/linux/bmips/bcm6361/base-files/lib/upgrade/platform.sh
```
- `02_network` ora usa `ucidef_set_interfaces_lan_wan "lan1 lan2 lan3 lan4" "wan"`
- `01_leds` imposta LED netdev internet/lan + USB
- `platform.sh` abilita **sysupgrade via nand_do_upgrade** (modellato su bcm6362)
Patch series rigenerata e riverificata: 6 patch, 10 file totali OK.


## 21. PATCH SERIES PR-READY + REPORT CONSOLIDATO (round 30)
### 21.1 Patch series PR-ready
Le 6 patch sono state rigenerate con **commit message completi**
(Subject + corpo tecnico + Signed-off-by placeholder):
`0001-add-bcm6361-subtarget.patch` ... `0006-add-bcm6361-kernel-configuration.patch`.
Verificate con l'applier fedele: Makefile + 9 file nuovi tutti OK byte-per-byte.
Per l'invio: personalizzare From/Signed-off-by e usare `git am`.

### 21.2 Report consolidato
Creato `PORT_REPORT.md`: executive summary con hardware ricostruito, analisi
firmware, deliverable, evidenza di verifica (11 verifiche superate),
lavoro residuo (build/test/upstream) e indice file.


## 22. SUITE DI VERIFICA UNICA (round 31)
Creato `run_all_checks.py` che esegue in un comando tutte le verifiche offline:
1. DTS con dtc reale (exit 0, DTB 13.625 byte)
2. Patch series applicabile su albero reale (10 file OK)
3. Matrice driver (20 righe verificate, 1 da confermare: RNG)
4. Kernel config (tutti i simboli necessari)
5. JFFS2 cferam (200.084 byte, dirent cferam.000)
6. WFI tag (chip 0x6361, flashType 3, version 0x5731)
7. Layout immagine (kernel JFFS2 @0, cferam @5MB, WFI tag in coda)
8. Formato .chk byte-per-byte (header identico allo stock)
9. Drift vs master (nessun drift)
10. Struttura port (9 file + 6 patch)

**RISULTATO: 10/10 verifiche superate.**
Comando: `python3 netgear-d6300/run_all_checks.py`


## 23. UPSTREAM COMPLIANCE — COMMENTI IN INGLESE (round 32)
OpenWrt richiede commenti e documentazione in **inglese**. I file del port
avevano commenti in italiano: sono stati tradotti **68 righe** in 6 file:
| File | Righe tradotte |
|---|---|
| dts/bcm6361-netgear-d6300.dts | 41 |
| image/bcm6361.mk | 14 |
| dts/bcm6361.dtsi | 8 |
| bcm6361/config-6.18 | 3 |
| base-files .../01_leds | 1 |
| base-files .../02_network | 1 |
Verifica: 0 commenti italiani residui.
DTS ricompilato (exit 0, DTB 13.625 byte), patch series rigenerata (6 patch),
suite `run_all_checks.py`: **10/10 verifiche superate**.
Scelta aggiuntiva: `led_internet_fail` usa ora `label = "red:internet"` invece
di `function = LED_FUNCTION_STATUS` (semantica upstream più corretta).


## 24. FIX CRITICO — FALLBACK SoC "brcm,bcm6362" (round 33)
### 24.1 Il problema
Le patch OpenWrt del target bmips:
- `200-mips-bmips-automatically-detect-CPU-frequency.patch`
- `201-mips-bmips-automatically-detect-RAM-size.patch`

contengono tabelle di compatibili **che NON includono il bcm6361**:
```c
{ "brcm,bcm6318" }, { "brcm,bcm6328" }, { "brcm,bcm6358" },
{ "brcm,bcm6362" }, { "brcm,bcm6368" }, { "brcm,bcm63268" }
```
e cercano il match sul **root compatible** del DTB:
```c
if (of_flat_dt_is_compatible(of_get_flat_dt_root(), cf->compatible))
```
- **CPU frequency**: se nessun match, c'è un fallback che legge la proprietà
  DT `mips-hpt-frequency` (presente: 200 MHz) → sopravvivrebbe.
- **RAM size**: se nessun match, **nessun `memblock_add()`** → il kernel
  avrebbe **0 MB di RAM → panic**. Il DTS del 6362 ha `memory@0 reg=<0 0>`
  proprio perché la RAM viene aggiunta dalla patch 201.

### 24.2 La soluzione (con precedente upstream!)
Aggiungere il fallback al compatible del device DTS:
```dts
compatible = "netgear,d6300", "brcm,bcm6361", "brcm,bcm6362";
```
Precedente **identico** in upstream: i device BCM6369 usano
`compatible = "...", "brcm,bcm6369", "brcm,bcm6368";`
(bcm6369-netgear-evg2000.dts, bcm6369-comtrend-wap-5813n.dts) perché le
tabelle conoscono solo il 6368.

### 24.3 Verifica
- DTS ricompilato (exit 0), patch series rigenerata con il commit message
  0003 aggiornato (spiega il fallback), suite **10/10**.
- **Senza questo fix il device non sarebbe partito** (mancata inizializzazione RAM).


## 25. VERIFICHE SoC-SPECIFICHE AGGIUNTIVE (round 34)
Controllati gli altri punti del target bmips che potrebbero dipendere dalla SoC:

| Elemento | Esito |
|---|---|
| patch 202 (mips: bmips: tweak Kconfig options) | generica, nessuna tabella SoC -> OK |
| enetsw driver (`bcm6368-enetsw.c`) | `of_device_id` include **brcm,bcm6362-enetsw** -> OK |
| power controller (`drivers/pmdomain/bcm/bcm63xx-power.c`) | include **brcm,bcm6362-power-controller** -> OK |
| config kernel | `CONFIG_BCM63XX_POWER=y`, `CONFIG_PM_GENERIC_DOMAINS(_OF)=y` -> OK |
| CPU freq autodetect (patch 200) | fallback su proprietà DT `mips-hpt-frequency` (presente) |
| RAM autodetect (patch 201) | **richiede il fallback compatible** (già corretto, vedi §24) |

### Suite estesa a 12 check
Aggiunti due regression test:
- **11. Fallback SoC (critico)**: verifica che il device DTS contenga il
  fallback "brcm,bcm6362" e che le patch 200/201 NON conoscano il bcm6361
  (controprova che il fallback è necessario).
- **12. Power domain drivers**: verifica CONFIG_BCM63XX_POWER e PM domains.

Risultato: **12/12 verifiche superate**.


## 26. SCOPERTE DALLE FOTO HARDWARE (ispezione scheda D6300)
### 26.1 Chip NAND reale = ST (non Micron!)
Dal retro scheda, chip **U2003**: sigla **"NAND512W3A2S NXE"** (logo ST,
lotto 99A79 VS, MYS 99 334).
La tabella chip NAND supportati nel CFE (`cferam`, offset 0x2dbd0) contiene:
```
Samsung K9F5608U0
ST NAND512W3A2CN6
ST NAND01GW3B2CN6
Micron MT29F1G08AAC
Hynix H27U1G8F2B
Hynix H27U518S2C
```
Quindi il CFE supporta sia il chip ST 512Mbit (=64MB) sia i 1Gbit (=128MB).

**Implicazione:** se il flash reale è il ST NAND512W3A2C (64MB, tipicamente
**blocchi 16KB / pagine 512B**), la ricetta immagine NON deve usare
BLOCKSIZE=128k/PAGESIZE=2048/flashType=3 ma i valori del DGND3700v2:
BLOCKSIZE=16k, PAGESIZE=512, SUBPAGESIZE=256, CFE_WFI_FLASH_TYPE=2 e
CFE_RAM_JFFS2_PAD=496k (496k = 31 blocchi da 16k, esatto).
→ **DA VERIFICARE** con il boot log CFE ("Total Flash size: %dK with %d sectors"
e stringa del device NAND) + /proc/mtd. Non modificare la ricetta prima.

### 26.2 Test point trovati sul retro
Colonna di **6 pad tondi dorati** vicino al bordo destro (accanto ai LED
LED257/LED258), serigrafia:
```
TP100, TP101, TP102, TP103, TP104, TP105
```
(+ TP2 isolato in un'altra zona). Candidati per la console UART (4 segnali
console + 2 test). Da provare con l'adattatore CH340G: GND su foro di
fissaggio, RXD su un pad alla volta, 115200 8N1, power cycle.
Filtro utile: continuità tra i TP e il connettore J7 (pannello frontale) —
se un TP "bipa" verso J7, è un segnale LED/pulsante, non UART.


## 27. BOOTLOG COMPLETO CATTURATO — SCOPERTE DECISIVE (20/11)
Console UART su **J252**: pad 2 = GND, pad 3 = TX router (115200 8N1).
Log salvato in `netgear-d6300/boot_D6300_full.log`.

### 27.1 La piattaforma reale è BCM6362 (non BCM6361!)
Dal log:
```
BCM6362 Platform Boot Code V1.0.9-4.12L.04
CFE version 1.0.38-112.70 for BCM96362 (32bit,SP,BE)
Chip ID: BCM6362B0, MIPS: 400MHz, DDR: 333MHz, Bus: 166MHz
Board Id: 96362ADVN2xh
kernel: CPU revision is: 0002a070 (Broadcom4350)
```
Il D6300 risponde **BCM6362B0** (board id 96362ADVN2xh): il target OpenWrt
corretto è il **subtarget bcm6362 esistente**, non un nuovo bcm6361.
Conseguenza: il port va ristrutturato come **device dentro bcm6362**
(DTS che include bcm6362.dtsi + ricetta in bcm6362.mk + base-files del sottotarget).

### 27.2 NAND: ST NAND512W3A2CN6, 64 MB, blocchi 16 KB, pagine 512 B
```
NAND flash device: name ST NAND512W3A2CN6, id 0x2076 block 16KB size 65536KB
BrcmNAND mfg 20 76 ST ST_NAND512W3A 64MB on CS0
NAND Config: chipSize=64 MB, blockSize=16K, pageSize=512B, ecclevel=15
Bad block table Bbt0 found at page 0001ffe0 / 1tbB at page 0001ffc0
```
Quindi la **ricetta 128k/type3 era sbagliata**: servono i valori del
DGND3700v2 (bcm6362) → **BLOCKSIZE=16k, PAGESIZE=512,
CFE_RAM_JFFS2_PAD=496k, CFE_WFI_FLASH_TYPE=2, CFE_WFI_VERSION=0x5731**.
Confermato anche: cferam D6300 ≠ cferam DGND3700v2 → serve la nostra
(196.380 B) nel repo bcm63xx-cfe con nome `netgear,d6300/cferam`.

### 27.3 Partizioni viste dal kernel stock (bcm963xx_mtd)
```
0x0000000-0x00004000 : nvram          (16 KB)
0x0004000-0x1D80000 : rootfs_update   (~30,9 MB)
0x1D80000-0x3AFC000 : rootfs          (~30,9 MB)   <- CFE avvia qui
0x3B00000-0x3F00000 : data            (4 MB)
```
Gap 0x3AFC000-0x3B00000 (16 KB) e tail 0x3F00000-0x4000000 (1 MB)
non partizionati (probabile area CFE/flags).
Boot: `Booting from latest image (0xb9d80000)` = flash base 0xb8000000 +
0x1D80000 → **rootfs**. cmdline: `root=mtd:rootfs ro rootfstype=jffs2
console=ttyS0,115200`.

### 27.4 Altri dati utili
- RAM: 128 MB (memory 0x07f00000 usable, 1 MB riservato DSL)
- Kernel stock: **Linux 2.6.30** (buildroot 2010.02, gcc 4.4.2, 2017-02-14) — correggere il dato 2.6.22
- Switch esterno: **BCM53125** ("External switch id = 53125", driver 53115 forzato)
  → nel DTS il nodo mdio_ext usa `brcm,bcm53125` (come DGND3700v2!)
- WiFi 2.4 GHz: **BCM435f** integrato (wl0) → nel recipe va incluso `$(B43_PACKAGES)`
- WiFi 5 GHz: modulo mini-PCIe **BCM94360** con chip **BCM4360KMLG** (802.11ac 3x3,
  1300 Mbps; PN Netgear **T77H390T00** LF, E100069772-D4). Durante la cattura la
  scheda era smontata (per questo "PCIe: No device found"): con scheda inserita
  il kernel la enumera come 14e4:43a0/43b1 e **non esiste driver mainline** per
  BCM4360 (né b43 né brcmfmac) → **5 GHz non supportato dal port OpenWrt**
  (limitazione documentata). Il 2.4G resta l'unica radio potenzialmente utile (b43).
  **Esperimento futuro**: sostituzione con scheda mini-PCIe **Atheros AR9280**
  (ath9k, 5 GHz N 300 Mbps) — guida in port/ESPERIMENTO_MINI_PCIE_5GHZ.md.
- MAC base: c4:04:15:18:35:10 (+1 per WAN) — da cferom
- CFE: autoboot con delay 1 s, IP 192.168.1.1/24, netmask ffffff00, host .100
- Comandi CFE disponibili: flashimage, chkw, f, w, e n/p/a, erasenvram, d, s

### 27.5 Piano di ristrutturazione del port
1. DTS `bcm6362-netgear-d6300.dts` (include bcm6362.dtsi, compatible
   "netgear,d6300", "brcm,bcm6362"; LED GPIO 4/5/10/26/30 dal gpio_test.sh;
   switch: switch0 port4 extsw + mdio_ext switch@1e bcm53125 con LAN1-4/WAN;
   nflash: partizioni D6300 con cferom + nvmem MAC; uart0 okay)
2. Ricetta in `image/bcm6362.mk`: device `netgear_d6300` con i parametri
   16k/512/496k/type2/0x5731 e `CFE_RAM_FILE := netgear,d6300/cferam`
3. base-files: case "netgear,d6300" in bcm6362/base-files (02_network,
   01_leds, platform.sh)
4. cferam: `netgear,d6300/cferam` (nostro, 196.380 B) in bcm63xx-cfe
5. Rimozione del subtarget bcm6361 (non serve più)


## 28. RISTRUTTURAZIONE DEL PORT SU bcm6362 (20/11)
Con il bootlog è emerso che il D6300 è una piattaforma **BCM6362**
(CFE "for BCM96362", board id 96362ADVN2xh, chip id BCM6362B0). Il port è
stato quindi riscritto come **device del subtarget `bcm6362` esistente**,
eliminando il falso subtarget bcm6361.

### 28.1 Nuovi file del port
```
target/linux/bmips/dts/bcm6362-netgear-d6300.dts        (nuovo)
target/linux/bmips/image/bcm6362.mk                     (device netgear_d6300)
target/linux/bmips/bcm6362/base-files/etc/board.d/01_leds
target/linux/bmips/bcm6362/base-files/etc/board.d/02_network
target/linux/bmips/bcm6362/base-files/lib/upgrade/platform.sh
bcm63xx-cfe: netgear,d6300/cferam (196.380 B, estratto dallo stock)
```
Dati usati: NAND ST NAND512W3A2CN6 (64 MB, blocchi 16 KB, pagine 512 B),
switch BCM53125, partizioni stock (cferom/rootfs_update/wfi/flag/data),
LED GPIO 4/5/7/10/26/30, MAC da cferom (offset 0x6a0 da verificare),
PCIe abilitata (slot mini-PCIe), console su uart0.

### 28.2 Ricetta immagine (allineata a DGND3700v2)
```
CHIP_ID := 6362
CFE_RAM_FILE := netgear,d6300/cferam
CFE_RAM_JFFS2_NAME := cferam
CFE_RAM_JFFS2_PAD := 496k
BLOCKSIZE := 16k
PAGESIZE := 512
CFE_WFI_FLASH_TYPE := 2
CFE_WFI_VERSION := 0x5731
DEVICE_PACKAGES += $(USB2_PACKAGES) $(B43_PACKAGES) kmod-leds-bcm6328 kmod-leds-gpio
```

### 28.3 Patch series ridotta (3 patch, verificate)
```
0001 bmips: add Netgear D6300 device tree        (DTS nuovo)
0002 bmips: bcm6362: add Netgear D6300 image     (bcm6362.mk)
0003 bmips: bcm6362: add Netgear D6300 base-files (01_leds/02_network/platform.sh)
```
+ PR separata a openwrt/bcm63xx-cfe per `netgear,d6300/cferam`.

### 28.4 Verifiche eseguite
- DTS compilato con dtc (via pcpp): **exit 0**, DTB 11.764 byte, roundtrip OK
  (2 warning benigni identici al riferimento upstream DGND3700v2)
- Patch applicate fedelmente ai file upstream: **tutte coincidono**
- Voci ancora da verificare sul device: offset MAC in cferom, layout CFE esatto,
  tasti (reset/WPS), mapping 24 LED seriali, supporto b43 2.4 GHz


## 29. CORREZIONE: NOME DEL FILE CFERAM NEL JFFS2 (20/11)
Evidenza dal firmware stock: il JFFS2 contiene il file **`cferam.000`**
(non `cferam`), come per il device Huawei HG253s-v2. Il CFE del D6300
(boot ROM + CFE 1.0.38-112.70) cerca quel nome nella partizione immagine.

Correzione applicata:
- repo bcm63xx-cfe: `netgear,d6300/cferam` → **`netgear,d6300/cferam.000`**
- ricetta:
  ```
  CFE_RAM_FILE := netgear,d6300/cferam.000
  CFE_RAM_JFFS2_NAME := cferam.000
  ```
- patch 0002 rigenerata
(Il file ha sempre 196.380 byte, sha256 baefac12..., md5 5b996cd5...)


## 30. IMMAGINE SIMULATA + PACCHETTO DI CONSEGNA (round 38)
### 30.1 Simulazione cfe.bin con la ricetta bcm6362
`simulate_cfe_bin_bcm6362.py` assembla l'immagine secondo la ricetta:
```
0x00000000  cferam JFFS2 (1-openwrt v0 + cferam.000 v1)   196.700 B
            + padding 0xFF                                  → 507.904 B (496k)
0x0007C000  kernel (KERNEL_SIZE 5 MB, placeholder)          5.242.880 B
0x0057C000  UBI rootfs (placeholder 8 MB)                   8.388.608 B
0x00D7C000  WFI tag (crc, 0x5731, chip 0x6362, flashType 2)        20 B
0x00D7C014  fine immagine: 14.139.412 B (13,48 MB)
```
Verifiche: magic JFFS2, dirent cferam.000 a 0xEC, kernel a 0x7C000,
WFI tag corretto, CRC valido, immagine entro la partizione wfi (29,48 MB).
→ **STRUTTURA VALIDA** (mappa in `build_test/LAYOUT_CFE_BIN_bcm6362.txt`).

### 30.2 Pacchetto di consegna
`D6300_OpenWrt_Port_2026-11-20.zip` (workspace root) con:
- openwrt/ (DTS, ricetta, base-files, cferam.000, 3 patch, archivio bcm6361)
- docs/ (11 documenti del progetto)
- build_test/ (DTB, .i, roundtrip, immagine simulata, mappa, cferam)
- boot_D6300_full.log, SESSIONE_HW_NOTE.md
- scripts/ (suite, validatore, restructure, simulazione)
- README_FIRST.txt con indice, stato e prossimi passi
