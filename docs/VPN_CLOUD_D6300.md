# VPN e cloud privato sul D6300 con OpenWrt

Guida operativa · 20/11/2026

## Risposta breve

**Non è previsto di default.** L'immagine OpenWrt del D6300 (come tutte le
immagini ufficiali) è **minimale**: include solo il sistema base e i driver del
device (USB, switch, LED, b43). VPN, storage USB e condivisione file si
aggiungono in uno di questi modi:

1. **Dopo il flash** con `opkg install ...` (se il router ha accesso a internet)
2. **Nel build**, aggiungendo i pacchetti a `DEVICE_PACKAGES` nella ricetta
   (immagine più grande: attenzione ai 64 MB di flash)

## Cosa permette l'hardware

| Risorsa | Dato | Conseguenza |
|---|---|---|
| CPU | BCM6362 BMIPS4350 2x 400 MHz | VPN senza accelerazione AES: throughput limitato |
| RAM | 128 MB | ok per ksmbd + WireGuard; **no** Nextcloud |
| Flash | 64 MB (rootfs ~30 MB) | pochi MB liberi per pacchetti → usare `extroot` su USB |
| USB | 2x USB 2.0 (EHCI/OHCI) | hard disk fino a ~30-40 MB/s reali |

---

## 1) VPN

### Opzione consigliata: WireGuard
Pacchetti:
```
opkg update
opkg install kmod-wireguard wireguard-tools luci-proto-wireguard qrencode
```
Uso tipico: **server VPN** per accedere alla rete di casa dall'esterno
(telefono/PC con client WireGuard), oppure **client** verso un provider VPN.

- Throughput realistico su questa CPU: **~15-40 Mbps**
- Doppia funzione: anche accesso ai file del disco USB tramite la VPN

### OpenVPN (più lento, ma compatibile ovunque)
```
opkg install openvpn-openssl luci-app-openvpn
```
Throughput realistico: **~5-15 Mbps** (no AES hardware).

### Altri (se presenti nei feed della tua versione)
- **Tailscale**: `tailscale` (mesh VPN, comodissima per il cloud privato)
- **ZeroTier**: `zerotier`
- Verifica disponibilità: `opkg list | grep -i tailscale`

⚠️ Per il server VPN serve un **DDNS** (IP pubblico dinamico?):
`opkg install ddns-scripts luci-app-ddns` + apertura porta UDP 51820 sul firewall.

---

## 2) Hard disk USB come cloud privato

### a) Base: montaggio del disco
```
opkg update
opkg install kmod-usb-storage kmod-fs-ext4 kmod-fs-vfat kmod-fs-exfat \
              block-mount usbutils
```
- Formattare il disco **ext4** (consigliato) o exFAT (compatibile Windows)
- Montaggio persistente in LuCI → Sistema → Mount Points (o `/etc/config/fstab`
  con UUID)
- ⚠️ Formattare da Linux/PC, non dal router (per ext4 serve `e2fsprogs`)

### b) Condivisione in rete locale: **ksmbd** (leggero, consigliato)
```
opkg install ksmbd-server ksmbd-tools luci-app-ksmbd
```
Alternativa: `samba4-server` (più funzioni, più RAM/CPU: ~35 MB RAM in più).

### c) Accesso "cloud" da browser/smartphone
| Soluzione | Pacchetto | Note |
|---|---|---|
| **FileBrowser** (web UI) | `filebrowser` / `luci-app-filebrowser` | ~10 MB, gestione file da browser; verifica disponibilità nel feed |
| **SFTP** (accesso sicuro) | `openssh-sftp-server` | già hai SSH; funziona con FileZilla/app |
| **DLNA** (TV/media) | `minidlna` + `luci-app-minidlna` | streaming film/musica |
| **rclone** (backup offsite) | `rclone` | copia su Google Drive/OneDrive/S3 ecc. |
| **Syncthing** (sync) | `syncthing` | pesante in RAM (~80-100 MB): solo con extroot |

### d) Extroot: spostare il rootfs su USB (consigliato)
Con 30 MB di rootfs i pacchetti finiscono presto:
1. Partizione ext4 sul disco (es. 1 GB)
2. `opkg install block-mount kmod-fs-ext4`
3. Configurare `extroot` in `/etc/config/fstab` (guida OpenWrt "extroot")
→ il router usa il disco per i pacchetti e lo spazio libero

### ❌ Cosa NON è fattibile
- **Nextcloud / ownCloud**: richiedono PHP + database + ~1 GB RAM → **no**
- Samba4 pesante su 128 MB se in contemporanea a WireGuard + ksmbd
- Transcodifica video (Plex/Jellyfin): CPU 400 MHz senza accelerazione → **no**

---

## 3) Includere i pacchetti nel build (opzionale)

Nel file `port/openwrt/image/bcm6362.mk`, per una build "cloud-ready":
```
DEVICE_PACKAGES += $(USB2_PACKAGES) $(B43_PACKAGES) \
    kmod-leds-bcm6328 kmod-leds-gpio \
    kmod-usb-storage kmod-fs-ext4 kmod-fs-exfat block-mount \
    ksmbd-server luci-app-ksmbd \
    wireguard-tools kmod-wireguard luci-proto-wireguard
```
⚠️ L'immagine cresce: con 64 MB di flash è meglio **opkg + extroot** oppure
includere solo WireGuard (~1 MB) e lasciare il resto a opkg.

## 4) Test post-flash (ordine consigliato)

1. `lsusb` e `dmesg | tail` → disco riconosciuto
2. `blkid` → UUID del disco; montaggio via LuCI
3. `opkg install ksmbd-server` → share attiva; test da PC
4. `opkg install wireguard-tools kmod-wireguard` → server WG; test da telefono
5. `df -h` → spazio libero; se poco, configurare extroot
6. Backup dei file importanti sul PC (il disco USB non è un backup!)

## 5) Nota importante sul D6300 in OpenWrt

Il **modem DSL non è supportato**: il D6300 in OpenWrt va usato come router
dietro un modem (WAN Ethernet) oppure in cascata. VPN e cloud privato
funzionano normalmente su WAN Ethernet.
