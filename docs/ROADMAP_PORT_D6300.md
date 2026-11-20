# ROADMAP PORT OPENWRT — NETGEAR D6300 (BCM6361)

> NOTA: gli item fino a 3.41 si riferiscono al percorso storico (bcm6361).
> Dal bootlog (20/11) la piattaforma reale e' **BCM6362**: vedi item 3.42+ e STATO §27-30.

Versione: 19/11/2026 · Stato: Fase 1 (analisi) COMPLETATA, Fase 2-3 in corso

## Obiettivo
Portare OpenWrt sul Netgear D6300 (BCM6361, bmips) e proporne l'integrazione
upstream nel target `bmips`, come nuovo subtarget `bcm6361`.

---

## FASE 0 — PREPARAZIONE (completata)
| # | Attività | Stato | Esito |
|---|---|---|---|
| 0.1 | Verifica hardware (TechInfoDepot + autopsia) | ✅ | BCM6361, 128MB RAM, 128MB NAND, 5G BCM4360 mini-PCIe |
| 0.2 | Device acceso e raggiungibile (192.168.0.1) | ✅ | vivo, fw 1.0.0.102 |
| 0.3 | Backup firmware stock (.chk) | ✅ | D6300-V1.0.0.102_1.0.102.chk (24,72 MB, md5 6901...) |

## FASE 1 — ANALISI FIRMWARE STOCK (completata)
| # | Attività | Stato | Esito |
|---|---|---|---|
| 1.1 | Parsing header CHK | ✅ | magic 0x2A23245E, board **U12L216T00_NETGEAR** |
| 1.2 | Estrazione payload | ✅ | stock_payload.bin 25.919.508 byte |
| 1.3 | Identificazione componenti | ✅ | cferam (CFE) + kernel LZMA (vmlinux.lz) + JFFS2 dual-rootfs |
| 1.4 | Identificazione chip NAND | ✅ | **MT29F1G08AAC** → 2KB pagine, 128KB blocchi |
| 1.5 | Verifica supporto CFE NAND | ✅ | stringhe NAND/NAND_RFS_OFS/flashimage |
| 1.6 | Decompressione kernel stock | ✅ | kernel `vmlinuz` (ino 485) LZMA estratto e decompresso: **Linux 2.6.22** (2014) |
| 1.7 | Estrazione cferam | ✅ | `cferam.000` = **196.380 byte** estratto e validato (stringhe CFE) |
| 1.8 | Parser JFFS2 con CRC | ✅ | `parse_jffs2_final.py`: 15.902 nodi validati, 1.572 dirent |
| 1.9 | Struttura payload chiarita | ✅ | rootfs JFFS2 con layout inode decifrato e validato via data_crc |
| 1.10 | Provenienza CFE_RAM_FILE | ✅ | repo `openwrt/bcm63xx-cfe`; file `netgear,d6300/cferam` pronto (196.380 byte) |
| 1.11 | Estrazione completa rootfs stock | ✅ | 979 file, 42,5 MB (zlib per compr=6) |
| 1.12 | Dati board/LED/GPIO dal rootfs | ✅ | board_data (MAC), gpio_test.sh (sled gpio2/3, 24 LED), modello N1600 |
| 1.13 | Chip switch confermato | ✅ | **BCM53115** (173 occorrenze nel rootfs vs 1 di 53125) — DTS corretto |
| 1.14 | Mappatura porte da nvram | ✅ | eth0-eth3 = LAN1-4, eth4 = WAN; MAC lan/wan confermati |

## FASE 2 — RICOSTRUZIONE STATO BCM6361/bmips (completata al 90%)
| # | Attività | Stato | Esito |
|---|---|---|---|
| 2.1 | Verifica bmips master | ✅ | SUBTARGETS: 6318/6328/6358/6362/6368/63268 — **no 6361** |
| 2.2 | Verifica storico bcm63xx | ✅ | bcm6361 **mai esistito** (v17/v18/v19) |
| 2.3 | Individuazione piattaforma più vicina | ✅ | **bcm6362** (DGND3700v2) |
| 2.4 | Matrice driver disponibili | ✅ | vedi STATO_RICOSTRUZIONE_BCM6361.md §3 |
| 2.5 | Individuazione dati mancanti | ✅ | boot log seriale, /proc/mtd, GPIO, switch, WFI version |
| 2.6 | Scelta strategia DTS | ✅ | DTS "6362-compatibile" + compatible 6361, da correggere dopo il test |

## FASE 3 — SVILUPPO PORT (in corso)
| # | Attività | Stato | File |
|---|---|---|---|
| 3.1 | Subtarget `bcm6361` | ✅ pronta | `openwrt/bcm6361/target.mk` |
| 3.2 | Patch Makefile target | ✅ pronta | `openwrt/bmips-Makefile.patch` |
| 3.3 | `bcm6361.dtsi` | ✅ bozza | `openwrt/dts/bcm6361.dtsi` |
| 3.4 | `bcm6361-netgear-d6300.dts` | ✅ bozza | `openwrt/dts/bcm6361-netgear-d6300.dts` |
| 3.5 | Ricetta immagine | ✅ pronta | `openwrt/image/bcm6361.mk` |
| 3.6 | Kernel config | ✅ | `openwrt/bcm6361/config-6.18` |
| 3.7 | base-files rete/LED | ✅ bozza | `openwrt/base-files/...` |
| 3.8 | Compilazione DTS con dtc reale | ✅ | **dtc 1.8.1 (MSYS2) + pcpp: exit 0, DTB 13.285 byte**, 121 nodi, roundtrip OK |
| 3.8b | Compilazione completa OpenWrt (build) | ⬜ | richiede ambiente Linux + toolchain |
| 3.9 | cferam file | ⬜ | dipende da 1.7 |
| 3.10 | Patch pinctrl 6361 (se serve) | ⬜ | solo se il test mostra differenze |
| 3.11 | Validazione DTS | ✅ | `validate_dts.py`: struttura OK, 55/55 e 80/80 graffe, compatibili verificati |
| 3.12 | Guida build/installazione | ✅ | `INSTALL_BUILD_D6300.md` |
| 3.13 | Serie patch upstream (6 patch) | ✅ | `openwrt/patches/` — verificata su albero simulato |
| 3.15 | Validazione modello JFFS2/boot vs ricetta | ✅ | stock: dummy v0/ino2 + cferam.000 v1/ino3 = identico a cfe-jffs2-cferam |
| 3.16 | WFI tag: flash type corretto | ✅ | 3 = NAND 128k (da cfe-wfi-tag.py), NON 2 |
| 3.17 | Formato .chk decodificato | ✅ | header + checksum Netgear + confronto stock vs mkchkimg |
| 3.18 | DTS con warning estesi | ✅ | unit_address_vs_reg, simple_bus_reg, ... => 2 warning = identici al reference upstream |
| 3.19 | Patch series verificata con applier fedele | ✅ | applicata a albero con Makefile reale: 7 file OK byte-per-byte |
| 3.20 | Script apply_port.sh | ✅ | applicazione automatica su albero OpenWrt Linux |
| 3.21 | WFI tag generator | ✅ | `build_artifacts.py`: tag 20 byte (crc JAM, chip 0x6361, flashType 3) |
| 3.22 | JFFS2 cferam builder | ✅ | 200.084 byte, 52 nodi; roundtrip: cferam identico, dirent v0/v1 corretti |
| 3.23 | Review ricetta immagine | ✅ | rimosso PAD 496k (non multiplo di 128k), rimossi B43/WiFi, flash type 3 |
| 3.24 | Matrice driver verificata | ✅ | DRIVER_MATRIX.md: tutti i compatibili hanno driver (mainline/bmips/patch) |
| 3.25 | Drift check vs master | ✅ | nessun drift: riferimenti identici a master (Makefile, bcm6362.*, dgnd3700v2, config) |
| 3.26 | Header kernel verificato | ✅ | vmlinux.lz stock = cfe-bin-header.py (entry 0x80010000, size 1.500.201) |
| 3.27 | Layout immagine simulato | ✅ | kernel JFFS2 + pad 5MB + cferam JFFS2 + WFI tag: mappa verificata |
| 3.28 | Kernel config verificato | ✅ | tutti i simboli driver presenti (JFFS2 non necessario: lo legge il CFE) |
| 3.29 | Script build_d6300.sh | ✅ | build completa automatica su Linux (port + target + cferam + make) |
| 3.30 | Formato .chk verificato byte-per-byte | ✅ | header stock ricostruito identico (kernel/image/header checksum MATCH) |
| 3.31 | Generatore factory .chk | ✅ | `make_chk.py`: .chk D6300 con board id, region, versione e checksum corretti |
| 3.32 | Mappatura LED confermata | ✅ | gpio_test.sh: INET_FAIL=4, INET_ACT=5, GIGA=10, LAN10=26, LAN=30 + 24 serial LED |
| 3.33 | base-files per-subtarget | ✅ | spostati in `bcm6361/base-files/` (upstream), aggiunti 01_leds e platform.sh (sysupgrade) |
| 3.34 | Patch series PR-ready | ✅ | 6 patch con Subject+body+Signed-off-by, verificate |
| 3.35 | Report consolidato | ✅ | `PORT_REPORT.md` con tutte le evidenze |
| 3.36 | Suite di verifica unica | ✅ | `run_all_checks.py`: 10/10 verifiche superate |
| 3.37 | Upstream compliance: commenti in inglese | ✅ | 68 righe tradotte nei 6 file del port, 0 residui |
| 3.38 | FIX CRITICO: fallback SoC bcm6362 | ✅ | necessario per CPU freq/RAM autodetect (patch 200/201); precedente upstream bcm6369->bcm6368 |
| 3.39 | Suite estesa a 12 check | ✅ | aggiunti regression test: fallback SoC (critico) e power domain |
| 3.40 | Ispezione hardware da foto | ✅ | chip NAND reale = ST NAND512W3A2C (64MB, CFE-supportato); trovati TP100-TP105 (candidati console). Da verificare con boot log. |
| 3.42 | **Ristrutturazione su bcm6362** | ✅ | device `netgear_d6300` nel subtarget bcm6362: DTS (bcm53125, partizioni stock, LED, PCIe), ricetta 16k/512/496k/type2/0x5731, base-files; 3 patch verificate, DTS compilato (DTB 11.764 B) |
| 3.43 | Correzione nome cferam | ✅ | file nel JFFS2 = `cferam.000` (evidenza stock); ricetta/repo aggiornati, patch 0002 rigenerata |
| 3.44 | Coerenza partizioni verificata | ✅ | 5 partizioni senza overlap, entro 64 MB, 1 MB liberi in coda |
| 3.45 | Capienza wfi verificata | ✅ | kernel 5 MB + pad 496k → 24 MB liberi per UBI rootfs |
| 3.46 | Wiki + driver matrix aggiornati | ✅ | WIKI riscritta per bcm6362; nota driver matrix |
| 3.47 | Suite estesa a 10 check | ✅ | 10/10 superati |
| 3.48 | Immagine cfe.bin simulata | ✅ | struttura valida: cferam.000 + kernel 5MB + UBI + WFI tag (chip 0x6362, flash 2) |
| 3.49 | Pacchetto di consegna | ✅ | `D6300_OpenWrt_Port_2026-11-20.zip` con port, docs, artefatti |
| 3.50 | Suite a 11 check | ✅ | 11/11 superati |
| 3.51 | Drift check vs master | ✅ | 6 file di riferimento identici a OpenWrt master (nessun drift) |
| 3.52 | QC documenti finale | ✅ | INSTALL_BUILD e PROPOSTA_UPSTREAM riscritti per bcm6362; note storiche; titoli allineati |
| 3.53 | Guida VPN + cloud privato | ✅ | `VPN_CLOUD_D6300.md`: WireGuard, ksmbd, filebrowser, rclone, extroot, limiti |
| 3.54 | Scheda prossimi passi + pacchetto finale | ✅ | `PROSSIMI_PASSI.md`; ZIP aggiornato (build, flash, PR, upgrade) |
| 3.41 | **BOOTLOG COMPLETO catturato** | ✅ | console UART su J252 (pad2=GND, pad3=TX). Scoperto: piattaforma **BCM6362** (non 6361), NAND ST 64MB 16KB/512B, partizioni stock. Ricetta da riallineare a DGND3700v2 (16k/type2/496k/0x5731). |
| 3.14 | Validazione DTS con label/reference | ✅ | `validate_dts.py` — 0 problemi, 14 righe di diff vs bcm6362 |

## FASE 4 — TEST SU DISPOSITIVO (piano pronto, richiede accesso fisico/seriale)

> 📄 **Piano dettagliato**: `TEST_PLAN_D6300.md` — materiale, UART, comandi CFE
> (estratti dal firmware), backup NAND, flash, verifica, rollback.
| # | Attività | Criterio di accettazione |
|---|---|---|
| 4.1 | Collegamento UART (115200 8N1) | log CFE visibile |
| 4.2 | Boot log CFE → board id, WFI, partizioni | dati raccolti |
| 4.3 | Shell stock → /proc/mtd, dmesg, GPIO | mappa partizioni reale |
| 4.4 | Scrittura immagine via CFE (tftp/flashimage) o sysupgrade | avvio OpenWrt |
| 4.5 | Verifica ser: console, ethernet, LED, pulsanti | boot completo |
| 4.6 | Verifica NAND/UBI (sola lettura prima) | mtd funzionante |
| 4.7 | Verifica USB, PCIe (WiFi 5G BCM4360), switch | funzioni base |
| 4.8 | Test stabilità 24h | nessun kernel panic |

**Regola d'oro**: mai scrivere la flash senza backup dump completo della NAND stock
(`dd if=/dev/mtd0 ...` da CFE o seriale) e senza modalità di recupero verificata.

## FASE 5 — UPSTREAM (proposta community)
| # | Attività | Criterio |
|---|---|---|
| 5.1 | Preparare patch set pulito (git format-patch) | ✅ 6 patch pronte e verificate (UPSTREAM_PR_DRAFT.md) |
| 5.1b | Commit message + PR description | ✅ UPSTREAM_PR_DRAFT.md |
| 5.1c | Bozza pagina wiki device | ✅ WIKI_D6300_DRAFT.md |
| 5.2 | Documentazione device (wiki OpenWrt) | pagina D6300 con dati testati |
| 5.3 | Invio a openwrt-devel | mail + PR su GitHub |
| 5.4 | Risposta a review | revisione e iterazione |
| 5.5 | Merge nel master | target bmips con subtarget bcm6361 |

## RISCHI E MITIGAZIONI
| Rischio | Probabilità | Mitigazione |
|---|---|---|
| Driver 6362 non compatibili col 6361 | media | DTS con compatibili 6362; patch driver mirate |
| Brick del device | media | backup NAND completo + CFE recovery + seriale |
| Pinctrl 6361 diverso | media | derivare da datasheet/CFE; fallback GPIO generico |
| WiFi 5G (BCM4360) non funzionante | alta | è un modulo "smart" con CPU propria: spesso non supportato (come su altri router) |
| Modem DSL non supportato | certa | documentare: D6300 usato come router Ethernet |
| NAND geometry errata | bassa | chip identificato (MT29F1G08AAC) |
| Tempo limitato | alta | roadmap incrementale: prima boot minimo, poi periferiche |

## MILESTONE
1. **M1** — Build compila con subtarget bcm6361 (no errori) → verifica in CI locale
2. **M2** — Primo boot su device (console seriale)
3. **M3** — Rete funzionante (LAN/WAN) + LED
4. **M4** — Port completo e testato (USB, PCIe best-effort)
5. **M5** — Patch upstream accettate
