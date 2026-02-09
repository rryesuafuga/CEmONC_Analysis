# 🏥 Mbale RRH Neonatal Unit — Monthly Reporting Tool

Automated reporting tool for the Neonatal Unit at Mbale Regional Referral Hospital, Uganda. Generates publication-quality tables and Lancet-style visualizations from monthly logbook data.

## Features

- Upload password-protected Excel spreadsheets or CSV exports
- Generates all 12 required monthly report sections
- Publication-quality tables with Lancet journal styling
- Interactive Plotly visualizations
- Downloadable Excel report with all tables
- Sub-reports for deaths only, ELBW (<1000g), and VLBW (1000–1499g)
- Filter by specific month(s) or view cumulative data

## Quick Start

```bash
# Clone the repository
git clone https://github.com/<your-username>/neonatal-report.git
cd neonatal-report

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Deployment

See [ARCHITECTURE.md](ARCHITECTURE.md) for full deployment instructions including:
- Streamlit Community Cloud (free, recommended)
- Docker container
- Private server (VPS)

## Developed By

**Raymond R. Wayesu** — Biostatistician, Elgon Centre for Health Research & Innovation (ELCHRI)

Commissioned by **Dr Adam Hewitt-Smith**, Mbale Regional Referral Hospital / University of Oxford
