"""Shared UI theme: professional Swiss-minimal styling for the app.

Design system (via ui-ux-pro-max): Minimalism & Swiss, IBM Plex Sans, high
contrast, dashboard density. Semantic colors for the 3 risk classes. SVG icons
(no emoji-as-icon). Call setup_page() at the top of every page.
"""
from __future__ import annotations

import streamlit as st

# --- Brand palette -------------------------------------------------------
NAVY = "#0B2A4A"
PRIMARY = "#1565C0"
INK = "#0F172A"
MUTED = "#64748B"
BORDER = "#E2E8F0"
CARD = "#FFFFFF"
SURFACE = "#F1F5F9"

RISK = {
    "Eligible":     {"fg": "#15803D", "bg": "#DCFCE7", "label": "Eligible"},
    "High_Risk":    {"fg": "#B45309", "bg": "#FEF3C7", "label": "High Risk"},
    "Not_Eligible": {"fg": "#B91C1C", "bg": "#FEE2E2", "label": "Not Eligible"},
}

# --- Inline SVG icons (Lucide-style, currentColor) -----------------------
ICONS = {
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>',
    "rupee": '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12"/><path d="M6 8h12"/><path d="m6 13 8.5 8"/><path d="M6 13h3"/><path d="M9 13c6.667 0 6.667-10 0-10"/></svg>',
    "chart": '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><rect x="7" y="10" width="3" height="7"/><rect x="12" y="6" width="3" height="11"/><rect x="17" y="13" width="3" height="4"/></svg>',
    "gauge": '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>',
    "database": '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></svg>',
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp, button, input, select, textarea {
    font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Cleaner chrome */
#MainMenu, footer {visibility: hidden;}
.stApp header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px;}

/* Sidebar */
section[data-testid="stSidebar"] {background: %(NAVY)s;}
section[data-testid="stSidebar"] * {color: #E2E8F0 !important;}
section[data-testid="stSidebar"] a {border-radius: 8px;}
section[data-testid="stSidebar"] a:hover {background: rgba(255,255,255,.08);}

/* Page hero header */
.app-hero {
    display: flex; align-items: center; gap: 16px;
    padding: 22px 26px; margin-bottom: 22px; border-radius: 14px;
    background: linear-gradient(135deg, %(NAVY)s 0%%, %(PRIMARY)s 100%%);
    color: #fff; box-shadow: 0 6px 20px rgba(11,42,74,.18);
}
.app-hero .hero-icon {
    display: flex; align-items: center; justify-content: center;
    width: 52px; height: 52px; border-radius: 12px;
    background: rgba(255,255,255,.14); color: #fff; flex: none;
}
.app-hero h1 {margin: 0; font-size: 1.55rem; font-weight: 600; line-height: 1.2; color:#fff;}
.app-hero p {margin: 3px 0 0; font-size: .9rem; color: rgba(255,255,255,.82);}

/* Buttons */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    border-radius: 8px; font-weight: 600; border: 1px solid transparent;
    transition: all .2s ease; padding: .5rem 1.1rem;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-1px); box-shadow: 0 4px 12px rgba(21,101,192,.25);
}

/* Metric cards */
[data-testid="stMetric"] {
    background: %(CARD)s; border: 1px solid %(BORDER)s; border-radius: 12px;
    padding: 16px 18px; box-shadow: 0 1px 2px rgba(15,23,42,.04);
}
[data-testid="stMetricLabel"] {color: %(MUTED)s; font-weight: 500;}
[data-testid="stMetricValue"] {color: %(INK)s; font-weight: 600;}

/* Inputs */
[data-testid="stForm"] {
    border: 1px solid %(BORDER)s; border-radius: 14px; padding: 8px 22px 4px;
    background: %(CARD)s;
}
.stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
    border-radius: 8px;
}

/* Section subheaders inside forms */
[data-testid="stForm"] h3 {
    font-size: .8rem; text-transform: uppercase; letter-spacing: .06em;
    color: %(PRIMARY)s; font-weight: 600; margin-top: 1rem;
    border-bottom: 1px solid %(BORDER)s; padding-bottom: .4rem;
}

/* Result banner */
.result-card {
    border-radius: 14px; padding: 22px 26px; margin: 4px 0 18px;
    border: 1px solid %(BORDER)s;
}
.result-card .rc-label {font-size: .8rem; text-transform: uppercase;
    letter-spacing: .06em; font-weight: 600; opacity: .8;}
.result-card .rc-value {font-size: 2rem; font-weight: 700; margin-top: 2px;}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {gap: 4px;}
.stTabs [data-baseweb="tab"] {border-radius: 8px 8px 0 0; font-weight: 500;}

/* Tables */
[data-testid="stDataFrame"] {border-radius: 10px; border: 1px solid %(BORDER)s;}
</style>
""" % {"NAVY": NAVY, "PRIMARY": PRIMARY, "INK": INK, "MUTED": MUTED,
       "BORDER": BORDER, "CARD": CARD}


def setup_page(title: str, icon_emoji: str = "💳"):
    st.set_page_config(page_title=f"{title} · EMIPredict AI",
                       page_icon=icon_emoji, layout="wide")
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str, icon: str = "shield"):
    st.markdown(
        f"""
        <div class="app-hero">
            <div class="hero-icon">{ICONS.get(icon, ICONS['shield'])}</div>
            <div><h1>{title}</h1><p>{subtitle}</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def result_card(label: str, value: str, fg: str, bg: str):
    st.markdown(
        f"""
        <div class="result-card" style="background:{bg};border-color:{fg}33;">
            <div class="rc-label" style="color:{fg};">{label}</div>
            <div class="rc-value" style="color:{fg};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
