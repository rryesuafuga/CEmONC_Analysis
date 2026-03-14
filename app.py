"""
CEmONC Facility Readiness Assessment — Analysis Dashboard
==========================================================
Elgon Sub-Region (ELMNS), Uganda
Data source: KoboToolbox export (CSV or XLSX)
Author: Raymond R. Wayesu (UVRI / ELCHRI)

This Streamlit application analyses CEmONC Facility Readiness Assessment
data exported from KoboToolbox and produces publication-quality tables,
visualisations, and a downloadable Excel report.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io
import os
import warnings

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────
# CONFIGURATION & STYLING
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CEmONC Facility Readiness Dashboard",
    page_icon="\U0001F3E5",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Lancet-inspired colour palette
LANCET_COLORS = [
    "#00468B",  # Dark blue
    "#ED0000",  # Red
    "#42B540",  # Green
    "#0099B4",  # Teal
    "#925E9F",  # Purple
    "#FDAF91",  # Peach
    "#AD002A",  # Dark red
    "#ADB6B6",  # Grey
    "#1B1919",  # Near-black
    "#E0A800",  # Amber
]

READINESS_COLORS = {
    "Poor (<50%)": "#D32F2F",
    "Moderate (50-74%)": "#FFA000",
    "Good (>=75%)": "#388E3C",
}

LANCET_BG = "#FFFFFF"
LANCET_GRID = "#E5E5E5"
LANCET_TEXT = "#1B1919"
LANCET_FONT = "Arial, Helvetica, sans-serif"

# CSS for Lancet-style tables and layout
st.markdown("""
<style>
    .main .block-container { max-width: 1200px; padding-top: 1.5rem; }

    .lancet-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, Helvetica, sans-serif;
        font-size: 13px;
        color: #1B1919;
        margin: 12px 0;
    }
    .lancet-table thead th {
        background-color: #00468B;
        color: #FFFFFF;
        font-weight: 600;
        padding: 8px 12px;
        text-align: left;
        border-bottom: 2px solid #00468B;
        font-size: 13px;
    }
    .lancet-table tbody td {
        padding: 6px 12px;
        border-bottom: 1px solid #E5E5E5;
        font-size: 13px;
    }
    .lancet-table tbody tr:nth-child(even) {
        background-color: #F8F9FA;
    }
    .lancet-table tbody tr:hover {
        background-color: #EDF2F7;
    }
    .lancet-table tfoot td {
        font-weight: 700;
        border-top: 2px solid #00468B;
        padding: 8px 12px;
        background-color: #F0F4F8;
        font-size: 13px;
    }

    .report-section {
        font-family: Arial, Helvetica, sans-serif;
        color: #00468B;
        border-bottom: 2px solid #00468B;
        padding-bottom: 4px;
        margin-top: 24px;
        margin-bottom: 12px;
    }

    .metric-card {
        background: #F8F9FA;
        border-left: 4px solid #00468B;
        padding: 12px 16px;
        border-radius: 0 4px 4px 0;
        margin: 6px 0;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #00468B;
    }
    .metric-label {
        font-size: 13px;
        color: #666;
    }

    [data-testid="stSidebar"] {
        background-color: #F0F4F8;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# DOMAIN DEFINITIONS
# ──────────────────────────────────────────────────────────────

# 12 assessment domains — score column, possible column, display label
DOMAINS = [
    ("anc_total_score",   "anc_total_possible",   "ANC Quality",     "anc_pct"),
    ("intra_total_score", "intra_total_possible",  "Intrapartum",     "intra_pct"),
    ("theatre_score",     "theatre_possible",      "Theatre",         "theatre_pct"),
    ("pp_score",          "pp_possible",           "Postpartum",      "pp_pct"),
    ("oth_score",         "oth_possible",          "Others",          "oth_pct"),
    ("med_score",         "med_possible",          "Medicines",       "med_pct"),
    ("mpdsr_score",       "mpdsr_possible",        "MPDSR",           "mpdsr_pct"),
    ("hr_adequate",       "hr_possible",           "Human Resource",  "hr_pct"),
    ("diag_score",        "diag_possible",         "Diagnostics",     "diag_pct"),
    ("st_score",          "st_possible",           "Stores",          "st_pct"),
    ("ref_score",         "ref_possible",          "Referral",        "ref_pct"),
    ("lead_score",        "lead_possible",         "Leadership",      "lead_pct"),
]

# Default maximum scores per domain (from the XLSForm)
DOMAIN_MAX_DEFAULTS = {
    "anc_total_possible": 18,
    "intra_total_possible": 24,
    "theatre_possible": 7,
    "pp_possible": 5,
    "oth_possible": 4,
    "med_possible": 8,
    "mpdsr_possible": 7,
    "hr_possible": 4,
    "diag_possible": 8,
    "st_possible": 4,
    "ref_possible": 5,
    "lead_possible": 3,
}

# Facility code → readable label mapping (KoboToolbox exports the 'name' values)
FACILITY_LABELS = {
    "budadiri": "Budadiri", "buwasa": "Buwasa", "muyembe": "Muyembe",
    "bududa": "Bududa", "bufumbo": "Bufumbo", "mukuju": "Mukuju",
    "bubulo": "Bubulo", "bukwo": "Bukwo", "kaproron": "Kaproron",
    "kapchorwa": "Kapchorwa", "kaserem": "Kaserem", "namatala": "Namatala",
    "bugobero": "Bugobero", "masafu_gh": "Masafu General Hospital",
    "tororo_gh": "Tororo General Hospital", "mulanda": "Mulanda",
    "nagongera": "Nagongera", "bukasakya": "Bukasakya", "busolwe": "Busolwe",
    "rubongi": "Rubongi", "palisa": "Palisa", "butebo": "Butebo",
    "kibuku": "Kibuku", "budaka": "Budaka", "busiu": "Busiu",
    "nabiganda": "Nabiganda", "bulucheke": "Bulucheke",
}

TEAM_LABELS = {
    "team1": "Team 1 - Dr Wanyera Peter",
    "team2": "Team 2 - Dr Baifa Arwinyo",
    "team3": "Team 3 - Dr Mugabe Kenneth",
    "team4": "Team 4 - Dr Basil Bwambale",
}


# ──────────────────────────────────────────────────────────────
# DATA PROCESSING FUNCTIONS
# ──────────────────────────────────────────────────────────────

def strip_group_prefix(df):
    """
    KoboToolbox exports column names with group prefixes separated by '/'.
    e.g. 'anc_quality/anc_bp/bp_routine_taking' → 'bp_routine_taking'.
    This strips to the final field name.
    """
    df = df.copy()
    df.columns = [col.split("/")[-1] for col in df.columns]
    if df.columns.duplicated().any():
        st.warning("Duplicate column names found after stripping group prefixes. Check form design.")
    return df


def clean_data(df):
    """
    Master cleaning pipeline for CEmONC Facility Readiness Assessment data.
    Handles both KoboToolbox exports (coded values) and pre-processed data.
    """
    df = df.copy()

    # Strip KoboToolbox group prefixes if present
    if any("/" in str(c) for c in df.columns):
        df = strip_group_prefix(df)

    # ── Map coded facility names to labels ──
    if "facility_name" in df.columns:
        df["facility_name"] = df["facility_name"].astype(str).str.strip()
        df["facility_name"] = df["facility_name"].replace(FACILITY_LABELS)

    # ── Map coded team numbers to labels ──
    if "team_number" in df.columns:
        df["team_number"] = df["team_number"].astype(str).str.strip()
        df["team_number"] = df["team_number"].replace(TEAM_LABELS)

    # ── Ensure domain score columns are numeric ──
    score_cols = [d[0] for d in DOMAINS]
    possible_cols = [d[1] for d in DOMAINS]
    for col in score_cols + possible_cols + ["grand_total_score", "grand_total_possible", "grand_pct"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Fill missing 'possible' columns with defaults ──
    for poss_col, default_val in DOMAIN_MAX_DEFAULTS.items():
        if poss_col not in df.columns:
            df[poss_col] = default_val
        else:
            df[poss_col] = df[poss_col].fillna(default_val)

    # ── Compute grand totals if missing ──
    existing_score_cols = [c for c in score_cols if c in df.columns]
    existing_poss_cols = [c for c in possible_cols if c in df.columns]

    if "grand_total_score" not in df.columns or df["grand_total_score"].isna().all():
        df["grand_total_score"] = df[existing_score_cols].sum(axis=1)

    if "grand_total_possible" not in df.columns or df["grand_total_possible"].isna().all():
        df["grand_total_possible"] = df[existing_poss_cols].sum(axis=1)

    if "grand_pct" not in df.columns or df["grand_pct"].isna().all():
        df["grand_pct"] = (df["grand_total_score"] / df["grand_total_possible"] * 100).round(1)

    # ── Compute domain percentages ──
    for score_col, poss_col, _, pct_col in DOMAINS:
        if score_col in df.columns and poss_col in df.columns:
            df[pct_col] = (df[score_col] / df[poss_col] * 100).round(1)

    # ── Readiness category (WHO SARA thresholds) ──
    df["readiness_cat"] = pd.cut(
        df["grand_pct"],
        bins=[-np.inf, 50, 75, np.inf],
        labels=["Poor (<50%)", "Moderate (50-74%)", "Good (>=75%)"],
    )

    return df


# ──────────────────────────────────────────────────────────────
# TABLE & FIGURE RENDERING FUNCTIONS
# ──────────────────────────────────────────────────────────────

def render_lancet_table(df_table, title="", footer_row=None, table_num=None):
    """Render a DataFrame as a Lancet-style HTML table."""
    table_label = f"<strong>Table {table_num}.</strong> " if table_num else ""

    html = f'<p style="font-family: {LANCET_FONT}; font-size: 13px; color: {LANCET_TEXT}; margin-bottom: 4px;">'
    html += f'{table_label}<em>{title}</em></p>'
    html += '<table class="lancet-table"><thead><tr>'

    for col in df_table.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"

    for _, row in df_table.iterrows():
        html += "<tr>"
        for val in row:
            html += f"<td>{val}</td>"
        html += "</tr>"

    if footer_row is not None:
        html += "</tbody><tfoot><tr>"
        for val in footer_row:
            html += f"<td>{val}</td>"
        html += "</tr></tfoot>"
    else:
        html += "</tbody>"

    html += "</table>"
    return html


def lancet_plotly_layout(fig, title="", xaxis_title="", yaxis_title="", height=450):
    """Apply Lancet journal styling to a Plotly figure."""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family=LANCET_FONT, size=14, color=LANCET_TEXT),
            x=0.0, xanchor="left",
        ),
        font=dict(family=LANCET_FONT, size=12, color=LANCET_TEXT),
        plot_bgcolor=LANCET_BG,
        paper_bgcolor=LANCET_BG,
        xaxis=dict(
            title=xaxis_title,
            showgrid=False,
            linecolor=LANCET_TEXT,
            linewidth=1,
            ticks="outside",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            title=yaxis_title,
            gridcolor=LANCET_GRID,
            gridwidth=0.5,
            linecolor=LANCET_TEXT,
            linewidth=1,
            ticks="outside",
            tickfont=dict(size=11),
        ),
        legend=dict(
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor=LANCET_GRID,
            borderwidth=1,
        ),
        margin=dict(l=60, r=30, t=50, b=60),
        height=height,
    )
    return fig


# ──────────────────────────────────────────────────────────────
# ANALYSIS & VISUALISATION FUNCTIONS
# ──────────────────────────────────────────────────────────────

def compute_domain_summary(dat):
    """Compute domain-level summary statistics (mean, SD, min, max)."""
    pct_cols = [d[3] for d in DOMAINS if d[3] in dat.columns]
    domain_labels = [d[2] for d in DOMAINS if d[3] in dat.columns]

    rows = []
    for label, pct_col in zip(domain_labels, pct_cols):
        s = dat[pct_col].dropna()
        rows.append({
            "Domain": label,
            "Mean (%)": round(s.mean(), 1) if len(s) > 0 else 0,
            "SD (%)": round(s.std(), 1) if len(s) > 1 else 0,
            "Min (%)": round(s.min(), 1) if len(s) > 0 else 0,
            "Max (%)": round(s.max(), 1) if len(s) > 0 else 0,
        })

    summary = pd.DataFrame(rows).sort_values("Mean (%)", ascending=True).reset_index(drop=True)
    return summary


def build_facility_scores_table(dat):
    """Build the facility-level scores table for display and export."""
    cols = ["facility_name"]
    if "team_number" in dat.columns:
        cols.append("team_number")
    cols += ["grand_total_score", "grand_total_possible", "grand_pct", "readiness_cat"]
    pct_cols = [d[3] for d in DOMAINS if d[3] in dat.columns]
    cols += pct_cols

    display_cols = {
        "facility_name": "Facility",
        "team_number": "Team",
        "grand_total_score": "Score",
        "grand_total_possible": "Possible",
        "grand_pct": "Overall (%)",
        "readiness_cat": "Readiness",
    }
    for _, _, label, pct_col in DOMAINS:
        if pct_col in dat.columns:
            display_cols[pct_col] = f"{label} (%)"

    existing = [c for c in cols if c in dat.columns]
    tbl = dat[existing].copy().sort_values("grand_pct", ascending=False).reset_index(drop=True)
    tbl = tbl.rename(columns={k: v for k, v in display_cols.items() if k in tbl.columns})
    return tbl


def plot_facility_ranking(dat, fig_num=3):
    """Horizontal bar chart of facility readiness scores, colour-coded."""
    plot_df = dat.sort_values("grand_pct", ascending=True).copy()

    fig = go.Figure()

    for cat, colour in READINESS_COLORS.items():
        mask = plot_df["readiness_cat"] == cat
        subset = plot_df[mask]
        if len(subset) == 0:
            continue
        fig.add_trace(go.Bar(
            y=subset["facility_name"],
            x=subset["grand_pct"],
            orientation="h",
            name=cat,
            marker_color=colour,
            marker_line_color=LANCET_TEXT,
            marker_line_width=0.3,
            text=subset["grand_pct"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(size=10),
        ))

    # Threshold lines
    fig.add_vline(x=50, line_dash="dash", line_color="#D32F2F", line_width=1,
                  annotation_text="50%", annotation_position="top")
    fig.add_vline(x=75, line_dash="dash", line_color="#388E3C", line_width=1,
                  annotation_text="75%", annotation_position="top")

    n = len(dat)
    fig = lancet_plotly_layout(
        fig,
        title=f"Figure {fig_num}. CEmONC facility readiness scores — Elgon Sub-Region (n={n})",
        xaxis_title="Overall Readiness Score (%)",
        yaxis_title="",
        height=max(450, n * 28),
    )
    fig.update_xaxes(range=[0, 108], dtick=25)
    fig.update_layout(
        barmode="stack",
        legend=dict(title="Readiness Category", orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def plot_domain_bars(domain_summary, n_facilities, fig_num=4):
    """Horizontal bar chart of mean domain scores with SD error bars."""
    fig = go.Figure()

    # Colour bars by threshold
    bar_colors = []
    for _, row in domain_summary.iterrows():
        m = row["Mean (%)"]
        if m >= 75:
            bar_colors.append(READINESS_COLORS["Good (>=75%)"])
        elif m >= 50:
            bar_colors.append(READINESS_COLORS["Moderate (50-74%)"])
        else:
            bar_colors.append(READINESS_COLORS["Poor (<50%)"])

    fig.add_trace(go.Bar(
        y=domain_summary["Domain"],
        x=domain_summary["Mean (%)"],
        orientation="h",
        marker_color=bar_colors,
        marker_line_color=LANCET_TEXT,
        marker_line_width=0.3,
        error_x=dict(
            type="data",
            array=domain_summary["SD (%)"],
            visible=True,
            color="grey",
            thickness=1.5,
            width=4,
        ),
        text=domain_summary["Mean (%)"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        textfont=dict(size=10),
    ))

    fig.add_vline(x=50, line_dash="dash", line_color="#D32F2F", line_width=1,
                  annotation_text="50%", annotation_position="top")
    fig.add_vline(x=75, line_dash="dash", line_color="#388E3C", line_width=1,
                  annotation_text="75%", annotation_position="top")

    fig = lancet_plotly_layout(
        fig,
        title=f"Figure {fig_num}. Domain-level readiness (mean ± SD) across {n_facilities} facilities",
        xaxis_title="Mean Readiness Score (%)",
        yaxis_title="",
        height=max(400, len(domain_summary) * 38),
    )
    fig.update_xaxes(range=[0, 108], dtick=25)
    return fig


def plot_heatmap(dat, fig_num=5):
    """Facility x Domain readiness heatmap."""
    pct_cols = [d[3] for d in DOMAINS if d[3] in dat.columns]
    domain_labels = [d[2] for d in DOMAINS if d[3] in dat.columns]

    heat_df = dat[["facility_name"] + pct_cols].copy()
    # Sort facilities by mean score across domains
    heat_df["_mean"] = heat_df[pct_cols].mean(axis=1)
    heat_df = heat_df.sort_values("_mean", ascending=True)
    heat_df = heat_df.drop(columns=["_mean"])

    z_values = heat_df[pct_cols].values
    y_labels = heat_df["facility_name"].tolist()
    x_labels = domain_labels

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0.0, "#D32F2F"],     # 0%   — Red (Poor)
            [0.50, "#FFA000"],    # 50%  — Amber (Moderate threshold)
            [0.75, "#FFFDE7"],    # 75%  — Light yellow (Good threshold)
            [1.0, "#388E3C"],     # 100% — Green (Good)
        ],
        zmin=0,
        zmax=100,
        colorbar=dict(
            title=dict(text="Score (%)", font=dict(size=11)),
            ticksuffix="%",
            tickvals=[0, 25, 50, 75, 100],
            len=0.75,
        ),
        text=z_values,
        texttemplate="%{text:.0f}",
        textfont=dict(size=9, color="#1B1919"),
        hoverongaps=False,
        hovertemplate="%{y}<br>%{x}: %{z:.1f}%<extra></extra>",
    ))

    n = len(y_labels)
    fig = lancet_plotly_layout(
        fig,
        title=f"Figure {fig_num}. Facility x domain readiness heatmap (n={n})",
        xaxis_title="",
        yaxis_title="",
        height=max(500, n * 28),
    )
    fig.update_xaxes(tickangle=45, side="bottom")
    fig.update_layout(yaxis=dict(showgrid=False))
    return fig


def plot_readiness_distribution(dat, fig_num=1):
    """Bar chart of readiness categories (Lancet style — avoids pie charts)."""
    cats = ["Poor (<50%)", "Moderate (50-74%)", "Good (>=75%)"]
    counts = dat["readiness_cat"].value_counts().reindex(cats).fillna(0).astype(int)
    n = len(dat)

    fig = go.Figure()
    for cat in cats:
        fig.add_trace(go.Bar(
            x=[cat],
            y=[counts[cat]],
            name=cat,
            marker_color=READINESS_COLORS[cat],
            text=[f"{counts[cat]} ({counts[cat]/n*100:.0f}%)"],
            textposition="outside",
            textfont=dict(size=11),
            showlegend=False,
        ))

    fig = lancet_plotly_layout(
        fig,
        title=f"Figure {fig_num}. Distribution of facilities by WHO SARA readiness category (n={n})",
        xaxis_title="Readiness Category",
        yaxis_title="Number of Facilities",
        height=400,
    )
    fig.update_yaxes(range=[0, max(counts.values) * 1.25])
    return fig


def plot_score_distribution(dat, fig_num=2):
    """Histogram of overall readiness scores with rug marks."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=dat["grand_pct"],
        nbinsx=12,
        marker_color=LANCET_COLORS[0],
        marker_line_color=LANCET_TEXT,
        marker_line_width=0.5,
        opacity=0.85,
        name="Facilities",
    ))
    # Add threshold lines
    fig.add_vline(x=50, line_dash="dash", line_color="#D32F2F", line_width=1.5,
                  annotation_text="Poor/Moderate (50%)", annotation_position="top left",
                  annotation_font_size=10, annotation_font_color="#D32F2F")
    fig.add_vline(x=75, line_dash="dash", line_color="#388E3C", line_width=1.5,
                  annotation_text="Moderate/Good (75%)", annotation_position="top left",
                  annotation_font_size=10, annotation_font_color="#388E3C")
    # Add mean marker
    mean_val = dat["grand_pct"].mean()
    fig.add_vline(x=mean_val, line_dash="dot", line_color=LANCET_COLORS[4], line_width=2,
                  annotation_text=f"Mean ({mean_val:.1f}%)", annotation_position="top right",
                  annotation_font_size=10, annotation_font_color=LANCET_COLORS[4])

    fig = lancet_plotly_layout(
        fig,
        title=f"Figure {fig_num}. Distribution of overall facility readiness scores (n={len(dat)})",
        xaxis_title="Overall Readiness Score (%)",
        yaxis_title="Number of Facilities",
        height=400,
    )
    fig.update_xaxes(range=[0, 100])
    return fig


# ──────────────────────────────────────────────────────────────
# EXCEL EXPORT
# ──────────────────────────────────────────────────────────────

def generate_excel_report(all_tables):
    """Export all tables to a formatted Excel workbook."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        header_fmt = workbook.add_format({
            "bold": True,
            "bg_color": "#00468B",
            "font_color": "#FFFFFF",
            "border": 1,
            "font_name": "Arial",
            "font_size": 11,
        })
        cell_fmt = workbook.add_format({
            "border": 1,
            "font_name": "Arial",
            "font_size": 10,
        })

        for sheet_name, df_tbl in all_tables.items():
            safe_name = sheet_name[:31]
            df_tbl.to_excel(writer, sheet_name=safe_name, index=False, startrow=1)
            ws = writer.sheets[safe_name]

            for col_idx, col_name in enumerate(df_tbl.columns):
                ws.write(0, col_idx, col_name, header_fmt)

            for col_idx, col_name in enumerate(df_tbl.columns):
                max_len = max(
                    df_tbl[col_name].astype(str).str.len().max(),
                    len(col_name)
                ) + 3
                ws.set_column(col_idx, col_idx, min(max_len, 50))

    output.seek(0)
    return output


# ──────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ──────────────────────────────────────────────────────────────

def main():
    # ── Header ──
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 0 0;">
        <h1 style="color: #00468B; font-family: Arial; margin-bottom: 0;">
            CEmONC Facility Readiness Dashboard
        </h1>
        <p style="color: #666; font-size: 15px; margin-top: 4px;">
            Elgon Sub-Region, Uganda &nbsp;|&nbsp; Facility Readiness Assessment Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("### Data Upload")
        st.markdown(
            "Upload the CEmONC Facility Readiness Assessment data "
            "exported from **KoboToolbox** (CSV or XLSX format)."
        )

        file_type = st.radio("File format:", ["Excel (.xlsx)", "CSV (.csv)"], horizontal=True)

        uploaded_file = st.file_uploader(
            "Choose file", type=["xlsx", "csv"],
            help="Upload the KoboToolbox export file"
        )

        st.divider()
        st.markdown("### Report Settings")
        show_individual_items = st.checkbox("Show individual item scores", value=False,
                                            help="Display the yes/no responses for each checklist item")

    # ── Load data ──
    dat = None
    is_demo = False

    if uploaded_file is not None:
        try:
            if file_type == "CSV (.csv)":
                dat = pd.read_csv(uploaded_file, encoding="utf-8")
            else:
                dat = pd.read_excel(uploaded_file, engine="openpyxl")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return
    else:
        # Load demo data if available
        demo_path = os.path.join(os.path.dirname(__file__), "data", "demo_cemonc_assessment.csv")
        if os.path.exists(demo_path):
            dat = pd.read_csv(demo_path, encoding="utf-8")
            is_demo = True
            st.info(
                "Running in **demo mode** with simulated assessment data for 27 facilities. "
                "Upload your own KoboToolbox export via the sidebar to analyse real data."
            )
        else:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px; color: #666;">
                <h3 style="color: #00468B;">Welcome</h3>
                <p>Upload your CEmONC Facility Readiness Assessment data from KoboToolbox
                using the sidebar to begin the analysis.</p>
                <p style="font-size: 13px;">
                    Supported formats: <strong>.xlsx</strong> or <strong>.csv</strong> export
                    from KoboToolbox (DATA &gt; Downloads).
                </p>
                <hr style="width: 50%; margin: 30px auto;">
                <p style="font-size: 13px;">
                    <strong>How to export from KoboToolbox:</strong><br>
                    1. Log into <a href="https://kf.kobotoolbox.org" target="_blank">kf.kobotoolbox.org</a><br>
                    2. Open your CEmONC project<br>
                    3. Go to DATA &gt; Downloads<br>
                    4. Choose XLS or CSV format<br>
                    5. Click Export, then Download<br>
                    6. Upload the file here
                </p>
            </div>
            """, unsafe_allow_html=True)
            return

    # ── Clean data ──
    dat = clean_data(dat)

    n_facilities = len(dat)
    if n_facilities == 0:
        st.warning("No valid facility records found in the uploaded data.")
        return

    # ── Sidebar filters ──
    with st.sidebar:
        st.divider()
        st.markdown("### Filters")

        # Team filter
        if "team_number" in dat.columns:
            teams = sorted(dat["team_number"].dropna().unique().tolist())
            selected_teams = st.multiselect("Assessment Team:", teams, default=teams)
            dat = dat[dat["team_number"].isin(selected_teams)]

        # Readiness category filter
        cats = ["Poor (<50%)", "Moderate (50-74%)", "Good (>=75%)"]
        available_cats = [c for c in cats if c in dat["readiness_cat"].values]
        selected_cats = st.multiselect("Readiness Category:", available_cats, default=available_cats)
        dat = dat[dat["readiness_cat"].isin(selected_cats)]

        # Facility filter
        if "facility_name" in dat.columns:
            facilities = sorted(dat["facility_name"].dropna().unique().tolist())
            selected_facilities = st.multiselect("Facility:", facilities, default=facilities)
            dat = dat[dat["facility_name"].isin(selected_facilities)]

    n_filtered = len(dat)
    if n_filtered == 0:
        st.warning("No facilities match the current filter criteria.")
        return

    # ── Summary metrics ──
    mean_score = dat["grand_pct"].mean()
    median_score = dat["grand_pct"].median()
    min_score = dat["grand_pct"].min()
    max_score = dat["grand_pct"].max()

    n_good = (dat["readiness_cat"] == "Good (>=75%)").sum()
    n_moderate = (dat["readiness_cat"] == "Moderate (50-74%)").sum()
    n_poor = (dat["readiness_cat"] == "Poor (<50%)").sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{n_filtered}</div>
            <div class="metric-label">Facilities Assessed</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{mean_score:.1f}%</div>
            <div class="metric-label">Mean Readiness Score</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{median_score:.1f}%</div>
            <div class="metric-label">Median Readiness Score</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{min_score:.0f}% - {max_score:.0f}%</div>
            <div class="metric-label">Range</div>
        </div>
        """, unsafe_allow_html=True)

    # Category breakdown
    cat_col1, cat_col2, cat_col3 = st.columns(3)
    with cat_col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #388E3C;">
            <div class="metric-value" style="color: #388E3C;">{n_good}</div>
            <div class="metric-label">Good (&ge;75%)</div>
        </div>
        """, unsafe_allow_html=True)
    with cat_col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #FFA000;">
            <div class="metric-value" style="color: #FFA000;">{n_moderate}</div>
            <div class="metric-label">Moderate (50-74%)</div>
        </div>
        """, unsafe_allow_html=True)
    with cat_col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #D32F2F;">
            <div class="metric-value" style="color: #D32F2F;">{n_poor}</div>
            <div class="metric-label">Poor (&lt;50%)</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Tables & figures for export ──
    all_tables = {}
    tc = 1   # table counter
    fc = 1   # figure counter

    # ══════════════════════════════════════════════════════════
    # SECTION 1: OVERALL READINESS SUMMARY
    # ══════════════════════════════════════════════════════════

    st.markdown('<h2 style="color: #00468B; text-align: center;">Section 1 — Overall Readiness Summary</h2>',
                unsafe_allow_html=True)

    # Summary statistics table
    iqr_25 = dat["grand_pct"].quantile(0.25)
    iqr_75 = dat["grand_pct"].quantile(0.75)
    summary_stats = pd.DataFrame({
        "Statistic": ["Facilities assessed", "Mean readiness score",
                       "Standard deviation", "Median readiness score",
                       "Interquartile range (IQR)",
                       "Minimum score", "Maximum score", "Range"],
        "Value": [
            str(n_filtered),
            f"{mean_score:.1f}%",
            f"{dat['grand_pct'].std():.1f}%",
            f"{median_score:.1f}%",
            f"{iqr_25:.1f}% \u2013 {iqr_75:.1f}%",
            f"{min_score:.1f}%",
            f"{max_score:.1f}%",
            f"{max_score - min_score:.1f} percentage points",
        ],
    })
    st.markdown(render_lancet_table(
        summary_stats,
        title="Overall CEmONC facility readiness — descriptive statistics, Elgon Sub-Region, Uganda",
        table_num=tc
    ), unsafe_allow_html=True)
    all_tables[f"T{tc}_Summary_Stats"] = summary_stats
    tc += 1

    # Readiness category table
    cat_tbl = pd.DataFrame({
        "Readiness Category": ["Good (\u226575%)", "Moderate (50\u201374%)", "Poor (<50%)"],
        "n": [n_good, n_moderate, n_poor],
        "% of Total": [
            f"{n_good / n_filtered * 100:.1f}%",
            f"{n_moderate / n_filtered * 100:.1f}%",
            f"{n_poor / n_filtered * 100:.1f}%",
        ],
    })
    st.markdown(render_lancet_table(
        cat_tbl,
        title="Distribution of facilities by readiness category (WHO SARA thresholds)",
        footer_row=["Total", str(n_filtered), "100.0%"],
        table_num=tc
    ), unsafe_allow_html=True)
    all_tables[f"T{tc}_Readiness_Categories"] = cat_tbl
    tc += 1

    # Readiness category bar chart
    col_fig1, col_fig2 = st.columns(2)
    with col_fig1:
        fig_cat = plot_readiness_distribution(dat, fig_num=fc)
        st.plotly_chart(fig_cat, use_container_width=True)
        fc += 1
    with col_fig2:
        fig_hist = plot_score_distribution(dat, fig_num=fc)
        st.plotly_chart(fig_hist, use_container_width=True)
        fc += 1

    st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 2: FACILITY RANKING
    # ══════════════════════════════════════════════════════════

    st.markdown('<h2 style="color: #00468B; text-align: center;">Section 2 — Facility Ranking</h2>',
                unsafe_allow_html=True)

    facility_tbl = build_facility_scores_table(dat)
    st.markdown(render_lancet_table(
        facility_tbl,
        title="CEmONC facility readiness scores ranked by overall percentage, Elgon Sub-Region",
        table_num=tc
    ), unsafe_allow_html=True)
    all_tables[f"T{tc}_Facility_Scores"] = facility_tbl
    tc += 1

    # Facility ranking bar chart
    fig_ranking = plot_facility_ranking(dat, fig_num=fc)
    st.plotly_chart(fig_ranking, use_container_width=True)
    fc += 1

    st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 3: DOMAIN-LEVEL READINESS
    # ══════════════════════════════════════════════════════════

    st.markdown('<h2 style="color: #00468B; text-align: center;">Section 3 — Domain-Level Readiness</h2>',
                unsafe_allow_html=True)

    domain_summary = compute_domain_summary(dat)

    # Add max-possible column for context
    domain_max_lookup = {d[2]: DOMAIN_MAX_DEFAULTS.get(d[1], "") for d in DOMAINS}
    domain_summary_display = domain_summary.copy()
    domain_summary_display.insert(1, "Max Items", domain_summary_display["Domain"].map(domain_max_lookup))

    st.markdown(render_lancet_table(
        domain_summary_display,
        title="Domain-level readiness summary (mean, SD, range) across assessed facilities",
        table_num=tc
    ), unsafe_allow_html=True)
    all_tables[f"T{tc}_Domain_Summary"] = domain_summary_display
    tc += 1

    # Domain bars
    fig_domains = plot_domain_bars(domain_summary, n_facilities=n_filtered, fig_num=fc)
    st.plotly_chart(fig_domains, use_container_width=True)
    fc += 1

    st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 4: FACILITY x DOMAIN HEATMAP
    # ══════════════════════════════════════════════════════════

    st.markdown('<h2 style="color: #00468B; text-align: center;">Section 4 — Facility x Domain Heatmap</h2>',
                unsafe_allow_html=True)

    if "facility_name" in dat.columns:
        fig_heat = plot_heatmap(dat, fig_num=fc)
        st.plotly_chart(fig_heat, use_container_width=True)
        fc += 1
    else:
        st.info("Facility name column not found — cannot generate heatmap.")

    st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 5: INDIVIDUAL ITEM ANALYSIS (optional)
    # ══════════════════════════════════════════════════════════

    if show_individual_items:
        st.markdown('<h2 style="color: #00468B; text-align: center;">Section 5 — Individual Item Analysis</h2>',
                    unsafe_allow_html=True)

        # Identify yes/no columns (individual checklist items)
        yn_cols = [c for c in dat.columns if dat[c].dropna().isin(["yes", "no"]).all() and len(dat[c].dropna()) > 0]

        if yn_cols:
            item_rows = []
            for col in yn_cols:
                n_yes = (dat[col] == "yes").sum()
                n_total = dat[col].notna().sum()
                pct = round(n_yes / n_total * 100, 1) if n_total > 0 else 0
                item_rows.append({
                    "Item": col.replace("_", " ").title(),
                    "Field Name": col,
                    "Yes": n_yes,
                    "No": n_total - n_yes,
                    "Total": n_total,
                    "Yes (%)": f"{pct}%",
                    "_pct_val": pct,
                })

            item_df = pd.DataFrame(item_rows).sort_values("_pct_val", ascending=True).reset_index(drop=True)
            display_item_df = item_df[["Item", "Yes", "No", "Total", "Yes (%)"]].copy()

            st.markdown(render_lancet_table(
                display_item_df,
                title="Individual checklist item compliance across assessed facilities",
                table_num=tc
            ), unsafe_allow_html=True)
            all_tables[f"T{tc}_Individual_Items"] = display_item_df
            tc += 1

            # Top 10 weakest items bar chart
            weakest = item_df.head(10).copy()

            # Colour by compliance threshold
            weak_colors = [
                "#D32F2F" if v < 50 else "#FFA000" if v < 75 else "#388E3C"
                for v in weakest["_pct_val"]
            ]

            fig_weak = go.Figure(go.Bar(
                y=weakest["Item"],
                x=weakest["_pct_val"],
                orientation="h",
                marker_color=weak_colors,
                marker_line_color=LANCET_TEXT,
                marker_line_width=0.3,
                text=weakest["Yes (%)"],
                textposition="outside",
                textfont=dict(size=10),
            ))
            fig_weak = lancet_plotly_layout(
                fig_weak,
                title=f"Figure {fc}. Ten lowest-compliance checklist items across {n_filtered} facilities",
                xaxis_title="Facilities with 'Yes' (%)",
                yaxis_title="",
                height=420,
            )
            fig_weak.update_xaxes(range=[0, 108], dtick=25)
            st.plotly_chart(fig_weak, use_container_width=True)
            fc += 1
        else:
            st.info("No individual yes/no item columns found in the data.")

        st.divider()

    # ══════════════════════════════════════════════════════════
    # SECTION 6: TEAM COMPARISON (if team data available)
    # ══════════════════════════════════════════════════════════

    if "team_number" in dat.columns and dat["team_number"].nunique() > 1:
        st.markdown('<h2 style="color: #00468B; text-align: center;">Section 6 — Team Comparison</h2>',
                    unsafe_allow_html=True)

        team_summary = dat.groupby("team_number").agg(
            Facilities=("grand_pct", "size"),
            Mean_Score=("grand_pct", "mean"),
            Median_Score=("grand_pct", "median"),
            Min_Score=("grand_pct", "min"),
            Max_Score=("grand_pct", "max"),
        ).reset_index()
        team_summary.columns = ["Team", "Facilities", "Mean (%)", "Median (%)", "Min (%)", "Max (%)"]
        team_summary = team_summary.round(1).sort_values("Mean (%)", ascending=False).reset_index(drop=True)

        st.markdown(render_lancet_table(
            team_summary,
            title="Assessment team comparison — facilities assessed and readiness score distribution",
            table_num=tc
        ), unsafe_allow_html=True)
        all_tables[f"T{tc}_Team_Comparison"] = team_summary
        tc += 1

        # Team comparison box plot
        fig_team = go.Figure()
        teams_sorted = team_summary["Team"].tolist()
        for i, team in enumerate(teams_sorted):
            team_data = dat[dat["team_number"] == team]["grand_pct"]
            fig_team.add_trace(go.Box(
                y=team_data,
                name=team.split(" - ")[-1] if " - " in team else team,
                marker_color=LANCET_COLORS[i % len(LANCET_COLORS)],
                boxpoints="all",
                jitter=0.3,
                pointpos=-1.5,
            ))
        fig_team.add_hline(y=50, line_dash="dash", line_color="#D32F2F", line_width=1,
                           annotation_text="50%", annotation_position="bottom right",
                           annotation_font_size=10, annotation_font_color="#D32F2F")
        fig_team.add_hline(y=75, line_dash="dash", line_color="#388E3C", line_width=1,
                           annotation_text="75%", annotation_position="bottom right",
                           annotation_font_size=10, annotation_font_color="#388E3C")
        fig_team = lancet_plotly_layout(
            fig_team,
            title=f"Figure {fc}. Overall readiness score distribution by assessment team",
            xaxis_title="",
            yaxis_title="Overall Readiness Score (%)",
            height=450,
        )
        fig_team.update_yaxes(range=[0, 105])
        st.plotly_chart(fig_team, use_container_width=True)
        fc += 1

    st.divider()

    # ── Download button ──
    st.markdown('<h3 style="color: #00468B;">Download Full Report</h3>', unsafe_allow_html=True)

    excel_data = generate_excel_report(all_tables)
    st.download_button(
        label="Download Excel Report",
        data=excel_data,
        file_name="CEmONC_Readiness_Analysis_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # ── Footer ──
    st.divider()
    st.markdown("""
    <div style="text-align: center; font-size: 12px; color: #999; padding: 10px;">
        CEmONC Facility Readiness Dashboard v1.0 &nbsp;|&nbsp; Elgon Sub-Region, Uganda<br>
        Developed by Raymond R. Wayesu &nbsp;|&nbsp; UVRI / Elgon Centre for Health Research &amp; Innovation (ELCHRI)
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
