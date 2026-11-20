# MATRICE DRIVER — compatibili DTS del Netgear D6300 (BCM6362)
Verificata sui sorgenti reali (kernel master + target bmips + patch OpenWrt)
Data: 19/11/2026

## Legenda
- ✅ = driver trovato e verificato nel sorgente
- 🔧 = fornito da file/patch del target bmips
- ⚙️ = gestito da arch/mips/bmips o fallback generico
- ⚠️ = da verificare al primo boot (non bloccante)

## Matrice completa

| Compatible nel DTS | Driver / gestione | Fonte verificata | Stato |
|---|---|---|---|
| `brcm,bcm6362` | SoC: arch/mips/bmips (dt-bindings bmips) | OpenWrt bmips | ✅ |
| `brcm,bmips4350` | CPU: arch/mips/bmips | kernel | ⚙️ |
| `mti,cpu-interrupt-controller` | irqchip MIPS | kernel | ⚙️ |
| `brcm,bcm6362-clocks` | clk-bcm63xx-gate.c | kernel | ✅ |
| `brcm,bcm6345-reset` | reset-bcm6345.c | kernel | ✅ |
| `brcm,bcm6345-l1-intc` | irq-bcm6345-l1.c | kernel | ✅ |
| `brcm,bcm6345-ext-intc` | irq-bcm6345-ext | patch 100 bmips | 🔧 |
| `brcm,bcm6345-uart` | bcm63xx_uart.c | kernel | ✅ |
| `brcm,bcm7038-wdt` | bcm7038_wdt.c | kernel | ✅ |
| `brcm,bcm6362-pinctrl` | pinctrl-bcm6362.c | kernel | ✅ |
| `brcm,bcm6362-gpio` | pinctrl-bcm63xx.c | kernel | ✅ |
| `brcm,bcm6362-gpio-sysctl` | syscon (simple-mfd) | kernel (syscon) | ⚙️ |
| `brcm,nand-bcm6368` + `brcm,brcmnand` | brcmnand/bcm6368_nand.c | kernel | ✅ |
| `brcm,nandcs` | brcmnand (bindings) | kernel | ✅ |
| `brcm,bcm6362-enetsw` | bcm6368-enetsw.c | **file bmips** | 🔧 |
| `brcm,bcm6362-switch` | b53_mmap.c (DSA) | kernel | ✅ |
| `brcm,bcm53115` | b53_mdio.c | kernel | ✅ |
| `brcm,bcm6368-mdio-mux` | mdio-mux-bcm6368.c | kernel | ✅ |
| `brcm,bcm6328-pcie` | pcie-bcm6328.c | **file bmips** | 🔧 |
| `brcm,bcm6362-ehci` | generic-ehci (fallback) | kernel | ⚙️ |
| `brcm,bcm6362-ohci` | generic-ohci (fallback) | kernel | ⚙️ |
| `brcm,bcm6362-usbh-phy` | phy-bcm63xx-usbh.c | kernel | ✅ |
| `brcm,bcm6328-leds` | leds-bcm6328.c | kernel | ✅ |
| `brcm,bcm6328-hsspi` | spi-bcm63xx-hsspi.c | kernel | ✅ |
| `brcm,bcm6358-spi` | spi-bcm63xx.c | kernel | ✅ |
| `brcm,wfi` | mtdsplit BCM WFI | OpenWrt (`CONFIG_MTD_SPLIT_BCM_WFI_FW=y`) | 🔧 |
| `brcm,bcm6368-rng` | hw_random bcm63xx | **da verificare** | ⚠️ |
| `netgear,d6300` | machine (DTS) | questo port | ⚙️ |
| `gpio-keys-polled` | gpio-keys | kernel | ✅ |
| `gpio-leds` | leds-gpio | kernel | ✅ |
| `fixed-clock`, `fixed-partitions`, `fixed-layout` | kernel | ✅ |
| `syscon-reboot`, `simple-bus`, `simple-mfd` | kernel | ✅ |

## Note importanti
1. **enetsw** e **pcie-bcm6328** non sono in mainline: sono forniti come **file**
   da `target/linux/bmips/files/` (verificato: `bcm6368-enetsw.c` registra
   `brcm,bcm6362-enetsw`; `pcie-bcm6328.c` registra `brcm,bcm6328-pcie`).
2. **switch interno**: `brcm,bcm6362-switch` è gestito da **b53_mmap.c** (DSA)
   → il nodo `switch0` del DTS è corretto.
3. **switch esterno**: `brcm,bcm53115` gestito da **b53_mdio.c** → il DTS usa
   il compatible giusto (confermato dal rootfs stock: 173 occorrenze di bcm53115).
4. **RNG** (`brcm,bcm6368-rng`): driver non localizzato nei sorgenti esaminati;
   è opzionale (hw_random) e non blocca il boot → ⚠️ da verificare.
5. **ehci/ohci**: `brcm,bcm6362-ehci/ohci` non hanno driver dedicato ma il
   fallback `generic-ehci`/`generic-ohci` è presente nella lista compatible dei
   driver generici → il probe funziona tramite il secondo compatible.

## Metodo di verifica
Script: `verify_drivers.py`, `verify_drivers2-5.py`
Sorgenti scaricati in: `netgear-d6300/driver_ref/`
- kernel master: drivers/clk/bcm, drivers/reset, drivers/irqchip, drivers/tty/serial,
  drivers/watchdog, drivers/pinctrl/bcm, drivers/mtd/nand/raw/brcmnand,
  drivers/net/dsa/b53, drivers/net/mdio, drivers/phy/broadcom, drivers/leds, drivers/spi
- OpenWrt bmips: patches-6.18/*, files/drivers/**, files/include/dt-bindings/**

---

## NOTA (20/11/2026) — piattaforma BCM6362

Il port è stato ristrutturato come device del subtarget **bcm6362**: tutti i
driver dei blocchi usati (enetsw, switch BCM53125 via b53, NAND brcmnand,
UART, EHCI/OHCI/USB PHY, PCIe BCM6328, watchdog, LED bcm6328, pinctrl bcm6362,
b43 per il 2.4 GHz) sono **già supportati dal target bmips upstream**.
Non servono patch driver: le verifiche di questa matrice restano valide come
riferimento dei compatibili usati nel DTS.
