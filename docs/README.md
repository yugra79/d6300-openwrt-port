# PORT OPENWRT — NETGEAR D6300 (BCM6362)

## Documenti
| File | Contenuto |
|---|---|
| **PORT_REPORT.md** | **report consolidato del progetto (executive summary)** |
| STATO_RICOSTRUZIONE_BCM6361.md | analisi hardware, firmware stock, stato bmips, matrice driver |
| ROADMAP_PORT_D6300.md | fasi 0-5, milestone, rischi |
| INSTALL_BUILD_D6300.md | come applicare i file e compilare |
| PROPOSTA_UPSTREAM.md | bozza per openwrt-devel / PR |
| TEST_PLAN_D6300.md | piano di test hardware (UART, CFE, backup NAND, flash, rollback) |
| BOOTLOG_WORKSHEET.md | foglio da compilare con i dati del boot log seriale |
| apply_port.sh | script per applicare il port a un albero OpenWrt su Linux |
| build_d6300.sh | build completa automatica (port + target + cferam + make) |
| UPSTREAM_PR_DRAFT.md | commit message ufficiali, PR description, Q&A reviewer |
| WIKI_D6300_DRAFT.md | bozza pagina wiki device (techdata, install, recovery) |
| DRIVER_MATRIX.md | matrice compatibili DTS -> driver verificati sui sorgenti reali |

## File del port (openwrt/)
| File | Destinazione nel tree OpenWrt |
|---|---|
| bmips-Makefile.patch | target/linux/bmips/Makefile |
| dts/bcm6362-netgear-d6300.dts | target/linux/bmips/dts/ |
| image/bcm6362.mk | target/linux/bmips/image/bcm6362.mk (device netgear_d6300) |
| bcm6362/base-files/etc/board.d/01_leds | target/linux/bmips/bcm6362/base-files/etc/board.d/ |
| bcm6362/base-files/etc/board.d/02_network | idem |
| bcm6362/base-files/lib/upgrade/platform.sh | target/linux/bmips/bcm6362/base-files/lib/upgrade/ |
| patches/0001-0006 + series | serie di patch git-style (uso: git am) |
| bcm63xx-cfe/netgear,d6300/cferam | CFE bootloader estratto (196.380 byte) — per la build dell'immagine |

## Script di supporto (cartella superiore)
| File | Funzione |
|---|---|
| analyze_stock.py | parsing header .chk e firme |
| analyze_payload.py | struttura payload, kernel, filesystem |
| parse_jffs2_final.py | parser JFFS2 con CRC (in rifinitura) |
| port/validate_new_port.py | validazione DTS + patch del port bcm6362 |
| port/build_port_files.py | rigenera i file del port dai riferimenti |

## Artefatti di validazione (build_test/)
| File | Contenuto |
|---|---|
| bcm6362-netgear-d6300.dtb | **DTB compilato con dtc 1.8.1 (11.764 byte)** |
| bcm6362-netgear-d6300.i | DTS preprocessato (pcpp, 15.431 byte) |
| roundtrip.dts | DTB riconvertito in DTS (722 righe, 108 nodi) |
| wfi_tag.bin | WFI tag 20 byte per il D6300 (chip 0x6361, flashType 3) |
| cferam.jffs2 | partizione JFFS2 cferam (200 KB) generata e verificata offline |
| simulated_image.bin | immagine CFE simulata (5,19 MB): kernel JFFS2 + cferam + WFI tag |
| LAYOUT_MAP.txt | mappa degli offset dell'immagine |
| factory_test.chk | .chk Netgear generato (formato stock verificato byte-per-byte) |

## Toolchain di validazione inclusa
- `dtc.exe` (DTC 1.8.1, MSYS2) in `default-workspace/dtc_win/`
- `pcpp` (preprocessore C Python) in `default-workspace/pylibs/`
- header dt-bindings in `default-workspace/dtc_inc/`
- script: `netgear-d6300/validate_new_port.py` (DTS + patch, bcm6362)

## Manutenzione / aggiornamento
| Cosa | Come |
|---|---|
| **Verificare TUTTO in un comando** | **`python3 netgear-d6300/run_all_checks.py`** (12 verifiche) |
| Controllare se OpenWrt master è cambiato | `python3 netgear-d6300/drift_check.py` |
| Rigenerare i file del port | `python3 netgear-d6300/port/build_port_files.py` |
| Ricompilare/validare il port | `python3 netgear-d6300/validate_new_port.py` |
| Rigenerare il port + patch | `python3 netgear-d6300/restructure_bcm6362.py` |
| Verificare la patch series | `python3 netgear-d6300/verify_patches.py` |
| Applicare a un albero OpenWrt | `./apply_port.sh <percorso port>` (su Linux) |

## Stato
- Fase 1 (analisi): COMPLETATA al 90% (cferam/kernel: estrazione da rifinire)
- Fase 2 (ricostruzione bmips): COMPLETATA
- Fase 3 (sviluppo): file pronti, manca build su Linux e cferam
- Fase 4 (test device): DA FARE (richiede UART + accesso fisico)
- Fase 5 (upstream): bozza pronta
| simulated_cfe_bin_bcm6362.bin | immagine cfe.bin simulata (13,48 MB, WFI tag valido) |
| LAYOUT_CFE_BIN_bcm6362.txt | mappa del layout dell'immagine |
