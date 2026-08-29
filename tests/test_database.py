import os

from conftest import CLIENTE_DATI


def test_inizializza_dati_base(db):
    azienda = db.get_azienda()
    assert azienda is not None
    assert azienda[2] == "Mario"
    assert len(db.get_archivio_servizi()) == 3


def test_aggiungi_e_recupera_cliente(db):
    assert db.aggiungi_cliente(CLIENTE_DATI) is True
    clienti = db.get_clienti()
    assert len(clienti) == 1
    assert clienti[0][1] == "Acme SRL"


def test_salva_fattura_e_storico(db_con_cliente, tmp_path):
    xml_path = str(tmp_path / "fattura.xml")
    pdf_path = str(tmp_path / "fattura.pdf")
    open(xml_path, "w").close()
    open(pdf_path, "w").close()

    db_con_cliente.salva_fattura(
        ("1", "2026-06-01", 1, 100.0, 4.0, 0.0, 2.0, 106.0, xml_path, pdf_path)
    )

    storico = db_con_cliente.get_storico_fatture()
    assert len(storico) == 1
    assert storico[0][1] == "1"
    assert storico[0][6] == 106.0


def test_verifica_numero_fattura(db_con_cliente, tmp_path):
    db_con_cliente.salva_fattura(
        ("10", "2026-06-01", 1, 100.0, 0.0, 0.0, 0.0, 100.0, "a.xml", "a.pdf")
    )

    ok, _ = db_con_cliente.verifica_numero_fattura("10")
    assert ok is False

    ok, _ = db_con_cliente.verifica_numero_fattura("5")
    assert ok is False

    ok, _ = db_con_cliente.verifica_numero_fattura("11")
    assert ok is True

    ok, messaggio = db_con_cliente.verifica_numero_fattura("abc")
    assert ok is False
    assert "numero intero" in messaggio


def test_verifica_numero_fattura_escludi_id(db_con_cliente):
    db_con_cliente.salva_fattura(
        ("10", "2026-06-01", 1, 100.0, 0.0, 0.0, 0.0, 100.0, "a.xml", "a.pdf")
    )
    fattura_id = db_con_cliente.get_storico_fatture()[0][0]

    ok, _ = db_con_cliente.verifica_numero_fattura("10", escludi_id=fattura_id)
    assert ok is True


def test_verifica_data_fattura(db_con_cliente):
    db_con_cliente.salva_fattura(
        ("1", "2026-06-15", 1, 100.0, 0.0, 0.0, 0.0, 100.0, "a.xml", "a.pdf")
    )

    ok, _ = db_con_cliente.verifica_data_fattura("2026-06-01")
    assert ok is False

    ok, _ = db_con_cliente.verifica_data_fattura("2026-06-20")
    assert ok is True


def test_aggiorna_e_marca_inviata(db_con_cliente, tmp_path):
    xml_path = str(tmp_path / "f1.xml")
    pdf_path = str(tmp_path / "f1.pdf")
    open(xml_path, "w").close()
    open(pdf_path, "w").close()

    db_con_cliente.salva_fattura(
        ("1", "2026-06-01", 1, 100.0, 0.0, 0.0, 0.0, 100.0, xml_path, pdf_path)
    )
    fattura_id = db_con_cliente.get_storico_fatture()[0][0]

    db_con_cliente.aggiorna_fattura(
        fattura_id,
        ("1", "2026-06-02", 1, 150.0, 0.0, 0.0, 0.0, 150.0, xml_path, pdf_path),
    )
    fattura = db_con_cliente.get_fattura_by_id(fattura_id)
    assert fattura[2] == "2026-06-02"
    assert fattura[8] == 150.0

    db_con_cliente.marca_inviata(fattura_id)
    assert db_con_cliente.get_storico_fatture()[0][8] == 1

    db_con_cliente.marca_non_inviata(fattura_id)
    assert db_con_cliente.get_storico_fatture()[0][8] == 0


def test_elimina_fattura_rimuove_file(db_con_cliente, tmp_path):
    xml_path = tmp_path / "da_eliminare.xml"
    pdf_path = tmp_path / "da_eliminare.pdf"
    xml_path.write_text("<xml/>")
    pdf_path.write_text("pdf")

    db_con_cliente.salva_fattura(
        ("1", "2026-06-01", 1, 100.0, 0.0, 0.0, 0.0, 100.0, str(xml_path), str(pdf_path))
    )
    fattura_id = db_con_cliente.get_storico_fatture()[0][0]

    db_con_cliente.elimina_fattura(fattura_id)

    assert db_con_cliente.get_storico_fatture() == []
    assert not os.path.exists(xml_path)
    assert not os.path.exists(pdf_path)
