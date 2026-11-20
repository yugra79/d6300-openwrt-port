# PROSSIMI PASSI — cosa fare quando hai Linux e il router

Scheda rapida · 20/11/2026 · progetto D6300 (base: `D6300_OpenWrt_Port_2026-11-20.zip`)

## A. Build (30-60 min, una volta sola)

Serve Linux (Ubuntu/WSL2/VM). Su Windows:
```powershell
wsl --install -d Ubuntu      # poi riavvia
```
Su Ubuntu:
```bash
cd /mnt/c/Users/padd0l/Documents/deepseek-harness/default-workspace
# estrai il pacchetto se non l'hai fatto
unzip D6300_OpenWrt_Port_2026-11-20.zip
cd D6300_OpenWrt_Port
sudo apt update && sudo apt install -y build-essential git python3 rsync
./scripts/build_d6300.sh /mnt/c/.../D6300_OpenWrt_Port
# (script: clona OpenWrt, applica le 3 patch, mette il cferam, builda)
```
Risultato atteso:
```
openwrt/bin/targets/bmips/bcm6362/
  openwrt-bmips-bcm6362-netgear_d6300-squashfs-sysupgrade.bin
  openwrt-bmips-bcm6362-netgear_d6300-squashfs-cfe.bin
```

## B. Backup PRIMA del flash
- Backup del firmware stock: già in mano (`D6300-V1.0.0.102_1.0.102.chk`)
- Salva il bootlog stock: `boot_D6300_full.log` (già nel progetto)
- Se puoi: dump di cferom/data via CFE prima di scrivere

## C. Flash via console seriale (UART)
Collegamento (verificato):
```
CH340G GND -> pad 2 di J252
CH340G RXD -> pad 3 di J252   (TX router, 115200 8N1)
CH340G TXD -> pad 1 o 4       (RX router, per interrompere il CFE)
jumper CH340 = 3,3 V — VCC mai collegato
```
Procedura:
1. Apri PuTTY COM, 115200 8N1, logging su file
2. Accendi il router e premi **Ctrl+C/Invio** entro 1 secondo
3. Al prompt CFE: `help` (verifica comandi)
4. TFTP: server 192.168.1.100, CFE 192.168.1.1
5. Carica con il comando che il CFE accetta (vedi TEST_PLAN §12):
   `flashimage` (immagine cfe.bin) oppure `chkw` (immagine .chk)
6. Attendi il messaggio di fine flash, poi power cycle
7. Salva TUTTO il log (anche del flash)

⚠️ Se qualcosa va storto: il CFE resta raggiungibile via seriale e TFTP
(la partizione di boot non viene toccata dal flash dell'immagine).

## D. Verifiche post-flash (ordine)
```bash
cat /proc/mtd                 # cferom, rootfs_update, wfi, flag, data
ip -br link                   # lan1-4, wan
ip link show                  # MAC = c4:04:15:18:35:10 (da cferom)
dmesg | grep -i b43           # 2.4 GHz
lsusb                         # chiavetta USB
leds                          # LED GPIO
```
- Se il MAC è sbagliato → correggere l'offset nvmem (0x6a0) nella DTS
- Se b43 non carica → documentare come limitazione (come il 5 GHz)

## E. Pubblicazione upstream
1. Calcola l'hash del cferam (già fatto: md5 5b996cd5…, sha256 baefac12…)
2. Apri **PR a openwrt/bcm63xx-cfe**: aggiungi `netgear,d6300/cferam.000`
3. Apri **PR a openwrt/openwrt**: applica le 3 patch con `git am`, personalizza
   `From:`/`Signed-off-by:` con i tuoi dati, push e apri la PR
   (testo pronto in `docs/UPSTREAM_PR_DRAFT.md`)
4. Rispondi alle review: il punto più discusso sarà il layout partizioni
   (derivato dal bootlog) e l'offset MAC — porta i log come evidenza

## F. Upgrade 5 GHz (opzionale, dopo)
- Scheda mini-PCIe **AR9280** (ath9k) → 5 GHz 802.11n 300 Mbps
- Guida: `docs/ESPERIMENTO_MINI_PCIE_5GHZ.md`

## G. VPN + cloud privato (opzionale)
- WireGuard + ksmbd + extroot: guida `docs/VPN_CLOUD_D6300.md`
