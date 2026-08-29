#!/bin/bash
set -e

APP_NAME="Fattura Forfettario xml"
APP_DIR="/home/savini/fatture_elettronica_qt"
BUILD_DIR="$APP_DIR/build"
APPIMAGE_DIR="$BUILD_DIR/AppImage"
OUTPUT_DIR="$APP_DIR/dist"
APPIMAGETOOL="$HOME/.local/bin/appimagetool-x86_64.AppImage"

echo "=== Creazione AppImage per $APP_NAME ==="

# Pulisci directory precedenti ma preserva appimagetool
rm -rf "$APPIMAGE_DIR" "$OUTPUT_DIR"
mkdir -p "$APPIMAGE_DIR" "$OUTPUT_DIR"

# Attiva venv e installa PyInstaller
source "$APP_DIR/venv/bin/activate"
pip install pyinstaller --quiet

# Crea AppDir con PyInstaller (onedir invece di onefile)
echo "Creazione AppDir con PyInstaller..."
cd "$APP_DIR"
pyinstaller --name="FatturaForfettario" \
    --onedir \
    --windowed \
    -y \
    --add-data="gui:gui" \
    --add-data="utils:utils" \
    --add-data="generatore.py:." \
    --add-data="database.py:." \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.QtWidgets \
    --distpath="$BUILD_DIR/dist" \
    main.py

# Copia la directory creata come AppDir
echo "Creazione struttura AppImage..."
PYINSTALLER_DIR="$BUILD_DIR/dist/FatturaForfettario"
cp -a "$PYINSTALLER_DIR"/. "$APPIMAGE_DIR/"

# Crea desktop file
cat > "$APPIMAGE_DIR/FatturaForfettario.desktop" << 'EOF'
[Desktop Entry]
Name=Fattura Forfettario xml
Comment=Generatore fatture elettroniche forfettarie
Exec=FatturaForfettario
Icon=FatturaForfettario
Type=Application
Categories=Office;Finance;
Terminal=false
EOF

# Crea icona semplice (SVG)
cat > "$APPIMAGE_DIR/FatturaForfettario.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <rect width="256" height="256" fill="#4CAF50" rx="32"/>
  <text x="128" y="128" font-family="Arial" font-size="80" fill="white" text-anchor="middle" dominant-baseline="middle">F</text>
  <text x="128" y="180" font-family="Arial" font-size="40" fill="white" text-anchor="middle">Fattura</text>
</svg>
EOF

# Crea AppRun
cat > "$APPIMAGE_DIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}

# Imposta i percorsi per le librerie
export PATH="${HERE}:${PATH}"
export LD_LIBRARY_PATH="${HERE}:${LD_LIBRARY_PATH}"

# Crea database se non esiste nella directory di lavoro
if [ ! -f "gestionale_forfettario_qt.sqlite" ]; then
    touch gestionale_forfettario_qt.sqlite 2>/dev/null || true
fi

exec "${HERE}/FatturaForfettario" "$@"
EOF

chmod +x "$APPIMAGE_DIR/AppRun"

# Scarica appimagetool se non esiste
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Download appimagetool..."
    mkdir -p "$(dirname "$APPIMAGETOOL")"
    wget -q "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" -O "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
fi

# Crea AppImage
echo "Creazione AppImage..."
cd "$BUILD_DIR"
ARCH=x86_64 "$APPIMAGETOOL" "$APPIMAGE_DIR" "$OUTPUT_DIR/Fattura_Forfettario_xml-x86_64.AppImage"

echo ""
echo "=== AppImage creata con successo! ==="
echo "Posizione: $OUTPUT_DIR/Fattura_Forfettario_xml-x86_64.AppImage"
""