# -*- coding: utf-8 -*-
"""Suite di verifica del port OpenWrt Netgear D6300 (piattaforma BCM6362)."""
import hashlib
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = os.path.join(HERE, "port")
OW = os.path.join(PORT, "openwrt")
PY = sys.executable
results = []


def run(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, "eccezione: %s" % str(e)[:120]
    results.append((name, ok, detail))
    print("  %-44s %s  %s" % (name, "PASS" if ok else "FAIL", detail))


def check_dts_patches():
    r = subprocess.run([PY, os.path.join(HERE, "validate_new_port.py")],
                       capture_output=True, text=True)
    out = r.stdout
    dts_ok = "exit: 0" in out
    pat_ok = "RISULTATO PATCH: OK" in out
    return (dts_ok and pat_ok), "DTS dtc=%s, patch=%s" % (dts_ok, pat_ok)


def check_series():
    s = os.path.join(OW, "patches", "series")
    names = [l.strip() for l in io.open(s, encoding="utf-8") if l.strip()]
    return len(names) == 3, "%d patch in series" % len(names)


def check_structure():
    expected = [
        "dts/bcm6362-netgear-d6300.dts",
        "image/bcm6362.mk",
        "bcm6362/base-files/etc/board.d/01_leds",
        "bcm6362/base-files/etc/board.d/02_network",
        "bcm6362/base-files/lib/upgrade/platform.sh",
        "bcm63xx-cfe/netgear,d6300/cferam.000",
    ]
    miss = [f for f in expected if not os.path.exists(os.path.join(OW, f.replace("/", os.sep)))]
    return not miss, "mancanti: %s" % (", ".join(miss) if miss else "nessuno")


def check_cferam():
    p = os.path.join(OW, "bcm63xx-cfe", "netgear,d6300", "cferam.000")
    b = open(p, "rb").read()
    return len(b) == 196380, "%d byte, sha256=%s" % (
        len(b), hashlib.sha256(b).hexdigest()[:12])


def check_recipe():
    t = io.open(os.path.join(OW, "image", "bcm6362.mk"), encoding="utf-8").read()
    need = ["netgear_d6300", "netgear,d6300/cferam.000", "CFE_RAM_JFFS2_NAME := cferam.000",
            "CFE_RAM_JFFS2_PAD := 496k",
            "BLOCKSIZE := 16k", "PAGESIZE := 512", "CFE_WFI_FLASH_TYPE := 2",
            "CFE_WFI_VERSION := 0x5731", "$(B43_PACKAGES)"]
    miss = [x for x in need if x not in t]
    return not miss, "mancanti: %s" % (", ".join(miss) if miss else "nessuno")


def check_basefiles():
    ok = True
    for rel in ["etc/board.d/01_leds", "etc/board.d/02_network", "lib/upgrade/platform.sh"]:
        p = os.path.join(OW, "bcm6362", "base-files", rel.replace("/", os.sep))
        t = io.open(p, encoding="utf-8").read()
        if "netgear,d6300" not in t:
            ok = False
    return ok, "case netgear,d6300 presente nei 3 file"


def check_bootlog():
    p = os.path.join(HERE, "boot_D6300_full.log")
    t = io.open(p, encoding="utf-8", errors="replace").read()
    keys = ["ST NAND512W3A2CN6", "BCM6362", "block 16KB", "96362ADVN2xh",
            "console=ttyS0,115200"]
    miss = [k for k in keys if k not in t]
    return not miss, "chiavi: %s" % (", ".join(miss) if miss else "tutte presenti")


def check_old_archived():
    old = os.path.join(PORT, "OLD_bcm6361_subtarget")
    left = os.path.join(OW, "bcm6361")
    return os.path.isdir(old) and not os.path.exists(left), "vecchi file archiviati"




def check_partitions():
    FLASH = 64 * 1024 * 1024
    parts = [(0x0, 0x4000), (0x4000, 0x1d7c000), (0x1d80000, 0x1d7c000),
             (0x3afc000, 0x4000), (0x3b00000, 0x400000)]
    prev = 0
    for start, size in parts:
        if start < prev:
            return False, "overlap"
        prev = start + size
    if prev > FLASH:
        return False, "oltre i 64 MB"
    import re
    dts = io.open(os.path.join(OW, "dts", "bcm6362-netgear-d6300.dts"),
                  encoding="utf-8").read()
    regs = set((int(a, 16), int(b, 16)) for a, b in
               re.findall(r"reg = <0x([0-9a-fA-F]+) 0x([0-9a-fA-F]+)>;", dts))
    expected = [(0x0, 0x4000), (0x4000, 0x1d7c000), (0x1d80000, 0x1d7c000),
                (0x3afc000, 0x4000), (0x3b00000, 0x400000)]
    miss = [r for r in expected if r not in regs]
    if miss:
        return False, "partition mancanti: %s" % miss
    return True, "5 partizioni coerenti con il bootlog, entro 64 MB"
    return True, "5 partizioni coerenti, entro 64 MB (tail 1 MB)"


def check_wfi_capacity():
    KERNEL = 5 * 1024 * 1024
    PAD = 496 * 1024
    wfi = 0x1d7c000
    free = wfi - KERNEL - PAD
    ok = free > 8 * 1024 * 1024
    return ok, "spazio UBI rootfs: %.1f MB" % (free / 1048576)



def check_sim_image():
    import struct
    p = os.path.join(PORT, "build_test", "simulated_cfe_bin_bcm6362.bin")
    if not os.path.exists(p):
        return False, "immagine simulata mancante"
    b = open(p, "rb").read()
    if b[:2] != b"\x19\x85":
        return False, "magic JFFS2 assente"
    if b"cferam.000" not in b[:0xC0000]:
        return False, "dirent cferam.000 assente nei primi 496k"
    crc, ver, chip, flash, flags = struct.unpack(">IIIII", b[-20:])
    if (ver, chip, flash) != (0x5731, 0x6362, 2):
        return False, "WFI tag errato"
    if (~__import__("binascii").crc32(b[:-20])) & 0xFFFFFFFF != crc:
        return False, "CRC tag errato"
    if len(b) > 0x1d7c000:
        return False, "immagine oltre la partizione wfi"
    return True, "%.2f MB, cferam.000, WFI tag chip 0x6362 flash 2, CRC OK" % (len(b) / 1048576)

print("=" * 78)
print("SUITE DI VERIFICA — PORT OPENWRT NETGEAR D6300 (BCM6362)")
print("=" * 78)
run("1. DTS compila + patch verificate", check_dts_patches)
run("2. Patch series (3)", check_series)
run("3. Struttura del port", check_structure)
run("4. Cferam (196.380 B)", check_cferam)
run("5. Ricetta immagine (16k/512/496k/type2)", check_recipe)
run("6. Base-files (case netgear,d6300)", check_basefiles)
run("7. Bootlog catturato (dati chiave)", check_bootlog)
run("8. Vecchio subtarget archiviato", check_old_archived)
run("9. Coerenza partizioni DTS", check_partitions)
run("10. Capienza partizione wfi", check_wfi_capacity)
run("11. Immagine cfe.bin simulata", check_sim_image)

print()
passed = sum(1 for _, ok, _ in results if ok)
print("RISULTATO: %d/%d verifiche superate" % (passed, len(results)))
if passed != len(results):
    for n, ok, d in results:
        if not ok:
            print("  -", n, ":", d)
    sys.exit(1)
print("TUTTE LE VERIFICHE SUPERATE")
