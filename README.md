# Gestionale Fatture Elettroniche - Regime Forfettario

Applicazione desktop per generare fatture elettroniche in formato XML pronte per essere inviate all'Agenzia delle Entrate. Non utilizza il sistema SDI. Solo  per professionisti in regime forfettario. Genera anche file PDF.

## Avvio

```bash
./avvia.sh
```

Oppure:

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

## Test

```bash
source venv/bin/activate
pip install pytest
pytest tests/
```
