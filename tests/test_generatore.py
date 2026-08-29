import xml.etree.ElementTree as ET

from generatore import (
    CASSA_PREVIDENZIALE,
    MAPPA_PROFESSIONI,
    Generatore,
    get_cassa_professione,
    get_tipo_cassa_professione,
)


def test_mappa_professioni_allineata_a_cassa():
    for chiave in MAPPA_PROFESSIONI.values():
        assert chiave in CASSA_PREVIDENZIALE


def test_get_tipo_cassa_professione():
    assert get_tipo_cassa_professione("Avvocato") == "TC01"
    assert get_tipo_cassa_professione("Commercialista") == "TC02"
    assert get_tipo_cassa_professione("Sconosciuto") == "TC99"
    assert get_tipo_cassa_professione("") == "TC99"


def test_get_cassa_professione():
    cassa = get_cassa_professione("Biologo")
    assert cassa is not None
    assert cassa["tipo"] == "TC19"
    assert get_cassa_professione("") is None


def test_crea_xml_contiene_elementi_obbligatori(dati_fattura_esempio):
    xml_bytes = Generatore.crea_xml(dati_fattura_esempio)
    xml_text = xml_bytes.decode("utf-8")

    assert xml_text.startswith("<?xml")
    assert "FatturaElettronica" in xml_text
    assert "FPR12" in xml_text
    assert "RSSMRA80A01H501U" in xml_text
    assert "Consulenza" in xml_text
    assert "ImportoTotaleDocumento" in xml_text


def test_crea_xml_include_bollo_e_rivalsa(dati_fattura_esempio):
    root = ET.fromstring(Generatore.crea_xml(dati_fattura_esempio))
    xml_text = ET.tostring(root, encoding="unicode")

    assert "DatiBollo" in xml_text
    assert "DatiCassaPrevidenziale" in xml_text
    assert "2.00" in xml_text


def test_crea_pdf_restituisce_bytes(dati_fattura_esempio):
    pdf_bytes = Generatore.crea_pdf(dati_fattura_esempio, "fattura.xml")
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 100
    assert pdf_bytes[:4] == b"%PDF"
