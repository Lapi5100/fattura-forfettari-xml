#!/bin/bash
# Script per (re)creare l'ambiente virtuale del progetto
# Elimina la cartella venv esistente, la ricrea e installa le dipendenze da requirements.txt

set -e  # ferma lo script in caso di errore

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS="$PROJECT_DIR/requirements.txt"

echo "=== Inizio (re)creazione ambiente virtuale ==="
echo "Cartella progetto: $PROJECT_DIR"

# Rimuovi eventuale venv esistente
if [ -d "$VENV_DIR" ]; then
    echo "Rimozione dell'ambiente virtuale esistente..."
    rm -rf "$VENV_DIR"
fi

# Crea nuovo ambiente virtuale
echo "Creazione nuovo ambiente virtuale in $VENV_DIR ..."
python3 -m venv "$VENV_DIR"

# Attiva l'ambiente
echo "Attivazione ambiente virtuale..."
source "$VENV_DIR/bin/activate"

# Aggiorna pip (opzionale ma consigliato)
echo "Aggiornamento pip..."
pip install --upgrade pip

# Installa le dipendenze
if [ -f "$REQUIREMENTS" ]; then
    echo "Installazione delle dipendenze da $REQUIREMENTS ..."
    pip install -r "$REQUIREMENTS"
else
    echo "ATTENZIONE: file $REQUIREMENTS non trovato!"
    exit 1
fi

echo ""
echo "=== Ambiente virtuale creato con successo ==="
echo "Per attivarlo manualmente:"
echo "    source $VENV_DIR/bin/activate"
echo "Per avviare l'applicazione:"
echo "    $VENV_DIR/bin/python main.py"
echo ""