# CEmONC Facility Readiness Assessment — Analysis Dashboard

Automated analysis dashboard for CEmONC (Comprehensive Emergency Obstetric and Newborn Care) Facility Readiness Assessment data from the Elgon Sub-Region, Uganda. Generates publication-quality tables, interactive visualisations, and downloadable Excel reports from KoboToolbox survey exports.

## Features

- Upload KoboToolbox exports (CSV or XLSX)
- Automatic handling of KoboToolbox group-prefixed column names
- Facility code-to-label mapping for 27 CEmONC facilities
- 12 domain readiness scores with WHO SARA threshold classification
- Overall readiness summary with key statistics
- Facility ranking with colour-coded readiness categories
- Domain-level comparison with mean and SD error bars
- Facility x Domain interactive heatmap
- Individual checklist item compliance analysis (optional)
- Assessment team comparison with box plots
- Filter by team, readiness category, or specific facility
- Downloadable Excel report with all analysis tables
- Publication-quality Lancet-style tables and Plotly visualisations

## Assessment Domains (12 Themes)

| # | Domain | Max Score |
|---|--------|-----------|
| 1 | ANC Quality | 18 |
| 2 | Intrapartum Care | 24 |
| 3 | Theatre | 7 |
| 4 | Postpartum Care | 5 |
| 5 | Other Important Areas | 4 |
| 6 | MCH Medicines | 8 |
| 7 | MPDSR | 7 |
| 8 | Human Resource | 4 |
| 9 | Diagnostics | 8 |
| 10 | Stores / MCH Commodities | 4 |
| 11 | Referral | 5 |
| 12 | Leadership | 3 |
| | **Grand Total** | **97** |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/rryesuafuga/CEmONC_Analysis.git
cd CEmONC_Analysis

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Data Source

Data is collected using the **CEmONC Facility Readiness Assessment XLSForm** deployed on KoboToolbox. See the `repurpose/` folder for:

- `CEmONC_Facility_Readiness_XLSForm.xlsx` — the XLSForm used for data collection
- `KoboToolbox_Setup_Guide_ELMNS.docx` — field setup guide for assessment teams
- `CEmONC_Analysis_Script.R` — the original R analysis script this dashboard is based on

### How to export data from KoboToolbox

1. Log into [kf.kobotoolbox.org](https://kf.kobotoolbox.org)
2. Open your CEmONC project
3. Go to **DATA > Downloads**
4. Choose **XLS** or **CSV** format
5. Click **Export**, then **Download**
6. Upload the downloaded file to this dashboard

## Deployment

See [ARCHITECTURE.md](ARCHITECTURE.md) for full deployment instructions including:
- Streamlit Community Cloud (free, recommended)
- Docker container
- Private server (VPS)

## Developed By

**Raymond R. Wayesu** — Biostatistician, UVRI / Elgon Centre for Health Research & Innovation (ELCHRI)
