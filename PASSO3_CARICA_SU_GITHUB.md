# PASSO 3 — Caricare il repo su GitHub (modo semplice)

## Metodo A — trascinamento (2 minuti)

1. Nella pagina del repo GitHub (quella creata al passo 2) clicca
   **"uploading an existing file"**
2. Apri Esplora File di Windows e vai a:
   `C:\Users\padd0l\Documents\deepseek-harness\default-workspace\d6300-openwrt-ci`
3. Premi **Ctrl+A** per selezionare TUTTO (devi vedere anche `.github`)
4. **Trascina** la selezione nella zona "Drag files here" della pagina GitHub
5. Attendi la lista file (38 file) → in basso **Commit changes**

⚠️ Se la cartella `.github` non viene caricata (a volte i browser la saltano),
usa il Metodo B solo per il workflow.

## Metodo B — workflow creato a mano (sicuro al 100%)

### B1. Carica tutto il resto
1. Seleziona in `d6300-openwrt-ci` tutti gli elementi **tranne** `.github`
2. Trascinali su GitHub → Commit changes
3. Verifica che nella home del repo ci siano: `README.md`, `openwrt/`, `docs/`,
   `scripts/`, `build_test/`, `UPLOAD_STEPS.md`, `LICENSE_NOTE.txt`

### B2. Crea il workflow a mano
1. Nella home del repo: **Add file → Create new file**
2. Nel campo del nome scrivi ESATTAMENTE:
   ```
   .github/workflows/build-d6300.yml
   ```
   (GitHub creerà le cartelle automaticamente)
3. Apri il file `WORKFLOW_PASTE.txt` (in questa cartella), **copia tutto** il
   contenuto e **incollalo** nell'editor GitHub
4. In basso: **Commit changes** (es. "add build workflow")
5. Vai sulla tab **Actions** → se compare l'avviso, clicca
   **"I understand my workflows, go ahead and enable them"**
6. Dovresti vedere il workflow **Build D6300 firmware** → **Run workflow**

## Verifica finale
Nella home del repo deve apparire:
```
.github/          ← contiene workflows/build-d6300.yml
openwrt/          ← patches, dts, image, bcm6362, bcm63xx-cfe
docs/             ← 15 documenti
scripts/          ← suite e strumenti
build_test/       ← artefatti di validazione
README.md  UPLOAD_STEPS.md  LICENSE_NOTE.txt
```

Poi: **Actions** → *Build D6300 firmware* → **Run workflow** → attendi 1-2 ore
→ scarica l'artifact **d6300-openwrt-images**.
