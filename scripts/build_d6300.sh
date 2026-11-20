#!/bin/bash
# =====================================================================
# build_d6300.sh — build completa OpenWrt per Netgear D6300 (BCM6361)
# Da eseguire su Linux (Ubuntu/Debian, WSL va bene).
#
# Uso:
#   ./build_d6300.sh /percorso/netgear-d6300
#
# Lo script:
#   1. verifica l'ambiente
#   2. clona OpenWrt (se non presente) e applica il port
#   3. seleziona target/subtarget/device
#   4. inietta il cferam nel package bcm63xx-cfe
#   5. compila
# =====================================================================
set -e

NETGEAR_DIR="${1:-}"
if [ -z "$NETGEAR_DIR" ]; then
    echo "Uso: $0 /percorso/netgear-d6300"
    exit 1
fi
PORT_DIR="$NETGEAR_DIR/port"
CFERAM="$PORT_DIR/openwrt/bcm63xx-cfe/netgear,d6300/cferam"

if [ ! -f "$CFERAM" ]; then
    echo "ERRORE: cferam non trovato in $CFERAM"
    exit 1
fi

echo "== [1/6] verifica ambiente =="
for cmd in git make gcc python3 wget rsync; do
    command -v $cmd >/dev/null || { echo "MANCA: $cmd"; exit 1; }
done
echo "   ok"

echo "== [2/6] prepara OpenWrt =="
if [ ! -f "rules.mk" ]; then
    echo "   clono OpenWrt (shallow)..."
    git clone --depth 1 https://git.openwrt.org/openwrt/openwrt.git
    cd openwrt
fi
bash "$PORT_DIR/apply_port.sh" "$PORT_DIR"

echo "== [3/6] seleziona target =="
if [ ! -f "scripts/config" ]; then echo "ERRORE: non sembra un tree OpenWrt"; exit 1; fi
cat >> .config <<EOF
CONFIG_TARGET_bmips=y
CONFIG_TARGET_bmips_bcm6362=y
CONFIG_TARGET_bmips_bcm6362_DEVICE_netgear_d6300=y
CONFIG_TARGET_MULTI_PROFILE=y
EOF
make defconfig
grep -q "CONFIG_TARGET_bmips_bcm6362_DEVICE_netgear_d6300=y" .config \
    && echo "   target selezionato" \
    || { echo "   ERRORE: target non selezionato"; exit 1; }

echo "== [4/6] prepara il package bcm63xx-cfe =="
make package/kernel/bcm63xx-cfe/prepare V=s
BUILD_SRC=$(find build_dir -maxdepth 3 -type d -name "bcm63xx-cfe-*" | head -n1)
if [ -z "$BUILD_SRC" ]; then
    echo "   ATTENZIONE: sorgente del package non trovato, cferam forzato in staging dopo il build"
else
    mkdir -p "$BUILD_SRC/netgear,d6300"
    cp "$CFERAM" "$BUILD_SRC/netgear,d6300/cferam"
    echo "   cferam inserito in $BUILD_SRC/netgear,d6300/"
fi

echo "== [5/6] build (30-60 min) =="
make -j$(nproc) V=s

echo "== [6/6] risultati =="
ls -la bin/targets/bmips/bcm6362/ 2>/dev/null || echo "   (directory risultati non trovata)"
echo
echo "Immagine attesa:"
echo "  bin/targets/bmips/bcm6362/openwrt-bmips-bcm6362-netgear_d6300-*.bin"
echo
echo "Se il build si ferma per cferam mancante:"
echo "  STAGE=\$(find staging_dir -maxdepth 2 -type d -name image | head -n1)"
echo "  mkdir -p \$STAGE/bcm63xx-cfe/netgear,d6300 && cp $CFERAM \$STAGE/bcm63xx-cfe/netgear,d6300/cferam"
echo "  make target/linux/install V=s"
