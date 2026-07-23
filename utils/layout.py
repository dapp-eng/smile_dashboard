import streamlit as st
from contextlib import contextmanager

# CSS for the SMILE dashboard

_LAYOUT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800;900&display=swap');

/* chrome cleanup */
#MainMenu, footer {visibility: hidden;}

/* main content spacing */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 4rem !important;
}
/* sidebar top padding */
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
}

/* KPI card */
.smile-metric-card {
    background: var(--smile-card-bg, var(--secondary-background-color, #FFFFFF));
    border: 1px solid var(--smile-card-border, var(--border-color, #E2E8F0));
    border-radius: 16px;
    padding: 20px 14px 16px;
    text-align: center;
    min-height: 128px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 1px 3px rgba(0,0,0,0.04),
        0 4px 6px rgba(0,0,0,0.03),
        0 8px 24px rgba(30,58,138,0.04);
    transition: transform 0.25s cubic-bezier(.4,0,.2,1), box-shadow 0.25s cubic-bezier(.4,0,.2,1);
    position: relative;
    overflow: hidden;
}
.smile-metric-card:hover {
    transform: translateY(-3px);
    box-shadow:
        0 4px 6px rgba(0,0,0,0.05),
        0 10px 20px rgba(0,0,0,0.04),
        0 20px 40px rgba(52,98,237,0.08);
}
/* accent bar - override per card with --smile-accent / --smile-accent-2 */
.smile-metric-card::before {
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
}

/* KPI text - label small, value large and single-line */
.smile-metric-card .smile-metric-label,
p.smile-metric-label {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: var(--text-color) !important;
    opacity: 0.6;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 8px 0 !important;
    line-height: 1.3 !important;
    white-space: nowrap;
    overflow: hidden;
    max-width: 100%;
}
.smile-metric-card .smile-metric-value,
p.smile-metric-value {
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
}

/* delta badges */
.smile-delta {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 20px;
    margin-top: 6px;
    letter-spacing: 0.02em;
}
.smile-delta-success { background: rgba(16,185,129,0.12); color: #10B981; }
.smile-delta-danger { background: rgba(239,68,68,0.12); color: #EF4444; }
.smile-delta-warning { background: rgba(212,167,44,0.12); color: #D4A72C; }
.smile-delta-neutral { background: rgba(110,119,129,0.12); color: #6E7781; }

/* -- Panel / Card — raised container -- */
.smile-panel {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color, #E2E8F0);
    border-radius: 16px;
    padding: 24px 28px 20px;
    margin-bottom: 16px;
    overflow: auto;
    box-shadow:
        0 1px 3px rgba(0,0,0,0.04),
        0 4px 6px rgba(0,0,0,0.03);
    transition: box-shadow 0.25s ease;
}
.smile-panel:hover {
    box-shadow:
        0 4px 8px rgba(0,0,0,0.06),
        0 12px 24px rgba(0,0,0,0.04);
}
.smile-panel-title {
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    font-size: 19px;
    color: var(--text-color);
    margin: 0 0 16px 0;
    letter-spacing: 0.01em;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--border-color, #E2E8F0);
}

/* -- Filter bar -- */
.smile-filter-bar {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color, #E2E8F0);
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

/* -- Page header -- */
.smile-page-header {
    margin-bottom: 4px;
}
.smile-page-header h1 {
    font-family: 'Montserrat', sans-serif;
    font-weight: 800;
    font-size: 60px;
    margin-bottom: 0;
    background: linear-gradient(135deg, #3462ED 0%, #4748B0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.smile-page-caption {
    font-family: 'Inter', sans-serif;
    font-size: 25px;
    color: var(--text-color);
    opacity: 0.5;
    margin-top: 2px;
    margin-bottom: 24px;
}

/* section divider */
.smile-divider {
    border: none;
    border-top: 1px solid var(--border-color, #E2E8F0);
    margin: 32px 0 20px;
}

/* validation status badges */
.smile-check-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 10px;
    margin-bottom: 4px;
}
.smile-check-passed { background: rgba(16,185,129,0.12); color: #10B981; }
.smile-check-failed { background: rgba(239,68,68,0.12); color: #EF4444; }

/* sidebar dark background */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #121F45 0%, #0D1733 100%) !important;
}

/* sidebar text white on dark */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.85) !important;
}
section[data-testid="stSidebar"] .sidebar-brand { padding: 4px 0 8px; text-align: left; }
section[data-testid="stSidebar"] .sidebar-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 12px 0 8px;
}
section[data-testid="stSidebar"] .sidebar-version {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: rgba(255,255,255,0.3) !important;
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .sidebar-info {
    font-family: 'Inter', sans-serif;
    margin-top: 4px;
    padding: 14px 16px;
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.06);
}
/* collapse the stMarkdown wrapper gap above sidebar-info */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:has(.sidebar-info) {
    margin-top: -8px;
}
section[data-testid="stSidebar"] .sidebar-info-title {
    font-size: 9px !important;
    font-weight: 700 !important;
    color: rgba(255,255,255,0.35) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 0 0 8px 0 !important;
}
section[data-testid="stSidebar"] .sidebar-info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px !important;
    color: rgba(255,255,255,0.6) !important;
    margin: 4px 0 !important;
    line-height: 1.4 !important;
}
section[data-testid="stSidebar"] .sidebar-info-value {
    color: rgba(255,255,255,0.85) !important;
    font-weight: 600;
}
/* sidebar logo size */
section[data-testid="stSidebar"] img[data-testid="stLogo"] {
    max-height: 80px !important;
    width: auto !important;
}

/* sidebar nav items */
section[data-testid="stSidebar"] nav a {
    border-radius: 8px !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    margin-bottom: 2px !important;
}
section[data-testid="stSidebar"] nav a span,
section[data-testid="stSidebar"] nav a p {
    color: rgba(255,255,255,0.85) !important;
}
section[data-testid="stSidebar"] nav a:hover {
    background: rgba(52,98,237,0.12) !important;
    transform: translateX(2px);
}
section[data-testid="stSidebar"] nav a[aria-selected="true"],
section[data-testid="stSidebar"] nav a[aria-current="page"] {
    background: rgba(52,98,237,0.2) !important;
    border-left: 3px solid #3462ED !important;
}

/* animations */
@keyframes smileValueReveal {
    from { opacity: 0; transform: translateY(12px) scale(0.9); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes smileCardFadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.smile-panel { animation: smileCardFadeIn 0.5s ease-out; }

/* widget overrides */
div[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color, #E2E8F0);
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
div[data-baseweb="select"] { border-radius: 10px !important; }
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ---- global type scale ----
   Everything below is scoped to .block-container on purpose: the sidebar has
   its own deliberately smaller scale (see the sidebar-* rules above) and must
   not inherit these. */

/* section headings — pages write these as st.markdown("#### ...") */
.block-container h3 { font-size: 26px !important; }
.block-container h4 { font-size: 22px !important; }

/* body copy. The :not() keeps this rule off the .smile-* paragraphs
   (panel titles, page caption, metric label/value), which set their own
   sizes and would otherwise lose to this selector on specificity. */
.block-container [data-testid="stMarkdownContainer"] p:not([class^="smile-"]) {
    font-size: 16px;
}
.block-container [data-testid="stCaptionContainer"] p { font-size: 14px; }

/* widget labels: slider, checkbox, radio, multiselect, selectbox */
.block-container [data-testid="stWidgetLabel"] p,
.block-container .stCheckbox label p,
.block-container .stRadio label p { font-size: 15px; }

/* native st.metric (used in the talent-request detail panel) */
.block-container [data-testid="stMetricLabel"] p { font-size: 13px; }
.block-container [data-testid="stMetricValue"] { font-size: 26px; }
</style>
"""

_THEME_VARS = {
    "light": {
        "--background-color": "#F8FAFC",
        "--secondary-background-color": "#FFFFFF",
        "--text-color": "#1E293B",
        "--border-color": "#E2E8F0",
    },
    "dark": {
        "--background-color": "#0F172A",
        "--secondary-background-color": "#1E293B",
        "--text-color": "#F1F5F9",
        "--border-color": "#334155",
    },
}


def _theme_var_css():
    try:
        mode = st.context.theme.type or "light"
    except Exception:
        mode = "light"
    decls = "".join(f"{k}:{v};" for k, v in _THEME_VARS.get(mode, _THEME_VARS["light"]).items())
    return f"<style>:root{{{decls}}}</style>"


def inject_global_css():
    # inject CSS once per page render
    st.markdown(_theme_var_css(), unsafe_allow_html=True)
    st.markdown(_LAYOUT_CSS, unsafe_allow_html=True)


# page-level helpers

def page_header(title, caption="", *, page_title=None):
    # page title + optional caption with gradient heading style
    inject_global_css()
    st.markdown(
        f'<div class="smile-page-header"><h1>{title}</h1></div>',
        unsafe_allow_html=True,
    )
    if caption:
        st.markdown(
            f'<p class="smile-page-caption">{caption}</p>',
            unsafe_allow_html=True,
        )


def section_divider():
    # thin horizontal rule between sections
    st.markdown('<hr class="smile-divider">', unsafe_allow_html=True)


# container primitives

@contextmanager
def filter_bar():
    # filter section wrapper - no border, plain flow
    yield


@contextmanager
def chart_panel(title="", height=420, subtitle=""):
    # chart container with optional title
    if title:
        subtitle_html = f"<div style='font-family: \"Inter\", sans-serif; font-size: 12px; color: var(--text-color); opacity: 0.65; margin: 4px 0 0 0; font-weight: 400; text-transform: none; letter-spacing: normal;'>{subtitle}</div>" if subtitle else ""
        st.markdown(
            f'<div class="smile-panel-title" style="margin-bottom:12px;">{title}{subtitle_html}</div>',
            unsafe_allow_html=True,
        )
    yield


@contextmanager
def table_panel(title="", height=380):
    # table/dataframe container with optional title
    if title:
        st.markdown(
            f'<p class="smile-panel-title" style="margin-bottom:12px;">{title}</p>',
            unsafe_allow_html=True,
        )
    yield


@contextmanager
def panel(title="", height=None):
    # generic panel wrapper
    if title:
        st.markdown(
            f'<p class="smile-panel-title" style="margin-bottom:12px;">{title}</p>',
            unsafe_allow_html=True,
        )
    yield


# metric strip

def metric_strip(items):
    # KPI row - all cards equal height, value font dominant over label
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


# card grid helper
def card_grid(n_cols=2):
    return st.columns(n_cols, gap="medium")


# sidebar helpers

def render_sidebar_brand():
    # Logo rendered via st.logo (called in app.py), this is a no-op fallback
    pass


def render_sidebar_footer():
    # Info panel + version tag shown below nav menu
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-info">'
            '<p class="sidebar-info-title">Data Source</p>'
            '<div class="sidebar-info-row">'
            '<span>Tables</span>'
            '<span class="sidebar-info-value">6 tables</span>'
            '</div>'
            '<div class="sidebar-info-row">'
            '<span>Storage</span>'
            '<span class="sidebar-info-value">CSV + Supabase</span>'
            '</div>'
            '<div class="sidebar-info-row">'
            '<span>Sync</span>'
            '<span class="sidebar-info-value">Auto</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="sidebar-version">SMILE v1.0  |  SSDC 2026</p>',
            unsafe_allow_html=True,
        )
