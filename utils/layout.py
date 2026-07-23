# layout helpers, global css, and sidebar components for the smile dashboard

import streamlit as st
from contextlib import contextmanager
from utils.i18n import t, get_lang, set_lang, LANGUAGES


# global css stylesheet injected once per page render

def _build_css(mode: str = "light") -> str:
    # build the full css string with theme variables baked in

    theme_vars = {
        "light": {
            "--bg-color": "#F8FAFC",
            "--card-bg": "#FFFFFF",
            "--text-color": "#1E293B",
            "--border-color": "#E2E8F0",
            "--muted-color": "#475569",
            "--hover-shadow": "rgba(30,58,138,0.08)",
            "--widget-bg": "#FFFFFF",
            "--widget-text": "#1E293B",
            "--dropdown-bg": "#FFFFFF",
            "--dropdown-text": "#1E293B",
            "--table-header-bg": "#F1F5F9",
            "--table-border": "#E2E8F0",
        },
        "dark": {
            "--bg-color": "#0F172A",
            "--card-bg": "#1E293B",
            "--text-color": "#F1F5F9",
            "--border-color": "#334155",
            "--muted-color": "#94A3B8",
            "--hover-shadow": "rgba(52,98,237,0.12)",
            "--widget-bg": "#1E293B",
            "--widget-text": "#F1F5F9",
            "--dropdown-bg": "#1E293B",
            "--dropdown-text": "#F1F5F9",
            "--table-header-bg": "#334155",
            "--table-border": "#334155",
        },
    }

    vs = theme_vars.get(mode, theme_vars["light"])
    root_vars = "".join(f"{k}:{v};" for k, v in vs.items())

    dark_dataframe_css = """
/* DARK MODE DATAFRAME CANVAS DARK NAVY SYNC (#1E293B) */
.stApp [data-testid="stDataFrame"] canvas,
.stApp [data-testid="stDataFrame"] iframe,
.stApp div[data-testid="stDataFrame"] canvas,
div[data-testid="stDataFrame"] canvas {
    filter: invert(0.86) sepia(0.35) hue-rotate(185deg) saturate(2.8) brightness(1.15) !important;
}
.stApp [data-testid="stDataFrame"],
.stApp [data-testid="stDataFrame"] > div,
div[data-testid="stDataFrame"] {
    background-color: #1E293B !important;
    background: #1E293B !important;
    border-color: #334155 !important;
}
""" if mode == "dark" else ""

    return f"""<style>
:root {{{root_vars}}}

{dark_dataframe_css}

/* Streamlit Theme Variables Override for DataFrames and Canvas */
:root {{
    --background-color: var(--bg-color) !important;
    --secondary-background-color: var(--card-bg) !important;
    --primary-color: #3462ED !important;
    --gdg-bg-cell: var(--card-bg) !important;
    --gdg-bg-cell-medium: var(--card-bg) !important;
    --gdg-bg-header: var(--table-header-bg) !important;
    --gdg-bg-header-has-filter: var(--table-header-bg) !important;
    --gdg-bg-header-hover: var(--table-header-bg) !important;
    --gdg-text-dark: var(--text-color) !important;
    --gdg-text-medium: var(--text-color) !important;
    --gdg-text-light: var(--text-color) !important;
    --gdg-text-header: var(--text-color) !important;
    --gdg-text-header-selected: var(--text-color) !important;
    --gdg-border-color: var(--border-color) !important;
}}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800;900&display=swap');

/* chrome cleanup */
#MainMenu, footer {{visibility: hidden;}}

/* 1. STREAMLIT TOP HEADER BAR (with Deploy button) */
header[data-testid="stHeader"],
[data-testid="stHeader"] {{
    background-color: var(--bg-color) !important;
    background: var(--bg-color) !important;
    color: var(--text-color) !important;
}}
header[data-testid="stHeader"] * {{
    color: var(--text-color) !important;
}}

/* main content spacing */
.block-container {{
    padding-top: 1.2rem !important;
    padding-bottom: 4rem !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1rem;
}}

/* force background and text on main area ONLY */
.stApp {{
    background-color: var(--bg-color) !important;
}}
.stApp .block-container [data-testid="stMarkdownContainer"] p,
.stApp .block-container [data-testid="stMarkdownContainer"] li,
.stApp .block-container [data-testid="stMarkdownContainer"] span,
.stApp .block-container h1, .stApp .block-container h2,
.stApp .block-container h3, .stApp .block-container h4,
.stApp .block-container h5, .stApp .block-container h6 {{
    color: var(--text-color) !important;
}}
.stApp .block-container [data-testid="stCaptionContainer"] p {{
    color: var(--muted-color) !important;
}}

/* ENSURE ALL PLOTLY CHART TEXT TICKS AND LABELS RESPOND TO ACTIVE THEME MODE */
.stApp .block-container div[data-testid="stPlotlyChart"] svg .xtick text,
.stApp .block-container div[data-testid="stPlotlyChart"] svg .ytick text,
.stApp .block-container div[data-testid="stPlotlyChart"] svg .gtitle,
.stApp .block-container div[data-testid="stPlotlyChart"] svg .xtitle,
.stApp .block-container div[data-testid="stPlotlyChart"] svg .ytitle,
.stApp .block-container div[data-testid="stPlotlyChart"] svg .legendtext,
.stApp .block-container div[data-testid="stPlotlyChart"] svg .annotation-text,
.stApp .block-container div[data-testid="stPlotlyChart"] svg text.pointtext {{
    fill: var(--text-color) !important;
}}

/* kpi card */
.smile-metric-card {{
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 16px 10px 14px;
    text-align: center;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 1px 3px rgba(0,0,0,0.04),
        0 4px 6px rgba(0,0,0,0.03),
        0 8px 24px var(--hover-shadow);
    transition: transform 0.25s cubic-bezier(.4,0,.2,1), box-shadow 0.25s cubic-bezier(.4,0,.2,1);
    position: relative;
    overflow: hidden;
}}
.smile-metric-card:hover {{
    transform: translateY(-3px);
    box-shadow:
        0 4px 6px rgba(0,0,0,0.05),
        0 10px 20px rgba(0,0,0,0.04),
        0 20px 40px var(--hover-shadow);
}}
.smile-metric-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(
        90deg,
        var(--smile-accent, #3462ED),
        var(--smile-accent-2, var(--smile-accent, #4748B0))
    );
    border-radius: 16px 16px 0 0;
}}

/* kpi text — Responsive, wrapping, never truncated */
.smile-metric-card .smile-metric-label,
p.smile-metric-label {{
    font-family: 'Inter', sans-serif !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    color: var(--text-color) !important;
    opacity: 0.6;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin: 0 0 6px 0 !important;
    line-height: 1.25 !important;
    white-space: normal !important;
    word-break: break-word !important;
    text-align: center !important;
    max-width: 100%;
}}
.smile-metric-card .smile-metric-value,
p.smile-metric-value {{
    font-family: 'Montserrat', sans-serif !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    color: var(--smile-value-color, var(--text-color)) !important;
    margin: 0 !important;
    line-height: 1.1 !important;
    white-space: nowrap;
    overflow: hidden;
    max-width: 100%;
    animation: smileValueReveal 0.7s cubic-bezier(.4,0,.2,1);
}}

/* delta badges */
.smile-delta {{
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 20px;
    margin-top: 6px;
    letter-spacing: 0.02em;
}}
.smile-delta-success {{ background: rgba(16,185,129,0.12); color: #10B981; }}
.smile-delta-danger {{ background: rgba(239,68,68,0.12); color: #EF4444; }}
.smile-delta-warning {{ background: rgba(212,167,44,0.12); color: #D4A72C; }}
.smile-delta-neutral {{ background: rgba(110,119,129,0.12); color: #6E7781; }}

/* panel / card */
.smile-panel {{
    background-color: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px;
    padding: 24px 28px 20px;
    margin-bottom: 16px;
    overflow: auto;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 6px rgba(0,0,0,0.03);
    transition: box-shadow 0.25s ease;
    animation: smileCardFadeIn 0.5s ease-out;
}}
.smile-panel:hover {{
    box-shadow: 0 4px 8px rgba(0,0,0,0.06), 0 12px 24px rgba(0,0,0,0.04);
}}
.smile-panel,
.smile-panel h1, .smile-panel h2, .smile-panel h3, .smile-panel h4, .smile-panel h5, .smile-panel h6,
.smile-panel p, .smile-panel span, .smile-panel div, .smile-panel td, .smile-panel th, .smile-panel strong,
.smile-panel label, .smile-panel b, .smile-panel i {{
    color: var(--text-color) !important;
}}
.smile-panel-title {{
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    font-size: 18px;
    color: var(--text-color) !important;
    margin: 0 0 16px 0;
    letter-spacing: 0.01em;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--border-color);
}}

/* 2. DATAFRAMES & BASEWEB TABLES LIGHT/DARK MODE SYNC */
.stApp div[data-testid="stDataFrame"],
.stApp div[data-testid="stDataFrame"] > div,
.stApp div[data-testid="stDataFrame"] iframe,
.stApp div[data-testid="stDataFrame"] canvas,
.stApp div[data-testid="stDataFrame"] [data-testid="stTable"],
.stApp div[data-testid="stDataFrame"] [role="grid"],
.stApp div[data-testid="stDataFrame"] [role="region"],
.stApp div[data-testid="stDataFrame"] [role="row"],
.stApp div[data-baseweb="table"],
.stApp div[data-baseweb="table-head"],
.stApp div[data-baseweb="table-body"],
.stApp div[data-baseweb="table-row"],
.stApp div[data-baseweb="table-cell"],
.stApp div[data-baseweb="data-table"],
div[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] canvas,
div[data-baseweb="table"] {{
    background-color: var(--card-bg) !important;
    background: var(--card-bg) !important;
    color: var(--text-color) !important;
    border-color: var(--border-color) !important;
}}

.stApp [data-testid="stDataFrame"] {{
    --gdg-bg-cell: var(--card-bg) !important;
    --gdg-bg-header: var(--table-header-bg) !important;
    --gdg-bg-header-hover: var(--table-header-bg) !important;
    --gdg-text-dark: var(--text-color) !important;
    --gdg-text-medium: var(--text-color) !important;
    --gdg-text-header: var(--text-color) !important;
    --gdg-border-color: var(--border-color) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid var(--border-color) !important;
}}

.stApp div[data-testid="stDataFrame"] [role="columnheader"],
.stApp div[data-testid="stDataFrame"] [role="columnheader"] *,
.stApp div[data-baseweb="table-head"],
.stApp div[data-baseweb="table-head"] *,
div[data-testid="stDataFrame"] [role="columnheader"],
div[data-baseweb="table-head"] * {{
    background-color: var(--table-header-bg) !important;
    background: var(--table-header-bg) !important;
    color: var(--text-color) !important;
    font-weight: 600 !important;
}}

.stApp div[data-testid="stDataFrame"] [role="gridcell"],
.stApp div[data-testid="stDataFrame"] [role="gridcell"] *,
.stApp div[data-baseweb="table-cell"],
.stApp div[data-baseweb="table-cell"] *,
div[data-testid="stDataFrame"] [role="gridcell"],
div[data-baseweb="table-cell"] * {{
    background-color: var(--card-bg) !important;
    background: var(--card-bg) !important;
    color: var(--text-color) !important;
}}

.stApp table,
.stApp .smile-panel table,
.stApp [data-testid="stTable"] table {{
    background-color: var(--card-bg) !important;
    color: var(--text-color) !important;
    border-color: var(--border-color) !important;
}}
.stApp table th,
.stApp .smile-panel table th,
.stApp [data-testid="stTable"] table th {{
    background-color: var(--table-header-bg) !important;
    color: var(--text-color) !important;
    border-bottom: 2px solid var(--border-color) !important;
}}
.stApp table td,
.stApp .smile-panel table td,
.stApp [data-testid="stTable"] table td {{
    background-color: var(--card-bg) !important;
    color: var(--text-color) !important;
    border-bottom: 1px solid var(--border-color) !important;
}}
.stApp table tr:hover td,
.stApp .smile-panel table tr:hover td {{
    background-color: var(--table-header-bg) !important;
}}

/* 3. PRIMARY BUTTONS AND DOWNLOAD REPORT BUTTON (STRICT BLUE BG WITH WHITE TEXT IN BOTH MODES) */
.stApp button[kind="primary"],
.stApp button[type="primary"],
.stApp .stButton > button[kind="primary"],
.stApp .stButton > button[type="primary"],
.stApp .stDownloadButton > button,
.stApp div[data-testid="stDownloadButton"] > button,
.stApp .stDownloadButton a,
.stApp div[data-testid="stDownloadButton"] a,
button[kind="primary"],
button[type="primary"] {{
    background-color: #3462ED !important;
    background: #3462ED !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
}}

.stApp button[kind="primary"] *,
.stApp button[type="primary"] *,
.stApp .stButton > button[kind="primary"] *,
.stApp .stButton > button[type="primary"] *,
.stApp .stDownloadButton > button *,
.stApp div[data-testid="stDownloadButton"] > button *,
.stApp .stDownloadButton a *,
.stApp div[data-testid="stDownloadButton"] a *,
.stApp div[data-testid="stDownloadButton"] p,
.stApp div[data-testid="stDownloadButton"] span,
button[kind="primary"] *,
button[type="primary"] * {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 600 !important;
}}

/* PDF BADGE STRICT WHITE TEXT EXEMPTION */
.stApp .block-container .smile-pdf-badge,
.stApp .block-container .smile-pdf-badge *,
.stApp .block-container .smile-pdf-badge span,
.stApp [data-testid="stMarkdownContainer"] .smile-pdf-badge,
.stApp [data-testid="stMarkdownContainer"] .smile-pdf-badge *,
.smile-pdf-badge,
.smile-pdf-badge *,
.smile-pdf-badge span {{
    color: #FFFFFF !important;
    background-color: #3462ED !important;
    background: #3462ED !important;
}}

/* 4. BASEWEB SELECT, MULTISELECT, INPUTS, POPOVERS & SEARCH BARS */
.stApp div[data-baseweb="select"],
.stApp div[data-baseweb="select"] > div,
.stApp div[data-baseweb="base-input"],
.stApp div[data-baseweb="input"],
.stApp div[data-baseweb="input"] > div,
.stApp input[data-testid="stTextInput"],
.stApp .stTextInput input,
div[data-baseweb="select"],
div[data-baseweb="input"],
div[data-baseweb="input"] > div {{
    background-color: var(--widget-bg) !important;
    background: var(--widget-bg) !important;
    color: var(--widget-text) !important;
    border-color: var(--border-color) !important;
}}

.stApp div[data-baseweb="input"] input,
.stApp div[data-baseweb="select"] input,
div[data-baseweb="input"] input {{
    color: var(--widget-text) !important;
    -webkit-text-fill-color: var(--widget-text) !important;
    background-color: transparent !important;
}}

/* PLACEHOLDER TEXT VISIBILITY FIX FOR SEARCH BARS & INPUTS */
.stApp input::placeholder,
.stApp textarea::placeholder,
.stApp div[data-baseweb="input"] input::placeholder,
.stApp div[data-baseweb="select"] input::placeholder,
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="input"] input::-webkit-input-placeholder,
div[data-baseweb="input"] input::-moz-placeholder,
div[data-baseweb="input"] input:-ms-input-placeholder {{
    color: var(--muted-color) !important;
    -webkit-text-fill-color: var(--muted-color) !important;
    opacity: 1 !important;
}}

div[data-baseweb="select"] span,
div[data-baseweb="select"] div {{
    color: var(--widget-text) !important;
}}

div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[data-baseweb="menu"] {{
    background-color: var(--dropdown-bg) !important;
    color: var(--dropdown-text) !important;
    border: 1px solid var(--border-color) !important;
}}
div[data-baseweb="popover"] li,
ul[data-baseweb="menu"] li,
div[data-baseweb="option"],
div[data-baseweb="option"] * {{
    background-color: var(--dropdown-bg) !important;
    color: var(--dropdown-text) !important;
}}
div[data-baseweb="tag"],
span[data-baseweb="tag"] {{
    background-color: rgba(52, 98, 237, 0.15) !important;
    border: 1px solid var(--border-color) !important;
}}
div[data-baseweb="tag"] *,
span[data-baseweb="tag"] * {{
    color: var(--text-color) !important;
}}

/* 3. CHECKBOX VERTICAL CENTERING & ALIGNMENT */
.stRadio label p,
.stCheckbox label p,
[data-testid="stWidgetLabel"] p {{
    color: var(--text-color) !important;
}}
div[data-testid="stCheckbox"] {{
    display: flex;
    align-items: center;
    min-height: 42px;
    margin-top: auto;
    margin-bottom: 0;
}}
div[data-testid="stCheckbox"] label {{
    display: flex;
    align-items: center;
    margin-bottom: 0 !important;
}}

/* page header */
.smile-page-header {{
    margin-bottom: 2px;
}}
.smile-page-header h1 {{
    font-family: 'Montserrat', sans-serif;
    font-weight: 800;
    font-size: 54px;
    margin-bottom: 0;
    background: linear-gradient(135deg, #3462ED 0%, #4748B0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.smile-page-caption {{
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    color: var(--muted-color) !important;
    font-weight: 500;
    margin-top: 4px;
    margin-bottom: 24px !important;
    line-height: 1.5;
}}
.smile-bt-caption {{
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: var(--muted-color) !important;
    margin-top: 0;
    margin-bottom: 24px;
    line-height: 1.5;
}}

/* section divider */
.smile-divider {{
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 28px 0 20px;
}}

/* sidebar dark background (constant navy in both light and dark modes) */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #121F45 0%, #0D1733 100%) !important;
}}

/* remove Streamlit native nav separators & pull footer up closer to nav */
section[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"],
section[data-testid="stSidebar"] nav + hr,
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] + hr {{
    display: none !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
    border-bottom: none !important;
    padding-bottom: 0 !important;
    margin-bottom: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] + div[data-testid="stElementContainer"] {{
    margin-top: -14px !important;
}}

/* single clean divider lines in sidebar — top divider line perfectly centered vertically */
section[data-testid="stSidebar"] .sidebar-divider-top {{
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.12) !important;
    margin: 0 0 12px 0 !important;
    padding: 0 !important;
    height: 0 !important;
}}
section[data-testid="stSidebar"] .sidebar-divider {{
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.12) !important;
    margin: 14px 0 !important;
    padding: 0 !important;
    height: 0 !important;
}}

/* sidebar section title (centered) */
section[data-testid="stSidebar"] .sidebar-section-title {{
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: rgba(255,255,255,0.45) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    text-align: center;
    margin: 0 0 6px 0;
}}

/* sidebar mode active icon (large, centered, consistent size) */
section[data-testid="stSidebar"] .sidebar-mode-icon {{
    text-align: center;
    font-size: 30px;
    line-height: 1;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2px 0 6px 0;
    user-select: none;
}}

/* sidebar info panel (sumber data box - equal top & bottom spacing) */
section[data-testid="stSidebar"] .sidebar-info {{
    font-family: 'Inter', sans-serif;
    margin: 14px 0;
    padding: 16px;
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.08);
}}
section[data-testid="stSidebar"] .sidebar-info-title {{
    font-size: 9px !important;
    font-weight: 700 !important;
    color: rgba(255,255,255,0.45) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 0 0 10px 0 !important;
    text-align: left;
}}
section[data-testid="stSidebar"] .sidebar-info-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px !important;
    margin: 6px 0 !important;
    line-height: 1.4 !important;
}}

/* FORCE LIGHT TEXT ON SIDEBAR ELEMENTS REGARDLESS OF THEME MODE */
section[data-testid="stSidebar"] .sidebar-info-row span {{
    color: rgba(255,255,255,0.7) !important;
}}
section[data-testid="stSidebar"] .sidebar-info-value {{
    color: #FFFFFF !important;
    font-weight: 600 !important;
}}
section[data-testid="stSidebar"] nav a span,
section[data-testid="stSidebar"] nav a p {{
    color: rgba(255,255,255,0.85) !important;
}}

/* sidebar logo */
section[data-testid="stSidebar"] img[data-testid="stLogo"] {{
    max-height: 80px !important;
    width: auto !important;
}}

/* sidebar nav items */
section[data-testid="stSidebar"] nav a {{
    border-radius: 8px !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    margin-bottom: 2px !important;
}}
section[data-testid="stSidebar"] nav a:hover {{
    background: rgba(52,98,237,0.12) !important;
    transform: translateX(2px);
}}
section[data-testid="stSidebar"] nav a[aria-selected="true"],
section[data-testid="stSidebar"] nav a[aria-current="page"] {{
    background: rgba(52,98,237,0.2) !important;
    border-left: 3px solid #3462ED !important;
}}

/* sidebar version tag (centered) */
section[data-testid="stSidebar"] .sidebar-version {{
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: rgba(255,255,255,0.35) !important;
    text-align: center;
    margin: 10px 0 0 0;
    padding: 0;
}}

/* animations */
@keyframes smileValueReveal {{
    from {{ opacity: 0; transform: translateY(12px) scale(0.9); }}
    to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
@keyframes smileCardFadeIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* widget overrides for theme compat */
div[data-testid="stMetric"] {{
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}
div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {{
    color: var(--text-color) !important;
}}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: var(--text-color) !important;
}}
div[data-baseweb="select"] {{ border-radius: 10px !important; }}

/* text input and placeholder overrides */
input[data-testid="stTextInput"],
.stTextInput input,
div[data-baseweb="input"] input {{
    color: var(--widget-text) !important;
    -webkit-text-fill-color: var(--widget-text) !important;
    background: var(--widget-bg) !important;
}}

input[data-testid="stTextInput"]::placeholder,
.stTextInput input::placeholder,
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="input"] input::-webkit-input-placeholder {{
    color: var(--muted-color) !important;
    -webkit-text-fill-color: var(--muted-color) !important;
    opacity: 1 !important;
}}

/* type scale (scoped to main content, not sidebar) */
.block-container h3 {{ font-size: 24px !important; }}
.block-container h4 {{ font-size: 20px !important; }}
.block-container [data-testid="stMarkdownContainer"] p:not([class^="smile-"]) {{
    font-size: 15px;
}}
.block-container [data-testid="stCaptionContainer"] p {{ font-size: 13px; }}
.block-container [data-testid="stWidgetLabel"] p,
.block-container .stCheckbox label p,
.block-container .stRadio label p {{ font-size: 14px; }}
.block-container [data-testid="stMetricLabel"] p {{ font-size: 13px; }}
.block-container [data-testid="stMetricValue"] {{ font-size: 26px; }}

/* hide default streamlit radio button circles for mode/lang toggles */
div[data-testid="stSidebar"] .stRadio > div {{
    gap: 0 !important;
}}
</style>"""


# global css injection

def _get_mode() -> str:
    return st.session_state.get("theme_mode", "light")


def inject_global_css():
    # inject the global css stylesheet once per page render
    mode = _get_mode()
    st.markdown(_build_css(mode), unsafe_allow_html=True)


# page level helpers

def page_header(title: str, caption: str = "", bt_caption: str = "", *, page_title: str = None):
    # render page title and single concise description text starting with BT code
    inject_global_css()
    st.markdown(
        f'<div class="smile-page-header"><h1>{title}</h1></div>',
        unsafe_allow_html=True,
    )
    desc = bt_caption or caption
    if desc:
        st.markdown(
            f'<p class="smile-page-caption">{desc}</p>',
            unsafe_allow_html=True,
        )


def section_divider():
    # thin horizontal rule between sections
    st.markdown('<hr class="smile-divider">', unsafe_allow_html=True)


# container primitives

@contextmanager
def filter_bar():
    # filter section wrapper
    yield


@contextmanager
def chart_panel(title: str = "", height: int = 420):
    # chart container with optional title
    if title:
        st.markdown(
            f'<p class="smile-panel-title" style="margin-bottom:12px;">{title}</p>',
            unsafe_allow_html=True,
        )
    yield


@contextmanager
def table_panel(title: str = "", height: int = 380):
    # table/dataframe container with optional title
    if title:
        st.markdown(
            f'<p class="smile-panel-title" style="margin-bottom:12px;">{title}</p>',
            unsafe_allow_html=True,
        )
    yield


@contextmanager
def panel(title: str = "", height: int = None):
    # generic panel wrapper
    if title:
        st.markdown(
            f'<p class="smile-panel-title" style="margin-bottom:12px;">{title}</p>',
            unsafe_allow_html=True,
        )
    yield


# metric strip

def metric_strip(items: list):
    # render a row of kpi cards with equal height
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        label = item["label"]
        value = item["value"]
        delta = item.get("delta", "")
        sentiment = item.get("sentiment", "neutral")

        style_parts = []
        color = item.get("color")
        if color:
            if isinstance(color, (tuple, list)):
                start, end = color[0], color[-1]
            else:
                start = end = color
            style_parts.append(f"--smile-accent:{start}")
            style_parts.append(f"--smile-accent-2:{end}")
        value_color = item.get("value_color")
        if value_color:
            style_parts.append(f"--smile-value-color:{value_color}")
        if item.get("bg"):
            style_parts.append(f"--smile-card-bg:{item['bg']}")
        if item.get("border"):
            style_parts.append(f"--smile-card-border:{item['border']}")
        style = f' style="{";".join(style_parts)}"' if style_parts else ""

        delta_html = ""
        if delta:
            delta_html = (
                f'<span class="smile-delta smile-delta-{sentiment}">'
                f'{delta}</span>'
            )

        with col:
            st.markdown(
                f"""
                <div class="smile-metric-card"{style}>
                    <div class="smile-metric-label">{label}</div>
                    <div class="smile-metric-value">{value}</div>
                    {delta_html}
                </div>
                """,
                unsafe_allow_html=True,
            )


# backward compat alias
animated_metric_strip = metric_strip


# card grid

def card_grid(n_cols: int = 2):
    # return streamlit columns for a card grid layout
    return st.columns(n_cols, gap="medium")


# sidebar components

def render_sidebar_brand():
    # logo is rendered via st.logo in app.py; this is a no-op fallback
    pass


def render_sidebar_footer():
    # info panel + version tag + mode/lang controls in sidebar with clean vertical spacing
    current_mode = _get_mode()
    current_lang = get_lang()

    with st.sidebar:
        # single clean divider separating navigation links from footer controls (centered spacing)
        st.markdown('<hr class="sidebar-divider-top">', unsafe_allow_html=True)

        # mode title + single centered active SVG icon (yellow sun circle / blue moon circle) with balanced spacing
        if current_mode == "light":
            mode_icon_html = '<div style="display:flex; align-items:center; justify-content:center; margin:10px auto 14px auto;"><div style="width:42px; height:42px; border-radius:50%; background:#F7C948; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 12px rgba(247,201,72,0.45);"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4" fill="#FFFFFF" stroke="none"></circle><line x1="12" y1="2" x2="12" y2="4"></line><line x1="12" y1="20" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="6.34" y2="6.34"></line><line x1="17.66" y1="17.66" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="4" y2="12"></line><line x1="20" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="6.34" y2="17.66"></line><line x1="17.66" y1="6.34" x2="19.07" y2="4.93"></line></svg></div></div>'
        else:
            mode_icon_html = '<div style="display:flex; align-items:center; justify-content:center; margin:10px auto 14px auto;"><div style="width:42px; height:42px; border-radius:50%; background:#24A2FF; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 12px rgba(36,162,255,0.45);"><svg width="18" height="18" viewBox="0 0 24 24" fill="#FFFFFF" stroke="none"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg></div></div>'

        st.markdown(
            f'<div class="sidebar-section-title">{t("sidebar.switch_mode")}</div>{mode_icon_html}',
            unsafe_allow_html=True,
        )

        mc1, mc2 = st.columns(2)
        with mc1:
            if st.button(":material/wb_sunny: Light", key="btn_mode_light", use_container_width=True,
                          type="primary" if current_mode == "light" else "secondary"):
                st.session_state["theme_mode"] = "light"
                st.rerun()
        with mc2:
            if st.button(":material/nights_stay: Dark", key="btn_mode_dark", use_container_width=True,
                          type="primary" if current_mode == "dark" else "secondary"):
                st.session_state["theme_mode"] = "dark"
                st.rerun()

        # language title (dynamic translation, centered, compact top margin)
        st.markdown(f"""
        <div class="sidebar-section-title" style="margin-top: 10px;">{t("sidebar.language")}</div>
        """, unsafe_allow_html=True)

        lc1, lc2 = st.columns(2)
        with lc1:
            if st.button(":material/language: ID", key="btn_lang_id", use_container_width=True,
                          type="primary" if current_lang == "id" else "secondary"):
                set_lang("id")
                st.rerun()
        with lc2:
            if st.button(":material/g_translate: EN", key="btn_lang_en", use_container_width=True,
                          type="primary" if current_lang == "en" else "secondary"):
                set_lang("en")
                st.rerun()

        # divider before sumber data box
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

        # sumber data box (contents untouched, box container perfectly spaced)
        st.markdown(
            '<div class="sidebar-info">'
            f'<p class="sidebar-info-title">{t("sidebar.data_source")}</p>'
            '<div class="sidebar-info-row">'
            f'<span>{t("sidebar.tables")}</span>'
            '<span class="sidebar-info-value">6 tables</span>'
            '</div>'
            '<div class="sidebar-info-row">'
            f'<span>{t("sidebar.storage")}</span>'
            '<span class="sidebar-info-value">CSV + Supabase</span>'
            '</div>'
            '<div class="sidebar-info-row">'
            f'<span>{t("sidebar.sync")}</span>'
            f'<span class="sidebar-info-value">{t("sidebar.auto")}</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # divider after sumber data box
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

        # footer version tag (centered)
        st.markdown(
            '<p class="sidebar-version">SMILE v1.0 &nbsp;|&nbsp; SSDC 2026</p>',
            unsafe_allow_html=True,
        )


def render_mode_toggle():
    # legacy helper - mode toggle is now rendered as part of render_sidebar_footer
    pass


def render_lang_toggle():
    # legacy helper - lang toggle is now rendered as part of render_sidebar_footer
    pass
