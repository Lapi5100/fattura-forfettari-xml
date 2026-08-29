import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import Database


CLIENTE_DATI = (
    "Acme SRL", "", "", "Via Roma", "1", "00100", "Roma", "RM", "IT",
    "IT12345678901", "12345678901", "0000000", "B2B",
)


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "test.sqlite"))
    yield database
    database.conn.close()


@pytest.fixture
def db_con_cliente(db):
    db.aggiungi_cliente(CLIENTE_DATI)
    return db


@pytest.fixture
def dati_fattura_esempio():
    return {
        "cedente_denominazione": "Mario Rossi",
        "cedente_nome": "Mario",
        "cedente_cognome": "Rossi",
        "cedente_indirizzo": "Via Test",
        "cedente_num_civico": "1",
        "cedente_cap": "00100",
        "cedente_comune": "Roma",
        "cedente_prov": "RM",
        "cedente_piva": "IT12345678901",
        "cedente_cf": "RSSMRA80A01H501U",
        "cedente_titolo": "",
        "tipo_professionista": "Commercialista",
        "tipo_cassa": "TC02",
        "numero_albo": "123",
        "provincia_albo": "RM",
        "data_iscrizione_albo": "01/01/2020",
        "cassa_appartenenza": "Cassa commercialisti",
        "albo_professionale": "Commercialisti",
        "iban": "IT60X0542811101000000123456",
        "regime_fiscale": "RF19",
        "cliente_denominazione": "Acme SRL",
        "cliente_nome": "",
        "cliente_cognome": "",
        "cliente_indirizzo": "Via Roma",
        "cliente_num_civico": "1",
        "cliente_cap": "00100",
        "cliente_comune": "Roma",
        "cliente_prov": "RM",
        "cliente_nazione": "IT",
        "cliente_piva": "IT98765432109",
        "cliente_cf": "98765432109",
        "codice_sdi_dest": "0000000",
        "numero": "1",
        "data": "2026-06-30",
        "progressivo": "1",
        "righe": [
            {
                "desc": "Consulenza",
                "qta": 1.0,
                "prezzo": 100.0,
                "totale": 100.0,
                "natura": "N2.2",
            }
        ],
        "imponibile_competenza": 100.0,
        "rivalsa": 4.0,
        "perc_rivalsa": 4.0,
        "cassa_albo": 0.0,
        "perc_cassa": 0.0,
        "bollo": 2.0,
        "totale_documento": 106.0,
        "natura_riepilogo": "N2.2",
    }


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
