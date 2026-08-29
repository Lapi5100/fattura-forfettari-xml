# Creazione Eseguibile Windows - FatturaForfettario

## Prerequisiti

1. **Windows 11 64-bit**
2. **Python 3.10 o superiore** - Scarica da https://www.python.org/downloads/
   - Durante l'installazione, spunta "Add Python to PATH"

## Passaggi per creare l'eseguibile

### 1. Installa le dipendenze

Apri il Prompt dei comandi o PowerShell nella directory del progetto e esegui:

```cmd
pip install pyinstaller PyQt6 fpdf
```

### 2. Crea l'eseguibile

Esegui lo script batch:

```cmd
build_windows.bat
```

Oppure manualmente:

```cmd
pyinstaller --clean FatturaForfettario.spec
```

### 3. Trova l'eseguibile

L'eseguibile si troverà in:
```
dist\FatturaForfettario\FatturaForfettario.exe
```

## Creazione Installer (opzionale)

Per creare un installer professionale:

1. Scarica **Inno Setup** da https://jrsoftware.org/isdl.php
2. Installa Inno Setup
3. Compila lo script:

```cmd
iscc installer_script.iss
```

L'installer verrà creato come `FatturaForfettario-Setup.exe`

## Distribuzione

Per distribuire l'applicazione:

1. **Solo eseguibile**: Zip della cartella `dist\FatturaForfettario\`
2. **Con installer**: Usa il file `FatturaForfettario-Setup.exe`

## Note

- L'eseguibile include tutte le dipendenze necessarie
- Il database SQLite verrà creato automaticamente alla prima esecuzione
- Non è richiesta l'installazione di Python sul computer dell'utente finale

## Risoluzione problemi

### Errore "Python non trovato"
Assicurati di aver aggiunto Python al PATH durante l'installazione.

### Errore durante PyInstaller
Prova a pulire e ricreare:
```cmd
rmdir /s /q build dist
pyinstaller --clean FatturaForfettario.spec
```

### Antivirus blocca l'eseguibile
PyInstaller crea eseguibili che possono essere rilevati come falsi positivi. Firma il codice o aggiungi un'eccezione all'antivirus.
