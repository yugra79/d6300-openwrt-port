# -*- coding: utf-8 -*-
"""RISTRUTTURAZIONE: port del Netgear D6300 come device del subtarget bcm6362.
Crea: nuovo DTS, nuova ricetta bcm6362.mk, base-files del bcm6362 modificati,
patch series ridotta, e archivia i vecchi file bcm6361.
"""
import io
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = os.path.join(HERE, "port")
OW = os.path.join(PORT, "openwrt")
REF = os.path.join(HERE, "openwrt_ref")
REB = os.path.join(REF, "bcm6362_basefiles")

os.makedirs(os.path.join(OW, "dts"), exist_ok=True)
os.makedirs(os.path.join(OW, "image"), exist_ok=True)
os.makedirs(os.path.join(OW, "bcm6362", "base-files", "etc", "board.d"), exist_ok=True)
os.makedirs(os.path.join(OW, "bcm6362", "base-files", "lib", "upgrade"), exist_ok=True)

# ============ 1) NUOVO DTS ============
DTS = """// SPDX-License-Identifier: GPL-2.0-or-later

#include "bcm6362.dtsi"

/ {
	model = "Netgear D6300";
	compatible = "netgear,d6300", "brcm,bcm6362";

	// TODO: boot/running LEDs, once the mapping of the 24 serial LED
	// positions is known (see comments below).

	leds {
		compatible = "gpio-leds";

		// LED connections confirmed from the stock firmware gpio_test.sh:
		//   INET_FAIL_LED    = GPIO 4
		//   INET_ACT_LED     = GPIO 5
		//   GIGA_10_LINK_LED = GPIO 7
		//   GIGA_LINK_LED    = GPIO 10
		//   LAN_10_LINK_LED  = GPIO 26
		//   LAN_LINK_LED     = GPIO 30
		led_internet_fail: led-4 {
			label = "red:internet";
			gpios = <&gpio 4 GPIO_ACTIVE_LOW>;
		};

		led_internet_act: led-5 {
			label = "amber:internet";
			gpios = <&gpio 5 GPIO_ACTIVE_LOW>;
		};

		led_giga10: led-7 {
			label = "green:giga10";
			gpios = <&gpio 7 GPIO_ACTIVE_LOW>;
		};

		led_giga: led-10 {
			label = "green:giga";
			gpios = <&gpio 10 GPIO_ACTIVE_LOW>;
		};

		led_lan10: led-26 {
			label = "green:lan10";
			gpios = <&gpio 26 GPIO_ACTIVE_LOW>;
		};

		led_lan: led-30 {
			label = "green:lan";
			gpios = <&gpio 30 GPIO_ACTIVE_LOW>;
		};
	};

	// TODO: keys (reset/wps/wlan). The stock firmware does not expose the
	// GPIO numbers; they must be determined on the device before enabling.
};

&ehci {
	status = "okay";
};

&ethernet {
	status = "okay";

	nvmem-cells = <&macaddr_cferom_6a0>;
	nvmem-cell-names = "mac-address";
};

&mdio_ext {
	switch@1e {
		compatible = "brcm,bcm53125";
		reg = <30>;

		dsa,member = <1 0>;

		ports {
			#address-cells = <1>;
			#size-cells = <0>;

			port@0 {
				reg = <0>;
				label = "lan1";
			};

			port@1 {
				reg = <1>;
				label = "lan2";
			};

			port@2 {
				reg = <2>;
				label = "lan3";
			};

			port@3 {
				reg = <3>;
				label = "lan4";
			};

			port@4 {
				reg = <4>;
				label = "wan";
			};

			port@8 {
				reg = <8>;

				phy-mode = "rgmii-id";
				ethernet = <&switch0port4>;

				fixed-link {
					speed = <1000>;
					full-duplex;
				};
			};
		};
	};
};

&nflash {
	status = "okay";

	nandcs@0 {
		compatible = "brcm,nandcs";
		reg = <0>;
		nand-ecc-step-size = <512>;
		nand-ecc-strength = <15>;
		nand-on-flash-bbt;

		#address-cells = <1>;
		#size-cells = <1>;

		partitions {
			compatible = "fixed-partitions";
			#address-cells = <1>;
			#size-cells = <1>;

			// Partition layout derived from the stock firmware boot log
			// (Linux 2.6.30, bcm963xx_mtd): nvram/rootfs_update/rootfs/data.
			// The CFE boots the "latest image" from the rootfs area (0x1d80000).
			// TODO: verify the exact CFE layout (cferom size, flags area)
			// from the CFE prompt before the upstream submission.

			partition@0 {
				label = "cferom";
				reg = <0x0000000 0x0004000>;
				read-only;

				nvmem-layout {
					compatible = "fixed-layout";
					#address-cells = <1>;
					#size-cells = <1>;

					// TODO: verify the MAC offset on the device
					// (DGND3700v2 uses 0x6a0 in its cferom).
					macaddr_cferom_6a0: macaddr@6a0 {
						reg = <0x6a0 0x6>;
					};
				};
			};

			partition@4000 {
				label = "rootfs_update";
				reg = <0x0004000 0x1d7c000>;
			};

			partition@1d80000 {
				compatible = "brcm,wfi";
				label = "wfi";
				reg = <0x1d80000 0x1d7c000>;
				brcm,cferam = "cferam";
			};

			partition@3afc000 {
				label = "flag";
				reg = <0x3afc000 0x0004000>;
				read-only;
			};

			partition@3b00000 {
				label = "data";
				reg = <0x3b00000 0x0400000>;
			};
		};
	};
};

&ohci {
	status = "okay";
};

&pcie {
	status = "okay";
};

&pinctrl {
	pinctrl_leds: leds {
		function = "led";
		pins = "gpio1";
	};
};

&switch0 {
	dsa,member = <0 0>;

	ports {
		switch0port4: port@4 {
			reg = <4>;
			label = "extsw";

			phy-mode = "rgmii-id";

			fixed-link {
				speed = <1000>;
				full-duplex;
			};
		};
	};
};

&uart0 {
	status = "okay";
};

&usbh {
	status = "okay";
};

// Note: the stock firmware also drives the 24 serial LEDs on GPIO2 (clock)
// and GPIO3 (data), plus GPIO 32/33/34 directly. Their function mapping is
// unknown; the serial LED controller is therefore left disabled for now.
"""
P = os.path.join(OW, "dts", "bcm6362-netgear-d6300.dts")
io.open(P, "w", encoding="utf-8", newline="\n").write(DTS)
print("scritto:", P.replace(HERE, "."), len(DTS), "byte")

# ============ 2) RICETTA bcm6362.mk ============
up = io.open(os.path.join(REF, "bcm6362.mk"), encoding="utf-8").read()
assert "netgear_dgnd3700-v2" in up, "bcm6362.mk upstream non valido"

device = """define Device/netgear_d6300
  $(Device/bcm63xx-nand)
  DEVICE_VENDOR := NETGEAR
  DEVICE_MODEL := D6300
  CHIP_ID := 6362
  CFE_RAM_FILE := netgear,d6300/cferam
  CFE_RAM_JFFS2_NAME := cferam
  CFE_RAM_JFFS2_PAD := 496k
  BLOCKSIZE := 16k
  PAGESIZE := 512
  DEVICE_PACKAGES += $(USB2_PACKAGES) \\
    $(B43_PACKAGES) \\
    kmod-leds-bcm6328 kmod-leds-gpio
  CFE_WFI_FLASH_TYPE := 2
  CFE_WFI_VERSION := 0x5731
endef
TARGET_DEVICES += netgear_d6300
"""
marker = "TARGET_DEVICES += netgear_dgnd3700-v2"
assert marker in up
new = up.replace(marker, marker + "\n\n" + device.rstrip("\n"), 1)
P = os.path.join(OW, "image", "bcm6362.mk")
io.open(P, "w", encoding="utf-8", newline="\n").write(new)
print("scritto:", P.replace(HERE, "."), len(new), "byte")

# ============ 3) BASE-FILES bcm6362 ============
def sub(base, name):
    src = os.path.join(REB, base)
    t = io.open(src, encoding="utf-8").read()
    return t


# 02_network
t = sub("etc_board.d_02_network", "02_network")
t = t.replace("""huawei,hg253s-v2 |\\
netgear,dgnd3700-v2)
	ucidef_set_interfaces_lan_wan "lan1 lan2 lan3 lan4" "wan\"""",
              """huawei,hg253s-v2 |\\
netgear,d6300 |\\
netgear,dgnd3700-v2)
	ucidef_set_interfaces_lan_wan "lan1 lan2 lan3 lan4" "wan\"""")
P = os.path.join(OW, "bcm6362", "base-files", "etc", "board.d", "02_network")
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("scritto:", P.replace(HERE, "."))

# 01_leds
t = sub("etc_board.d_01_leds", "01_leds")
t = t.replace("""netgear,dgnd3700-v2)
	ucidef_set_led_usbport "usb1" "USB1" "green:usb1" "usb1-port1" "usb2-port1"
	ucidef_set_led_usbport "usb2" "USB2" "green:usb2" "usb1-port2" "usb2-port2"
	;;""",
              """netgear,d6300)
	ucidef_set_led_netdev "internet" "Internet" "amber:internet" "wan"
	ucidef_set_led_netdev "lan" "LAN" "green:lan" "lan"
	;;
netgear,dgnd3700-v2)
	ucidef_set_led_usbport "usb1" "USB1" "green:usb1" "usb1-port1" "usb2-port1"
	ucidef_set_led_usbport "usb2" "USB2" "green:usb2" "usb1-port2" "usb2-port2"
	;;""")
P = os.path.join(OW, "bcm6362", "base-files", "etc", "board.d", "01_leds")
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("scritto:", P.replace(HERE, "."))

# platform.sh
t = sub("lib_upgrade_platform.sh", "platform.sh")
t = t.replace("""	huawei,hg253s-v2 |\\
	netgear,dgnd3700-v2)""",
              """	huawei,hg253s-v2 |\\
	netgear,d6300 |\\
	netgear,dgnd3700-v2)""")
P = os.path.join(OW, "bcm6362", "base-files", "lib", "upgrade", "platform.sh")
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("scritto:", P.replace(HERE, "."))

# ============ 4) ARCHIVIA VECCHI FILE bcm6361 ============
old = os.path.join(PORT, "OLD_bcm6361_subtarget")
os.makedirs(old, exist_ok=True)
to_move = [
    os.path.join(OW, "bcm6361"),
    os.path.join(OW, "dts", "bcm6361.dtsi"),
    os.path.join(OW, "dts", "bcm6361-netgear-d6300.dts"),
    os.path.join(OW, "image", "bcm6361.mk"),
]
for p in to_move:
    if os.path.exists(p):
        dst = os.path.join(old, os.path.basename(p) if os.path.isfile(p) else "bcm6361")
        if os.path.exists(dst):
            shutil.rmtree(dst) if os.path.isdir(dst) else os.remove(dst)
        shutil.move(p, dst)
        print("archiviato:", p.replace(HERE, "."), "->", dst.replace(HERE, "."))

# ============ 5) PATCH SERIES ============
PAT = os.path.join(OW, "patches")
os.makedirs(PAT, exist_ok=True)
for f in os.listdir(PAT):
    os.remove(os.path.join(PAT, f))

import difflib
import hashlib


def new_file_diff(path, data):
    lines = data.splitlines()
    out = ["diff --git a/%s b/%s" % (path, path),
           "new file mode 100644",
           "index 0000000.." + hashlib.sha1(data.encode()).hexdigest()[:7],
           "--- /dev/null",
           "+++ b/%s" % path,
           "@@ -0,0 +1,%d @@" % len(lines)]
    out += ["+" + l for l in lines]
    return "\n".join(out) + "\n"


def mod_diff(path, old, new):
    a, b = old.splitlines(), new.splitlines()
    diff = list(difflib.unified_diff(a, b, fromfile="a/" + path, tofile="b/" + path, lineterm=""))
    out = ["diff --git a/%s b/%s" % (path, path),
           "index %s..%s 100644" % (hashlib.sha1(old.encode()).hexdigest()[:7],
                                    hashlib.sha1(new.encode()).hexdigest()[:7]),
           "--- a/%s" % path,
           "+++ b/%s" % path]
    out += diff[2:]
    return "\n".join(out) + "\n"


def mkpatch(n, subject, body_lines, diffs):
    name = "%04d-%s.patch" % (n, subject.split(":")[-1].strip().lower().replace(" ", "-"))
    txt = ("From 0000000000000000000000000000000000000000 Mon Sep 17 00:00:00 2001\n"
           "From: Port D6300 <port@example.org>\n"
           "Date: Fri, 20 Nov 2026 15:30:00 +0300\n"
           "Subject: [PATCH] %s\n\n" % subject)
    for l in body_lines:
        txt += l + "\n"
    txt += "\n---\n" + "\n".join(diffs) + "\n-- \n2.43.0\n"
    io.open(os.path.join(PAT, name), "w", encoding="utf-8", newline="\n").write(txt)
    print("  patch:", name, len(txt), "byte")
    return name


series = []
# 0001 DTS
series.append(mkpatch(1, "bmips: add Netgear D6300 device tree", [
    "Add support for the Netgear D6300, a BCM6362 based VDSL/ADSL router",
    "with 128 MB RAM, 64 MB NAND, 5x GbE (BCM53125 switch), 2x USB 2.0,",
    "an integrated 2.4 GHz radio and a BCM4360 5 GHz module on mini-PCIe.",
    "",
    "Board data derived from the stock firmware analysis and boot log:",
    "- NAND: ST NAND512W3A2CN6 (64 MB, 16 KB blocks, 512 B pages)",
    "- switch: BCM53125 (5 GbE ports, RGMII to the internal switch)",
    "- port mapping: lan1-lan4, wan",
    "- LEDs: internet/giga/lan via GPIO 4/5/7/10/26/30",
    "- partition layout: cferom, rootfs_update, wfi, flag, data",
    "",
    "The 5 GHz BCM4360 module is not supported (no mainline driver).",
], [new_file_diff("target/linux/bmips/dts/bcm6362-netgear-d6300.dts", DTS)]))

# 0002 ricetta
series.append(mkpatch(2, "bmips: bcm6362: add Netgear D6300 image", [
    "Add the image recipe for the Netgear D6300:",
    "- 16 KB blocks / 512 B pages, matching the ST NAND512W3A2CN6",
    "- cferam from bcm63xx-cfe (netgear,d6300/cferam)",
    "- 496k cferam JFFS2 padding (multiple of the 16 KB erase block)",
    "- CFE_WFI_FLASH_TYPE 2 (16 KB blocks) and version 0x5731",
    "- USB 2.0, b43 (2.4 GHz) and GPIO LED packages",
], [mod_diff("target/linux/bmips/image/bcm6362.mk", up, new)]))

# 0003 base-files
diffs = []
f1 = os.path.join(REB, "etc_board.d_01_leds")
new1 = io.open(os.path.join(OW, "bcm6362", "base-files", "etc", "board.d", "01_leds"),
               encoding="utf-8").read()
diffs.append(mod_diff("target/linux/bmips/bcm6362/base-files/etc/board.d/01_leds",
                      io.open(f1, encoding="utf-8").read(), new1))
f2 = os.path.join(REB, "etc_board.d_02_network")
new2 = io.open(os.path.join(OW, "bcm6362", "base-files", "etc", "board.d", "02_network"),
               encoding="utf-8").read()
diffs.append(mod_diff("target/linux/bmips/bcm6362/base-files/etc/board.d/02_network",
                      io.open(f2, encoding="utf-8").read(), new2))
f3 = os.path.join(REB, "lib_upgrade_platform.sh")
new3 = io.open(os.path.join(OW, "bcm6362", "base-files", "lib", "upgrade", "platform.sh"),
               encoding="utf-8").read()
diffs.append(mod_diff("target/linux/bmips/bcm6362/base-files/lib/upgrade/platform.sh",
                      io.open(f3, encoding="utf-8").read(), new3))
series.append(mkpatch(3, "bmips: bcm6362: add Netgear D6300 base-files", [
    "Add the Netgear D6300 to the bcm6362 base-files:",
    "- 01_leds: netdev triggers for the internet and LAN LEDs",
    "- 02_network: LAN1-4 / WAN configuration",
    "- platform.sh: sysupgrade via nand_do_upgrade",
], diffs))

io.open(os.path.join(PAT, "series"), "w", encoding="utf-8", newline="\n").write("\n".join(series) + "\n")
print("series:", len(series), "patch")
print("DONE")
