# -*- coding: utf-8 -*-
"""Valida il nuovo port bcm6362: compila il DTS con dtc e verifica le patch."""
import io
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(HERE)
PORT = os.path.join(HERE, "port")
OW = os.path.join(PORT, "openwrt")
REF = os.path.join(HERE, "openwrt_ref")
REB = os.path.join(REF, "bcm6362_basefiles")
DTC = os.path.join(WS, "dtc_win", "dtc.exe")
INC = os.path.join(WS, "dtc_inc")
BUILD = os.path.join(PORT, "build_test", "new_port_bcm6362")
os.makedirs(BUILD, exist_ok=True)
sys.path.insert(0, os.path.join(WS, "pylibs"))

import pcpp  # noqa: E402

print("=" * 74)
print("1) PREPARO LA BUILD DIR (dts + dtsi di riferimento)")
shutil.copy(os.path.join(REF, "dts__bcm6362.dtsi"), os.path.join(BUILD, "bcm6362.dtsi"))
shutil.copy(os.path.join(OW, "dts", "bcm6362-netgear-d6300.dts"),
            os.path.join(BUILD, "bcm6362-netgear-d6300.dts"))
print("  build dir:", BUILD)

print()
print("2) PREPROCESSING (pcpp)")
src = os.path.join(BUILD, "bcm6362-netgear-d6300.dts")
pre = os.path.join(BUILD, "bcm6362-netgear-d6300.i")
pp = pcpp.Preprocessor()
pp.add_path(INC)
pp.add_path(BUILD)
code = io.open(src, encoding="utf-8").read()
pp.parse(code, source=src)
with io.open(pre, "w", encoding="utf-8", newline="\n") as fh:
    pp.write(fh)
print("  preprocessato:", os.path.getsize(pre), "byte")

print()
print("3) COMPILAZIONE dtc")
dtb = os.path.join(BUILD, "bcm6362-netgear-d6300.dtb")
cmd = [DTC, "-I", "dts", "-O", "dtb", "-o", dtb, pre]
p = subprocess.run(cmd, capture_output=True, text=True)
print("  exit:", p.returncode)
if p.stderr.strip():
    print("  stderr:", p.stderr.strip()[:3000])
if os.path.exists(dtb):
    print("  DTB:", os.path.getsize(dtb), "byte")
    # roundtrip + controlli
    rt = os.path.join(BUILD, "roundtrip.dts")
    p2 = subprocess.run([DTC, "-I", "dtb", "-O", "dts", "-o", rt, dtb],
                        capture_output=True, text=True)
    print("  roundtrip exit:", p2.returncode)
    if os.path.exists(rt):
        txt = io.open(rt, encoding="utf-8", errors="replace").read()
        print("  roundtrip: %d righe, %d nodi" % (len(txt.splitlines()), txt.count("{")))
        for kw in ["brcm,bcm6362", "netgear,d6300", "bcm53125", "wfi",
                   "macaddr", "uart", "pcie", "usb"]:
            print("    contiene %-16s : %s" % (kw, kw in txt))

print()
print("4) VERIFICA PATCH (applica i diff e confronta)")


def apply_unified(old_text, diff_text):
    """Applica un diff unificato (solo hunk) a old_text."""
    old_lines = old_text.splitlines()
    out = []
    idx = 0
    lines = diff_text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("@@"):
            # "@@ -a,b +c,d @@"
            import re
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", ln)
            start = int(m.group(1)) - 1
            out.extend(old_lines[idx:start])
            idx = start
            i += 1
            while i < len(lines) and not lines[i].startswith("@@") and not lines[i].startswith("diff --git"):
                h = lines[i]
                if h.startswith("-- ") or h.startswith("\\ No newline"):
                    break
                if h == "":
                    break
                if h.startswith(" "):
                    out.append(old_lines[idx])
                    idx += 1
                elif h.startswith("-"):
                    idx += 1
                elif h.startswith("+"):
                    out.append(h[1:])
                i += 1
            continue
        i += 1
    out.extend(old_lines[idx:])
    return "\n".join(out)


patches = os.path.join(OW, "patches")
series = [l.strip() for l in io.open(os.path.join(patches, "series"), encoding="utf-8") if l.strip()]
ok = True
for name in series:
    txt = io.open(os.path.join(patches, name), encoding="utf-8").read()
    print(" ", name)
    # estrae i diff dal patch
    parts = txt.split("diff --git ")
    for part in parts[1:]:
        part = "diff --git " + part
        header, _, diff = part.partition("\n")
        path = header.split(" b/")[-1].strip()
        target = None
        for base, rel in [(REF, None)]:
            pass
        # mappa path -> file di riferimento upstream e file di destinazione
        if path.endswith("bcm6362-netgear-d6300.dts"):
            dest = os.path.join(OW, "dts", "bcm6362-netgear-d6300.dts")
            ours = io.open(dest, encoding="utf-8").read()
            # confronto contenuto aggiunto
            added = "\n".join(l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
            same = added.strip() == ours.strip()
            print("    %s: NEW FILE -> coincidenza contenuto: %s" % (path.split("/")[-1], same))
            ok = ok and same
        elif path.endswith("image/bcm6362.mk"):
            upstream = io.open(os.path.join(REF, "bcm6362.mk"), encoding="utf-8").read()
            ours = io.open(os.path.join(OW, "image", "bcm6362.mk"), encoding="utf-8").read()
            res = apply_unified(upstream, diff)
            same = res.strip() == ours.strip()
            print("    %s: applicata a upstream -> coincide: %s" % (path.split("/")[-1], same))
            ok = ok and same
        elif "base-files" in path:
            rel = path.split("bcm6362/base-files/")[1]
            mapping = {
                "etc/board.d/01_leds": "etc_board.d_01_leds",
                "etc/board.d/02_network": "etc_board.d_02_network",
                "lib/upgrade/platform.sh": "lib_upgrade_platform.sh",
            }
            upstream = io.open(os.path.join(REB, mapping[rel]), encoding="utf-8").read()
            ours = io.open(os.path.join(OW, "bcm6362", "base-files", rel.replace("/", os.sep)),
                           encoding="utf-8").read()
            res = apply_unified(upstream, diff)
            same = res.strip() == ours.strip()
            print("    %s: applicata -> coincide: %s" % (rel, same))
            ok = ok and same

print()
print("RISULTATO PATCH:", "OK" if ok else "PROBLEMI")
