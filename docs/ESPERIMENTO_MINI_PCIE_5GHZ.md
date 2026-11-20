# Esperimento: sostituzione scheda mini-PCIe 5 GHz del D6300

Obiettivo: ottenere il **5 GHz funzionante in OpenWrt** sostituendo la scheda
originale BCM4360 (senza driver mainline) con una scheda **Atheros AR9280**
supportata da `ath9k`.

## 1. Hardware

| Elemento | Dettaglio |
|---|---|
| Slot | mini-PCIe (PCIe x1), alimentazione 3,3 V |
| Scheda originale | Broadcom **BCM94360** con chip **BCM4360KMLG** (802.11ac 3x3, PN Netgear T77H390T00) — da **conservare** per il firmware stock |
| Scheda sostitutiva | **Atheros AR9280** (mini-PCIe, es. AR5BXB92): 2x2 802.11n dual-band 300 Mbps, supportata da `ath9k` in mainline |
| Antenne | La scheda AR9280 ha **2 connettori U.FL**; il D6300 ha 3 cavi (3x3) → collegarne 2, il terzo resta libero |
| Costo indicativo | 10-20 EUR (usata) |

## 2. Procedura fisica

1. Scollegare alimentazione e aprire il router
2. Svitare e rimuovere la scheda BCM4360 (conservarla in busta antistatica)
3. Inserire la AR9280 nello slot mini-PCIe, avvitare
4. Collegare 2 dei 3 cavi antenna ai connettori U.FL della AR9280
5. Richiudere e alimentare

## 3. Verifica in OpenWrt (quando il port sarà pronto)

1. `lspci` (o `cat /sys/bus/pci/devices/*/vendor`) → deve comparire
   **168c:002a** (AR9280)
2. `dmesg | grep ath9k` → ath9k carica la scheda e crea `wlan0`/`phy0`
3. `iw phy` → deve elencare le bande **2.4 GHz e 5 GHz** e i canali
4. Configurare l'AP 5 GHz in `/etc/config/wireless` (hostapd)
5. Impostare il dominio regolatorio `IT`

## 4. Note e rischi

- Il firmware stock **non userà** la AR9280 (usa il driver `wl` Broadcom):
  per tornare allo stock rimontare la scheda originale
- La slot è PCIe standard: nessuna whitelist lato CFE
- La scheda AR9280 può dare anche il 2.4 GHz, ma il 2.4 GHz del D6300 è
  già integrato nel SoC (BCM435f, b43): evitare conflitti, usare una radio per banda
- Antenne: il D6300 ha 3 cavi per la 5 GHz; con 2x2 si perdono i 3x3 (velocità
  massima 300 Mbps invece di 1300) ma si guadagna il supporto mainline
- Regolatorio: la AR9280 ha un EEPROM con dominio regolatorio proprio; ath9k
  applica le regole FCC/ETSI — verificare i canali consentiti in Italia
- Nessuna modifica necessaria al DTS: `&pcie` è già abilitato in bcm6362.dtsi;
  `kmod-ath9k` si installa via opkg (o si aggiunge a DEVICE_PACKAGES in un secondo momento)

## 5. Esito atteso

| Banda | Prima (BCM4360) | Dopo (AR9280) |
|---|---|---|
| 5 GHz | ❌ nessun driver | ✅ **802.11n 300 Mbps** (ath9k) |
| 2.4 GHz | b43 (BCM435f) | b43 (BCM435f) — invariato |

Se l'esperimento funziona, la limitazione "5 GHz non supportato" si riduce a
"5 GHz AC non supportato, ma 5 GHz N sì con scheda sostitutiva" — e la cosa
può essere documentata nella pagina wiki del device.
