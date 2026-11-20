# Installazione e build — OpenWrt su Netgear D6300 (BCM6362)

Guida aggiornata al 20/11/2026 · piattaforma **BCM6362** (non bcm6361).

## 0. Prerequisiti
- Linux (Ubuntu/Debian o WSL2). Su Windows: `wsl --install -d Ubuntu`
- ~25 GB liberi, connessione internet, 30-60 minuti di build
- Tool: git, make, gcc, python3, rsync (installabili con `sudo apt install build-essential git python3 rsync`)

## 1. Ottenere OpenWrt e le patch

```bash
git clone --depth 1 https://git.openwrt.org/openwrt/openwrt.git
cd openwrt

# copiare le 3 patch del port (dalla cartella D6300_OpenWrt_Port/openwrt/patches)
git am /percorso/D6300_OpenWrt_Port/openwrt/patches/0001-*.patch
git am /percorso/D6300_OpenWrt_Port/openwrt/patches/0002-*.patch
git am /percorso/D6300_OpenWrt_Port/openwrt/patches/0003-*.patch
```
Le patch aggiungono:
- `target/linux/bmips/dts/bcm6362-netgear-d6300.dts`
- il device `netgear_d6300` in `target/linux/bmips/image/bcm6362.mk`
- il case `netgear,d6300` nei base-files del subtarget bcm6362

## 2. cferam nel package bcm63xx-cfe

Il package `bcm63xx-cfe` scarica il repo git upstream; il file
`netgear,d6300/cferam.000` (196.380 byte) va inserito PRIMA del build:

```bash
make package/boot/bcm63xx-cfe/prepare V=s
SRC=$(find build_dir -maxdepth 4 -type d -name "bcm63xx-cfe-*" | head -n1)
mkdir -p "$SRC/netgear,d6300"
cp /percorso/D6300_OpenWrt_Port/openwrt/bcm63xx-cfe/netgear,d6300/cferam.000 "$SRC/netgear,d6300/"
```
(In alternativa, se la PR a openwrt/bcm63xx-cfe è già merged, questo passo non serve.)

## 3. Selezione target e build
```bash
cat >> .config <<EOF
CONFIG_TARGET_bmips=y
CONFIG_TARGET_bmips_bcm6362=y
CONFIG_TARGET_bmips_bcm6362_DEVICE_netgear_d6300=y
EOF
make defconfig
grep -q netgear_d6300 .config && echo "target OK"
make -j$(nproc) V=s
```

Oppure: `./build_d6300.sh /percorso/progetto` (script incluso, fa tutto).

## 4. Risultati
```
bin/targets/bmips/bcm6362/
  openwrt-bmips-bcm6362-netgear_d6300-squashfs-sysupgrade.bin
  openwrt-bmips-bcm6362-netgear_d6300-squashfs-cfe.bin   <- immagine per il CFE
```

## 5. Flash + verifiche
- Metodo e comandi: vedi `TEST_PLAN_D6300.md` §12 (console J252, CFE, TFTP)
- Verifiche post-flash: `/proc/mtd`, MAC (cferom offset 0x6a0), LED, USB, b43

## 6. Limitazioni note
- 5 GHz BCM4360 non supportato (nessun driver mainline) — upgrade possibile con
  scheda mini-PCIe AR9280 (vedi ESPERIMENTO_MINI_PCIE_5GHZ.md)
- DSL non supportato
- 2.4 GHz BCM435f via b43 (da verificare)
