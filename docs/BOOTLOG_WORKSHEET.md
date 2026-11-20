# WORKSHEET — BOOT LOG D6300
Compilare questo foglio quando si cattura il boot log seriale.
Serve per completare il DTS e la PR upstream.

## Setup
- [ ] Adattatore CH340G su **3,3V** (jumper)
- [ ] Collegati solo **GND, TX, RX** (VCC NON collegato, TX/RX incrociati)
- [ ] PuTTY: **115200 8N1**, logging su file `boot_D6300.log`
- [ ] Router aperto e pin UART identificati (GND verificato col multimetro)

---

## 1. Dati dal log CFE (copiare qui le righe)

```
versione CFE: ................................................
data build CFE: ..............................................
chip ID: .....................................................
board ID: ....................................................
boot delay: ..................................................
versione WFI: ................................................
flash type / geometria NAND: .................................
```

Righe di esempio da cercare nel log:
- `CFE version ...`
- `Board Id ...`
- `boot    offset=0x..., size=0x...`
- `rootfs1 offset=0x..., size=0x...`
- `rootfs2 offset=0x..., size=0x...`
- `Total Flash size: ...`
- `NAND Access Control register = ...`
- `Image chksum / Calc chksum`
- `Booting from latest/previous image`

---

## 2. Interruzione boot e comandi CFE

- [ ] Boot interrotto (premuto tasto durante il countdown)
- [ ] Al prompt CFE: `help` salvato nel log

Se `help` funziona, copiare l'elenco comandi qui:
```
.....................................................
```

Comandi utili da provare (solo lettura, NON scrivere):
- [ ] `d` — dump memoria (annotare cosa mostra)
- [ ] `b` — stampa boot line/parametri board
- [ ] Eventuale `i` / `info` — info flash/partizioni

---

## 3. Dati da shell stock (se si ottiene accesso)

- [ ] `cat /proc/mtd`  → incollare l'output:
```
.....................................................
```
- [ ] `dmesg | grep -i nand` → modello/ECC:
```
.....................................................
```
- [ ] `dmesg | grep -i eth` / switch → chip switch (53115?):
```
.....................................................
```
- [ ] `cat /proc/version` → kernel stock:
```
.....................................................
```
- [ ] `ip a` / `ifconfig -a` → interfacce:
```
.....................................................
```
- [ ] `cat /proc/cmdline`:
```
.....................................................
```

---

## 4. LED e pulsanti
- [ ] Quali LED si accendono al boot e in che ordine
- [ ] LED di power: colore in boot normale / failsafe
- [ ] Pulsanti presenti (reset, wps, wifi)
- [ ] Comportamento: reset premuto 10s, wps

Annotazioni:
```
.....................................................
```

---

## 5. MAC address
- [ ] MAC LAN (etichetta): ................................
- [ ] MAC WAN (etichetta): ................................
- [ ] MAC visto in `dmesg`/`ifconfig`: ................................
- [ ] MAC in flash (se visibile con hexdump): ................................

---

## 6. File da consegnare
- [ ] `boot_D6300.log` (log seriale completo, dal primo momento)
- [ ] Questo worksheet compilato
- [ ] (opzionale) dump delle partizioni se ottenibile

**Con questi dati** si completano: partizioni nel DTS, `CFE_WFI_VERSION`,
`CFE_WFI_FLASH_TYPE`, posizione MAC (nvmem), GPIO LED/pulsanti, e si può
finalizzare la PR upstream.


---

## RISULTATI CATTURATI — 20/11/2026

| Campo | Valore |
|---|---|
| CFE | `BCM6362 Platform Boot Code V1.0.9-4.12L.04` / `CFE version 1.0.38-112.70 for BCM96362` |
| Build date | Thu Oct 11 11:14:13 CST 2012 |
| Chip ID | **BCM6362B0** — MIPS 400 MHz, DDR 333 MHz, bus 166 MHz |
| Board Id | **96362ADVN2xh** |
| RAM | 128 MB (memory 0x07f00000 usable) |
| NAND | **ST NAND512W3A2CN6** id 0x2076 — 64 MB, blocchi 16 KB, pagine 512 B, ECC 15/512 |
| BBT | Bbt0 @ page 0x1ffe0, 1tbB @ page 0x1ffc0 |
| Partizioni | nvram 0x0-0x4000 · rootfs_update 0x4000-0x1d80000 · rootfs 0x1d80000-0x3afc000 · data 0x3b00000-0x3f00000 |
| Boot | "Booting from latest image (0xb9d80000)" = rootfs |
| Kernel stock | Linux 2.6.30 (buildroot 2010.02, gcc 4.4.2, 2017-02-14) |
| Cmdline | root=mtd:rootfs ro rootfstype=jffs2 console=ttyS0,115200 |
| Switch | esterno **BCM53125** (driver 53115 forzato) |
| WiFi 2.4 | BCM435f (wl0) |
| WiFi 5G | BCM4360 mini-PCIe non presente in cattura (scheda smontata) |
| MAC base | c4:04:15:18:35:10 |
| Board IP CFE | 192.168.1.1:ffffff00, host .100 |

Log completo: `netgear-d6300/boot_D6300_full.log`
