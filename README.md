# Gestionale Fatture Elettroniche - Regime Forfettario

Applicazione desktop, creata con AI, per generare fatture elettroniche in formato XML pronte per essere inviate all'Agenzia delle Entrate. Non utilizza il sistema SDI. Solo per professionisti in regime forfettario. Genera anche file PDF.

## Avvio

Puoi avviare l'applicazione in due modi:

### 1. Utilizzando lo script di avvio (consigliato)
```bash
./avvia.sh
```

### 2. Avvio manuale (rigenerando prima l'ambiente virtuale)
Se preferisci gestire manualmente l'ambiente virtuale, oppure se hai bisogno di rigenerarlo (ad esempio dopo aver modificato le dipendenze), puoi utilizzare lo script dedicato:

```bash
./setup_venv.sh
source venv/bin/activate
python main.py
```

In alternativa, puoi seguire questi passi manualmente:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Test

Un unico test di avvio (crea la finestra principale e chiude tutto dopo 100 ms):

```bash
QT_QPA_PLATFORM=offscreen python test_run.py
```

Non ci sono altri framework di test configurati.

## Struttura

```
main.py                 Avvio applicazione
database.py             SQLite (azienda, clienti, servizi, fatture)
generatore.py           XML Fattura Elettronica e PDF
gui/                    Interfaccia PyQt6
utils/csv_exporter.py   Esportazione CSV
test_run.py             Test di avvio headless
hooks/                  Hook PyInstaller (piattaforma Qt xcb)
Fatture/                XML e PDF generati (non versionati)
AGENTS.md               Istruzioni per agenti AI
```

Il database (`gestionale_forfettario_qt.sqlite`), la cartella `Fatture/` e
`AGENTS.md` non sono versionati: restano locali alla macchina.

## Build

- **Windows**: `build_windows.bat` oppure `pyinstaller --clean FatturaForfettario.spec`
  (vedi `BUILD_WINDOWS.md`; richiede `pip install pyinstaller PyQt6 fpdf`).
- **Linux AppImage**: `./build_appimage_fixed.sh` (installa da solo pyinstaller nel venv).

## Invio all'Agenzia delle Entrate

L'XML non è firmato. Per l'invio del file bisogna accedere con SPID nel sito dell'Agenzia delle Entrate nell'area relativa alla fatturazione elettronica: https://ivaservizi.agenziaentrate.gov.it/ser/fatturewizard/#/home — importare il file XML, verificare il contenuto ed inviarlo.
