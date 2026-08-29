; Script Inno Setup per creare installer Windows
; Scarica Inno Setup da: https://jrsoftware.org/isdl.php

[Setup]
AppName=FatturaForfettario
AppVersion=1.0
DefaultDirName={pf}\FatturaForfettario
DefaultGroupName=FatturaForfettario
OutputBaseFilename=FatturaForfettario-Setup
Compression=lzma
SolidCompression=yes
; Richiede privilegi di amministratore
PrivilegesRequired=admin
; Icona dell'applicazione (opzionale)
; IconFile=gui\icon.ico

[Files]
; Copia tutti i file dalla directory dist\FatturaForfettario
Source: "dist\FatturaForfettario\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Crea icona sul desktop
Name: "{userdesktop}\FatturaForfettario"; Filename: "{app}\FatturaForfettario.exe"
; Crea icona nel menu Start
Name: "{group}\FatturaForfettario"; Filename: "{app}\FatturaForfettario.exe"

[Run]
; Esegue l'applicazione dopo l'installazione
Filename: "{app}\FatturaForfettario.exe"; Description: "Avvia FatturaForfettario"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Rimuove la directory dell'applicazione durante la disinstallazione
Type: filesandordirs; Name: "{app}"
