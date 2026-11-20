# PIANO DI TEST HARDWARE — NETGEAR D6300 (BCM6362)
Data: 19/11/2026 · Versione 1.0
Obiettivo: raccogliere i dati dal device, fare backup completo, flashare OpenWrt, verificare

---

## 0. MATERIALE NECESSARIO
| Oggetto | Note |
|---|---|
| **Adattatore USB-TTL CH340G** | 3,3V/5V commutabile (già disponibile ✓) |
| Cavetti dupont femmina-femmina | 3 fili: GND, TX, RX |
| Multimetro | per identificare i pin UART |
| Cacciavite / apertura router | viti torx o a scatto |
| PC con porta USB | Windows/Linux |
| Rete Ethernet tra PC e router | cavo diretto |
| (opz.) Programmatore/lettore NAND | solo se si vuole dump hardware |

---

## 1. APERTURA E IDENTIFICAZIONE UART
1. Scollegare alimentazione e cavi
2. Aprire il case (viti sotto / coperchio a scatto)
3. Cercare un **header 4 pin** (o 4 pad di test) vicino al SoC o al bordo:
   - tipicamente: **3V3 / GND / TX / RX** (a volte 5 pin con BOOT)
4. **GND**: multimetro in continuità con lo schermo metallico/connettore USB
5. **VCC**: ~3,3 V con router acceso (NON collegarlo)
6. **TX/RX**: ~3,3 V a riposo; il TX "lampeggia" durante il boot
7. Se i pad non sono etichettati: cercare la serigrafia o forum (TechInfoDepot/OpenWrt forum)

⚠️ **REGOLA**: collegare **solo GND, TX, RX**. Mai VCC. Jumper adattatore su **3,3 V**.

---

## 2. COLLEGAMENTO (con router SPENTO)
```
Adattatore CH340G          D6300
GND      ────────────────  GND
TXD      ────────────────  RXD (pin RX del router)
RXD      ────────────────  TXD (pin TX del router)
(jumper su 3.3V, VCC NON collegato)
```
Ordine: **GND per primo**, poi RX/TX.

---

## 3. SETUP SOFTWARE (PC Windows)
1. Installare driver **WCH CH340** (wch.cn) → appare **COMx** in Gestione dispositivi
2. **PuTTY**:
   - Connection type: **Serial**
   - Serial line: **COMx**
   - Speed: **115200**
   - Connection → Serial: 8 data bits, 1 stop, **no** parity, no flow control
3. **Logging**: Session → Logging → "All session output" → file `boot_D6300.log`
   (serve per l'upstream: log del boot CFE!)
4. Alimentare il router e osservare l'output

Se non si vede nulla:
- Verificare incrocio TX/RX (scambiarli è il 90% degli errori)
- Verificare GND comune
- Prova ad altre velocità: 115200 (standard), 57600, 38400
- Verificare 3,3V (non 5V) sul jumper

---

## 4. COSA REGISTRARE AL PRIMO BOOT (dati per il port!)

> 📄 Usa il foglio **BOOTLOG_WORKSHEET.md** per annotare tutti i dati.
Con il log di PuTTY salverai:
| Dato | Perché serve |
|---|---|
| Versione CFE e data build | per `CFE_WFI_VERSION` e compatibilità |
| **Board ID** (es. U12L216T00_NETGEAR) | per `NETGEAR_BOARD_ID` nella ricetta |
| **Chip ID** (6361) | conferma subtarget |
| **NAND**: modello, pagina, blocco, ECC | per `BLOCKSIZE/PAGESIZE/SUBSIZE` |
| **Flash type WFI** | per `CFE_WFI_FLASH_TYPE` |
| **Partition table / layout** | per il DTS (partizioni reali) |
| MAC address | per nvmem-cells nel DTS |
| Pesi e log di boot | documentazione upstream |

Comando se il CFE si ferma al prompt: `help` (elenco comandi), poi `b` per bootare.

---

## 5. COMANDI CFE (estratti dal cferam originale del D6300)
Dal firmware stock sono state estratte queste descrizioni (comandi tipici CFE bcm63xx):

| Comando | Descrizione (dal firmware) | Uso |
|---|---|---|
| `help` / `?` | elenco comandi | prima cosa da fare |
| `b` | "Print boot line and board parameter info" / boot | avvio |
| `f [ip:]file` | "Write image to the flash" (flash via TFTP) | **flash image** |
| `flashimage [ip:]file` | "Flashes a compressed image after the bootloader" | flash immagine compressa |
| `chkw` | "Write chkw image start from beginning of the flash" | **flash di un .chk Netgear** |
| `w` | "Write the whole image start from beginning of the flash" | immagine intera |
| `e` / `e n` / `e a` | "Erase NAND flash", "Erase [n]vram or all flash except bootrom" | erase (⚠️) |
| `d` | "Dump memory or registers" | **dump RAM/registri** |
| `s` | "Set memory or registers" | set |
| `boardid` / prompt interattivo | "Board Id (0-#", MAC, PSI, log size | configurazione board |
| `nvram` | erase persistent storage | ⚠️ |

Prompt interattivi visti nel firmware: Board Id, Number of MAC Addresses (1-32), Base MAC Address,
PSI size (1-64 KBytes), Backup PSI, System Log Size (0-256 KB), Main Thread Number,
Device Pin (WPS), Voice Board Configuration.

⚠️ **Mai** digitare comandi `e`/`nvram` senza backup: possono rendere il device non avviabile.

---

## 5-BIS. DETTAGLI CFE DEL D6300 (estratti dal firmware)
| Dato | Valore |
|---|---|
| Boot delay | configurabile **0-9 secondi** (utile per interrompere il boot) |
| Selezione immagine | 0=latest, 1=previous (**dual rootfs**) |
| IP di default CFE | **192.168.1.1** (bootline: `e=192.168.1.1:ffffff00 h=192.168.1.100`) |
| Modalità recovery | TFTP (`f`), `flashimage`, `chkw` (.chk), web upload, **NMRP** |
| Controllo block size | rifiuta immagini con block size ≠ atteso (128KB) |
| Messaggi da vedere | "Finished flashing image", "Booting from latest/previous image" |

⚠️ Nota: lo stock firmware usa 192.168.0.1, il **CFE recovery usa 192.168.1.1**.
Per interrompere il boot: aprire PuTTY PRIMA di accendere e premere un tasto
durante il countdown (o impostare Boot delay > 0 da menu CFE).

## 6. BACKUP COMPLETO (PRIMA DI QUALSIASI SCRITTURA)

### 6.1 Metodo A — dump NAND da CFE (consigliato)
1. Accendere col seriale connesso, interrompere il boot (spazio/tasto durante il countdown)
2. Dal prompt CFE:
   ```
   d <indirizzo> <lunghezza>       # dump memoria (verificare sintassi con help)
   ```
   oppure, se il CFE del D6300 supporta il dump della flash, salvare la NAND
3. Salvare tutto il log seriale nel file di logging PuTTY

### 6.2 Metodo B — shell stock (se accessibile)
1. Collegare Ethernet, IP PC 192.168.0.2
2. Login web stock (192.168.0.1) — verificare se è disponibile una shell di debug
3. Se disponibile:
   ```
   cat /proc/mtd                      # mappa partizioni
   dd if=/dev/mtd0 of=/tmp/backup_mtd0.bin
   dd if=/dev/mtd1 of=/tmp/backup_mtd1.bin
   ...
   ```
   scaricare i file via wget/tftp

### 6.3 Metodo C — telnetenable (Netgear)
Su alcuni Netgear il telnet è disabilitato ma attivabile con la utility
"telnetenable" (magic packet con MAC). Da provare in demo:
- Impostare il PC su 192.168.0.2
- `telnetenable.exe <MAC> <user> <pass>` (tool open source)
- `telnet 192.168.0.1` → se funziona, si ha shell root → metodo B

### 6.4 Backup firmware stock
Il file `D6300-V1.0.0.102_1.0.102.chk` è già salvato in `netgear-d6300/` ✓ (revert di emergenza).

---

## 6-BIS. PERCORSO .CHK (sperimentale, senza seriale)
Il formato .chk del D6300 è stato **completamente reversesato e verificato**
(header ricostruito byte-per-byte, tutti i checksum MATCH). Il generatore è
`netgear-d6300/make_chk.py`.

Possibile percorso (DA TESTARE, solo dopo backup):
1. generare l'immagine OpenWrt (`build_d6300.sh`)
2. avvolgerla in un .chk:
   ```
   python3 -c "import sys; sys.path.insert(0,'netgear-d6300'); import make_chk;      img=open('immagine.bin','rb').read();      open('openwrt_d6300.chk','wb').write(make_chk.make_chk(img))"
   ```
3. caricare il .chk dal **web UI stock** (Firmware Update)
4. ⚠️ RISCHIO: il web stock potrebbe rifiutare immagini non-Netgear o fare
   controlli aggiuntivi. Il metodo sicuro resta il **CFE seriale**.

## 7. FLASH DI OPENWRT (solo dopo backup verificato)
1. PC con **TFTP server** (tftpd32/tftpd64) sulla cartella con l'immagine
2. Rete: PC **192.168.0.2**, router **192.168.0.1**
3. Avviare il router con seriale; interrompere il boot → prompt CFE
4. Comandi (verificare con `help`):
   ```
   ipaddr 192.168.0.1
   serverip 192.168.0.2
   f 192.168.0.2:openwrt-bmips-bcm6362-netgear_d6300-squashfs-cfe.bin
   flashimage
   ```
   oppure per il .chk: `chkw 192.168.0.2:immagine.chk`
5. Attendere "Finished flashing image" (10-15 min)
6. Riavviare e monitorare il boot seriale

---

## 8. VERIFICA PRIMO BOOT (checklist)
- [ ] CFE carica il kernel OpenWrt (log seriale)
- [ ] Kernel boot senza panic
- [ ] Console root su UART (login prompt)
- [ ] `cat /proc/cpuinfo` → BMIPS4350 x2
- [ ] `cat /proc/mtd` → partizioni corrette
- [ ] `dmesg | grep -i nand` → MT29F1G08AAC, ECC ok
- [ ] LED power/internet/wlan
- [ ] Porte Ethernet (LAN/WAN) con `ip a`
- [ ] USB 2.0
- [ ] Wi-Fi 2.4G (se driver disponibile)
- [ ] PCIe/5G (best effort, BCM4360 probabilmente non supportato)

---

## 9. ROLLBACK (se qualcosa va storto)
1. Spegnere, riaccendere e interrompere il CFE
2. `chkw 192.168.0.2:D6300-V1.0.0.102_1.0.102.chk` → ripristina lo stock
   (dal CFE, IP PC **192.168.0.2** oppure **192.168.1.2** se il CFE usa la subnet 1.x)
3. Se il CFE non risponde:
   - Verificare seriale/TX-RX
   - Prova reset prolungato (30s) all'accensione
   - Se brick completo: programmatore NAND (CH341A + clip) con il dump di backup

---

## 10. DATI DA RACCOGLIERE PER L'UPSTREAM
Per la PR servono:
- [ ] Log completo del boot CFE (file PuTTY)
- [ ] Board ID e versione CFE/WFI
- [ ] `cat /proc/mtd` (dopo il port, o dal CFE)
- [ ] MAC address e posizione in flash
- [ ] GPIO di LED/pulsanti
- [ ] Modello switch (integrato o BCM53125)
- [ ] dmesg OpenWrt pulito
- [ ] Test sysupgrade + revert a stock documentato

---

## 11. RISCHI
| Rischio | Mitigazione |
|---|---|
| Brick del device | backup NAND + .chk stock + seriale |
| Danno elettrico (5V) | jumper 3,3V, mai VCC |
| Identificazione pin errata | multimetro, mai collegare VCC |
| Perdita di dati | backup PRIMA di ogni scrittura |
| Tempo | fare le cose con calma, una alla volta |


## 12. AGGIORNAMENTO POST-BOOTLOG (bcm6362) — 20/11

### 12.1 Console seriale (trovata e funzionante)
| J252 | Funzione | Note |
|---|---|---|
| pad 1 | linea dati (probabile RX router) | 3,29 V idle |
| **pad 2** | **GND** | 0 Ω verso massa |
| **pad 3** | **TX router** | 3,29 V idle, console a 115200 8N1 |
| pad 4 | linea dati (2ª linea) | 3,27 V idle |

Adattatore: CH340G, jumper **3,3 V**, COM. Attenzione: il **guscio USB non è GND**.

### 12.2 Bootloader
- CFE 1.0.38-112.70 (BCM96362), autoboot con **1 secondo** di delay
- A 115200 si ferma con "*** Press any key to stop auto run (1 seconds) ***"
  → per interrompere serve il **TXD dell'adattatore sul pad 1 o 4** (RX router)
- IP CFE: **192.168.1.1/24**, host IP 192.168.1.100
- Comandi CFE disponibili (stringhe nel cferam): `flashimage`, `chkw`, `f`, `w`,
  `e n/p/a`, `erasenvram`, `d`, `s`

### 12.3 Flash del firmware OpenWrt — DA CONFERMARE
Dopo la build (`build_d6300.sh`) l'artefatto è `openwrt-bmips-bcm6362-netgear_d6300-*.bin`
(immagine WFI: kernel + cferam JFFS2 + UBI + tag).
Metodi candidati (verificare sul device quale il CFE accetta):
1. **`flashimage`** dal prompt CFE (server TFTP su 192.168.1.100) con l'immagine
2. **`chkw`** con un `.chk` generato (formato verificato; avvolgere l'immagine)
3. Recovery Netgear (tftp/HTTP) se disponibile
In tutti i casi: **backup prima** (il `data`/nvram contengono MAC e configurazione).

### 12.4 Verifiche post-flash (ordine)
1. Boot log: `CFE version`, `NAND flash device: ST NAND512W3A2CN6`, `Chip ID: BCM6362B0`
2. Kernel OpenWrt: `Linux version ...` e `console [ttyS0] enabled`
3. `cat /proc/mtd` → cferom, rootfs_update, wfi, flag, data
4. `ip -br link` → lan1-4, wan; `ethtool` link
5. **MAC**: `ip link` deve mostrare il MAC del cferom (c4:04:15:18:35:10)
   → se sbagliato, correggere l'offset nvmem (0x6a0)
6. LED: test con `leds`/`ucidef` (GPIO 4/5/7/10/26/30)
7. WiFi: `dmesg | grep b43` (2.4 GHz) — il 5 GHz non è supportato
8. USB: `lsusb` con una chiavetta
9. Tasti: `evtest` — GPIO da identificare (TODO)
