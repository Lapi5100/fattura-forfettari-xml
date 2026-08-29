import csv
from pathlib import Path

from utils.csv_exporter import CSVExporter


def test_esporta_fatture_formato_italiano(tmp_path):
    fatture = [
        (
            1, "10", "2026-06-01", "Acme SRL", 100.0, 4.0, 0.0, 2.0, 106.0,
            "a.xml", "a.pdf", 0, "12345678901", "Mario", "Verdi",
        )
    ]
    output = tmp_path / "export.csv"
    CSVExporter.esporta_fatture(fatture, str(output))

    with open(output, encoding="utf-8") as csvfile:
        rows = list(csv.reader(csvfile, delimiter=";"))

    assert rows[0][0] == "Numero"
    assert rows[1][0] == "10"
    assert rows[1][6] == "100,00"
    assert rows[1][10] == "106,00"
