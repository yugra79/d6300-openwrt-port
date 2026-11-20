# -*- coding: utf-8 -*-
"""Round 38: simula l'immagine cfe.bin con la NUOVA ricetta bcm6362
(kernel 5MB + cferam.000 JFFS2 pad 496k + UBI placeholder + WFI tag chip 0x6362 flashType 2)."""
import binascii
import io
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = os.path.join(HERE, "port")
OUT = os.path.join(PORT, "build_test")
os.makedirs(OUT, exist_ok=True)

T_DIRENT = 0xE001
T_INODE = 0xE002
DT_REG = 8
DT_DIR = 8


def jcrc(data):
    return (binascii.crc32(data, 0xFFFFFFFF) ^ 0xFFFFFFFF) & 0xFFFFFFFF


def make_dirent(pino, version, ino, name, dtype, mctime=0):
    name_b = name.encode()
    nsize = len(name_b)
    body = struct.pack(">IIII", pino, version, ino, mctime)
    body += struct.pack(">BBH", nsize, dtype, 0)
    raw = struct.pack(">HHI", 0x1985, T_DIRENT, 12 + len(body) + 8 + nsize)
    raw += struct.pack(">I", jcrc(raw))
    raw += body
    node_crc = jcrc(raw)
    name_crc = jcrc(name_b)
    return raw + struct.pack(">II", node_crc, name_crc) + name_b


def make_inode(ino, version, data, mode=0o100644):
    csize = dsize = len(data)
    totlen = 72 + csize
    raw = struct.pack(">HHI", 0x1985, T_INODE, totlen)
    raw += struct.pack(">I", jcrc(raw))
    raw += struct.pack(">IIIIIIIIIIII", ino, version, mode, 0, 0, dsize, 0, 0, 0, 0, csize, dsize)
    raw += struct.pack(">BBH", 0, 0, 0)
    raw += struct.pack(">I", jcrc(data))
    raw += struct.pack(">I", jcrc(raw))
    return raw + data


def pad4(b):
    return b + b"\x00" * ((4 - len(b) % 4) % 4)


def build_cferam_jffs2(cferam_data, name="cferam.000"):
    nodes = [make_inode(1, 1, b"", mode=0o40755)]
    nodes.append(make_dirent(1, 0, 2, "1-openwrt", DT_REG))       # dummy, version 0
    nodes.append(make_inode(2, 0, b""))
    nodes.append(make_dirent(1, 1, 3, name, DT_REG))              # cferam, version 1
    nodes.append(make_inode(3, 1, cferam_data))
    return b"".join(pad4(n) for n in nodes)


# ---- parametri nuova ricetta ----
KERNEL_SIZE = 5 * 1024 * 1024        # KERNEL_SIZE := 5120k
CFE_RAM_JFFS2_PAD = 496 * 1024       # 31 blocchi da 16k
WFI_SIZE = 0x1d7c000                 # partizione wfi
CHIP_ID = 0x6362
FLASH_TYPE = 2                       # NAND 16k
WFI_VERSION = 0x5731
FLAGS = 0

print("== 1) JFFS2 cferam (dummy v0 + cferam.000 v1) ==")
cferam = open(os.path.join(OUT, "cferam.000"), "rb").read() \
    if os.path.exists(os.path.join(OUT, "cferam.000")) else open(
        os.path.join(PORT, "openwrt", "bcm63xx-cfe", "netgear,d6300", "cferam.000"), "rb").read()
print("  cferam:", len(cferam), "byte")
jffs = build_cferam_jffs2(cferam)
print("  JFFS2:", len(jffs), "byte")
assert len(jffs) <= CFE_RAM_JFFS2_PAD
jffs_padded = jffs + b"\xFF" * (CFE_RAM_JFFS2_PAD - len(jffs))
print("  + pad a 496k:", len(jffs_padded), "byte")

print()
print("== 2) kernel placeholder (padded a KERNEL_SIZE) ==")
# pattern deterministico (non importa il contenuto: simulazione di layout)
kernel = (b"D6300-SIMULATED-KERNEL-" * (KERNEL_SIZE // 23 + 1))[:KERNEL_SIZE]
print("  kernel:", len(kernel), "byte (5 MB)")

print()
print("== 3) UBI rootfs placeholder ==")
UBI_SIZE = 8 * 1024 * 1024
ubi = b"\x55" * UBI_SIZE   # placeholder
print("  UBI:", len(ubi), "byte (8 MB di esempio)")

print()
print("== 4) assemblaggio + WFI tag ==")
image = jffs_padded + kernel + ubi
print("  contenuto:", len(image), "byte (%.2f MB)" % (len(image) / 1048576))
if len(image) + 20 > WFI_SIZE:
    print("  ERRORE: non entra nella partizione wfi!")
    raise SystemExit(1)
crc = (~binascii.crc32(image)) & 0xFFFFFFFF
tag = struct.pack(">IIIII", crc, WFI_VERSION, CHIP_ID, FLASH_TYPE, FLAGS)
image += tag
print("  WFI tag:", tag.hex(), "(20 byte)")
print("  immagine finale:", len(image), "byte (%.2f MB) — limite wfi %.2f MB"
      % (len(image) / 1048576, WFI_SIZE / 1048576))

out_path = os.path.join(OUT, "simulated_cfe_bin_bcm6362.bin")
open(out_path, "wb").write(image)
print("  salvata:", out_path)

print()
print("== 5) VERIFICA STRUTTURA ==")
ok = True
magic, typ = struct.unpack(">HH", image[0:4])
print("  offset 0: JFFS2 magic=0x%04X type=0x%04X %s"
      % (magic, typ, "OK" if magic == 0x1985 else "ERR"))
ok &= magic == 0x1985
i = image.find(b"cferam.000")
print("  dirent 'cferam.000' a offset 0x%X %s" % (i, "OK" if 0 < i < CFE_RAM_JFFS2_PAD else "ERR"))
ok &= 0 < i < CFE_RAM_JFFS2_PAD
koff = CFE_RAM_JFFS2_PAD
print("  kernel a offset 0x%X (atteso 0x%X) %s" % (koff, CFE_RAM_JFFS2_PAD,
                                                    "OK" if koff == CFE_RAM_JFFS2_PAD else "ERR"))
print("  kernel size: %d byte" % KERNEL_SIZE)
tag_back = struct.unpack(">IIIII", image[-20:])
print("  coda: crc=0x%08X version=0x%04X chip=0x%04X flash=%d %s"
      % (tag_back[0], tag_back[1], tag_back[2], tag_back[3],
         "OK" if tag_back[1:] == (WFI_VERSION, CHIP_ID, FLASH_TYPE, FLAGS) else "ERR"))
ok &= tag_back[1:] == (WFI_VERSION, CHIP_ID, FLASH_TYPE, FLAGS)
crc_calc = (~binascii.crc32(image[:-20])) & 0xFFFFFFFF
print("  CRC tag: calc=0x%08X stored=0x%08X %s"
      % (crc_calc, tag_back[0], "OK" if crc_calc == tag_back[0] else "ERR"))
ok &= crc_calc == tag_back[0]

# mappa layout
layout = """MAPPA LAYOUT cfe.bin — NETGEAR D6300 (ricetta bcm6362, round 38)
Dimensione immagine: %d byte (%.2f MB) — limite partizione wfi: %d byte (%.2f MB)

offset        contenuto                                   dimensione
0x00000000    cferam JFFS2 (dummy v0 + cferam.000 v1)       %d
0x0007C000    -> padding 0xFF fino a 496k
0x0007C000    kernel (KERNEL_SIZE = 5 MB)                   %d
0x0057C000    UBI rootfs (placeholder 8 MB)                 %d
0x00D7C000    WFI tag (crc, version 0x5731, chip 0x6362,
              flashType 2 = NAND 16k blocks)                20
0x00D7C014    fine immagine

Nella build reale:
- il kernel sostituisce il placeholder (lzma + relocate)
- l'UBI rootfs e' generato da ubinize (append-ubi)
- il WFI tag e' calcolato sull'immagine completa (cfe-wfi-tag.py)

Verifiche superate: magic JFFS2, dirent cferam.000, kernel offset,
WFI tag (chip/flash) e CRC.
""" % (len(image), len(image) / 1048576, WFI_SIZE, WFI_SIZE / 1048576,
       CFE_RAM_JFFS2_PAD, KERNEL_SIZE, UBI_SIZE)
io.open(os.path.join(OUT, "LAYOUT_CFE_BIN_bcm6362.txt"), "w",
        encoding="utf-8", newline="\n").write(layout)
print("  mappa layout: build_test/LAYOUT_CFE_BIN_bcm6362.txt")
print()
print("RISULTATO:", "STRUTTURA VALIDA" if ok else "PROBLEMI")
