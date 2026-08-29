import xml.etree.ElementTree as ET
from xml.dom import minidom

from fpdf import FPDF

CASSA_PREVIDENZIALE = {
    "avvocato": {
        "nome": "Cassa nazionale previdenza e assistenza avvocati e procuratori legali",
        "tipo": "TC01",
    },
    "commercialista": {
        "nome": "Cassa previdenza dottori commercialisti",
        "tipo": "TC02",
    },
    "ingegnere": {
        "nome": "Cassa nazionale previdenza e assistenza ingegneri e architetti liberi professionisti",
        "tipo": "TC04",
    },
    "architetto": {
        "nome": "Cassa nazionale previdenza e assistenza ingegneri e architetti liberi professionisti",
        "tipo": "TC04",
    },
    "consulente_lavoro": {
        "nome": "Ente nazionale previdenza e assistenza consulenti del lavoro (ENPACL)",
        "tipo": "TC08",
    },
    "geometra": {
        "nome": "Cassa previdenza e assistenza geometri",
        "tipo": "TC03",
    },
    "perito_industriale": {
        "nome": "Ente previdenza periti industriali e periti industriali laureati (EPPI)",
        "tipo": "TC17",
    },
    "attuario": {
        "nome": "Ente previdenza e assistenza pluricategoriale (EPAP)",
        "tipo": "TC18",
    },
    "chimico": {
        "nome": "Ente previdenza e assistenza pluricategoriale (EPAP)",
        "tipo": "TC18",
    },
    "fisico": {
        "nome": "Ente previdenza e assistenza pluricategoriale (EPAP)",
        "tipo": "TC18",
    },
    "agronomo": {
        "nome": "Ente previdenza e assistenza pluricategoriale (EPAP)",
        "tipo": "TC18",
    },
    "forestale": {
        "nome": "Ente previdenza e assistenza pluricategoriale (EPAP)",
        "tipo": "TC18",
    },
    "geologo": {
        "nome": "Ente previdenza e assistenza pluricategoriale (EPAP)",
        "tipo": "TC18",
    },
    "biologo": {
        "nome": "Ente nazionale previdenza e assistenza biologi (ENPAB)",
        "tipo": "TC19",
    },
    "guida_alpina": {
        "nome": "INPS",
        "tipo": "TC22",
    },
}

MAPPA_PROFESSIONI = {
    "Avvocato": "avvocato",
    "Commercialista": "commercialista",
    "Consulente del Lavoro": "consulente_lavoro",
    "Ingegnere": "ingegnere",
    "Architetto": "architetto",
    "Geometra": "geometra",
    "Perito Industriale": "perito_industriale",
    "Attuario": "attuario",
    "Chimico": "chimico",
    "Fisico": "fisico",
    "Agronomo": "agronomo",
    "Forestale": "forestale",
    "Geologo": "geologo",
    "Biologo": "biologo",
    "Guida Alpina": "guida_alpina",
}


def get_cassa_professione(professione):
    chiave = MAPPA_PROFESSIONI.get(professione or "")
    return CASSA_PREVIDENZIALE.get(chiave) if chiave else None


def get_tipo_cassa_professione(professione):
    cassa = get_cassa_professione(professione)
    return cassa["tipo"] if cassa else "TC99"


def _el(parent, tag, text=None):
    node = ET.SubElement(parent, tag)
    if text is not None:
        node.text = text
    return node


def _el_if(parent, tag, text):
    if text:
        _el(parent, tag, text)


def _codice_iva(piva):
    piva = piva or ""
    return piva[2:] if piva.startswith("IT") else piva


def _euro(valore):
    return f"{valore:.2f}"


class Generatore:
    @staticmethod
    def crea_xml(dati):
        root = ET.Element("p:FatturaElettronica", {
            "xmlns:ds": "http://www.w3.org/2000/09/xmldsig#",
            "xmlns:p": "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2",
            "versione": "FPR12",
        })

        header = _el(root, "FatturaElettronicaHeader")
        dt = _el(header, "DatiTrasmissione")
        id_trasm = _el(dt, "IdTrasmittente")
        _el(id_trasm, "IdPaese", "IT")
        _el(id_trasm, "IdCodice", dati["cedente_cf"])
        _el(dt, "ProgressivoInvio", dati["progressivo"])
        _el(dt, "FormatoTrasmissione", "FPR12")
        _el(dt, "CodiceDestinatario", dati["codice_sdi_dest"])

        cedente = _el(header, "CedentePrestatore")
        da_c = _el(cedente, "DatiAnagrafici")
        if_c = _el(da_c, "IdFiscaleIVA")
        _el(if_c, "IdPaese", "IT")
        _el(if_c, "IdCodice", _codice_iva(dati["cedente_piva"]))
        _el(da_c, "CodiceFiscale", dati["cedente_cf"])
        an_c = _el(da_c, "Anagrafica")
        _el(an_c, "Nome", dati["cedente_nome"])
        _el(an_c, "Cognome", dati["cedente_cognome"])
        _el_if(an_c, "Titolo", dati.get("cedente_titolo"))
        _el_if(da_c, "AlboProfessionale", dati.get("albo_professionale"))
        _el_if(da_c, "ProvinciaAlbo", dati.get("provincia_albo"))
        _el_if(da_c, "NumeroIscrizioneAlbo", dati.get("numero_albo"))
        _el_if(da_c, "DataIscrizioneAlbo", dati.get("data_iscrizione_albo"))
        _el(da_c, "RegimeFiscale", "RF19")

        sede_c = _el(cedente, "Sede")
        _el(sede_c, "Indirizzo", dati["cedente_indirizzo"])
        _el_if(sede_c, "NumeroCivico", dati.get("cedente_num_civico"))
        _el(sede_c, "CAP", dati["cedente_cap"])
        _el(sede_c, "Comune", dati["cedente_comune"])
        _el(sede_c, "Provincia", dati["cedente_prov"])
        _el(sede_c, "Nazione", "IT")

        cess = _el(header, "CessionarioCommittente")
        da_cc = _el(cess, "DatiAnagrafici")
        cliente_piva = dati.get("cliente_piva") or ""
        if len(cliente_piva) > 5:
            if_cc = _el(da_cc, "IdFiscaleIVA")
            _el(if_cc, "IdPaese", "IT")
            _el(if_cc, "IdCodice", _codice_iva(cliente_piva))
        if dati.get("cliente_cf"):
            _el(da_cc, "CodiceFiscale", dati["cliente_cf"])
        an_cc = _el(da_cc, "Anagrafica")
        if dati["cliente_denominazione"]:
            _el(an_cc, "Denominazione", dati["cliente_denominazione"])
        else:
            _el(an_cc, "Nome", dati["cliente_nome"])
            _el(an_cc, "Cognome", dati["cliente_cognome"])

        sede_cc = _el(cess, "Sede")
        _el(sede_cc, "Indirizzo", dati["cliente_indirizzo"])
        _el_if(sede_cc, "NumeroCivico", dati.get("cliente_num_civico"))
        _el(sede_cc, "CAP", dati["cliente_cap"])
        _el(sede_cc, "Comune", dati["cliente_comune"])
        _el(sede_cc, "Provincia", dati["cliente_prov"])
        _el(sede_cc, "Nazione", dati["cliente_nazione"])

        body = _el(root, "FatturaElettronicaBody")
        dgd = _el(_el(body, "DatiGenerali"), "DatiGeneraliDocumento")
        _el(dgd, "TipoDocumento", "TD01")
        _el(dgd, "Divisa", "EUR")
        _el(dgd, "Data", dati["data"])
        _el(dgd, "Numero", dati["numero"])

        if dati["bollo"] > 0:
            dbollo = _el(dgd, "DatiBollo")
            _el(dbollo, "BolloVirtuale", "SI")
            _el(dbollo, "ImportoBollo", _euro(dati["bollo"]))

        def _blocco_cassa(tipo, perc, importo):
            dcp = _el(dgd, "DatiCassaPrevidenziale")
            _el(dcp, "TipoCassa", tipo)
            _el(dcp, "AlCassa", _euro(perc))
            _el(dcp, "ImportoContributoCassa", _euro(importo))
            _el(dcp, "ImponibileCassa", _euro(dati["imponibile_competenza"]))
            _el(dcp, "AliquotaIVA", "0.00")
            _el(dcp, "Natura", "N2.2")

        if dati["rivalsa"] > 0:
            _blocco_cassa("TC07", dati["perc_rivalsa"], dati["rivalsa"])
        if dati["cassa_albo"] > 0:
            _blocco_cassa(dati.get("tipo_cassa", "TC99"), dati["perc_cassa"], dati["cassa_albo"])

        _el(dgd, "ImportoTotaleDocumento", _euro(dati["totale_documento"]))

        dbs = _el(body, "DatiBeniServizi")
        for i, r in enumerate(dati["righe"], start=1):
            dl = _el(dbs, "DettaglioLinee")
            _el(dl, "NumeroLinea", str(i))
            _el(dl, "Descrizione", r["desc"])
            _el(dl, "Quantita", _euro(r["qta"]))
            _el(dl, "PrezzoUnitario", _euro(r["prezzo"]))
            _el(dl, "PrezzoTotale", _euro(r["totale"]))
            _el(dl, "AliquotaIVA", "0.00")
            _el(dl, "Natura", r["natura"])

        riep = _el(dbs, "DatiRiepilogo")
        _el(riep, "AliquotaIVA", "0.00")
        _el(riep, "Natura", dati["natura_riepilogo"])
        _el(riep, "ImponibileImporto", _euro(dati["imponibile_competenza"]))
        _el(riep, "Imposta", "0.00")

        xml_str = ET.tostring(root, encoding="utf-8", method="xml")
        pretty = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding="utf-8")
        lines = pretty.split(b"\n")
        return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + b"\n".join(lines[1:])

    @staticmethod
    def crea_pdf(dati, nome_file=None):
        del nome_file
        pdf = FPDF()
        pdf.add_page()

        pdf.set_draw_color(0, 100, 255)
        pdf.set_line_width(0.5)
        pdf.rect(5, 5, 200, 287, "D")
        pdf.set_draw_color(255, 165, 0)
        pdf.set_line_width(0.3)
        pdf.rect(6, 6, 198, 285, "D")

        pdf.set_y(10)
        pdf.set_x(10)
        pdf.set_font("Arial", size=9)

        indirizzo_prof = dati["cedente_indirizzo"]
        if dati.get("cedente_num_civico"):
            indirizzo_prof += f" {dati['cedente_num_civico']}"
        parti = []
        if dati.get("tipo_professionista"):
            parti.append(dati["tipo_professionista"])
        parti.extend([
            f"{dati['cedente_nome']} {dati['cedente_cognome']}",
            indirizzo_prof,
            f"{dati['cedente_cap']} {dati['cedente_comune']} ({dati['cedente_prov']})",
            f"Codice Fiscale: {dati['cedente_cf']}",
            f"Partita IVA: {dati['cedente_piva']}",
        ])
        pdf.multi_cell(95, 4, "\n".join(parti), 0, "L")

        pdf.set_font("Arial", "B", 11)
        pdf.cell(95, 4, "Regime Fiscale: Regime forfettario (art.1, c.54-89, L. 190/2014)", 0, 1)
        pdf.set_font("Arial", size=9)

        pdf.set_y(10)
        pdf.set_x(110)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(90, 10, "Fattura Ordinaria", ln=True, align="R")
        pdf.set_x(110)
        pdf.set_font("Arial", size=11)
        pdf.cell(90, 8, f"N. {dati['numero']}", ln=True, align="R")
        pdf.set_x(110)
        pdf.cell(90, 8, f"Data: {dati['data']}", ln=True, align="R")

        pdf.set_y(pdf.get_y() + 20)
        pdf.set_x(10)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(95, 6, "DESTINATARIO", 0, 1)
        pdf.set_font("Arial", size=9)

        nome_cliente = dati["cliente_denominazione"] or f"{dati['cliente_nome']} {dati['cliente_cognome']}"
        indirizzo_cli = dati["cliente_indirizzo"]
        if dati.get("cliente_num_civico"):
            indirizzo_cli += f" {dati['cliente_num_civico']}"
        fiscali = (
            f"P.IVA: {dati['cliente_piva']}"
            if dati.get("cliente_piva") and len(dati["cliente_piva"]) > 5
            else f"Codice Fiscale: {dati['cliente_cf']}"
        )
        pdf.multi_cell(
            95, 4,
            f"{nome_cliente}\n{indirizzo_cli}\n"
            f"{dati['cliente_cap']} {dati['cliente_comune']} ({dati['cliente_prov']})\n{fiscali}",
            0, "L",
        )
        pdf.ln(10)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(90, 7, "Descrizione", 1)
        pdf.cell(20, 7, "Qta", 1, align="C")
        pdf.cell(22, 7, "Prezzo", 1, align="R")
        pdf.cell(22, 7, "Totale", 1, align="R")
        pdf.cell(35, 7, "Natura", 1, align="C")
        pdf.ln()
        pdf.set_font("Arial", size=9)
        for r in dati["righe"]:
            x, y = pdf.get_x(), pdf.get_y()
            pdf.set_x(10)
            pdf.multi_cell(90, 5, r["desc"], 1, "L")
            h = pdf.get_y() - y
            pdf.set_xy(x + 90, y)
            pdf.cell(20, h, _euro(r["qta"]), 1, 0, "C")
            pdf.cell(22, h, f"Euro {_euro(r['prezzo'])}", 1, 0, "R")
            pdf.cell(22, h, f"Euro {_euro(r['totale'])}", 1, 0, "R")
            pdf.cell(35, h, "Non soggette - altri casi", 1, 0, "L")
            pdf.ln()

        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)

        def riga_totale(etichetta, importo):
            pdf.cell(145, 8, etichetta, 0, 0, "R")
            pdf.cell(35, 8, f"Euro {_euro(importo)}", 0, 0, "R")
            pdf.ln()

        riga_totale("Imponibile Competenza:", dati["imponibile_competenza"])
        if dati["rivalsa"] > 0:
            riga_totale(f"Rivalsa INPS ({dati['perc_rivalsa']}%):", dati["rivalsa"])
        if dati["cassa_albo"] > 0:
            riga_totale(f"Contributo Cassa ({dati['perc_cassa']}%):", dati["cassa_albo"])
        if dati["bollo"] > 0:
            riga_totale("Bollo virtuale:", dati["bollo"])
            pdf.set_font("Arial", size=7)
            pdf.cell(180, 4, "Bollo assolto ai sensi del decreto", 0, 1, "C")
            pdf.cell(180, 4, "MEF 17 GIUGNO 2014 (ART. 6)", 0, 1, "C")
            pdf.ln(2)

        totale_senza_bollo = dati["imponibile_competenza"] + dati["rivalsa"] + dati["cassa_albo"]
        pdf.set_font("Arial", "B", 14)
        pdf.cell(145, 10, "TOTALE:", 0, 0, "R")
        pdf.cell(35, 10, f"Euro {_euro(totale_senza_bollo)}", 0, 0, "R")
        pdf.ln(20)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 5, "Modalità di pagamento:", 0, 1)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, "Bonifico Bancario", 0, 1)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(30, 5, "IBAN:", 0, 0)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 5, dati.get("iban", "") or "", 0, 1)

        out = pdf.output(dest="S")
        return out if isinstance(out, bytearray) else out.encode("latin-1", "replace")
