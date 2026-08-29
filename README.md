# Gestionale Fatture Elettroniche - Regime Forfettario

Applicazione desktop per generare fatture elettroniche in formato XML pronte per essere inviate all'Agenzia delle Entrate. Non utilizza il sistema SDI. Solo  per professionisti in regime forfettario. Genera anche file PDF.

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

## Struttura

```
main.py                 Avvio applicazione
database.py             SQLite (azienda, clienti, servizi, fatture)
generatore.py           XML FatturaPA e PDF
gui/                    Interfaccia PyQt6
utils/csv_exporter.py   Esportazione CSV
tests/                  Test pytest
Fatture/                XML e PDF generati
```

L'XML non è firmato. Per l'invio del file bisogna accedere con SPID nel sito dell'Agenzia delle Entrate nell'area relativa alla fatturazione elettranica:   https://ivaservizi.agenziaentrate.gov.it/ser/fatturewizard/#/home  Importare il file xml verifacare il contenuto ed inviarlo.

