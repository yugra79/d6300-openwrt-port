# Netgear D6300 — port OpenWrt (BCM6362) · CI build

Repository per compilare il firmware OpenWrt del **Netgear D6300** (piattaforma
**BCM6362**) usando GitHub Actions, senza installare Linux.

## Come compilare (3 passi)

1. **Actions** (tab in alto) → *Build D6300 firmware* → pulsante **Run workflow**
2. Attendi 1-2 ore (la build gira sui server GitHub)
3. Alla fine, nella pagina del run, scarica l'**artifact** `d6300-openwrt-images`

Dentro trovi:
- `openwrt-bmips-bcm6362-netgear_d6300-squashfs-cfe.bin` — immagine da flashare via CFE
- `openwrt-bmips-bcm6362-netgear_d6300-squashfs-sysupgrade.bin` — aggiornamenti successivi
- `openwrt-commit.txt` — commit OpenWrt usato (per build riproducibili)

## Cosa contiene

```
.github/workflows/build-d6300.yml   workflow di build
openwrt/patches/*.patch             3 patch del port (DTS, ricetta, base-files)
openwrt/bcm63xx-cfe/netgear,d6300/cferam.000   CFE RAM image (196.380 byte)
openwrt/dts/, openwrt/image/, openwrt/bcm6362/base-files/   file del port
docs/                               documentazione (test plan, prossimi passi, VPN/cloud...)
build_test/                         artefatti di validazione offline
scripts/                            suite di verifica e validatori
```

## Dopo la build

- **Flash**: via console seriale UART (vedi `docs/TEST_PLAN_D6300.md` §12 e
  `docs/PROSSIMI_PASSI.md`). Pinout J252: pad 2 = GND, pad 3 = TX (115200 8N1).
- **Verifiche**: `/proc/mtd`, MAC, LED, USB, b43 (2.4 GHz).
- **5 GHz**: non supportato (BCM4360, nessun driver mainline) — vedi
  `docs/ESPERIMENTO_MINI_PCIE_5GHZ.md` per l'upgrade con AR9280.
- **VPN/cloud**: vedi `docs/VPN_CLOUD_D6300.md`.

## Note

- Il workflow compila dal commit **master** di OpenWrt al momento del run:
  se le patch non applicano più (drift upstream), il log lo mostra e le patch
  vanno riallineate.
- Repository pubblico = minuti GitHub Actions illimitati; privato = 2000 min/mese
  (una build ~1-2 ore).
- Il file `cferam.000` proviene dal firmware stock del D6300 ed è usato dal
  package bcm63xx-cfe (la licenza/provenienza è la stessa del repo upstream
  openwrt/bcm63xx-cfe).
