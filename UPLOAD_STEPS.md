# METTI ONLINE IL REPO E AVVIA LA BUILD — 5 passi

Tutto il repository è già pronto nella cartella `d6300-openwrt-ci`
(oppure nello ZIP `d6300-openwrt-ci.zip` sulla scrivania del workspace).
Restano solo i passaggi che richiedono il **tuo account GitHub** (credenziali
che non posso usare io).

## Passo 1 — Crea l'account GitHub (se non ce l'hai)
1. Vai su https://github.com/signup
2. Email + password + username (2 minuti, serve la verifica email)
3. Se hai già un account, salta al passo 2

## Passo 2 — Crea il repository
1. Vai su https://github.com/new
2. **Repository name**: `d6300-openwrt-port`
3. **Public** ← consigliato (minuti Actions illimitati; privato = 2000 min/mese)
4. NON spuntare "Add a README file" (lo caricheremo noi)
5. Click **Create repository**

## Passo 3 — Carica i file
1. Nella pagina del repo appena creato: **"uploading an existing file"**
   (link al centro: *…or upload an existing file*)
2. Apri la cartella `d6300-openwrt-ci` di questo workspace
3. **Seleziona TUTTO il contenuto della cartella** (Ctrl+A) — deve includere
   la cartella `.github` (contiene il workflow!) — e **trascinalo** nella
   pagina GitHub
4. Attendi il caricamento di tutti i file (37 file, pochi secondi)
5. **Commit changes** (messaggio libero, es. "D6300 OpenWrt port")

> ⚠️ Importante: trascina il **contenuto** della cartella, NON la cartella
> stessa, altrimenti tutto finisce in una sottocartella e il workflow non
> viene trovato.

Verifica: nella home del repo devi vedere `README.md`, la cartella `.github`,
`openwrt/`, `docs/`, `scripts/`, `build_test/`.

## Passo 4 — Avvia la build
1. Click sulla tab **Actions**
2. Se compare un avviso, click **"I understand my workflows, go ahead and enable them"**
3. Nel menu a sinistra: **Build D6300 firmware**
4. Click **Run workflow** (destra) → **Run workflow** (conferma)
5. La build parte: 1-2 ore (CPU server GitHub)

## Passo 5 — Scarica il firmware
1. Quando il run è verde (o rosso), apri il run
2. In fondo alla pagina, sezione **Artifacts**: scarica
   **d6300-openwrt-images.zip**
3. Dentro trovi:
   - `openwrt-bmips-bcm6362-netgear_d6300-squashfs-cfe.bin` ← immagine per CFE
   - `openwrt-bmips-bcm6362-netgear_d6300-squashfs-sysupgrade.bin`
   - `openwrt-commit.txt`

## Se la build fallisce
- Apri il run rosso → click sul passo fallito → copia le ultime righe del log
- Mandamele: le analizzo e correggo patch/ricetta
- (Le cause tipiche: drift upstream di OpenWrt → riallineo le patch)

## Dopo il firmware
- Flash via console UART/CFE: `docs/TEST_PLAN_D6300.md` §12 e `docs/PROSSIMI_PASSI.md`
- Pinout J252: pad 2 = GND, pad 3 = TX (115200 8N1); CH340 jumper 3,3 V
