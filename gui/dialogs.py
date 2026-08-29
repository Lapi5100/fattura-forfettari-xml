from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
)


class NuovoClienteDialog(QDialog):
    def __init__(self, parent=None, cliente_dati=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica Cliente" if cliente_dati else "Nuovo Cliente")
        self.setFixedSize(400, 500)

        layout = QFormLayout(self)
        def campo(indice):
            if not cliente_dati:
                return ""
            val = cliente_dati[indice]
            return val if val is not None else ""

        self.e_denominazione = QLineEdit(campo(1))
        self.e_nome = QLineEdit(campo(2))
        self.e_cognome = QLineEdit(campo(3))
        self.e_indirizzo = QLineEdit(campo(4))
        self.e_num_civico = QLineEdit(campo(5))
        self.e_cap = QLineEdit(campo(6))
        self.e_comune = QLineEdit(campo(7))
        self.e_provincia = QLineEdit(campo(8))
        self.e_piva = QLineEdit(campo(10))
        self.e_cf = QLineEdit(campo(11))
        self.e_sdi = QLineEdit(campo(12))

        layout.addRow("Denominazione:", self.e_denominazione)
        layout.addRow("Nome:", self.e_nome)
        layout.addRow("Cognome:", self.e_cognome)
        layout.addRow("Indirizzo:", self.e_indirizzo)
        layout.addRow("N. Civico:", self.e_num_civico)
        layout.addRow("CAP:", self.e_cap)
        layout.addRow("Comune:", self.e_comune)
        layout.addRow("Provincia:", self.e_provincia)
        layout.addRow("P.IVA:", self.e_piva)
        layout.addRow("Cod. Fiscale:", self.e_cf)
        layout.addRow("Codice SDI:", self.e_sdi)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_dati(self):
        return (
            self.e_denominazione.text(), self.e_nome.text(), self.e_cognome.text(),
            self.e_indirizzo.text(), self.e_num_civico.text(), self.e_cap.text(),
            self.e_comune.text(), self.e_provincia.text(), "IT",
            self.e_piva.text(), self.e_cf.text(), self.e_sdi.text(), "B2B",
        )


class ModificaRigaDialog(QDialog):
    salvato_archivio = pyqtSignal()

    def __init__(self, parent=None, nuovo=True, riga=None, db=None):
        super().__init__(parent)
        self.setWindowTitle("Nuova Riga" if nuovo else "Modifica Riga")
        self.setFixedSize(500, 450)
        self.db = db

        layout = QFormLayout(self)
        dati = riga if not nuovo else {"desc": "", "prezzo": 0, "qta": 1, "natura": "N2.2"}

        self.e_desc = QTextEdit()
        self.e_desc.setPlainText(dati["desc"])
        self.e_desc.setMaximumHeight(80)
        self.e_prezzo = QLineEdit(str(dati["prezzo"]))
        self.e_qta = QLineEdit(str(dati["qta"]))
        self.cb_natura = QComboBox()
        self.cb_natura.addItems(["N2.2", "N2.1", "N1", "N4"])
        self.cb_natura.setCurrentText(dati["natura"])

        layout.addRow("Descrizione:", self.e_desc)
        layout.addRow("Prezzo Unit.:", self.e_prezzo)
        layout.addRow("Quantità:", self.e_qta)
        layout.addRow("Natura IVA:", self.cb_natura)

        btn_salva_archivio = QPushButton("Salva in Archivio")
        btn_salva_archivio.clicked.connect(self.salva_in_archivio)
        layout.addRow(btn_salva_archivio)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def salva_in_archivio(self):
        try:
            riga = self.get_riga()
            if riga and self.db:
                self.db.aggiungi_servizio_archivio(riga["desc"], riga["prezzo"], riga["natura"])
                QMessageBox.information(self, "Successo", "Servizio salvato nell'archivio!")
                self.salvato_archivio.emit()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile salvare: {e}")

    def get_riga(self):
        try:
            prezzo = float(self.e_prezzo.text().replace(",", "."))
            qta = float(self.e_qta.text().replace(",", "."))
            return {
                "desc": self.e_desc.toPlainText(),
                "prezzo": prezzo,
                "qta": qta,
                "natura": self.cb_natura.currentText(),
                "totale": prezzo * qta,
            }
        except ValueError:
            return None
