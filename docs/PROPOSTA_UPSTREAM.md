# Proposta di integrazione upstream — Netgear D6300 (BCM6362)

## Sintesi
Il Netgear D6300 è un router VDSL/ADSL basato su **BCM6362B0** (confermato dal
bootlog: CFE "for BCM96362", board id 96362ADVN2xh, chip id 0x636220B0).
Il subtarget **bmips/bcm6362** esiste già in OpenWrt (device di riferimento:
Netgear DGND3700v2, stesso SoC). Il D6300 è quindi un **nuovo device** del
sottotarget esistente: nessuna patch all'architettura, nessun nuovo subtarget.

## Cosa aggiunge il port
1. DTS `bcm6362-netgear-d6300.dts`:
   - switch esterno **BCM53125** (5 porte GbE, RGMII), LAN1-4 + WAN
   - NAND **ST NAND512W3A2CN6** (64 MB, 16 KB blocchi, 512 B pagine), ECC 15/512
   - partizioni: cferom, rootfs_update, wfi, flag, data (da bootlog stock)
   - MAC da cferom, LED GPIO 4/5/7/10/26/30, PCIe mini-PCIe, UART0 console
2. Device `netgear_d6300` in `image/bcm6362.mk`:
   - BLOCKSIZE 16k, PAGESIZE 512, CFE_RAM_JFFS2_PAD 496k
   - CFE_WFI_FLASH_TYPE 2, CFE_WFI_VERSION 0x5731
   - CFE_RAM_FILE netgear,d6300/cferam.000 (nuovo, da bcm63xx-cfe)
   - pacchetti USB2, B43 (2.4 GHz), LED
3. Base-files del bcm6362: case `netgear,d6300` (led/netif/sysupgrade)

## PR previste
1. **openwrt/openwrt**: 3 commit (DTS, ricetta, base-files) — patch pronte
2. **openwrt/bcm63xx-cfe**: aggiunta `netgear,d6300/cferam.000`
   (estratto dal firmware stock, md5 5b996cd5dc353ac451bc380c0e4d0216)

## Limitazioni dichiarate
- 5 GHz BCM4360 non supportato (nessun driver mainline)
- DSL non supportato
- 2.4 GHz via b43 (da validare sul device)

## Stato dei test
- Validazione offline completata: DTS compilato (dtc), 3 patch verificate,
  immagine simulata con WFI tag valido (11/11 check)
- Test su hardware: da eseguire (serve build Linux + flash via CFE)
