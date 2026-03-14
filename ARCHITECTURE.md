# CEmONC Facility Readiness Assessment — Architecture & Deployment Guide

## Architecture & Deployment Guide

**Version:** 2.0
**Date:** March 2026
**Developer:** Raymond R. Wayesu, Biostatistician (UVRI / ELCHRI)

---

## 1. Project Overview

This tool analyses CEmONC (Comprehensive Emergency Obstetric and Newborn Care) Facility Readiness Assessment data collected via KoboToolbox across 27 health facilities in the Elgon Sub-Region, Uganda. It replaces manual analysis with an interactive web dashboard that produces publication-quality tables, visualisations, and downloadable reports.

### What the Tool Produces

| Section | Report Content |
|---------|---------------|
| 1 | Overall readiness summary statistics (mean, median, range, SD) |
| 2 | Facility ranking by overall readiness score with colour-coded categories |
| 3 | Domain-level readiness summary (12 domains — mean, SD, min, max) |
| 4 | Facility x Domain heatmap |
| 5 | Individual checklist item compliance analysis (optional) |
| 6 | Assessment team comparison |

### Readiness Categories (WHO SARA Thresholds)

| Category | Threshold | Colour |
|----------|-----------|--------|
| Good | >= 75% | Green |
| Moderate | 50–74% | Amber |
| Poor | < 50% | Red |

---

## 2. Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend & Backend** | Python + Streamlit | Web application framework |
| **Data Processing** | pandas, NumPy | Data cleaning, transformation, aggregation |
| **Visualisations** | Plotly | Interactive Lancet-style charts |
| **Excel Reading** | openpyxl | Reads .xlsx KoboToolbox exports |
| **Excel Export** | XlsxWriter | Generates formatted downloadable reports |
| **Deployment** | Streamlit Community Cloud + GitHub | Free hosting with automatic deploys |

---

## 3. Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Browser)                            │
│                                                             │
│  1. Visit URL → 2. Upload KoboToolbox export (CSV/XLSX)     │
│  3. View interactive dashboard → 4. Download Excel report    │
└──────────────────────┬──────────────────────────────────────┘
                       │  HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT APPLICATION (app.py)                  │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │  File Upload  │──▶│  Data Pipeline│──▶│  Analysis &    │  │
│  │  (CSV/XLSX)   │   │  (clean_data)│   │  Visualisation │  │
│  └──────────────┘   └──────────────┘   └───────┬────────┘  │
│                                                 │           │
│                     ┌───────────────────────────┤           │
│                     ▼                           ▼           │
│             ┌──────────────┐          ┌──────────────┐      │
│             │ Lancet Tables│          │ Plotly Charts │      │
│             │ (HTML render)│          │ (interactive) │      │
│             └──────────────┘          └──────────────┘      │
│                     │                           │           │
│                     ▼                           ▼           │
│             ┌────────────────────────────────────┐          │
│             │     Excel Export (XlsxWriter)       │          │
│             │     → Downloadable .xlsx report     │          │
│             └────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Upload:** User uploads a KoboToolbox CSV or XLSX export.
2. **Clean:** The `clean_data()` pipeline:
   - Strips KoboToolbox group prefixes from column names (e.g., `anc_quality/anc_bp/bp_routine_taking` → `bp_routine_taking`)
   - Maps facility codes to readable labels (e.g., `masafu_gh` → `Masafu General Hospital`)
   - Ensures all domain score columns are numeric
   - Fills missing "possible" columns with XLSForm defaults
   - Computes grand totals and domain percentages
   - Classifies facilities into WHO SARA readiness categories
3. **Analyse:** Computes summary statistics, domain-level summaries, and facility rankings.
4. **Visualise:** Generates interactive Plotly charts (bar charts, heatmap, pie chart, box plots).
5. **Export:** Packages all tables into a formatted Excel workbook.

---

## 4. Assessment Domains (12 Themes)

| # | Domain | Items | Max Score |
|---|--------|-------|-----------|
| 1 | ANC Quality | BP, HB, HR Screening, HRC, PPFP | 18 |
| 2 | Intrapartum Care | Labour Ward, Emergency Kits, Equipment, IPC, Doctors, Communication, Maternity Register | 24 |
| 3 | Theatre | Anaesthesia machine, bed, monitor, drugs, instruments | 7 |
| 4 | Postpartum Care | Delivery notes, files, monitoring, equipment, vitals | 5 |
| 5 | Other Important Areas | Doctor's house, duty rotas | 4 |
| 6 | MCH Medicines | Oxytocin, MgSO4, antihypertensives, antibiotics, etc. | 8 |
| 7 | MPDSR | Committee, minutes, reviews, actions, notification | 7 |
| 8 | Human Resource | Doctors, midwives, anaesthetists, duty rota | 4 |
| 9 | Diagnostics | Lab (blood, CBC, chemistry, Hb, glucometer) + ultrasound | 8 |
| 10 | Stores / MCH Commodities | MgSO4, antihypertensives, oxytocin, misoprostol in stores | 4 |
| 11 | Referral | Ambulance, fuel, focal person, transport evidence, parking | 5 |
| 12 | Leadership | DHO, ADHO, facility in-charge cadre | 3 |
| | **Grand Total** | | **97** |

---

## 5. Lancet-Style Visual Design

| Element | Specification |
|---------|--------------|
| Primary colour | `#00468B` (Lancet dark blue) |
| Readiness colours | `#388E3C` (Good), `#FFA000` (Moderate), `#D32F2F` (Poor) |
| Font | Arial / Helvetica (sans-serif) |
| Table headers | White text on `#00468B` background, 13px |
| Table body | 13px, alternating row shading (`#F8F9FA`) |
| Chart axes | Minimal grid, outside ticks, white background |

---

## 6. File Structure

```
CEmONC_Analysis/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview and quick start
├── ARCHITECTURE.md             # This file
├── .gitignore                  # Git ignore rules
├── data/                       # Legacy sample data (can be removed)
│   ├── Logbook.csv
│   ├── July - Jan 2026.xlsx
│   └── Validation List.csv
└── repurpose/                  # Reference materials
    ├── CEmONC_Facility_Readiness_XLSForm.xlsx  # XLSForm for data collection
    ├── KoboToolbox_Setup_Guide_ELMNS.docx      # Field setup guide
    └── CEmONC_Analysis_Script.R                # Original R analysis script
```

---

## 7. Deployment Guide — GitHub + Streamlit Community Cloud

### Step 1: Push to GitHub

```bash
cd CEmONC_Analysis/
git add .
git commit -m "CEmONC Facility Readiness Dashboard v1.0"
git push -u origin main
```

### Step 2: Deploy on Streamlit Community Cloud

1. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository: `rryesuafuga/CEmONC_Analysis`
5. Set **Branch** to: `main`
6. Set **Main file path** to: `app.py`
7. Click **"Deploy"**

The app will build and deploy within 2–5 minutes. You will receive a public URL like:

```
https://rryesuafuga-cemonc-analysis-app-xxxxx.streamlit.app
```

### Step 3: Share with Assessment Teams

Share the URL with the assessment teams and coordinators. They can:

1. Open the URL in any browser (phone or computer)
2. Upload the KoboToolbox export file
3. View the interactive dashboard with filtering
4. Download the Excel report

### Step 4: Update the App

Any time you push changes to the `main` branch on GitHub, Streamlit Community Cloud will automatically redeploy:

```bash
git add app.py
git commit -m "Update analysis dashboard"
git push origin main
# App redeploys automatically within ~1 minute
```

---

## 8. Privacy & Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **Data at rest** | No data is stored on the server. All processing happens in memory during the session. |
| **Data in transit** | Streamlit Community Cloud uses HTTPS by default. |
| **Access control** | The URL is not indexed by search engines but is accessible to anyone with the link. |
| **Facility-level data** | The dashboard displays aggregate readiness scores — no patient-level data is involved. |

---

## 9. Alternative Deployment Options

### Option A: Local Execution

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Option B: Docker Container

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t cemonc-dashboard .
docker run -p 8501:8501 cemonc-dashboard
```

### Option C: Private Server (VPS)

```bash
git clone https://github.com/rryesuafuga/CEmONC_Analysis.git
cd CEmONC_Analysis
pip install -r requirements.txt
nohup streamlit run app.py --server.port=8501 --server.headless=true &
```

Then configure Nginx to proxy requests from port 80/443 to 8501 with SSL (Let's Encrypt).

---

## 10. Contact & Support

| Role | Name | Contact |
|------|------|---------|
| Developer | Raymond R. Wayesu | UVRI / ELCHRI |

---

*Developed under the Elgon Centre for Health Research & Innovation (ELCHRI), in partnership with UVRI, Uganda.*
