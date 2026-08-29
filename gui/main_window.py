import datetime
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QTabWidget, QTableWidget, QTableWidgetItem, QComboBox,
    QPushButton, QLabel, QLineEdit, QCheckBox, QHeaderView, QMessageBox,
    QFileDialog, QDateEdit,
)

from database import Database
from generatore import Generatore, get_tipo_cassa_professione, get_cassa_professione, MAPPA_PROFESSIONI
from gui.dialogs import NuovoClienteDialog, ModificaRigaDialog
from gui.styles import APP_STYLESHEET
from utils.csv_exporter import CSVExporter

CARTELLA_FATTURE = "Fatture"
LOGO_PATH = Path(__file__).resolve().parent.parent / "logo.png"


def _row_get(row, key, default=""):
    if row is None:
        return default
    try:
        val = row[key]
    except (IndexError, KeyError):
        return default
    return default if val is None else val


def _nome_cliente(cliente):
    return _row_get(cliente, "denominazione") or f"{_row_get(cliente, 'nome')} {_row_get(cliente, 'cognome')}"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fattura Forfettario xml")
        self.setGeometry(100, 100, 1200, 900)

        self.db = Database()
        self.azienda = self.db.get_azienda()
        self.clienti_db = []
        self.servizi_archivio = []
        self.righe_fattura = []
        self.fattura_in_modifica = None
        self._storico = []

        self.setup_ui()
        self.inizializza_campi_fattura()

    def _az(self, campo, default=""):
        return _row_get(self.azienda, campo, default)

    @staticmethod
    def estrai_righe_da_xml(xml_path):
        if not xml_path or not os.path.exists(xml_path):
            return []
        try:
            root = ET.parse(xml_path).getroot()
            righe = []
            for dettaglio in root.findall(".//{*}DettaglioLinee"):
                desc = dettaglio.find("{*}Descrizione")
                qta = dettaglio.find("{*}Quantita")
                prezzo = dettaglio.find("{*}PrezzoUnitario")
                totale = dettaglio.find("{*}PrezzoTotale")
                natura = dettaglio.find("{*}Natura")
                if desc is None or qta is None or prezzo is None:
                    continue
                righe.append({
                    "desc": desc.text or "",
                    "qta": float(qta.text or 0),
                    "prezzo": float(prezzo.text or 0),
                    "totale": float(totale.text or 0) if totale is not None else 0,
                    "natura": (natura.text if natura is not None else None) or "N2.2",
                })
            return righe
        except ET.ParseError:
            return []

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(6)

        logo_label = QLabel()
        if LOGO_PATH.exists():
            pixmap = QPixmap(str(LOGO_PATH)).scaledToHeight(
                40, Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(logo_label)

        main_layout.addWidget(self.create_config_group())

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        self.tab_widget.addTab(self.create_nuova_fattura_tab(), "Nuova Fattura")
        self.tab_widget.addTab(self.create_storico_tab(), "Storico Fatture")

        footer_label = QLabel("Creator: Nicola Lapi")
        footer_label.setStyleSheet("color: #666; font-size: 10px;")
        main_layout.addWidget(footer_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self.setStyleSheet(APP_STYLESHEET)

    def create_config_group(self):
        group = QGroupBox("Dati Professionista & Parametri")
        layout = QGridLayout()

        layout.addWidget(QLabel("Professionista:"), 0, 0)
        self.cb_tipo_prof = QComboBox()
        self.cb_tipo_prof.addItems(["", *MAPPA_PROFESSIONI.keys()])
        self.cb_tipo_prof.setCurrentText(self._az("tipo_professionista"))
        self.cb_tipo_prof.currentTextChanged.connect(self._on_professione_changed)
        layout.addWidget(self.cb_tipo_prof, 0, 1)

        self.e_az_nom = QLineEdit(self._az("nome"))
        self.e_az_cog = QLineEdit(self._az("cognome"))
        layout.addWidget(QLabel("Nome:"), 0, 2)
        layout.addWidget(self.e_az_nom, 0, 3)
        layout.addWidget(QLabel("Cognome:"), 0, 4)
        layout.addWidget(self.e_az_cog, 0, 5)

        self.e_az_piva = QLineEdit(self._az("piva"))
        self.e_az_cf = QLineEdit(self._az("codice_fiscale"))
        layout.addWidget(QLabel("P.IVA:"), 1, 0)
        layout.addWidget(self.e_az_piva, 1, 1)
        layout.addWidget(QLabel("C.F.:"), 1, 2)
        layout.addWidget(self.e_az_cf, 1, 3)

        self.e_az_indirizzo = QLineEdit(self._az("indirizzo"))
        self.e_az_num_civico = QLineEdit(self._az("numero_civico"))
        self.e_az_cap = QLineEdit(self._az("cap"))
        layout.addWidget(QLabel("Indirizzo:"), 2, 0)
        layout.addWidget(self.e_az_indirizzo, 2, 1)
        layout.addWidget(QLabel("N. Civico:"), 2, 2)
        layout.addWidget(self.e_az_num_civico, 2, 3)
        layout.addWidget(QLabel("CAP:"), 2, 4)
        layout.addWidget(self.e_az_cap, 2, 5)

        self.e_az_comune = QLineEdit(self._az("comune"))
        self.e_az_prov = QLineEdit(self._az("provincia"))
        layout.addWidget(QLabel("Comune:"), 3, 0)
        layout.addWidget(self.e_az_comune, 3, 1)
        layout.addWidget(QLabel("Provincia:"), 3, 2)
        layout.addWidget(self.e_az_prov, 3, 3)

        self.e_az_titolo = QLineEdit(self._az("titolo"))
        self.lbl_albo_prof = QLabel("Albo Professionale:")
        self.e_albo_prof = QLineEdit(str(self._az("albo_professionale")))
        self.lbl_prov_albo = QLabel("Prov. Albo:")
        self.e_prov_albo = QLineEdit(self._az("provincia_albo"))
        layout.addWidget(QLabel("Titolo:"), 4, 0)
        layout.addWidget(self.e_az_titolo, 4, 1)
        layout.addWidget(self.lbl_albo_prof, 4, 2)
        layout.addWidget(self.e_albo_prof, 4, 3)
        layout.addWidget(self.lbl_prov_albo, 4, 4)
        layout.addWidget(self.e_prov_albo, 4, 5)

        self.lbl_data_iscr_albo = QLabel("Data Iscr. Albo:")
        self.e_data_iscr_albo = QLineEdit(str(self._az("data_iscrizione_albo")))
        self.lbl_num_albo = QLabel("N° Iscrizione Albo:")
        self.e_num_albo = QLineEdit(self._az("numero_albo"))
        self.lbl_cassa_app = QLabel("Cassa Appartenenza:")
        self.e_cassa_app = QLineEdit(str(self._az("cassa_appartenenza")))
        self.e_cassa_app.setCursorPosition(0)
        layout.addWidget(self.lbl_data_iscr_albo, 5, 0)
        layout.addWidget(self.e_data_iscr_albo, 5, 1)
        layout.addWidget(self.lbl_num_albo, 5, 2)
        layout.addWidget(self.e_num_albo, 5, 3)
        layout.addWidget(self.lbl_cassa_app, 5, 4)
        layout.addWidget(self.e_cassa_app, 5, 5)

        self.lbl_iban = QLabel("IBAN:")
        self.e_iban = QLineEdit(str(self._az("iban")))
        self.lbl_cassa_perc = QLabel("Cassa Albo %:")
        self.e_cassa_perc = QLineEdit(str(self._az("perc_cassa", "0")))
        layout.addWidget(self.lbl_iban, 6, 0)
        layout.addWidget(self.e_iban, 6, 1, 1, 2)
        layout.addWidget(self.lbl_cassa_perc, 6, 3)
        layout.addWidget(self.e_cassa_perc, 6, 4, 1, 2)

        self.var_rivalsa = QCheckBox("Attiva Rivalsa INPS (4%)")
        self.var_rivalsa.setChecked(bool(self._az("attiva_rivalsa", 0)))
        layout.addWidget(self.var_rivalsa, 7, 0, 1, 3)

        self.var_bollo_al_totale = QCheckBox("Aggiungi Bollo al Totale")
        self.var_bollo_al_totale.setChecked(False)
        self.var_bollo_al_totale.stateChanged.connect(self._aggiorna_label_totali)
        layout.addWidget(self.var_bollo_al_totale, 8, 0, 1, 3)

        btn_salva = QPushButton("Salva")
        btn_salva.clicked.connect(self.salva_config)
        layout.addWidget(btn_salva, 6, 6)

        group.setLayout(layout)
        self._aggiorna_stato_campi_professione()
        return group

    def suggerisci_cassa_previdenziale(self, professione):
        cassa = get_cassa_professione(professione)
        if cassa:
            self.e_cassa_app.setText(cassa["nome"])
            self.e_cassa_app.setCursorPosition(0)

    def _on_professione_changed(self, testo):
        self.suggerisci_cassa_previdenziale(testo)
        self._aggiorna_stato_campi_professione()

    def _aggiorna_stato_campi_professione(self):
        ha_valore = bool(self.cb_tipo_prof.currentText())
        for widget in (
            self.e_albo_prof, self.lbl_albo_prof, self.e_prov_albo, self.lbl_prov_albo,
            self.e_data_iscr_albo, self.lbl_data_iscr_albo, self.e_num_albo, self.lbl_num_albo,
            self.e_cassa_app, self.lbl_cassa_app, self.e_cassa_perc, self.lbl_cassa_perc,
        ):
            widget.setEnabled(ha_valore)

    def _get_fattura_selezionata(self):
        row = self.table_archivio.currentRow()
        if row < 0 or row >= len(self._storico):
            return None
        return self._storico[row]

    def _ensure_cartella_fatture(self):
        os.makedirs(CARTELLA_FATTURE, exist_ok=True)

    def _build_dati_xml(self, cliente, numero, data_oggi, imp_comp, rivalsa, cassa, bollo, totale, cassa_perc):
        return {
            "cedente_denominazione": str(self._az("denominazione") or f"{self._az('nome')} {self._az('cognome')}"),
            "cedente_nome": str(self._az("nome")),
            "cedente_cognome": str(self._az("cognome")),
            "cedente_indirizzo": str(self._az("indirizzo")),
            "cedente_num_civico": str(self._az("numero_civico")),
            "cedente_cap": str(self._az("cap")),
            "cedente_comune": str(self._az("comune")),
            "cedente_prov": str(self._az("provincia")),
            "cedente_piva": str(self._az("piva")),
            "cedente_cf": str(self._az("codice_fiscale")),
            "cedente_titolo": str(self._az("titolo")),
            "tipo_professionista": str(self._az("tipo_professionista")),
            "tipo_cassa": get_tipo_cassa_professione(self._az("tipo_professionista")),
            "numero_albo": str(self._az("numero_albo")),
            "provincia_albo": str(self._az("provincia_albo")),
            "data_iscrizione_albo": str(self._az("data_iscrizione_albo")),
            "cassa_appartenenza": str(self._az("cassa_appartenenza")),
            "albo_professionale": str(self._az("albo_professionale")),
            "iban": str(self._az("iban")),
            "regime_fiscale": "RF19",
            "cliente_denominazione": str(_row_get(cliente, "denominazione")),
            "cliente_nome": str(_row_get(cliente, "nome")),
            "cliente_cognome": str(_row_get(cliente, "cognome")),
            "cliente_indirizzo": str(_row_get(cliente, "indirizzo")),
            "cliente_num_civico": str(_row_get(cliente, "numero_civico")),
            "cliente_cap": str(_row_get(cliente, "cap")),
            "cliente_comune": str(_row_get(cliente, "comune")),
            "cliente_prov": str(_row_get(cliente, "provincia")),
            "cliente_nazione": str(_row_get(cliente, "nazione", "IT")),
            "cliente_piva": str(_row_get(cliente, "piva")),
            "cliente_cf": str(_row_get(cliente, "codice_fiscale")),
            "codice_sdi_dest": str(_row_get(cliente, "codice_sdi")),
            "numero": numero,
            "data": data_oggi,
            "progressivo": numero,
            "righe": self.righe_fattura,
            "imponibile_competenza": imp_comp,
            "rivalsa": rivalsa,
            "perc_rivalsa": 4.0,
            "cassa_albo": cassa,
            "perc_cassa": cassa_perc,
            "bollo": bollo,
            "totale_documento": totale,
            "natura_riepilogo": self.righe_fattura[0]["natura"] if self.righe_fattura else "N2.2",
        }

    def _salva_file_fattura(self, dati_xml, file_xml, file_pdf):
        with open(file_xml, "wb") as f:
            f.write(Generatore.crea_xml(dati_xml))
        with open(file_pdf, "wb") as f:
            f.write(Generatore.crea_pdf(dati_xml))

    def create_nuova_fattura_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        cliente_group = QGroupBox("1. Seleziona o Crea Cliente")
        cliente_layout = QHBoxLayout()
        cliente_layout.addWidget(QLabel("Cliente:"))
        self.combo_clienti = QComboBox()
        self.aggiorna_combo_clienti()
        self.combo_clienti.currentIndexChanged.connect(self.mostra_dati_cliente)
        cliente_layout.addWidget(self.combo_clienti)

        btn_nuovo = QPushButton("+ Nuovo Cliente")
        btn_nuovo.clicked.connect(self.nuovo_cliente)
        cliente_layout.addWidget(btn_nuovo)
        btn_mod = QPushButton("Modifica Cliente")
        btn_mod.clicked.connect(self.modifica_cliente)
        cliente_layout.addWidget(btn_mod)

        self.lbl_cliente_info = QLabel("Nessun cliente selezionato")
        self.lbl_cliente_info.setStyleSheet("color: gray;")
        cliente_layout.addWidget(self.lbl_cliente_info)
        cliente_layout.addStretch()
        cliente_group.setLayout(cliente_layout)
        layout.addWidget(cliente_group)

        dati_group = QGroupBox("2. Dati Fattura")
        dati_layout = QHBoxLayout()
        dati_layout.addWidget(QLabel("Numero:"))
        self.e_numero_fattura = QLineEdit()
        dati_layout.addWidget(self.e_numero_fattura)
        dati_layout.addWidget(QLabel("Data:"))
        self.e_data_fattura = QDateEdit()
        self.e_data_fattura.setCalendarPopup(True)
        self.e_data_fattura.setDate(datetime.date.today())
        self.e_data_fattura.setDisplayFormat("dd/MM/yyyy")
        dati_layout.addWidget(self.e_data_fattura)
        dati_layout.addStretch()
        dati_group.setLayout(dati_layout)
        layout.addWidget(dati_group)

        servizi_group = QGroupBox("3. Servizi (Doppio click per modificare)")
        servizi_layout = QVBoxLayout()
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Carica da Archivio:"))
        self.combo_archivio_servizi = QComboBox()
        self.aggiorna_combo_archivio_servizi()
        toolbar.addWidget(self.combo_archivio_servizi)

        btn_agg_arch = QPushButton("Aggiungi")
        btn_agg_arch.clicked.connect(self.aggiungi_da_archivio)
        toolbar.addWidget(btn_agg_arch)
        toolbar.addSpacing(20)

        btn_manuale = QPushButton("+ Aggiungi Manuale")
        btn_manuale.clicked.connect(self.aggiungi_manuale)
        toolbar.addWidget(btn_manuale)
        btn_rimuovi = QPushButton("- Rimuovi")
        btn_rimuovi.clicked.connect(self.rimuovi_riga)
        toolbar.addWidget(btn_rimuovi)
        btn_mod_riga = QPushButton("Modifica")
        btn_mod_riga.clicked.connect(self.modifica_riga)
        toolbar.addWidget(btn_mod_riga)
        toolbar.addStretch()
        servizi_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Descrizione", "Prezzo", "Qta", "Natura", "Totale"])
        self.table.setColumnWidth(0, 250)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.cellDoubleClicked.connect(self.modifica_riga)
        servizi_layout.addWidget(self.table)
        servizi_group.setLayout(servizi_layout)
        layout.addWidget(servizi_group)

        azioni = QHBoxLayout()
        self.lbl_totali = QLabel("Imponibile: 0.00 | Totale: 0.00 EUR")
        self.lbl_totali.setStyleSheet("font-size: 14px; font-weight: bold;")
        azioni.addWidget(self.lbl_totali)
        azioni.addStretch()
        self.btn_genera = QPushButton("GENERA FATTURA")
        self.btn_genera.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        self.btn_genera.clicked.connect(self._on_genera_clicked)
        azioni.addWidget(self.btn_genera)
        layout.addLayout(azioni)
        return widget

    def create_storico_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        btn_esporta = QPushButton("Esporta CSV")
        btn_esporta.clicked.connect(self.esporta_csv)
        toolbar.addWidget(btn_esporta)
        layout.addLayout(toolbar)

        self.table_archivio = QTableWidget()
        self.table_archivio.setColumnCount(8)
        self.table_archivio.setHorizontalHeaderLabels(
            ["Numero", "Data", "Cliente", "Nome", "Cognome", "Totale", "Inviata", "File"]
        )
        self.table_archivio.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_archivio)

        totali_group = QGroupBox("Totali Storico")
        totali_layout = QHBoxLayout()
        self.lbl_totale_imponibile = QLabel("Imponibile: 0,00 €")
        self.lbl_totale_cassa = QLabel("Cassa: 0,00 €")
        self.lbl_totale_bollo = QLabel("Bollo: 0,00 €")
        self.lbl_totale_documento = QLabel("Totale Documento: 0,00 €")
        for lbl in (self.lbl_totale_imponibile, self.lbl_totale_cassa, self.lbl_totale_bollo):
            lbl.setStyleSheet("font-weight: bold;")
        self.lbl_totale_documento.setStyleSheet("font-weight: bold; color: green;")
        totali_layout.addWidget(self.lbl_totale_imponibile)
        totali_layout.addWidget(self.lbl_totale_cassa)
        totali_layout.addWidget(self.lbl_totale_bollo)
        totali_layout.addWidget(self.lbl_totale_documento)
        totali_layout.addStretch()
        totali_group.setLayout(totali_layout)
        layout.addWidget(totali_group)

        azioni = QHBoxLayout()
        btn_inviata = QPushButton("Marca come Inviata")
        btn_inviata.clicked.connect(self.marca_inviata)
        azioni.addWidget(btn_inviata)
        btn_non = QPushButton("Torna a Non Inviata")
        btn_non.clicked.connect(self.marca_non_inviata)
        azioni.addWidget(btn_non)
        btn_elimina = QPushButton("Elimina Fattura")
        btn_elimina.clicked.connect(self.elimina_fattura)
        azioni.addWidget(btn_elimina)
        btn_mod = QPushButton("Modifica Fattura")
        btn_mod.clicked.connect(self.modifica_fattura)
        azioni.addWidget(btn_mod)
        azioni.addStretch()
        btn_archivio = QPushButton("Salva Archivio")
        btn_archivio.clicked.connect(self._salva_archivio)
        azioni.addWidget(btn_archivio)
        layout.addLayout(azioni)

        self.carica_archivio_fatture()
        return widget

    def inizializza_campi_fattura(self):
        ultima = self.db.get_ultima_fattura()
        if ultima:
            try:
                self.e_numero_fattura.setText(str(int(ultima[0]) + 1))
            except ValueError:
                self.e_numero_fattura.setText("1")
        else:
            self.e_numero_fattura.setText("1")

        self.e_data_fattura.setDate(datetime.date.today())
        self.imposta_limiti_data()

        ultimo_cliente = self.db.get_ultimo_cliente_fatturato()
        if ultimo_cliente is not None:
            idx = self.combo_clienti.findData(ultimo_cliente)
            if idx >= 0:
                self.combo_clienti.setCurrentIndex(idx)
                self.mostra_dati_cliente()

    def imposta_limiti_data(self):
        data_max = datetime.date.today()
        data_min = data_max - datetime.timedelta(days=12)
        ultima = self.db.get_ultima_fattura()
        if ultima:
            try:
                data_ultima = datetime.datetime.strptime(ultima[1], "%Y-%m-%d").date()
                data_min = max(data_min, data_ultima)
            except ValueError:
                pass
        self.e_data_fattura.setMinimumDate(QDate.fromString(data_min.isoformat(), "yyyy-MM-dd"))
        self.e_data_fattura.setMaximumDate(QDate.fromString(data_max.isoformat(), "yyyy-MM-dd"))

    def aggiorna_combo_clienti(self):
        self.clienti_db = self.db.get_clienti()
        self.combo_clienti.clear()
        for c in self.clienti_db:
            piva = _row_get(c, "piva") or _row_get(c, "codice_fiscale")
            self.combo_clienti.addItem(f"{_nome_cliente(c)} ({piva}) - ID:{c[0]}", c[0])

    def _cliente_corrente(self):
        cliente_id = self.combo_clienti.currentData()
        return next((c for c in self.clienti_db if c[0] == cliente_id), None)

    def nuovo_cliente(self):
        dialog = NuovoClienteDialog(self)
        if dialog.exec():
            if self.db.aggiungi_cliente(dialog.get_dati()):
                QMessageBox.information(self, "Successo", "Cliente salvato!")
                self.aggiorna_combo_clienti()
            else:
                QMessageBox.critical(self, "Errore", "P.IVA o Codice Fiscale già esistenti.")

    def modifica_cliente(self):
        if self.combo_clienti.currentIndex() < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona un cliente da modificare.")
            return
        cliente = self._cliente_corrente()
        if not cliente:
            return
        dialog = NuovoClienteDialog(self, cliente)
        if dialog.exec():
            if self.db.modifica_cliente(cliente[0], dialog.get_dati()):
                QMessageBox.information(self, "Successo", "Cliente modificato!")
                self.aggiorna_combo_clienti()
                self.mostra_dati_cliente()
            else:
                QMessageBox.critical(self, "Errore", "Impossibile modificare il cliente.")

    def mostra_dati_cliente(self):
        if self.combo_clienti.currentIndex() < 0:
            self.lbl_cliente_info.setText("Nessun cliente selezionato")
            self.lbl_cliente_info.setStyleSheet("color: gray;")
            return
        cliente = self._cliente_corrente()
        if not cliente:
            return
        indirizzo = _row_get(cliente, "indirizzo")
        civico = _row_get(cliente, "numero_civico")
        if civico:
            indirizzo += f" {civico}"
        indirizzo += f", {_row_get(cliente, 'cap')} {_row_get(cliente, 'comune')} ({_row_get(cliente, 'provincia')})"
        piva = _row_get(cliente, "piva") or _row_get(cliente, "codice_fiscale")
        self.lbl_cliente_info.setText(f"{_nome_cliente(cliente)} | P.IVA: {piva} | {indirizzo}")
        self.lbl_cliente_info.setStyleSheet("color: black;")

    def aggiorna_combo_archivio_servizi(self):
        self.servizi_archivio = self.db.get_archivio_servizi()
        self.combo_archivio_servizi.clear()
        for s in self.servizi_archivio:
            descr = str(_row_get(s, "descrizione")).replace("\n", " ").replace("\r", "")
            self.combo_archivio_servizi.addItem(
                f"{descr} - €{s['prezzo_unitario']:.2f} ({s['natura_iva']})", s["id"]
            )

    def aggiungi_da_archivio(self):
        if self.combo_archivio_servizi.currentIndex() < 0:
            return
        srv_id = self.combo_archivio_servizi.currentData()
        srv = next((s for s in self.servizi_archivio if s["id"] == srv_id), None)
        if not srv:
            return
        self.righe_fattura.append({
            "desc": srv["descrizione"],
            "prezzo": srv["prezzo_unitario"],
            "qta": 1.0,
            "natura": srv["natura_iva"],
            "totale": srv["prezzo_unitario"],
        })
        self.aggiorna_table()

    def aggiungi_manuale(self):
        dialog = ModificaRigaDialog(self, nuovo=True, riga=None, db=self.db)
        dialog.salvato_archivio.connect(self.aggiorna_combo_archivio_servizi)
        if dialog.exec():
            riga = dialog.get_riga()
            if riga:
                self.righe_fattura.append(riga)
                self.aggiorna_table()

    def rimuovi_riga(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona una riga da rimuovere.")
            return
        del self.righe_fattura[row]
        self.aggiorna_table()

    def modifica_riga(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona una riga da modificare.")
            return
        dialog = ModificaRigaDialog(self, nuovo=False, riga=self.righe_fattura[row], db=self.db)
        dialog.salvato_archivio.connect(self.aggiorna_combo_archivio_servizi)
        if dialog.exec():
            riga = dialog.get_riga()
            if riga:
                self.righe_fattura[row] = riga
                self.aggiorna_table()

    def aggiorna_table(self):
        self.table.setRowCount(len(self.righe_fattura))
        for i, r in enumerate(self.righe_fattura):
            self.table.setItem(i, 0, QTableWidgetItem(r["desc"]))
            self.table.setItem(i, 1, QTableWidgetItem(f"{r['prezzo']:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{r['qta']:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(r["natura"]))
            self.table.setItem(i, 4, QTableWidgetItem(f"{r['totale']:.2f}"))
        self.calcola_totali_e_aggiorna_label()

    def _aggiorna_label_totali(self):
        self.calcola_totali_e_aggiorna_label()

    def _perc_cassa(self):
        try:
            return float(self.e_cassa_perc.text() or 0)
        except ValueError:
            return 0.0

    def calcola_totali_e_aggiorna_label(self, imponibile_lordo=None):
        if imponibile_lordo is None:
            imponibile_lordo = sum(r["totale"] for r in self.righe_fattura)
        imp_competenza = imponibile_lordo
        rivalsa = imp_competenza * 0.04 if self.var_rivalsa.isChecked() else 0
        cassa_perc = self._perc_cassa()
        cassa = imp_competenza * (cassa_perc / 100.0) if cassa_perc > 0 else 0
        bollo = 2.0 if imp_competenza > 77.47 else 0.0
        totale = imp_competenza + rivalsa + cassa
        if self.var_bollo_al_totale.isChecked():
            totale += bollo
        self.lbl_totali.setText(
            f"Imp.Competenza: {imp_competenza:.2f} | Rivalsa: {rivalsa:.2f} | "
            f"Cassa: {cassa:.2f} | Bollo: {bollo:.2f} | TOTALE: {totale:.2f} EUR"
        )
        return imp_competenza, rivalsa, cassa, bollo, totale

    def salva_config(self):
        cassa_perc = self._perc_cassa()
        dati = (
            "", self.e_az_nom.text(), self.e_az_cog.text(),
            self.e_az_indirizzo.text(), self.e_az_num_civico.text(),
            self.e_az_cap.text(), self.e_az_comune.text(), self.e_az_prov.text(),
            self.e_az_piva.text(), self.e_az_cf.text(),
            self.cb_tipo_prof.currentText(),
            self.e_az_titolo.text(), self.e_num_albo.text(), self.e_prov_albo.text(),
            self.e_data_iscr_albo.text(), self.e_cassa_app.text(),
            1 if self.var_rivalsa.isChecked() else 0, 4.0,
            1 if cassa_perc > 0 else 0, cassa_perc, "Contributo Cassa",
            "0000000", self.e_albo_prof.text(), self.e_iban.text(),
        )
        self.db.update_azienda(dati)
        self.azienda = self.db.get_azienda()
        QMessageBox.information(self, "Salvato", "Configurazione aggiornata.")

    def _scarica_file(self, percorso_file):
        if not percorso_file or not os.path.exists(percorso_file):
            QMessageBox.warning(self, "Attenzione", "File non trovato.")
            return
        dest_path, _ = QFileDialog.getSaveFileName(
            self, "Salva file", os.path.basename(percorso_file), "All Files (*)"
        )
        if dest_path:
            shutil.copy2(percorso_file, dest_path)
            QMessageBox.information(self, "Successo", f"File salvato in:\n{dest_path}")

    def _salva_archivio(self):
        db_path = self.db.db_path
        if not os.path.exists(db_path):
            QMessageBox.warning(self, "Errore", "File del database non trovato.")
            return
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(os.path.basename(db_path))
        backup_path = os.path.join(os.path.dirname(os.path.abspath(db_path)) or ".", f"{base}_{timestamp}{ext}")
        try:
            shutil.copy2(db_path, backup_path)
            QMessageBox.information(self, "Successo", f"Archivio salvato come:\n{backup_path}")
        except OSError as e:
            QMessageBox.warning(self, "Errore", f"Impossibile salvare l'archivio: {e}")

    def carica_archivio_fatture(self):
        self._storico = list(self.db.get_storico_fatture_completo())
        self.table_archivio.setRowCount(len(self._storico))
        tot_imp = tot_cassa = tot_bollo = tot_doc = 0
        for i, f in enumerate(self._storico):
            self.table_archivio.setItem(i, 0, QTableWidgetItem(f[1]))
            self.table_archivio.setItem(i, 1, QTableWidgetItem(f[2]))
            self.table_archivio.setItem(i, 2, QTableWidgetItem(f[3] or ""))
            self.table_archivio.setItem(i, 3, QTableWidgetItem(f[13] or ""))
            self.table_archivio.setItem(i, 4, QTableWidgetItem(f[14] or ""))
            self.table_archivio.setItem(i, 5, QTableWidgetItem(f"€{f[8]:.2f}".replace(".", ",")))

            inviata_item = QTableWidgetItem("Sì" if f[11] else "No")
            inviata_item.setForeground(QColor("green") if f[11] else QColor("red"))
            self.table_archivio.setItem(i, 6, inviata_item)

            xml_path, pdf_path = f[9], f[10]
            file_widget = QWidget()
            file_layout = QHBoxLayout(file_widget)
            file_layout.setContentsMargins(2, 2, 2, 2)
            file_layout.setSpacing(4)
            btn_pdf = QPushButton("PDF")
            btn_pdf.setStyleSheet("padding: 2px 8px; font-size: 10px;")
            btn_pdf.setEnabled(bool(pdf_path) and os.path.exists(pdf_path))
            btn_pdf.clicked.connect(lambda checked=False, p=pdf_path: self._scarica_file(p))
            btn_xml = QPushButton("XML")
            btn_xml.setStyleSheet("padding: 2px 8px; font-size: 10px;")
            btn_xml.setEnabled(bool(xml_path) and os.path.exists(xml_path))
            btn_xml.clicked.connect(lambda checked=False, p=xml_path: self._scarica_file(p))
            file_layout.addWidget(btn_pdf)
            file_layout.addWidget(btn_xml)
            self.table_archivio.setCellWidget(i, 7, file_widget)

            tot_imp += f[4] or 0
            tot_cassa += f[6] or 0
            tot_bollo += f[7] or 0
            tot_doc += f[8] or 0

        self.lbl_totale_imponibile.setText(f"Imponibile: {tot_imp:.2f} €".replace(".", ","))
        self.lbl_totale_cassa.setText(f"Cassa: {tot_cassa:.2f} €".replace(".", ","))
        self.lbl_totale_bollo.setText(f"Bollo: {tot_bollo:.2f} €".replace(".", ","))
        self.lbl_totale_documento.setText(f"Totale Documento: {tot_doc:.2f} €".replace(".", ","))

    def _conferma_stato_invio(self, inviata):
        fattura = self._get_fattura_selezionata()
        if not fattura:
            QMessageBox.warning(self, "Attenzione", "Seleziona una fattura.")
            return
        domanda = (
            "Vuoi marcare questa fattura come inviata?"
            if inviata else
            "Vuoi marcare questa fattura come non inviata?"
        )
        reply = QMessageBox.question(
            self, "Conferma", domanda,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        if inviata:
            self.db.marca_inviata(fattura[0])
            msg = "Fattura marcata come inviata."
        else:
            self.db.marca_non_inviata(fattura[0])
            msg = "Fattura marcata come non inviata."
        self.carica_archivio_fatture()
        QMessageBox.information(self, "Successo", msg)

    def marca_inviata(self):
        self._conferma_stato_invio(True)

    def marca_non_inviata(self):
        self._conferma_stato_invio(False)

    def elimina_fattura(self):
        fattura = self._get_fattura_selezionata()
        if not fattura:
            QMessageBox.warning(self, "Attenzione", "Seleziona una fattura.")
            return
        if fattura[11]:
            QMessageBox.warning(self, "Attenzione", "Non è possibile eliminare una fattura già inviata.")
            return
        reply = QMessageBox.question(
            self, "Conferma Eliminazione",
            "Vuoi eliminare questa fattura? Questa azione è irreversibile.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.elimina_fattura(fattura[0])
            self.carica_archivio_fatture()
            self.inizializza_campi_fattura()
            QMessageBox.information(self, "Successo", "Fattura eliminata.")

    def modifica_fattura(self):
        if not self._storico:
            QMessageBox.warning(self, "Attenzione", "Nessuna fattura disponibile per la modifica.")
            return
        row = self.table_archivio.currentRow()
        if row < 0:
            row = len(self._storico) - 1
        fattura = self._storico[row]
        if fattura[11]:
            QMessageBox.warning(self, "Attenzione", "Non è possibile modificare una fattura già inviata.")
            return
        self.fattura_in_modifica = fattura[0]
        self.tab_widget.setCurrentIndex(0)
        self.popola_campi_da_fattura(fattura[0])
        self.btn_genera.setText("AGGIORNA FATTURA")

    def popola_campi_da_fattura(self, fattura_id):
        risultato = self.db.get_fattura_by_id(fattura_id)
        if not risultato:
            QMessageBox.warning(self, "Errore", "Fattura non trovata.")
            return
        numero, data, cliente_id = risultato["numero"], risultato["data"], risultato["cliente_id"]
        try:
            self.e_numero_fattura.setText(str(numero))
            self.e_data_fattura.setMinimumDate(QDate(1, 1, 1))
            self.e_data_fattura.setMaximumDate(QDate.currentDate())
            self.e_data_fattura.setDate(QDate.fromString(data, "yyyy-MM-dd"))
            idx = self.combo_clienti.findData(cliente_id)
            if idx >= 0:
                self.combo_clienti.setCurrentIndex(idx)
                self.mostra_dati_cliente()

            xml_path = risultato["file_xml"]
            if not xml_path or not os.path.exists(xml_path):
                expected = os.path.join(CARTELLA_FATTURE, f"Fattura_{numero}_{data.replace('-', '')}.xml")
                if os.path.exists(expected):
                    xml_path = expected
                else:
                    QMessageBox.critical(
                        self, "Errore",
                        f"Impossibile trovare il file XML per la fattura {numero}.\n"
                        f"Percorso cercato: {risultato['file_xml']}\nPercorso alternativo: {expected}",
                    )
                    return
            self.righe_fattura = self.estrai_righe_da_xml(xml_path)
            self.aggiorna_table()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare i dati della fattura: {e}")

    def _prepara_fattura(self, escludi_id=None):
        if self.combo_clienti.currentIndex() < 0 or not self.righe_fattura:
            QMessageBox.warning(self, "Attenzione", "Seleziona un cliente e inserisci almeno una riga.")
            return None
        cliente = self._cliente_corrente()
        if not cliente:
            return None
        imp_comp, rivalsa, cassa, bollo, totale = self.calcola_totali_e_aggiorna_label()
        numero = self.e_numero_fattura.text()
        data_oggi = self.e_data_fattura.date().toString("yyyy-MM-dd")
        valido, messaggio = self.db.verifica_numero_fattura(numero, escludi_id=escludi_id)
        if not valido:
            QMessageBox.warning(self, "Attenzione", messaggio)
            return None
        valido, messaggio = self.db.verifica_data_fattura(data_oggi, numero=numero, escludi_id=escludi_id)
        if not valido:
            QMessageBox.warning(self, "Attenzione", messaggio)
            return None
        cassa_perc = self._perc_cassa()
        return {
            "cliente_id": cliente[0],
            "numero": numero,
            "data": data_oggi,
            "totali": (imp_comp, rivalsa, cassa, bollo, totale),
            "dati_xml": self._build_dati_xml(
                cliente, numero, data_oggi, imp_comp, rivalsa, cassa, bollo, totale, cassa_perc
            ),
        }

    def _percorsi_fattura(self, numero, data_oggi, riusa_esistenti=False):
        self._ensure_cartella_fatture()
        if riusa_esistenti and self.fattura_in_modifica:
            result = self.db.get_fattura_files(self.fattura_in_modifica)
            if result and result[0] and result[1]:
                return result[0], result[1]
        nome = f"Fattura_{numero}_{data_oggi.replace('-', '')}"
        return (
            os.path.join(CARTELLA_FATTURE, f"{nome}.xml"),
            os.path.join(CARTELLA_FATTURE, f"{nome}.pdf"),
        )

    def _on_genera_clicked(self):
        if self.fattura_in_modifica is not None:
            self.aggiorna_fattura()
        else:
            self.genera_fattura()

    def genera_fattura(self):
        prep = self._prepara_fattura()
        if not prep:
            return
        file_xml, file_pdf = self._percorsi_fattura(prep["numero"], prep["data"])
        try:
            self._salva_file_fattura(prep["dati_xml"], file_xml, file_pdf)
            imp_comp, rivalsa, cassa, bollo, totale = prep["totali"]
            self.db.salva_fattura((
                prep["numero"], prep["data"], prep["cliente_id"],
                imp_comp, rivalsa, cassa, bollo, totale, file_xml, file_pdf,
            ))
            self.carica_archivio_fatture()
            QMessageBox.information(
                self, "Successo",
                f"Fattura generata!\nXML: {file_xml}\nPDF: {file_pdf}\nRicorda di firmare l'XML.",
            )
            self.righe_fattura = []
            self.aggiorna_table()
            self.inizializza_campi_fattura()
        except OSError as e:
            QMessageBox.critical(self, "Errore", f"Impossibile generare: {e}")

    def aggiorna_fattura(self):
        prep = self._prepara_fattura(escludi_id=self.fattura_in_modifica)
        if not prep:
            return
        file_xml, file_pdf = self._percorsi_fattura(prep["numero"], prep["data"], riusa_esistenti=True)
        try:
            self._salva_file_fattura(prep["dati_xml"], file_xml, file_pdf)
            imp_comp, rivalsa, cassa, bollo, totale = prep["totali"]
            self.db.aggiorna_fattura(
                self.fattura_in_modifica,
                (prep["numero"], prep["data"], prep["cliente_id"],
                 imp_comp, rivalsa, cassa, bollo, totale, file_xml, file_pdf),
            )
            self.carica_archivio_fatture()
            QMessageBox.information(
                self, "Successo",
                f"Fattura aggiornata!\nXML: {file_xml}\nPDF: {file_pdf}\nRicorda di firmare l'XML.",
            )
            self.reset_form_to_nuova_fattura()
        except OSError as e:
            QMessageBox.critical(self, "Errore", f"Impossibile aggiornare: {e}")

    def reset_form_to_nuova_fattura(self):
        self.fattura_in_modifica = None
        self.btn_genera.setText("GENERA FATTURA")
        self.righe_fattura = []
        self.aggiorna_table()
        self.inizializza_campi_fattura()

    def esporta_csv(self):
        fatture = self.db.get_storico_fatture_completo()
        if not fatture:
            QMessageBox.warning(self, "Attenzione", "Nessuna fattura da esportare.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salva CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            try:
                CSVExporter.esporta_fatture(fatture, file_path)
                QMessageBox.information(self, "Successo", f"Archivio esportato in {file_path}")
            except OSError as e:
                QMessageBox.critical(self, "Errore", f"Impossibile esportare: {e}")
