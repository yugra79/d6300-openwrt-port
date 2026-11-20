# Come procurarsi Linux per la build — tre strade

Il PC è Windows 10 22H2 (build 19045): tutte le opzioni sono compatibili.
La build OpenWrt richiede Linux, ~20-25 GB liberi e 1-3 ore di CPU.

---

## STRADA A (consigliata) — WSL2 + Ubuntu

Leggera (nessun PC virtuale completo), integrata in Windows, ideale per
compilare. **Serve una PowerShell come amministratore** (l'installazione
richiede privilegi elevati: non posso farla io da questa sessione).

### Passi (Windows 10 22H2)

1. **Apri PowerShell come amministratore**:
   Start → scrivi `PowerShell` → tasto destro → *Esegui come amministratore*

2. Prova il comando automatico:
   ```powershell
   wsl --install -d Ubuntu
   ```
   - Se funziona: scarica Ubuntu, chiede il **riavvio** → riavvia → al primo
     avvio di Ubuntu scegli **username** e **password** (li userai con `sudo`)
   - Se dice *"wsl --install non supportato"* (capita su Win10 22H2 senza
     aggiornamento), usa i passi manuali:

3. **Passi manuali (fallback)**:
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
   → **Riavvia il PC**
   → Scarica e installa il "WSL2 Linux kernel update package" da
   https://aka.ms/wsl2kernel (file `wsl_update_x64.msi`)
   → Poi:
   ```powershell
   wsl --set-default-version 2
   wsl --install -d Ubuntu
   ```

4. Verifica (PowerShell normale):
   ```powershell
   wsl -l -v
   ```
   Deve mostrare `Ubuntu  Running  2`.

5. Dentro Ubuntu, installa i prerequisiti build:
   ```bash
   sudo apt update
   sudo apt install -y build-essential git python3 rsync unzip \
       libncurses5-dev zlib1g-dev gawk gettext libssl-dev wget file
   ```

6. Build del firmware:
   ```bash
   cd /mnt/c/Users/padd0l/Documents/deepseek-harness/default-workspace
   unzip -o D6300_OpenWrt_Port_2026-11-20.zip
   cd D6300_OpenWrt_Port/scripts
   chmod +x build_d6300.sh
   ./build_d6300.sh /mnt/c/Users/padd0l/Documents/deepseek-harness/default-workspace/D6300_OpenWrt_Port
   ```

### Se WSL2 non parte
- Errore "virtualization not enabled" → attiva **VT-x/AMD-V nel BIOS**
- Windows 10 richiede "Funzionalità piattaforma macchina virtuale" attiva
- Verifica: `wsl --status` deve dire "Versione predefinita: 2"

---

## STRADA B — GitHub Actions (nessuna virtualizzazione!)

Il firmware viene compilato **dai server GitHub gratuitamente** (1-3 ore);
scarichi solo l'immagine pronta come ZIP. Perfetta se non vuoi toccare il PC.

1. Crea un account GitHub e un **repository privato** (es. `d6300-openwrt-port`)
2. Carica il contenuto di `D6300_OpenWrt_Port` + la cartella `.github/`
   con il workflow `build-d6300.yml` (istruzioni in `github_actions/README.md`)
3. Su GitHub → **Actions** → *Build D6300 firmware* → **Run workflow**
4. A fine build scarica l'artifact **d6300-openwrt-images**

Vantaggi: zero installazioni, CPU remota, artifact scaricabile.
Limite: serve account GitHub e i log/build restano sul cloud.

---

## STRADA C — VirtualBox + Ubuntu (interfaccia grafica)

Se preferisci una VM classica:

1. Installa **VirtualBox** (virtualbox.org) — richiede amministratore
2. Scarica **Ubuntu Server 22.04 LTS** (ubuntu.com, ~2 GB)
3. Crea VM: 4 GB RAM, 2-4 CPU, **25 GB disco**
4. Installa Ubuntu, poi segui i passi 5-6 della Strada A
5. Per copiare i file: cartella condivisa VirtualBox o ZIP via USB/rete

Più pesante di WSL2 (~10 GB di ISO/VM) ma isola tutto dal sistema.

---

## Raccomandazione

1. **Prova prima la Strada A** (WSL2): è la più veloce (15 min) e usa meno spazio
2. Se WSL2 dà problemi → **Strada B** (GitHub Actions): zero installazioni
3. VirtualBox solo se vuoi una VM grafica separata

## Dopo la build
L'immagine è in `openwrt/bin/targets/bmips/bcm6362/`:
- `openwrt-bmips-bcm6362-netgear_d6300-squashfs-cfe.bin` → per il CFE
- `openwrt-bmips-bcm6362-netgear_d6300-squashfs-sysupgrade.bin` → per aggiornamenti

Poi: flash via UART (vedi `TEST_PLAN_D6300.md` §12) e verifiche post-flash.
