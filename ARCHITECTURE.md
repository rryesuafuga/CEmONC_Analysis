# Mbale RRH Neonatal Unit — Automated Monthly Reporting Tool

## Architecture & Deployment Guide

**Version:** 1.0  
**Date:** February 2026  
**Developer:** Raymond R. Wayesu, Biostatistician  
**Commissioned by:** Dr Adam Hewitt-Smith, Anaesthesiologist & Acting Head of Anaesthesia & Critical Care, Mbale Regional Referral Hospital  
**End User:** Dr Kathy Hewitt-Smith

---

## 1. Project Overview

This tool automates the generation of monthly neonatal unit reports from the Mbale Regional Referral Hospital logbook data. It replaces a labour-intensive manual process with a web-based application where the user uploads the monthly spreadsheet and receives a complete report with publication-quality tables and Lancet-style visualizations.

### What the Tool Produces

The tool generates a comprehensive report addressing all 12 reporting requirements:

| Section | Report Content |
|---------|---------------|
| A.1 | Total admissions per month |
| A.2 | Place of birth — summary by facility level + top 10 |
| A.3 | Place of referral — summary by facility level + top 10 |
| A.4 | Maternal HIV status |
| A.5 | Mode of delivery |
| A.6 | Sex distribution |
| A.7 | Multiple births (singleton, twin, triplet, etc.) |
| A.8 | Birth weight categories (<1000g, 1000–1499g, 1500–2499g, ≥2500g) |
| A.9 | Final diagnosis (unknown if blank, includes "Other") |
| A.10 | Hospital outcome (combined 7-day and 28-day status) |
| B | All of the above repeated for patients who died |
| C1 | All of the above repeated for extremely low birth weight (<1000g) |
| C2 | All of the above repeated for very low birth weight (1000–1499g) |

Additionally, the tool provides Lancet journal-style visualizations for key indicators and a downloadable Excel workbook containing all tables.

---

## 2. Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend & Backend** | Python + Streamlit | Web application framework (no HTML/JS coding needed) |
| **Data Processing** | pandas, NumPy | Data cleaning, transformation, and aggregation |
| **Visualizations** | Plotly | Interactive Lancet-style charts and figures |
| **Excel Decryption** | msoffcrypto-tool | Decrypts password-protected Excel files |
| **Excel Reading** | openpyxl | Reads .xlsx files |
| **Excel Export** | XlsxWriter | Generates formatted downloadable Excel reports |
| **Deployment** | Streamlit Community Cloud + GitHub | Free hosting with automatic deploys |

### Why This Stack Was Chosen

Streamlit was selected over R Shiny, JavaScript/React, and standalone R scripts for these reasons:

- **Zero frontend code:** the entire application is a single Python file. No HTML, CSS, or JavaScript to maintain.
- **Free deployment:** Streamlit Community Cloud provides free hosting for public GitHub repositories, with no server administration.
- **Password-protected Excel support:** the `msoffcrypto-tool` library handles Excel decryption natively.
- **Publication-quality output:** Plotly produces Lancet-style visualizations with fine-grained control over typography, colour, and layout.
- **Maintainability:** if the developer is unavailable, any Python-literate person can modify the application.
- **User experience:** Dr Kathy visits a URL, uploads the file, and the report appears instantly with a download button.

---

## 3. Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Browser)                        │
│                                                         │
│  1. Visit URL → 2. Enter password → 3. Upload .xlsx     │
│  4. View interactive report → 5. Download Excel          │
└──────────────────────┬──────────────────────────────────┘
                       │  HTTPS
                       ▼
┌─────────────────────────────────────────────────────────┐
│              STREAMLIT APPLICATION (app.py)              │
│                                                         │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────┐  │
│  │  File Upload │───▶│  Data Pipeline│───▶│  Report    │  │
│  │  & Decrypt   │    │  (clean_data)│    │  Generator │  │
│  └─────────────┘    └──────────────┘    └─────┬──────┘  │
│                                                │         │
│                      ┌─────────────────────────┤         │
│                      ▼                         ▼         │
│              ┌──────────────┐         ┌──────────────┐   │
│              │ Lancet Tables│         │ Plotly Charts │   │
│              │ (HTML render)│         │ (interactive) │   │
│              └──────────────┘         └──────────────┘   │
│                      │                         │         │
│                      ▼                         ▼         │
│              ┌────────────────────────────────────┐      │
│              │     Excel Export (XlsxWriter)       │      │
│              │     → Downloadable .xlsx report     │      │
│              └────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│           STREAMLIT COMMUNITY CLOUD (Hosting)           │
│                                                         │
│  - Connected to GitHub repository                        │
│  - Auto-deploys on push to main branch                   │
│  - Free tier: sufficient for monthly reporting usage     │
│  - URL: https://<your-app>.streamlit.app                 │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Upload:** User uploads the password-protected `.xlsx` file (or a `.csv` export of the Logbook tab).
2. **Decrypt:** If `.xlsx` with password, `msoffcrypto-tool` decrypts the file in memory.
3. **Read:** `pandas` reads the "Logbook" sheet from the decrypted Excel.
4. **Clean:** The `clean_data()` pipeline standardizes all fields:
   - Parses dates from `DD.MM.YY` format
   - Standardizes case inconsistencies (e.g., "spontaneous Vaginal Delivery" → "Spontaneous Vaginal Delivery")
   - Classifies health facilities by Uganda health system level
   - Categorizes birth weights into WHO neonatal categories
   - Maps outcome codes (D, DD, R, S) to readable labels
   - Derives combined hospital outcome from 7-day and 28-day status
5. **Report:** Generates all 12 report sections with tables and visualizations.
6. **Export:** Packages all tables into a formatted Excel workbook for download.

---

## 4. Data Cleaning Logic

### Date Parsing

Dates are stored as `DD.MM.YY` (e.g., `16.07.25` = 16 July 2025). The pipeline uses `pd.to_datetime(col, format='%d.%m.%y')` and derives an `Admission_Month` period for grouping.

### Health Facility Classification

Place of birth and referral source names are classified using pattern matching on the Uganda health system hierarchy:

| Pattern in Name | Classification |
|----------------|----------------|
| Contains "RRH" | Regional Referral Hospital |
| Contains "G.H" or "GENERAL HOSPITAL" | General Hospital |
| Contains "D.H" or "DISTRICT HOSPITAL" | District Hospital |
| Contains "HOSPITAL" (other) | Hospital (Other/Private) |
| Contains "HCIV" | Health Centre IV |
| Contains "HCIII" | Health Centre III |
| Contains "HCII" | Health Centre II |
| Exact match "Home" | Home |
| Contains "BBA" | Born Before Arrival |
| All others | Other (Private Clinic/Not Classified) |

### Hospital Outcome Derivation

The combined outcome uses both the 7-day and 28-day status fields with this priority logic:

1. If either status is "DD" (death), the combined outcome is **Died**.
2. If 28-day status exists, use that (it is the most recent).
3. If only 7-day status exists, use that.
4. If both are blank, the combined outcome is **Unknown**.

### Data Quality Handling

Per Dr Adam's instructions, unknowns are explicitly included in all tables to quantify data completeness. The tool does not silently drop missing values; instead, it counts them as "Unknown" in every frequency table.

---

## 5. Lancet-Style Visual Design

The application uses a design system inspired by The Lancet journal:

| Element | Specification |
|---------|--------------|
| Primary colour | `#00468B` (Lancet dark blue) |
| Accent colours | `#ED0000` (red), `#42B540` (green), `#0099B4` (teal), `#925E9F` (purple) |
| Font | Arial / Helvetica (sans-serif) |
| Table headers | White text on `#00468B` background, 13px |
| Table body | 13px, alternating row shading (`#F8F9FA`) |
| Table footer | Bold, 2px top border in `#00468B` |
| Chart axes | Minimal grid, outside ticks, clean white background |
| Chart labels | 11–12px Arial |

---

## 6. File Structure

```
neonatal_report/
├── app.py                      # Main Streamlit application (single file)
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml             # Streamlit theme configuration
├── data/
│   └── Logbook.csv             # Demo dataset (optional, for testing)
├── README.md                   # This file (or a shorter version)
└── .gitignore                  # Standard Python gitignore
```

---

## 7. Deployment Guide — GitHub + Streamlit Community Cloud

### Step 1: Create the GitHub Repository

```bash
# On your local machine (requires Git installed)
cd neonatal_report/

# Initialize Git
git init
git add .
git commit -m "Initial commit: Neonatal reporting tool v1.0"

# Create repository on GitHub (via browser or GitHub CLI)
# Go to https://github.com/new and create a new repo called 'neonatal-report'
# Then push:
git remote add origin https://github.com/<your-username>/neonatal-report.git
git branch -M main
git push -u origin main
```

### Step 2: Create the `.gitignore`

Before pushing, ensure you have a `.gitignore` that excludes sensitive data:

```
# .gitignore
__pycache__/
*.pyc
.env
*.xlsx
data/Logbook.csv    # Remove this line if you want demo data in the repo
.DS_Store
```

### Step 3: Deploy on Streamlit Community Cloud

1. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository: `<your-username>/neonatal-report`
5. Set **Main file path** to: `app.py`
6. Click **"Deploy"**

The app will build and deploy within 2–5 minutes. You will receive a public URL like:

```
https://<your-username>-neonatal-report-app-xxxxx.streamlit.app
```

### Step 4: Share with Users

Share the URL with Dr Kathy and Dr Adam. They can bookmark it and use it each month by:

1. Opening the URL in any browser
2. Entering the spreadsheet password in the sidebar
3. Uploading the monthly `.xlsx` file
4. Viewing the report and downloading the Excel export

### Step 5: Update the App

Any time you push changes to the `main` branch on GitHub, Streamlit Community Cloud will automatically redeploy:

```bash
# After making changes to app.py
git add app.py
git commit -m "Add new visualization for diagnosis trends"
git push origin main
# App redeploys automatically within ~1 minute
```

---

## 8. Privacy & Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **Data at rest** | No data is stored on the server. All processing happens in memory during the session. When the session ends, all data is discarded. |
| **Data in transit** | Streamlit Community Cloud uses HTTPS by default. |
| **Password-protected Excel** | The password is entered by the user in the browser and used only to decrypt the file in memory. It is not logged or stored. |
| **Access control** | The Streamlit Community Cloud app URL is not indexed by search engines, but it is technically accessible to anyone with the link. For stricter access control, consider deploying on a private server (see Section 9). |
| **Patient identifiers** | The dataset contains IP numbers but no patient names. The reporting tool does not display individual-level records; it only generates aggregate summaries. |

### Recommendation for Sensitive Data

If the team requires stricter access control, consider one of these alternatives:

- **Streamlit Community Cloud with authentication:** Streamlit supports adding a basic password or OAuth via `st.secrets`. This restricts access to authorised users.
- **Private deployment on a VPS:** Deploy on a $5/month DigitalOcean droplet with Nginx reverse proxy and basic authentication.
- **Local execution:** Users can run `streamlit run app.py` on their own computers (requires Python installed).

---

## 9. Alternative Deployment Options

### Option A: Local Execution (No Server)

If users have Python installed:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in the default browser at `http://localhost:8501`.

### Option B: Docker Container

Create a `Dockerfile` for reproducible deployment:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t neonatal-report .
docker run -p 8501:8501 neonatal-report
```

### Option C: Private Server (VPS)

Deploy on a virtual private server (e.g., DigitalOcean, AWS Lightsail) with Nginx as a reverse proxy:

```bash
# On the VPS
git clone https://github.com/<your-username>/neonatal-report.git
cd neonatal-report
pip install -r requirements.txt
nohup streamlit run app.py --server.port=8501 --server.headless=true &
```

Then configure Nginx to proxy requests from port 80/443 to 8501 with SSL (Let's Encrypt).

---

## 10. Maintenance & Future Enhancements

### Monthly Workflow

1. The data team at Mbale RRH completes the monthly neonatal logbook in the password-protected Excel spreadsheet.
2. Dr Kathy opens the reporting tool URL in her browser.
3. She enters the spreadsheet password and uploads the file.
4. The report generates automatically. She reviews it on screen.
5. She clicks "Download Excel Report" to get a formatted workbook for archiving and sharing.

### Planned Enhancements

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| **Trend analysis** | Multi-month line charts showing trends in mortality, admissions, and diagnosis patterns | High |
| **Automated PDF export** | Generate a formatted PDF report suitable for printing and email distribution | Medium |
| **Data validation alerts** | Flag data quality issues (e.g., missing birth weights, impossible dates, unrecognised facility names) | Medium |
| **Benchmarking** | Compare current month against the same month in the previous year and against rolling averages | Low |
| **Dashboard view** | A condensed single-page dashboard with KPIs for quick executive review | Low |

### How to Add a New Report Section

1. Open `app.py`
2. Add a new block inside the `generate_report_section()` function following the pattern of existing sections
3. Create the frequency table using `freq_table()`
4. Render it using `render_lancet_table()`
5. Add a Plotly chart using `lancet_plotly_layout()` for consistent styling
6. Push to GitHub — the app redeploys automatically

---

## 11. Contact & Support

| Role | Name | Contact |
|------|------|---------|
| Developer | Raymond R. Wayesu | sseguya256@gmail.com |
| Project Lead | Dr Adam Hewitt-Smith | adamhewittsmith@gmail.com |
| End User | Dr Kathy Hewitt-Smith | kathy.burgoine@gmail.com |

---

*Developed under the Elgon Centre for Health Research & Innovation (ELCHRI), Mbale Regional Referral Hospital, Uganda.*
