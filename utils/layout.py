import streamlit as st
from contextlib import contextmanager
from utils.theme import COLORS

# CSS injection (call once per page via page_header)

_LAYOUT_CSS = """
<style>
/* ── Global chrome cleanup ── */
#MainMenu, footer {visibility: hidden;}

/* ── Metric card base ── */
div[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px 20px;
}

/* ── Panel: bordered container with title ── */
.smile-panel {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px 24px 16px;
    height: 100%;
    box-sizing: border-box;
}
.smile-panel-title {
    font-family: 'Montserrat', sans-serif;
    font-weight: 700;
    font-size: 15px;
    color: var(--text-color);
    margin: 0 0 12px 0;
    letter-spacing: 0.02em;
}

/* ── Filter bar (lighter, top strip) ── */
.smile-filter-bar {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 16px;
}

/* ── Section divider ── */
.smile-divider {
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 24px 0 20px;
}

/* ── Delta badges inside metric_strip ── */
.smile-delta {
    display: inline-block;
    font-size: 13px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 6px;
    margin-top: 4px;
}
.smile-delta-success {
    background: rgba(16, 185, 129, 0.12);
    color: #10B981;
}
.smile-delta-danger {
    background: rgba(239, 68, 68, 0.12);
    color: #EF4444;
}
.smile-delta-warning {
    background: rgba(212, 167, 44, 0.12);
    color: #d4a72c;
}
.smile-delta-neutral {
    background: rgba(110, 119, 129, 0.12);
    color: #6e7781;
}

/* ── Metric strip cards ── */
.smile-metric-card {
    background: var(--secondary-background-color);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 18px 20px 14px;
    text-align: center;
}
.smile-metric-label {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-color);
    opacity: 0.65;
    margin: 0 0 6px 0;
    letter-spacing: 0.03em;
}
.smile-metric-value {
    font-family: 'Montserrat', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: var(--text-color);
    margin: 0;
    line-height: 1.2;
}

/* ── Page header ── */
.smile-page-header {
    margin-bottom: 8px;
}
.smile-page-header h1 {
    font-family: 'Montserrat', sans-serif;
    font-weight: 800;
    margin-bottom: 0;
}
.smile-page-caption {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: var(--text-color);
    opacity: 0.55;
    margin-top: 2px;
    margin-bottom: 20px;
}
</style>
"""

_css_injected = False


def _inject_css():
    """Inject layout CSS once per page render."""
    global _css_injected
    if not _css_injected:
        st.markdown(_LAYOUT_CSS, unsafe_allow_html=True)
        _css_injected = True


# Page-level helpers

def page_header(title: str, caption: str = "", *, page_title: str = None):
    """
    Call at the very top of every page.
    Sets page_config, injects CSS, and renders a styled header.

    Parameters
    ----------
    title : str       — visible H1 on the page
    caption : str     — subtext (BT codes, owner, etc.)
    page_title : str  — browser tab title (defaults to `title`)
    """
    st.set_page_config(
        page_title=page_title or title,
        layout="wide",
    )
    _inject_css()
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
    """Themed horizontal rule between dashboard sections."""
    st.markdown('<hr class="smile-divider">', unsafe_allow_html=True)


# Container primitives (Tableau-style zones)

@contextmanager
def filter_bar():
    """
    Top-level filter strip. Put st.columns / selectboxes inside.

    Usage:
        with filter_bar():
            c1, c2, c3 = st.columns(3)
            with c1: st.selectbox(...)
    """
    with st.container():
        st.markdown('<div class="smile-filter-bar">', unsafe_allow_html=True)
        yield
        st.markdown('</div>', unsafe_allow_html=True)


@contextmanager
def chart_panel(title: str = "", height: int = 420):
    """
    Bordered panel for a chart, fixed pixel height.

    Usage:
        with chart_panel("Revenue Trend", height=400):
            st.plotly_chart(fig, use_container_width=True)
    """
    title_html = (
        f'<p class="smile-panel-title">{title}</p>' if title else ""
    )
    with st.container(height=height, border=False):
        st.markdown(
            f'<div class="smile-panel">{title_html}',
            unsafe_allow_html=True,
        )
        yield
        st.markdown('</div>', unsafe_allow_html=True)


@contextmanager
def table_panel(title: str = "", height: int = 380):
    """
    Bordered panel for a dataframe / table view, fixed pixel height.

    Usage:
        with table_panel("Student Detail", height=350):
            st.dataframe(df, use_container_width=True)
    """
    title_html = (
        f'<p class="smile-panel-title">{title}</p>' if title else ""
    )
    with st.container(height=height, border=False):
        st.markdown(
            f'<div class="smile-panel">{title_html}',
            unsafe_allow_html=True,
        )
        yield
        st.markdown('</div>', unsafe_allow_html=True)


@contextmanager
def panel(title: str = "", height: int = None):
    """
    Generic bordered panel. Height optional (auto if omitted).

    Usage:
        with panel("Notes"):
            st.write("...")
    """
    title_html = (
        f'<p class="smile-panel-title">{title}</p>' if title else ""
    )
    container_kw = {"height": height, "border": False} if height else {"border": False}
    with st.container(**container_kw):
        st.markdown(
            f'<div class="smile-panel">{title_html}',
            unsafe_allow_html=True,
        )
        yield
        st.markdown('</div>', unsafe_allow_html=True)


# Metric strip (row of KPI cards)

def metric_strip(items: list[dict]):
    """
    Render a row of KPI metric cards (Tableau summary-strip style).

    Parameters
    ----------
    items : list of dict, each with keys:
        - label  (str)  : metric name, e.g. "Total Students"
        - value  (str|int|float) : main number
        - delta  (str, optional) : e.g. "+12%", "-3pp"
        - sentiment (str, optional): "success"|"danger"|"warning"|"neutral"

    Usage:
        metric_strip([
            {"label": "Placed", "value": 320, "delta": "+8%", "sentiment": "success"},
            {"label": "Ghosting", "value": 14, "delta": "+2", "sentiment": "danger"},
            {"label": "Pending", "value": 56},
        ])
    """
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        label = item["label"]
        value = item["value"]
        delta = item.get("delta", "")
        sentiment = item.get("sentiment", "neutral")

        delta_html = ""
        if delta:
            delta_html = (
                f'<span class="smile-delta smile-delta-{sentiment}">'
                f'{delta}</span>'
            )

        with col:
            st.markdown(
                f"""
                <div class="smile-metric-card">
                    <p class="smile-metric-label">{label}</p>
                    <p class="smile-metric-value">{value}</p>
                    {delta_html}
                </div>
                """,
                unsafe_allow_html=True,
            )


# Card grid (multi-column layout helper)

def card_grid(n_cols: int = 2):
    """
    Return a list of st.columns for a card grid layout.

    Usage:
        cols = card_grid(3)
        with cols[0]:
            with chart_panel("Chart A", height=350):
                st.plotly_chart(fig1, use_container_width=True)
        with cols[1]:
            ...
    """
    return st.columns(n_cols, gap="medium")
