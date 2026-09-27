# Gestionale Fatture Elettroniche - Regime Forfettario

Questa è una applicazione desktop, creata con AI, nata per gestire le mie fatture elettroniche nella maniera semplice e veloce, è in fase di sviluppo e può contenere errori. 

L'applicazione genera fatture elettroniche in formato PDF e XML pronte per essere inviate all'Agenzia delle Entrate. Non utilizza il sistema SDI. Solo per autonomi che aderiscono al regime forfettario. Genera fatture per professionisti alla gestione separata, per iscritti alle casse professionali e per gli autonomi dello spettacolo iscritti all'exENPALS. 

Per windows scarica la cartella zip e scompattala dove vuoi. Avvia l'eseguibile per lanciare il programma.

Per linux scaricare l'eseguibile appimage per qualsiasi distribuzione.


| File | Link |
|------|------|
| Windows | [Scarica](https://github.com/Lapi5100/fattura-forfettari-xml/releases/download/0.8.0/Fattura_Forfettario-win-x86_64.zip) |
| Linux | [Scarica](https://github.com/Lapi5100/fattura-forfettari-xml/releases/download/0.8.0/Fattura_Forfettario-linux-x86_64.AppImage) |


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

L'XML viene creato senza firma. Per l'invio del file bisogna accedere con SPID nel sito dell'Agenzia delle Entrate nell'area relativa alla fatturazione elettranica:   https://ivaservizi.agenziaentrate.gov.it/ser/fatturewizard/#/home  Importare il file xml, verifacare il contenuto ed inviarlo.

