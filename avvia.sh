#!/bin/bash
# Script di avvio per l'applicazione fatture elettroniche

cd "$(dirname "$0")"

# Controlla se il virtual environment esiste
if [ ! -d "venv" ]; then
    echo "Virtual environment non trovato. Creazione in corso..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Avvia l'applicazione
python main.py
