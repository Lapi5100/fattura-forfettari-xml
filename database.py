import os
import sqlite3


class Database:
    def __init__(self, db_name="gestionale_forfettario_qt.sqlite"):
        self.db_path = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.crea_tabelle()
        self.inizializza_dati_base()

    def _colonne_mancanti(self, tabella, colonne):
        esistenti = {row[1] for row in self.cursor.execute(f"PRAGMA table_info({tabella})")}
        for nome, ddl in colonne.items():
            if nome not in esistenti:
                self.cursor.execute(f"ALTER TABLE {tabella} ADD COLUMN {ddl}")

    def crea_tabelle(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS azienda (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                denominazione TEXT, nome TEXT, cognome TEXT,
                indirizzo TEXT, numero_civico TEXT, cap TEXT, comune TEXT, provincia TEXT,
                piva TEXT, codice_fiscale TEXT,
                tipo_professionista TEXT, titolo TEXT, numero_albo TEXT, provincia_albo TEXT,
                data_iscrizione_albo TEXT, cassa_appartenenza TEXT,
                attiva_rivalsa BOOLEAN DEFAULT 0, perc_rivalsa REAL DEFAULT 4.0,
                attiva_cassa BOOLEAN DEFAULT 0, perc_cassa REAL DEFAULT 0.0, desc_cassa TEXT,
                lavoratore_spettacolo BOOLEAN DEFAULT 0,
                codice_sdi TEXT DEFAULT '0000000',
                albo_professionale TEXT,
                iban TEXT
            );
            CREATE TABLE IF NOT EXISTS clienti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                denominazione TEXT, nome TEXT, cognome TEXT,
                indirizzo TEXT, numero_civico TEXT, cap TEXT, comune TEXT, provincia TEXT,
                nazione TEXT DEFAULT 'IT',
                piva TEXT, codice_fiscale TEXT, codice_sdi TEXT DEFAULT '0000000',
                tipo_cliente TEXT DEFAULT 'B2B'
            );
            CREATE TABLE IF NOT EXISTS archivio_servizi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descrizione TEXT NOT NULL,
                prezzo_unitario REAL NOT NULL,
                unita_misura TEXT DEFAULT 'pz',
                natura_iva TEXT DEFAULT 'N2.2'
            );
            CREATE TABLE IF NOT EXISTS fatture (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL, data TEXT NOT NULL, cliente_id INTEGER,
                imponibile_competenza REAL, importo_rivalsa REAL, importo_cassa REAL,
                importo_bollo REAL, totale_documento REAL, file_xml TEXT, file_pdf TEXT,
                inviata BOOLEAN DEFAULT 0
            );
        """)
        self._colonne_mancanti("fatture", {"inviata": "inviata BOOLEAN DEFAULT 0"})
        self._colonne_mancanti("azienda", {
            "numero_civico": "numero_civico TEXT",
            "titolo": "titolo TEXT",
            "data_iscrizione_albo": "data_iscrizione_albo TEXT",
            "albo_professionale": "albo_professionale TEXT",
            "iban": "iban TEXT",
            "lavoratore_spettacolo": "lavoratore_spettacolo BOOLEAN DEFAULT 0",
        })
        self._colonne_mancanti("clienti", {"numero_civico": "numero_civico TEXT"})
        self.conn.commit()

    def inizializza_dati_base(self):
        if self.cursor.execute("SELECT COUNT(*) FROM azienda").fetchone()[0] == 0:
            self.cursor.execute("""
                INSERT INTO azienda (id, denominazione, nome, cognome, piva, codice_fiscale, lavoratore_spettacolo)
                VALUES (1, 'La Tua Attività', 'Mario', 'Rossi', 'IT12345678901', 'RSSMRA80A01H501U', 0)
            """)
        if self.cursor.execute("SELECT COUNT(*) FROM archivio_servizi").fetchone()[0] == 0:
            self.cursor.executemany(
                """INSERT INTO archivio_servizi
                   (descrizione, prezzo_unitario, unita_misura, natura_iva)
                   VALUES (?, ?, ?, ?)""",
                [
                    ("Consulenza Professionale", 50.00, "ora", "N2.2"),
                    ("Redazione Progetto", 150.00, "pz", "N2.2"),
                    ("Rimborso Spese", 20.00, "pz", "N2.2"),
                ],
            )
        self.conn.commit()

    def get_azienda(self):
        return self.cursor.execute("SELECT * FROM azienda WHERE id=1").fetchone()

    def update_azienda(self, dati):
        self.cursor.execute("""
            UPDATE azienda SET denominazione=?, nome=?, cognome=?, indirizzo=?, numero_civico=?,
            cap=?, comune=?, provincia=?, piva=?, codice_fiscale=?, tipo_professionista=?,
            titolo=?, numero_albo=?, provincia_albo=?, data_iscrizione_albo=?, cassa_appartenenza=?,
            attiva_rivalsa=?, perc_rivalsa=?, attiva_cassa=?, perc_cassa=?, desc_cassa=?,
            lavoratore_spettacolo=?, codice_sdi=?, albo_professionale=?, iban=? WHERE id=1
        """, dati)
        self.conn.commit()

    def get_clienti(self):
        return self.cursor.execute(
            "SELECT * FROM clienti ORDER BY denominazione, cognome"
        ).fetchall()

    def aggiungi_cliente(self, dati):
        try:
            self.cursor.execute("""
                INSERT INTO clienti (denominazione, nome, cognome, indirizzo, numero_civico, cap,
                    comune, provincia, nazione, piva, codice_fiscale, codice_sdi, tipo_cliente)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, dati)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def modifica_cliente(self, cliente_id, dati):
        try:
            self.cursor.execute("""
                UPDATE clienti SET denominazione=?, nome=?, cognome=?, indirizzo=?, numero_civico=?,
                    cap=?, comune=?, provincia=?, nazione=?, piva=?, codice_fiscale=?,
                    codice_sdi=?, tipo_cliente=?
                WHERE id=?
            """, dati + (cliente_id,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_archivio_servizi(self):
        return self.cursor.execute(
            "SELECT * FROM archivio_servizi ORDER BY descrizione"
        ).fetchall()

    def aggiungi_servizio_archivio(self, descrizione, prezzo_unitario, natura_iva):
        self.cursor.execute("""
            INSERT INTO archivio_servizi (descrizione, prezzo_unitario, unita_misura, natura_iva)
            VALUES (?, ?, 'pz', ?)
        """, (descrizione, prezzo_unitario, natura_iva))
        self.conn.commit()

    def salva_fattura(self, dati):
        self.cursor.execute("""
            INSERT INTO fatture (numero, data, cliente_id, imponibile_competenza, importo_rivalsa,
                importo_cassa, importo_bollo, totale_documento, file_xml, file_pdf, inviata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, dati)
        self.conn.commit()

    def get_fattura_by_id(self, fattura_id):
        return self.cursor.execute(
            "SELECT * FROM fatture WHERE id = ?", (fattura_id,)
        ).fetchone()

    def get_fattura_files(self, fattura_id):
        return self.cursor.execute(
            "SELECT file_xml, file_pdf FROM fatture WHERE id = ?", (fattura_id,)
        ).fetchone()

    def get_numero_fattura(self, fattura_id):
        row = self.cursor.execute(
            "SELECT numero FROM fatture WHERE id = ?", (fattura_id,)
        ).fetchone()
        return row[0] if row else None

    def aggiorna_fattura(self, fattura_id, dati):
        self.cursor.execute("""
            UPDATE fatture SET
            numero = ?, data = ?, cliente_id = ?, imponibile_competenza = ?,
            importo_rivalsa = ?, importo_cassa = ?, importo_bollo = ?,
            totale_documento = ?, file_xml = ?, file_pdf = ?
            WHERE id = ?
        """, dati + (fattura_id,))
        self.conn.commit()

    def elimina_fattura(self, fattura_id):
        result = self.get_fattura_files(fattura_id)
        if result:
            for path in (result[0], result[1]):
                if path and os.path.exists(path):
                    os.remove(path)
        self.cursor.execute("DELETE FROM fatture WHERE id = ?", (fattura_id,))
        self.conn.commit()

    def marca_inviata(self, fattura_id):
        self.cursor.execute("UPDATE fatture SET inviata = 1 WHERE id = ?", (fattura_id,))
        self.conn.commit()

    def marca_non_inviata(self, fattura_id):
        self.cursor.execute("UPDATE fatture SET inviata = 0 WHERE id = ?", (fattura_id,))
        self.conn.commit()

    def get_storico_fatture(self):
        return self.cursor.execute("""
            SELECT f.id, f.numero, f.data, c.denominazione, c.nome, c.cognome,
                    f.totale_documento, f.file_xml, f.inviata, f.file_pdf
            FROM fatture f JOIN clienti c ON f.cliente_id = c.id
            ORDER BY f.data ASC
        """).fetchall()

    def get_storico_fatture_completo(self):
        return self.cursor.execute("""
            SELECT f.id, f.numero, f.data, c.denominazione, f.imponibile_competenza,
                    f.importo_rivalsa, f.importo_cassa, f.importo_bollo, f.totale_documento,
                    f.file_xml, f.file_pdf, f.inviata, c.codice_fiscale, c.nome, c.cognome
            FROM fatture f JOIN clienti c ON f.cliente_id = c.id
            ORDER BY f.data ASC
        """).fetchall()

    def get_ultima_fattura(self):
        return self.cursor.execute(
            "SELECT numero, data FROM fatture ORDER BY data DESC, CAST(numero AS INTEGER) DESC LIMIT 1"
        ).fetchone()

    def get_ultimo_cliente_fatturato(self):
        row = self.cursor.execute(
            "SELECT cliente_id FROM fatture ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else None

    def verifica_numero_fattura(self, numero, escludi_id=None):
        try:
            numero_int = int(numero)
        except ValueError:
            return False, "Il numero della fattura deve essere un numero intero."

        escludi = escludi_id if escludi_id is not None else -1
        existing = self.cursor.execute(
            "SELECT id FROM fatture WHERE numero = ? AND id != ?",
            (numero, escludi),
        ).fetchone()
        if existing:
            return False, f"Esiste già una fattura con il numero {numero}."

        # Only enforce sequential numbering rules for new invoices (when not editing)
        if escludi_id is None:
            row = self.cursor.execute(
                "SELECT MAX(CAST(numero AS INTEGER)) FROM fatture WHERE id != ?",
                (escludi,),
            ).fetchone()
            max_num = row[0] if row else None
            if max_num is not None:
                if numero_int <= max_num:
                    return False, f"Il numero {numero} è inferiore o uguale alla fattura esistente {max_num}."
                if numero_int > max_num + 1:
                    return False, f"Il numero {numero} deve essere esattamente il successivo alla fattura esistente {max_num}."
        return True, None

    def verifica_data_fattura(self, data, numero=None, escludi_id=None):
        escludi = escludi_id if escludi_id is not None else -1
        if numero is not None:
            try:
                num_int = int(numero)
            except ValueError:
                return False, "Il numero della fattura deve essere un numero intero."
            row = self.cursor.execute("""
                SELECT data FROM fatture
                WHERE CAST(numero AS INTEGER) < ? AND id != ?
                ORDER BY CAST(numero AS INTEGER) DESC LIMIT 1
            """, (num_int, escludi)).fetchone()
            if row and data < row[0]:
                return False, (
                    f"La data {data} è precedente alla data della fattura "
                    f"numero {num_int - 1} ({row[0]})."
                )
            return True, None

        row = self.cursor.execute(
            "SELECT MAX(data) FROM fatture WHERE id != ?", (escludi,)
        ).fetchone()
        if row and row[0] and data < row[0]:
            return False, f"La data {data} è inferiore alla fattura esistente del {row[0]}."
        return True, None

    def executemany(self, query, params):
        self.cursor.executemany(query, params)
        self.conn.commit()