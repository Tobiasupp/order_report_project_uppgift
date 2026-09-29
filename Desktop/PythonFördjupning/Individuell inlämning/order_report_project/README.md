Beroenden : Pandas, pytest finns listat i requirements

Installation och förberedelser:

Projektet kräver **Python 3.10+**. Alla beroenden finns listade i `requirements.txt`.

1. Klona eller ladda ned projektmappen.
2. Skapa och aktivera en virtuell miljö:
   python -m venv .venv

Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

macOS/Linux:
source .venv/bin/activate

Installera beroenden
  
pip install -r requirements.txt

För att köra programmet kör från order_report_project:

python order_report.py

För testerna kör följande från samma mapp

python -m pytest

Order Report Project

Ett modulärt Python-projekt för automatiserad inläsning, validering, städning och rapportgenerering av orderdata. Programmet analyserar försäljnings- och returstatistik per kategori och region.


Projektstruktur


order_report_project/
├── data/
│   └── orders.csv             # Käll-CSV med orderdata
├── output/                    # Genererade CSV-rapporter
├── src/
│   └── order_report/          # Huvudpaket för källkod
│       ├── __init__.py
│       ├── config.py          # Dataclass för inställningar & sökvägar
│       ├── loading.py         # Filinläsning och sparning
│       ├── processing.py      # Datastädning och beräkningar
│       ├── reporting.py       # Aggregering och rapportskapande
│       └── validation.py      # Validering av struktur och datakvalitet
├── tests/
│   └── test_analytics.py      # Enhetstester med pytest
├── order_report.py            # Huvudfil / Entrypoint
├── requirements.txt           # Projektets beroenden
└── README.md