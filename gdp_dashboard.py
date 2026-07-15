import os
import glob
import base64
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

# =========================================================================
# PAGE CONFIG
# =========================================================================
st.set_page_config(page_title="Global GDP Dashboard", page_icon="🌐", layout="wide")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================================================================
# DESIGN SYSTEM — dark-mode-only, cyan/slate palette
# =========================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    :root {
        --bg-base: #0a0f1c;
        --bg-surface: #131c30;
        --bg-surface-2: #1b2740;
        --border-subtle: rgba(255,255,255,0.08);
        --border-strong: rgba(255,255,255,0.16);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --accent: #06b6d4;
        --accent-bright: #22d3ee;
        --accent-glow: rgba(6,182,212,0.35);
    }

    /* --- Keyframe animations --- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes chartDrawIn {
        from { opacity: 0; transform: scale(0.97) translateY(10px); }
        to   { opacity: 1; transform: scale(1) translateY(0); }
    }
    @keyframes softPulse {
        0%, 100% { box-shadow: 0 0 0 rgba(6,182,212,0); }
        50% { box-shadow: 0 0 22px var(--accent-glow); }
    }

    /* Page-load fade-in for the whole app content */
    section.main .block-container { animation: fadeIn 0.5s ease both; }

    .stApp {
        background:
            radial-gradient(circle at 15% -10%, rgba(6,182,212,0.10), transparent 35%),
            radial-gradient(circle at 90% 10%, rgba(139,92,246,0.07), transparent 35%),
            var(--bg-base);
        color: var(--text-primary);
    }
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    /* Scrollbars */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(6,182,212,0.35); border-radius: 10px; border: 2px solid transparent; background-clip: content-box; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(6,182,212,0.6); background-clip: content-box; }

    /* Sidebar — frosted glass panel */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(19,28,48,0.55), rgba(10,15,28,0.75));
        backdrop-filter: blur(16px) saturate(140%);
        -webkit-backdrop-filter: blur(16px) saturate(140%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stSelectbox label { color: var(--text-secondary) !important; font-weight: 600; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.03em; }

    /* Sliders — override Streamlit's default red with the cyan accent */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: var(--accent-bright) !important;
        border-color: var(--accent-bright) !important;
        box-shadow: 0 0 8px var(--accent-glow) !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div {
        background: var(--accent) !important;
    }
    div[data-testid="stSlider"] div[data-testid="stTickBar"] { display: none; }
    div[data-testid="stSlider"] label { color: var(--text-secondary) !important; }
    div[data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: var(--accent-bright) !important; font-weight: 700; background: var(--bg-surface-2) !important;
        border: 1px solid var(--accent); border-radius: 6px; padding: 1px 6px;
    }

    /* Headings */
    h1, h2, h3, h4 { color: var(--text-primary) !important; }

    /* Tabs — frosted glass pill bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px; background: rgba(19,28,48,0.45); backdrop-filter: blur(14px) saturate(150%);
        -webkit-backdrop-filter: blur(14px) saturate(150%);
        padding: 6px; border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.10); flex-wrap: nowrap; overflow-x: auto;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { height: 6px; }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb { background: rgba(6,182,212,0.4); border-radius: 10px; }
    .stTabs [data-baseweb="tab"],
    .stTabs [data-baseweb="tab"] * {
        color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 0 0 auto; white-space: nowrap; height: 42px; border-radius: 10px;
        background: transparent; font-weight: 600; padding: 0 18px;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover,
    .stTabs [data-baseweb="tab"]:hover * {
        color: var(--accent-bright) !important; background: rgba(6,182,212,0.10);
    }
    .stTabs [aria-selected="true"],
    .stTabs [aria-selected="true"] * {
        color: var(--accent-bright) !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(27,39,64,0.55) !important; backdrop-filter: blur(10px);
        box-shadow: 0 0 0 1px var(--accent-glow), 0 0 18px var(--accent-glow), inset 0 1px 0 rgba(255,255,255,0.08);
        border: 1px solid var(--accent);
    }
    /* Tab-switch fade transition: replays whenever a tab panel remounts */
    .stTabs [data-baseweb="tab-panel"] { animation: fadeInUp 0.45s ease both; }

    /* KPI metric cards (fallback styling if native st.metric is ever used) */
    div[data-testid="stMetric"] {
        background: linear-gradient(160deg, rgba(19,28,48,0.45), rgba(27,39,64,0.45));
        backdrop-filter: blur(14px) saturate(150%); -webkit-backdrop-filter: blur(14px) saturate(150%);
        border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 18px 20px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06); transition: all 0.25s ease;
        overflow: visible; animation: fadeInUp 0.5s ease both;
    }
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { animation-delay: 0.02s; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { animation-delay: 0.10s; }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] { animation-delay: 0.18s; }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] { animation-delay: 0.26s; }
    div[data-testid="stMetric"]:hover {
        border-color: var(--accent); box-shadow: 0 6px 28px var(--accent-glow); transform: translateY(-4px) scale(1.01);
    }
    div[data-testid="stMetric"] label { color: var(--text-secondary) !important; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.05em; }
    div[data-testid="stMetricValue"] {
        color: var(--accent-bright) !important;
        overflow: visible !important;
        white-space: normal !important;
        word-break: break-word;
        line-height: 1.25;
        font-size: 1.6rem !important;
        transition: color 0.2s ease;
    }

    /* Chart cards — glass panels so the page's radial background glow shows through */
    div[data-testid="stPlotlyChart"] {
        background: linear-gradient(160deg, rgba(19,28,48,0.42), rgba(27,39,64,0.38));
        backdrop-filter: blur(12px) saturate(140%); -webkit-backdrop-filter: blur(12px) saturate(140%);
        border: 1px solid rgba(255,255,255,0.10); border-radius: 16px;
        padding: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
        animation: chartDrawIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    div[data-testid="stPlotlyChart"]:hover {
        border-color: var(--accent); box-shadow: 0 6px 30px var(--accent-glow); transform: translateY(-3px);
    }

    /* Insights box */
    .insights-box {
        background: linear-gradient(135deg, rgba(6,182,212,0.14), rgba(27,39,64,0.35));
        backdrop-filter: blur(14px) saturate(150%); -webkit-backdrop-filter: blur(14px) saturate(150%);
        border: 1px solid rgba(255,255,255,0.12); border-left: 4px solid var(--accent);
        border-radius: 14px; padding: 20px 24px; margin-bottom: 22px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06);
        animation: fadeInUp 0.5s ease both;
        transition: box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .insights-box:hover { box-shadow: 0 4px 26px rgba(6,182,212,0.22), inset 0 1px 0 rgba(255,255,255,0.08); border-left-color: var(--accent-bright); }
    .insights-box h4 { margin-top: 0; color: var(--accent-bright) !important; font-size: 1.05rem; }
    .insights-box ul { margin: 8px 0 0 0; padding-left: 20px; }
    .insights-box li { color: var(--text-primary); margin-bottom: 7px; line-height: 1.5; font-size: 0.95rem; }
    .insights-box li b { color: var(--accent-bright); }

    /* Dark HTML table styling (kept for potential future reuse) — glass panel */
    .dark-table-wrapper {
        overflow: auto; border: 1px solid rgba(255,255,255,0.10); border-radius: 12px;
        background: rgba(19,28,48,0.35); backdrop-filter: blur(12px) saturate(140%);
        -webkit-backdrop-filter: blur(12px) saturate(140%);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
        animation: fadeIn 0.5s ease both; padding: 4px;
    }
    table.dark-table { border-collapse: collapse; width: 100%; font-size: 0.85rem; }
    table.dark-table thead th {
        position: sticky; top: 0; background: rgba(27,39,64,0.85); backdrop-filter: blur(8px); color: var(--accent-bright);
        text-align: left; padding: 10px 14px; border-bottom: 2px solid var(--accent); z-index: 1;
        text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.04em;
    }
    table.dark-table tbody td { padding: 8px 14px; color: var(--text-primary); border-bottom: 1px solid rgba(255,255,255,0.06); transition: background 0.15s ease; }
    table.dark-table tbody tr:hover { background: rgba(6,182,212,0.08); }

    /* Multiselect chips */
    span[data-baseweb="tag"] {
        background: var(--accent) !important; color: #04202a !important; font-weight: 600;
        transition: transform 0.15s ease, box-shadow 0.15s ease; animation: fadeInUp 0.3s ease both;
    }
    span[data-baseweb="tag"]:hover { transform: translateY(-1px); box-shadow: 0 3px 10px var(--accent-glow); }

    /* Captions / small text */
    .stCaption, .css-1629p8f { color: var(--text-secondary) !important; }

    /* Download button */
    .stDownloadButton button {
        background: var(--bg-surface-2); color: var(--accent-bright); border: 1px solid var(--accent);
        border-radius: 10px; font-weight: 600; transition: all 0.2s ease;
    }
    .stDownloadButton button:hover { background: var(--accent); color: #04202a; box-shadow: 0 0 16px var(--accent-glow); }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# DATA LOADING
# =========================================================================
@st.cache_data
def load_data():
    candidates = glob.glob(os.path.join(SCRIPT_DIR, "data", "*GDP*.xlsx")) + \
                 glob.glob(os.path.join(SCRIPT_DIR, "*GDP*.xlsx"))
    data_file = next((f for f in candidates if "world_gdp_data" in os.path.basename(f).lower()), None)
    if data_file is None and candidates:
        data_file = candidates[0]
    if data_file is None:
        st.error("Could not locate the World_GDP_Data.xlsx data file. Please make sure it sits alongside this script (or in a 'data' subfolder).")
        st.stop()

    df = pd.read_excel(data_file, sheet_name="Data")
    df.columns = df.columns.str.strip()
    df["IncomeGroup"] = df["IncomeGroup"].fillna("Unclassified")
    df["Year"] = df["Year"].astype(int)
    df["GDP"] = pd.to_numeric(df["GDP"], errors="coerce")
    df["GDP Per Capita"] = pd.to_numeric(df["GDP Per Capita"], errors="coerce")
    return df

df_full = load_data()

# =========================================================================
# HELPERS
# =========================================================================
def fmt_compact(n, prefix="$"):
    """Format large numbers compactly (e.g. 2,736,094,000,000 -> '$2.74T') for KPI cards."""
    if pd.isna(n):
        return "N/A"
    n = float(n)
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n >= 1_000_000_000_000:
        return f"{sign}{prefix}{n/1_000_000_000_000:.2f}T"
    if n >= 1_000_000_000:
        return f"{sign}{prefix}{n/1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{sign}{prefix}{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{sign}{prefix}{n/1_000:.1f}K"
    return f"{sign}{prefix}{n:,.0f}"


def style_fig(fig, legend=True, height=440):
    """Central Plotly dark-theme styling: transparent bg, theme-matched fonts/grid/colorbars."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1", size=12),
        title_font=dict(color="#f1f5f9", size=16),
        legend=dict(
            font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)",
            orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5
        ) if legend else dict(),
        showlegend=legend,
        margin=dict(l=10, r=10, t=50, b=60 if legend else 10),
        height=height,
        hoverlabel=dict(bgcolor="#1b2740", font_color="#f1f5f9", bordercolor="#06b6d4"),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.2)", color="#94a3b8")
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.2)", color="#94a3b8")
    try:
        fig.update_polars(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(gridcolor="rgba(148,163,184,0.18)", color="#94a3b8", linecolor="rgba(148,163,184,0.25)"),
            angularaxis=dict(gridcolor="rgba(148,163,184,0.18)", color="#94a3b8", linecolor="rgba(148,163,184,0.25)"),
        )
    except Exception:
        pass
    if fig.layout.coloraxis is not None:
        fig.update_layout(coloraxis_colorbar=dict(tickfont=dict(color="#94a3b8"), title_font=dict(color="#cbd5e1")))
    return fig


def render_dark_table(display_df, max_height=520):
    """Render a dataframe as a custom dark-themed HTML table (st.dataframe can't be restyled)."""
    d = display_df.copy()
    for col in d.select_dtypes(include=[np.number]).columns:
        if col == "Year":
            d[col] = d[col].map(lambda v: f"{int(v)}" if pd.notna(v) else "")
        else:
            d[col] = d[col].map(lambda v: f"{v:,.2f}".rstrip('0').rstrip('.') if pd.notna(v) else "")
    html = d.to_html(classes="dark-table", index=False, border=0, escape=True)
    st.markdown(f'<div class="dark-table-wrapper" style="max-height:{max_height}px;">{html}</div>', unsafe_allow_html=True)


def insights_box(title, points):
    items = "".join(f"<li>{p}</li>" for p in points)
    html = f'<div class="insights-box"><h4>💡 {title}</h4><ul>{items}</ul></div>'
    st.markdown(html, unsafe_allow_html=True)


_kpi_seq = {"n": 0}

def animated_metric(label, numeric=None, value=None, prefix="", suffix="", mode="compact", height=128):
    """Render a themed KPI card. If `numeric` is given, the number count-up-animates from 0 to its
    final value on render (formatted per `mode`: 'compact' -> $1.2T/B/M/K, 'percent' -> +12.3%,
    'int' -> plain integer with thousands separators). If only `value` is given, it's shown as static text."""
    _kpi_seq["n"] += 1
    uid = f"kpi_{_kpi_seq['n']}"

    use_counter = numeric is not None and pd.notna(numeric)
    if use_counter:
        value_inner = f'<div class="kpi-value" id="{uid}">0</div>'
        script = f"""<script>
        (function() {{
            var el = document.getElementById("{uid}");
            var target = {float(numeric)};
            var prefix = "{prefix}"; var suffix = "{suffix}"; var mode = "{mode}";
            function fmt(n) {{
                if (mode === "percent") {{
                    var s = n >= 0 ? "+" : "";
                    return s + n.toFixed(1) + suffix;
                }}
                if (mode === "int") {{
                    return prefix + Math.round(n).toLocaleString() + suffix;
                }}
                var sign = n < 0 ? "-" : ""; n = Math.abs(n); var out;
                if (n >= 1e12) out = (n/1e12).toFixed(2) + "T";
                else if (n >= 1e9) out = (n/1e9).toFixed(2) + "B";
                else if (n >= 1e6) out = (n/1e6).toFixed(1) + "M";
                else if (n >= 1e3) out = (n/1e3).toFixed(1) + "K";
                else out = n.toFixed(0);
                return sign + prefix + out + suffix;
            }}
            var start = null; var duration = 1100;
            function step(ts) {{
                if (!start) start = ts;
                var progress = Math.min((ts - start) / duration, 1);
                var eased = 1 - Math.pow(1 - progress, 3);
                el.textContent = fmt(target * eased);
                if (progress < 1) requestAnimationFrame(step);
                else el.textContent = fmt(target);
            }}
            requestAnimationFrame(step);
        }})();
        </script>"""
    else:
        display_text = value if value is not None else "N/A"
        value_inner = f'<div class="kpi-value" id="{uid}">{display_text}</div>'
        script = ""

    html = f"""
    <div class="kpi-card">
        <style>
            @keyframes fadeInUp {{ from {{opacity:0; transform:translateY(14px);}} to {{opacity:1; transform:translateY(0);}} }}
            html, body {{ margin:0; padding:0; background:transparent; }}
            .kpi-card {{
                font-family:'Inter',sans-serif;
                background:linear-gradient(160deg, rgba(19,28,48,0.5), rgba(27,39,64,0.4));
                backdrop-filter: blur(14px) saturate(150%); -webkit-backdrop-filter: blur(14px) saturate(150%);
                border:1px solid rgba(255,255,255,0.14); border-radius:16px; padding:18px 20px;
                box-shadow:0 4px 18px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.07);
                animation: fadeInUp 0.5s ease both;
                transition: all 0.25s ease; box-sizing:border-box; height:100px;
            }}
            .kpi-card:hover {{ border-color:#06b6d4; box-shadow:0 6px 28px rgba(6,182,212,0.35), inset 0 1px 0 rgba(255,255,255,0.1); transform:translateY(-4px) scale(1.01); }}
            .kpi-label {{ color:#94a3b8; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.05em; font-weight:600; margin-bottom:6px; }}
            .kpi-value {{ color:#22d3ee; font-size:1.6rem; font-weight:700; line-height:1.25; word-break:break-word; }}
        </style>
        <div class="kpi-label">{label}</div>
        {value_inner}
        {script}
    </div>
    """
    components.html(html, height=height, scrolling=False)


PALETTE = px.colors.qualitative.Vivid
CONTINUOUS_SCALE = "Tealgrn"

# =========================================================================
# HEADER (with optional org logo, gracefully skipped if not present)
# =========================================================================
_logo_candidates = glob.glob(os.path.join(SCRIPT_DIR, "*logo*.*")) + glob.glob(os.path.join(SCRIPT_DIR, "**", "*logo*.*"))
_logo_path = next((p for p in _logo_candidates if p.lower().endswith((".png", ".jpg", ".jpeg"))), None)

_logo_html = ""
if _logo_path:
    with open(_logo_path, "rb") as f:
        _logo_b64 = base64.b64encode(f.read()).decode()
    _ext = "png" if _logo_path.lower().endswith("png") else "jpeg"
    _logo_html = f'<div style="background:#ffffff; padding:8px 10px; border-radius:14px; box-shadow:0 6px 20px rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.15); flex-shrink:0; display:flex; align-items:center; animation: softPulse 3.5s ease-in-out infinite;"><img src="data:image/{_ext};base64,{_logo_b64}" style="height:58px; display:block; border-radius:4px;"></div>'

_header_html = f'<div style="display:flex; align-items:center; gap:20px; margin-bottom:4px; padding:16px 22px; border-radius:18px; background:linear-gradient(135deg, rgba(19,28,48,0.45), rgba(27,39,64,0.35)); backdrop-filter:blur(14px) saturate(150%); -webkit-backdrop-filter:blur(14px) saturate(150%); border:1px solid rgba(255,255,255,0.12); box-shadow:0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06); animation: fadeInUp 0.6s ease both;">{_logo_html}<div><h1 style="font-weight:700; color:#f1f5f9; margin:0; line-height:1.2; font-size:2.2rem;">🌐 Global GDP &amp; GDP Per Capita Dashboard</h1></div></div>'
st.markdown(_header_html, unsafe_allow_html=True)
_subtitle_placeholder = st.empty()
_subtitle_placeholder.markdown(
    "<p style='font-size:16px; margin-top:-6px; margin-bottom:26px;'><span style='color:#e2e8f0; opacity:0.65;'>World Bank national accounts data · 211 countries · 1960–2023</span></p>",
    unsafe_allow_html=True
)

# =========================================================================
# SIDEBAR — cascading filters + numeric range sliders
# =========================================================================
if _logo_path:
    st.sidebar.image(_logo_path, use_container_width=True)

st.sidebar.markdown("## 📋 Dashboard Filters")

year_min, year_max = int(df_full["Year"].min()), int(df_full["Year"].max())
year_range = st.sidebar.slider("Year Range", year_min, year_max, (2000, year_max), step=1)

all_regions = sorted(df_full["Region"].dropna().unique().tolist())
sel_regions = st.sidebar.multiselect("Region", all_regions, default=[])

region_scope = df_full[df_full["Region"].isin(sel_regions)] if sel_regions else df_full

all_income = sorted(region_scope["IncomeGroup"].dropna().unique().tolist())
sel_income = st.sidebar.multiselect("Income Group", all_income, default=[])

income_scope = region_scope[region_scope["IncomeGroup"].isin(sel_income)] if sel_income else region_scope

all_countries = sorted(income_scope["Country Name"].dropna().unique().tolist())
sel_countries = st.sidebar.multiselect("Country", all_countries, default=[])

st.sidebar.markdown("---")
gdp_lo, gdp_hi = float(df_full["GDP"].min()), float(df_full["GDP"].max())
gdppc_lo, gdppc_hi = float(df_full["GDP Per Capita"].min()), float(df_full["GDP Per Capita"].max())

gdp_hi_b = gdp_hi / 1_000_000_000       # display in US$ Billions
gdppc_hi_k = gdppc_hi / 1_000           # display in US$ Thousands

gdp_range_b = st.sidebar.slider(
    "GDP Range (US$ Billions)", 0.0, gdp_hi_b, (0.0, gdp_hi_b), format="%.0f"
)

gdppc_range_k = st.sidebar.slider(
    "GDP Per Capita Range (US$ Thousands)", 0.0, gdppc_hi_k, (0.0, gdppc_hi_k), format="%.1f"
)
st.sidebar.caption(f"${gdppc_range_k[0]*1000:,.0f}  –  ${gdppc_range_k[1]*1000:,.0f}")

# Convert back to raw units for filtering
gdp_range = (gdp_range_b[0] * 1_000_000_000, gdp_range_b[1] * 1_000_000_000)
gdppc_range = (gdppc_range_k[0] * 1_000, gdppc_range_k[1] * 1_000)

# Apply filters
mask = (df_full["Year"] >= year_range[0]) & (df_full["Year"] <= year_range[1])
if sel_regions:
    mask &= df_full["Region"].isin(sel_regions)
if sel_income:
    mask &= df_full["IncomeGroup"].isin(sel_income)
if sel_countries:
    mask &= df_full["Country Name"].isin(sel_countries)
mask &= df_full["GDP"].between(gdp_range[0], gdp_range[1])
mask &= df_full["GDP Per Capita"].between(gdppc_range[0], gdppc_range[1])

fdf = df_full[mask].copy()

st.sidebar.markdown("---")
st.sidebar.markdown(f"<p style='color:#ffffff; font-size:0.8rem;'>📊 {fdf['Country Name'].nunique()} countries · {len(fdf):,} records matched</p>", unsafe_allow_html=True)

if fdf.empty:
    _subtitle_placeholder.markdown(
        "<p style='font-size:16px; margin-top:-6px; margin-bottom:26px;'><span style='color:#e2e8f0; opacity:0.65;'>World Bank national accounts data · no data matches current filters</span></p>",
        unsafe_allow_html=True
    )
    st.warning("No data matches the current filter selection. Please broaden your filters in the sidebar.")
    st.stop()

latest_year = int(fdf["Year"].max())
earliest_year = int(fdf["Year"].min())
_subtitle_placeholder.markdown(
    f"<p style='font-size:16px; margin-top:-6px; margin-bottom:26px;'><span style='color:#e2e8f0; opacity:0.65;'>World Bank national accounts data · {fdf['Country Name'].nunique()} countries · {earliest_year}–{latest_year}</span></p>",
    unsafe_allow_html=True
)
latest_slice = fdf[fdf["Year"] == latest_year]
earliest_slice = fdf[fdf["Year"] == earliest_year]

# =========================================================================
# TABS
# =========================================================================
tab_overview, tab_gdp, tab_pc, tab_regional, tab_country = st.tabs([
    "🌍 Overview", "💰 GDP Analysis", "👤 GDP Per Capita", "🗺️ Regional & Income", "🔎 Country Deep Dive"
])

# -------------------------------------------------------------------------
# TAB 1 — OVERVIEW
# -------------------------------------------------------------------------
with tab_overview:
    total_gdp_latest = latest_slice["GDP"].sum()
    total_gdp_earliest = earliest_slice["GDP"].sum()
    growth_pct = ((total_gdp_latest - total_gdp_earliest) / total_gdp_earliest * 100) if total_gdp_earliest else np.nan
    avg_gdppc_latest = latest_slice["GDP Per Capita"].mean()
    top_country_row = latest_slice.loc[latest_slice["GDP"].idxmax()] if not latest_slice.empty else None
    n_countries = fdf["Country Name"].nunique()

    top_region_gdp = latest_slice.groupby("Region")["GDP"].sum().idxmax() if not latest_slice.empty else "N/A"

    insights_box(f"Dynamic Key Findings — Overview ({earliest_year}–{latest_year})", [
        f"Combined GDP across the <b>{n_countries}</b> selected countries reached <b>{fmt_compact(total_gdp_latest)}</b> in {latest_year}, "
        f"{'up' if growth_pct >= 0 else 'down'} <b>{abs(growth_pct):.1f}%</b> from {earliest_year}.",
        f"<b>{top_country_row['Country Name'] if top_country_row is not None else 'N/A'}</b> holds the largest economy in the selection at "
        f"<b>{fmt_compact(top_country_row['GDP']) if top_country_row is not None else 'N/A'}</b> in {latest_year}.",
        f"The average GDP per capita across selected countries was <b>{fmt_compact(avg_gdppc_latest, prefix='$')}</b> in {latest_year}.",
        f"<b>{top_region_gdp}</b> is the largest contributor to combined GDP among the regions currently in view.",
        f"Between {earliest_year} and {latest_year}, {(fdf.groupby('Country Name')['GDP'].apply(lambda s: s.iloc[-1] > s.iloc[0] if len(s) > 1 else False)).mean()*100:.0f}% of countries saw their GDP grow.",
        f"Income-group mix in the current selection: {', '.join(f'{k} ({v})' for k, v in latest_slice['IncomeGroup'].value_counts().items())}.",
    ])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        animated_metric(f"Total GDP ({latest_year})", numeric=total_gdp_latest, prefix="$", mode="compact")
    with k2:
        animated_metric(f"Avg GDP / Capita ({latest_year})", numeric=avg_gdppc_latest, prefix="$", mode="compact")
    with k3:
        animated_metric("Countries in View", numeric=n_countries, mode="int")
    with k4:
        animated_metric(f"Growth since {earliest_year}", numeric=growth_pct, mode="percent", suffix="%")

    world_trend = fdf.groupby("Year", as_index=False)["GDP"].sum()
    fig = px.area(world_trend, x="Year", y="GDP", title="Combined GDP Over Time", color_discrete_sequence=[PALETTE[0]])
    fig.update_traces(line=dict(width=2.5), fillcolor="rgba(6,182,212,0.18)")
    st.plotly_chart(style_fig(fig, height=480), use_container_width=True, key="chart_1")

    region_share = latest_slice.groupby("Region", as_index=False)["GDP"].sum()
    fig = px.pie(region_share, names="Region", values="GDP", hole=0.55, title=f"GDP Share by Region ({latest_year})",
                 color_discrete_sequence=PALETTE)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(style_fig(fig, height=480), use_container_width=True, key="chart_2")

    top10 = latest_slice.nlargest(10, "GDP")
    fig = px.treemap(top10, path=[px.Constant("World"), "Region", "Country Name"], values="GDP",
                      color="GDP", color_continuous_scale=CONTINUOUS_SCALE, title=f"Top 10 Economies — Treemap ({latest_year})")
    st.plotly_chart(style_fig(fig, legend=False, height=500), use_container_width=True, key="chart_3")

    funnel_df = latest_slice.groupby("IncomeGroup", as_index=False)["GDP"].sum().sort_values("GDP", ascending=False)
    fig = px.funnel(funnel_df, x="GDP", y="IncomeGroup", title=f"GDP Funnel by Income Group ({latest_year})",
                    color="IncomeGroup", color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig, legend=False, height=460), use_container_width=True, key="chart_4")

# -------------------------------------------------------------------------
# TAB 2 — GDP ANALYSIS
# -------------------------------------------------------------------------
with tab_gdp:
    growth_series = fdf.groupby("Year", as_index=False)["GDP"].sum().sort_values("Year")
    growth_series["pct_change"] = growth_series["GDP"].pct_change() * 100
    avg_annual_growth = growth_series["pct_change"].mean()
    top5 = latest_slice.nlargest(5, "GDP")
    bottom5 = latest_slice.nsmallest(5, "GDP")
    fastest_growth = (
        fdf[fdf["Year"].isin([earliest_year, latest_year])]
        .pivot_table(index="Country Name", columns="Year", values="GDP")
        .dropna()
    )
    fastest_growth_country = "N/A"
    if not fastest_growth.empty and earliest_year in fastest_growth.columns and latest_year in fastest_growth.columns:
        fastest_growth["growth"] = (fastest_growth[latest_year] - fastest_growth[earliest_year]) / fastest_growth[earliest_year] * 100
        fastest_growth_country = fastest_growth["growth"].idxmax()

    insights_box("Dynamic Key Findings — GDP Analysis", [
        f"The <b>top 5</b> economies in {latest_year} are: {', '.join(top5['Country Name'].tolist())}.",
        f"Combined GDP grew at an average of <b>{avg_annual_growth:.1f}%</b> per year across the selected window.",
        f"<b>{fastest_growth_country}</b> posted the fastest cumulative GDP growth between {earliest_year} and {latest_year} among fully-observed countries.",
        f"The smallest economies currently in view include: {', '.join(bottom5['Country Name'].tolist())}.",
        f"GDP is heavily concentrated: the top 5 countries account for <b>{(top5['GDP'].sum() / latest_slice['GDP'].sum() * 100):.1f}%</b> of total selected GDP in {latest_year}.",
        f"Median country GDP in {latest_year} stands at <b>{fmt_compact(latest_slice['GDP'].median())}</b>.",
    ])

    top15 = latest_slice.nlargest(15, "GDP").sort_values("GDP")
    fig = px.bar(top15, x="GDP", y="Country Name", orientation="h", color="GDP",
                 color_continuous_scale=CONTINUOUS_SCALE, title=f"Top 15 Economies by GDP ({latest_year})")
    st.plotly_chart(style_fig(fig, legend=False, height=560), use_container_width=True, key="chart_5")

    multi_country = sel_countries if sel_countries else top5["Country Name"].tolist()
    trend_df = fdf[fdf["Country Name"].isin(multi_country)]
    fig = px.line(trend_df, x="Year", y="GDP", color="Country Name", markers=True,
                  color_discrete_sequence=PALETTE, title="GDP Trend Over Time")
    st.plotly_chart(style_fig(fig, height=480), use_container_width=True, key="chart_6")

    fig = px.line(growth_series, x="Year", y="pct_change", title="Year-over-Year Combined GDP Growth (%)",
                  color_discrete_sequence=[PALETTE[3]])
    fig.update_traces(line=dict(width=2.5))
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(148,163,184,0.4)")
    st.plotly_chart(style_fig(fig, legend=False, height=460), use_container_width=True, key="chart_7")

    fig = px.scatter(latest_slice, x="GDP", y="GDP Per Capita", size="GDP", color="Region",
                      hover_name="Country Name", log_x=True, color_discrete_sequence=PALETTE,
                      title=f"GDP vs GDP Per Capita ({latest_year})")
    st.plotly_chart(style_fig(fig, height=500), use_container_width=True, key="chart_8")

# -------------------------------------------------------------------------
# TAB 3 — GDP PER CAPITA
# -------------------------------------------------------------------------
with tab_pc:
    top_pc = latest_slice.nlargest(10, "GDP Per Capita")
    bottom_pc = latest_slice.nsmallest(5, "GDP Per Capita")
    region_avg_pc = latest_slice.groupby("Region")["GDP Per Capita"].mean().sort_values(ascending=False)
    pc_gap = top_pc["GDP Per Capita"].iloc[0] / bottom_pc["GDP Per Capita"].iloc[0] if not bottom_pc.empty else np.nan
    global_median_pc = latest_slice["GDP Per Capita"].median()

    insights_box("Dynamic Key Findings — GDP Per Capita", [
        f"<b>{top_pc.iloc[0]['Country Name']}</b> leads on GDP per capita at <b>{fmt_compact(top_pc.iloc[0]['GDP Per Capita'])}</b> in {latest_year}.",
        f"<b>{region_avg_pc.index[0]}</b> has the highest average GDP per capita among regions at <b>{fmt_compact(region_avg_pc.iloc[0])}</b>.",
        f"The gap between the richest and poorest countries in view is roughly <b>{pc_gap:,.0f}×</b> in per-capita terms.",
        f"Global median GDP per capita across the selection is <b>{fmt_compact(global_median_pc)}</b> in {latest_year}.",
        f"The lowest per-capita economies currently in view include: {', '.join(bottom_pc['Country Name'].tolist())}.",
        f"High-income countries average <b>{fmt_compact(latest_slice[latest_slice.IncomeGroup=='High income']['GDP Per Capita'].mean())}</b> per capita, "
        f"versus <b>{fmt_compact(latest_slice[latest_slice.IncomeGroup=='Low income']['GDP Per Capita'].mean())}</b> for low-income countries.",
    ])

    fig = px.bar_polar(top_pc, r="GDP Per Capita", theta="Country Name", color="GDP Per Capita",
                        color_continuous_scale=CONTINUOUS_SCALE, title=f"Top 10 GDP Per Capita — Radial View ({latest_year})")
    st.plotly_chart(style_fig(fig, legend=False, height=520), use_container_width=True, key="chart_9")

    radar_df = region_avg_pc.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=radar_df["GDP Per Capita"], theta=radar_df["Region"], fill="toself",
                                   line=dict(color=PALETTE[1]), fillcolor="rgba(6,182,212,0.20)"))
    fig.update_layout(title="Average GDP Per Capita by Region — Radar", polar=dict(
        radialaxis=dict(showticklabels=True, gridcolor="rgba(148,163,184,0.15)"),
        angularaxis=dict(gridcolor="rgba(148,163,184,0.15)"), bgcolor="rgba(0,0,0,0)"
    ))
    st.plotly_chart(style_fig(fig, legend=False, height=480), use_container_width=True, key="chart_10")

    fig = px.violin(latest_slice, x="IncomeGroup", y="GDP Per Capita", color="IncomeGroup", box=True,
                     color_discrete_sequence=PALETTE, title=f"GDP Per Capita Distribution by Income Group ({latest_year})")
    st.plotly_chart(style_fig(fig, legend=False, height=480), use_container_width=True, key="chart_11")

    pc_trend = fdf.groupby("Year", as_index=False)["GDP Per Capita"].mean()
    fig = px.area(pc_trend, x="Year", y="GDP Per Capita", title="Average GDP Per Capita Over Time",
                  color_discrete_sequence=[PALETTE[2]])
    fig.update_traces(fillcolor="rgba(139,92,246,0.18)")
    st.plotly_chart(style_fig(fig, legend=False, height=460), use_container_width=True, key="chart_12")

# -------------------------------------------------------------------------
# TAB 4 — REGIONAL & INCOME COMPARISON
# -------------------------------------------------------------------------
with tab_regional:
    region_gdp = latest_slice.groupby("Region", as_index=False)["GDP"].sum().sort_values("GDP", ascending=False)
    income_gdp = latest_slice.groupby("IncomeGroup", as_index=False)["GDP"].sum().sort_values("GDP", ascending=False)
    largest_region = region_gdp.iloc[0]
    smallest_region = region_gdp.iloc[-1]
    n_high_income = latest_slice[latest_slice.IncomeGroup == "High income"]["Country Name"].nunique()
    n_low_income = latest_slice[latest_slice.IncomeGroup == "Low income"]["Country Name"].nunique()
    region_country_counts = latest_slice.groupby("Region")["Country Name"].nunique()

    insights_box("Dynamic Key Findings — Regional & Income Comparison", [
        f"<b>{largest_region['Region']}</b> is the largest region by combined GDP at <b>{fmt_compact(largest_region['GDP'])}</b> in {latest_year}.",
        f"<b>{smallest_region['Region']}</b> has the smallest combined GDP among regions in view, at <b>{fmt_compact(smallest_region['GDP'])}</b>.",
        f"<b>{n_high_income}</b> high-income and <b>{n_low_income}</b> low-income countries are represented in the current selection.",
        f"Income-group GDP ranking (largest to smallest): {', '.join(income_gdp['IncomeGroup'].tolist())}.",
        f"<b>{region_country_counts.idxmax()}</b> contributes the most countries to the current filter ({region_country_counts.max()}).",
        f"Regional GDP concentration: the top region alone accounts for <b>{(largest_region['GDP']/region_gdp['GDP'].sum()*100):.1f}%</b> of combined GDP.",
    ])

    fig = px.bar(region_gdp, x="Region", y="GDP", color="GDP", color_continuous_scale=CONTINUOUS_SCALE,
                 title=f"Total GDP by Region ({latest_year})")
    fig.update_xaxes(tickangle=-25)
    st.plotly_chart(style_fig(fig, legend=False, height=480), use_container_width=True, key="chart_13")

    fig = px.funnel(income_gdp, x="GDP", y="IncomeGroup", title=f"GDP Funnel by Income Group ({latest_year})",
                    color="IncomeGroup", color_discrete_sequence=PALETTE)
    st.plotly_chart(style_fig(fig, legend=False, height=460), use_container_width=True, key="chart_14")

    region_trend = fdf.groupby(["Year", "Region"], as_index=False)["GDP"].sum()
    fig = px.area(region_trend, x="Year", y="GDP", color="Region", color_discrete_sequence=PALETTE,
                  title="Regional GDP Over Time (Stacked)")
    st.plotly_chart(style_fig(fig, height=500), use_container_width=True, key="chart_15")

    fig = px.treemap(latest_slice, path=[px.Constant("World"), "IncomeGroup", "Region"], values="GDP",
                      color="GDP", color_continuous_scale=CONTINUOUS_SCALE, title=f"GDP by Income Group → Region ({latest_year})")
    st.plotly_chart(style_fig(fig, legend=False, height=500), use_container_width=True, key="chart_16")

# -------------------------------------------------------------------------
# TAB 5 — COUNTRY DEEP DIVE
# -------------------------------------------------------------------------
with tab_country:
    default_country = sel_countries[0] if sel_countries else latest_slice.nlargest(1, "GDP")["Country Name"].iloc[0]
    st.markdown("<p style='color:#ffffff; font-weight:600; margin-bottom:4px;'>Select a country to explore</p>", unsafe_allow_html=True)
    focus_country = st.selectbox("Select a country to explore", sorted(fdf["Country Name"].unique()),
                                  index=sorted(fdf["Country Name"].unique()).index(default_country) if default_country in fdf["Country Name"].unique() else 0,
                                  label_visibility="collapsed")

    cdf = fdf[fdf["Country Name"] == focus_country].sort_values("Year")
    c_latest = cdf[cdf.Year == cdf.Year.max()].iloc[0]
    c_earliest = cdf[cdf.Year == cdf.Year.min()].iloc[0]
    c_growth = (c_latest["GDP"] - c_earliest["GDP"]) / c_earliest["GDP"] * 100 if c_earliest["GDP"] else np.nan
    peak_year = cdf.loc[cdf["GDP"].idxmax(), "Year"]
    global_rank = int(latest_slice["GDP"].rank(ascending=False)[latest_slice["Country Name"] == focus_country].iloc[0]) if focus_country in latest_slice["Country Name"].values else None
    pc_rank = int(latest_slice["GDP Per Capita"].rank(ascending=False)[latest_slice["Country Name"] == focus_country].iloc[0]) if focus_country in latest_slice["Country Name"].values else None

    insights_box(f"Dynamic Key Findings — {focus_country}", [
        f"{focus_country}'s GDP grew from <b>{fmt_compact(c_earliest['GDP'])}</b> ({int(c_earliest['Year'])}) to <b>{fmt_compact(c_latest['GDP'])}</b> ({int(c_latest['Year'])}), a change of <b>{c_growth:+.1f}%</b>.",
        f"GDP per capita stood at <b>{fmt_compact(c_latest['GDP Per Capita'])}</b> in {int(c_latest['Year'])}.",
        f"Peak GDP within the selected window was reached in <b>{int(peak_year)}</b>.",
        f"{focus_country} belongs to the <b>{c_latest['Region']}</b> region and is classified as <b>{c_latest['IncomeGroup']}</b>.",
        f"Global GDP rank (within current filters, {latest_year}): <b>#{global_rank}</b>." if global_rank else "Global GDP rank unavailable for the current filter set.",
        f"Global GDP-per-capita rank (within current filters, {latest_year}): <b>#{pc_rank}</b>." if pc_rank else "GDP-per-capita rank unavailable for the current filter set.",
    ])

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        animated_metric(f"GDP ({int(c_latest['Year'])})", numeric=c_latest["GDP"], prefix="$", mode="compact")
    with k2:
        animated_metric(f"GDP / Capita ({int(c_latest['Year'])})", numeric=c_latest["GDP Per Capita"], prefix="$", mode="compact")
    with k3:
        animated_metric("Region", value=c_latest["Region"])
    with k4:
        animated_metric("Income Group", value=c_latest["IncomeGroup"])

    fig = px.area(cdf, x="Year", y="GDP", title=f"{focus_country} — GDP Over Time", color_discrete_sequence=[PALETTE[0]])
    fig.update_traces(fillcolor="rgba(6,182,212,0.18)", line=dict(width=2.5))
    st.plotly_chart(style_fig(fig, legend=False, height=460), use_container_width=True, key="chart_17")

    fig = px.line(cdf, x="Year", y="GDP Per Capita", title=f"{focus_country} — GDP Per Capita Over Time",
                  color_discrete_sequence=[PALETTE[1]], markers=True)
    st.plotly_chart(style_fig(fig, legend=False, height=460), use_container_width=True, key="chart_18")

    peer_region = latest_slice[latest_slice["Region"] == c_latest["Region"]].nlargest(10, "GDP")
    fig = px.bar(peer_region.sort_values("GDP"), x="GDP", y="Country Name", orientation="h",
                 color="GDP", color_continuous_scale=CONTINUOUS_SCALE,
                 title=f"Top Economies in {c_latest['Region']} ({latest_year})")
    st.plotly_chart(style_fig(fig, legend=False, height=480), use_container_width=True, key="chart_19")

    cdf["pct_change"] = cdf["GDP"].pct_change() * 100
    fig = px.bar(cdf.dropna(subset=["pct_change"]), x="Year", y="pct_change",
                 title=f"{focus_country} — YoY GDP Growth (%)", color="pct_change",
                 color_continuous_scale=CONTINUOUS_SCALE)
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(148,163,184,0.4)")
    st.plotly_chart(style_fig(fig, legend=False, height=460), use_container_width=True, key="chart_20")
