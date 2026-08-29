import csv

class CSVExporter:
    @staticmethod
    def esporta_fatture(fatture, file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            # Header
            writer.writerow([
                'Numero', 'Data', 'Cliente', 'Nome', 'Cognome', 'Codice Fiscale',
                'Imponibile Competenza', 'Rivalsa INPS', 'Cassa Professionale',
                'Bollo', 'Totale Documento'
            ])

            # Dati
            for f in fatture:
                writer.writerow([
                    f[1],  # Numero
                    f[2],  # Data
                    f[3],  # Cliente
                    f[13], # Nome
                    f[14], # Cognome
                    f[12], # Codice Fiscale
                    f"{f[4]:.2f}".replace('.', ','),  # Imponibile Competenza
                    f"{f[5]:.2f}".replace('.', ','),  # Rivalsa
                    f"{f[6]:.2f}".replace('.', ','),  # Cassa
                    f"{f[7]:.2f}".replace('.', ','),  # Bollo
                    f"{f[8]:.2f}".replace('.', ',')   # Totale
                ])
