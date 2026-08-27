"""Shared UI theme: professional Swiss-minimal styling for the app.

Design system (via ui-ux-pro-max): Minimalism & Swiss, IBM Plex Sans, high
contrast, dashboard density. Semantic colors for the 3 risk classes. SVG icons
(no emoji-as-icon). Call setup_page() at the top of every page.
"""
from __future__ import annotations

from pathlib import Path

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

# --- Animated inline SVG icons (Lucide-style, currentColor) --------------
# Animation is CSS-driven (classes below) and disabled under reduced-motion.
def _svg(inner: str, size: int = 26) -> str:
    return (f'<svg class="emi-ic" xmlns="http://www.w3.org/2000/svg" width="{size}" '
            f'height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')

ICONS = {
    "shield": _svg('<g class="ic-float"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>'
                   '<path class="ic-draw" d="m9 12 2 2 4-4"/></g>'),
    "check": _svg('<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
                  '<path class="ic-draw" d="m9 11 3 3L22 4"/>'),
    "rupee": _svg('<g class="ic-float"><path d="M6 3h12"/><path d="M6 8h12"/>'
                  '<path d="m6 13 8.5 8"/><path d="M6 13h3"/>'
                  '<path d="M9 13c6.667 0 6.667-10 0-10"/></g>'),
    "chart": _svg('<path d="M3 3v18h18"/>'
                  '<rect class="ic-bar" style="animation-delay:0s" x="7" y="10" width="3" height="7"/>'
                  '<rect class="ic-bar" style="animation-delay:.25s" x="12" y="6" width="3" height="11"/>'
                  '<rect class="ic-bar" style="animation-delay:.5s" x="17" y="13" width="3" height="4"/>'),
    "gauge": _svg('<path class="ic-needle" d="m12 14 4-4"/>'
                  '<path d="M3.34 19a10 10 0 1 1 17.32 0"/>'),
    "database": _svg('<g class="ic-float"><ellipse cx="12" cy="5" rx="9" ry="3"/>'
                     '<path d="M3 5v14a9 3 0 0 0 18 0V5"/>'
                     '<path d="M3 12a9 3 0 0 0 18 0"/></g>'),
    "info": _svg('<circle cx="12" cy="12" r="10"/>'
                 '<path class="ic-pulse" d="M12 16v-4"/>'
                 '<path class="ic-pulse" d="M12 8h.01"/>'),
}

# Brand logo (combined mark: shield + ascending bars + rising arrow).
# Multi-colour, fixed fills — for use on dark surfaces (sidebar, hero chip).
LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" '
    'viewBox="0 0 24 24">'
    '<path d="M12 2 20 5 V11 C20 16 12 22 12 22 C12 22 4 16 4 11 V5 Z" fill="#4F9BF0"/>'
    '<rect x="8" y="13" width="1.7" height="3.2" rx="0.6" fill="#fff" opacity="0.6"/>'
    '<rect x="10.6" y="11.4" width="1.7" height="4.8" rx="0.6" fill="#fff" opacity="0.85"/>'
    '<rect x="13.2" y="9.6" width="1.7" height="6.6" rx="0.6" fill="#fff"/>'
    '<path d="M7.6 13.2 10.8 10.6 14.6 7.4" fill="none" stroke="#fff" '
    'stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M14.6 7.4 12.7 7.7 M14.6 7.4 14.4 9.3" fill="none" stroke="#fff" '
    'stroke-width="1.2" stroke-linecap="round"/>'
    '</svg>'
)
ICONS["logo"] = LOGO_SVG

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp, button, input, select, textarea {
    font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* --- Animated SVG icons --- */
@keyframes emi-float {0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}
@keyframes emi-pulse {0%,100%{opacity:1}50%{opacity:.35}}
@keyframes emi-grow  {0%,100%{transform:scaleY(.5)}50%{transform:scaleY(1)}}
@keyframes emi-swing {0%,100%{transform:rotate(-16deg)}50%{transform:rotate(16deg)}}
@keyframes emi-draw  {0%{stroke-dashoffset:26}55%,100%{stroke-dashoffset:0}}
.emi-ic .ic-float  {animation:emi-float 3s ease-in-out infinite;}
.emi-ic .ic-pulse  {animation:emi-pulse 2s ease-in-out infinite;}
.emi-ic .ic-bar    {transform-box:fill-box;transform-origin:bottom;
                    animation:emi-grow 1.8s ease-in-out infinite;}
.emi-ic .ic-needle {transform-box:fill-box;transform-origin:20% 80%;
                    animation:emi-swing 2.6s ease-in-out infinite;}
.emi-ic .ic-draw   {stroke-dasharray:26;animation:emi-draw 2.8s ease-in-out infinite;}
@media (prefers-reduced-motion: reduce) {
    .emi-ic .ic-float, .emi-ic .ic-pulse, .emi-ic .ic-bar,
    .emi-ic .ic-needle, .emi-ic .ic-draw {animation:none;}
    .emi-ic .ic-draw {stroke-dashoffset:0;}
}

/* --- Nav / callout cards --- */
a.nav-card {
    display:flex; align-items:center; gap:10px; text-decoration:none;
    border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;
    background:#fff; color:#0B2A4A; font-weight:600; font-size:.92rem;
    transition:all .2s ease; box-shadow:0 1px 2px rgba(15,23,42,.04);
}
a.nav-card:hover {border-color:#1565C0; transform:translateY(-2px);
    box-shadow:0 6px 16px rgba(21,101,192,.16);}
a.nav-card .emi-ic {color:#1565C0;}
.emi-callout {
    display:flex; gap:12px; align-items:flex-start;
    border:1px solid #BAE0FD; background:#EFF8FF; color:#0B2A4A;
    border-radius:12px; padding:14px 18px; margin:6px 0 14px;
    font-size:.92rem; line-height:1.5;
}
.emi-callout .emi-ic {color:#1565C0; flex:none; margin-top:1px;}

/* Cleaner chrome */
#MainMenu, footer {visibility: hidden;}
.stApp header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px;}

/* Subtle premium background wash (cards stay white and lift off it) */
.stApp {
    background:
        radial-gradient(1100px 520px at 12% -8%, rgba(21,101,192,.07), transparent 60%),
        radial-gradient(1000px 520px at 100% 0%, rgba(11,42,74,.06), transparent 55%),
        linear-gradient(180deg, #F7FAFC 0%, #EEF3F8 100%);
    background-attachment: fixed;
}

/* Sidebar — compact, production-ready */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B2A4A 0%, #0E3560 100%);
    border-right: 1px solid rgba(255,255,255,.06);
    width: 260px !important; min-width: 260px !important;
    position: relative;
}
/* Flex column so brand + nav stack from the top */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    display: flex; flex-direction: column; height: 100%;
}
/* Neutralize Streamlit's wrappers around the footer so it anchors to the
   sidebar section, not the zero-height element container */
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sidebar-footer),
section[data-testid="stSidebar"] .stMarkdown:has(.sidebar-footer) {
    position: static !important;
}
/* Status footer pinned to the bottom of the sidebar */
section[data-testid="stSidebar"] .sidebar-footer {
    position: absolute; left: 0; right: 0; bottom: 18px; padding: 0 20px;
    z-index: 1;
}
/* Brand block sits at the TOP, above the navigation */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    order: -1; padding-top: 2px; padding-bottom: 6px;
}
/* Collapse button: aligned to the sidebar grid, subtle */
[data-testid="stSidebarCollapseButton"] {margin: 6px 10px 0 0;}
[data-testid="stSidebarCollapseButton"] button {
    color: #94A3B8; border-radius: 8px; padding: 4px;
    transition: background .18s ease, color .18s ease;
}
[data-testid="stSidebarCollapseButton"] button:hover {
    background: rgba(255,255,255,.08); color: #E2E8F0;
}
/* Navigation links — one grid, consistent spacing */
[data-testid="stSidebarNav"] {padding-top: 2px; margin-top: 0;}
[data-testid="stSidebarNav"] ul {gap: 3px; padding: 0;}
[data-testid="stSidebarNav"] li > a {
    padding: 7px 12px; margin: 1px 12px; border-radius: 8px;
    font-size: 14.5px; font-weight: 500; line-height: 1.3;
    border-left: 3px solid transparent;
    transition: background .18s ease, transform .18s ease, border-color .18s ease;
}
[data-testid="stSidebarNav"] li > a span {font-size: 14.5px;}
[data-testid="stSidebarNav"] li > a:hover {
    background: rgba(255,255,255,.08); transform: translateX(2px);
}
[data-testid="stSidebarNav"] li > a[aria-current="page"] {
    background: rgba(79,155,240,.20);
    border-left: 3px solid #4F9BF0; font-weight: 600;
}
[data-testid="stSidebarNav"] li > a[aria-current="page"] span {font-weight: 600;}
/* Brand logo slightly more prominent */
section[data-testid="stSidebar"] .brand-logo svg {width: 30px !important; height: 30px !important;}
/* Light text for sidebar labels/nav, but NOT inside white widgets */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {
    color: #E2E8F0 !important;
}
/* Keep multiselect controls readable: dark text on their white surface */
section[data-testid="stSidebar"] [data-baseweb="select"] {
    background:#fff; border-radius:8px;
}
section[data-testid="stSidebar"] [data-baseweb="select"] * {color:#0F172A !important;}
/* Selected chips: brand blue with white text */
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background:__PRIMARY__ !important; border-radius:6px;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] * {color:#fff !important;}
/* Dropdown popover text stays dark */
[data-baseweb="popover"] [role="option"] {color:#0F172A !important;}

/* Page hero header */
.app-hero {
    display: flex; align-items: center; gap: 16px;
    padding: 24px 28px; margin-bottom: 22px; border-radius: 16px;
    background:
        radial-gradient(520px 180px at 88% -30%, rgba(56,189,248,.35), transparent 60%),
        linear-gradient(120deg, __NAVY__ 0%, __PRIMARY__ 52%, #0E7490 100%);
    color: #fff; box-shadow: 0 10px 30px rgba(13,80,140,.28);
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
/* Gradient primary CTAs */
button[kind="primary"], button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, #1565C0 0%, #0E7490 100%) !important;
    border: none !important; color: #fff !important;
    box-shadow: 0 4px 14px rgba(14,116,144,.28) !important;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
    filter: brightness(1.06);
}

/* Metric cards */
[data-testid="stMetric"] {
    background: __CARD__; border: 1px solid __BORDER__; border-radius: 12px;
    padding: 18px 18px 16px; box-shadow: 0 2px 8px rgba(15,23,42,.05);
    position: relative; overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #1565C0, #0E7490);
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 6px 18px rgba(15,23,42,.10); transform: translateY(-1px);
    transition: all .18s ease;
}
[data-testid="stMetricLabel"] {color: __MUTED__; font-weight: 500;}
[data-testid="stMetricValue"] {color: __INK__; font-weight: 600;}

/* Inputs */
[data-testid="stForm"] {
    border: 1px solid __BORDER__; border-radius: 14px; padding: 8px 22px 4px;
    background: __CARD__;
}
.stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
    border-radius: 8px;
}

/* Section subheaders inside forms */
[data-testid="stForm"] h3 {
    font-size: .8rem; text-transform: uppercase; letter-spacing: .06em;
    color: __PRIMARY__; font-weight: 600; margin-top: 1rem;
    border-bottom: 1px solid __BORDER__; padding-bottom: .4rem;
}

/* Result banner */
.result-card {
    border-radius: 14px; padding: 22px 26px; margin: 4px 0 18px;
    border: 1px solid __BORDER__;
}
.result-card .rc-label {font-size: .8rem; text-transform: uppercase;
    letter-spacing: .06em; font-weight: 600; opacity: .8;}
.result-card .rc-value {font-size: 2rem; font-weight: 700; margin-top: 2px;}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px; border-bottom: 1px solid __BORDER__; margin-bottom: 4px;
}
.stTabs [data-baseweb="tab"] {
    padding: 8px 18px; border-radius: 8px 8px 0 0; font-weight: 500;
    color: __MUTED__; background: #EEF3F8;
}
.stTabs [data-baseweb="tab"]:hover {background: #E3EBF4; color: __INK__;}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: #fff; color: __PRIMARY__; font-weight: 600;
    border: 1px solid __BORDER__; border-bottom: 2px solid __PRIMARY__;
}

/* Tables */
[data-testid="stDataFrame"] {border-radius: 10px; border: 1px solid __BORDER__;}

/* Multiselect: let chips wrap & show full text (no inner scrollbar/ellipsis) */
[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:first-child {
    flex-wrap: wrap; max-height: none; overflow: visible; height: auto;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    max-width: none !important; border-radius: 6px;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
    max-width: none !important; overflow: visible !important;
    text-overflow: clip !important; white-space: normal !important;
}
</style>
"""
for _k, _v in {"NAVY": NAVY, "PRIMARY": PRIMARY, "INK": INK, "MUTED": MUTED,
               "BORDER": BORDER, "CARD": CARD}.items():
    _CSS = _CSS.replace("__%s__" % _k, _v)


STATUS_COLORS = {"good": "#15803D", "warn": "#B45309", "bad": "#B91C1C"}


_FAVICON = Path(__file__).resolve().parent / "assets" / "favicon.png"


def setup_page(title: str, icon_emoji: str = "💳"):
    icon = str(_FAVICON) if _FAVICON.exists() else icon_emoji
    st.set_page_config(page_title=f"{title} · EMIPredict AI",
                       page_icon=icon, layout="wide")
    st.markdown(_CSS, unsafe_allow_html=True)
    sidebar_brand()
    sidebar_footer()


def sidebar_footer():
    st.sidebar.markdown(
        """
        <div class="sidebar-footer">
          <div style="border-top:1px solid rgba(255,255,255,.12);padding-top:12px;">
            <div style="display:flex;align-items:center;gap:9px;font-size:.8rem;
                        color:#CBD5E1;font-weight:600;">
              <span style="width:8px;height:8px;border-radius:50%;background:#22C55E;
                           box-shadow:0 0 0 3px rgba(34,197,94,.20);"></span>
              Models active
            </div>
            <div style="font-size:.72rem;color:#8B9CB3;margin-top:7px;line-height:1.55;">
              XGBoost classifier + regressor<br>Tracked with MLflow
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand():
    st.sidebar.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:11px;padding:2px 0 14px 0;
                    margin:0 0 6px 0;
                    border-bottom:1px solid rgba(255,255,255,.12);">
          <span class="brand-logo" style="display:flex;">{ICONS['logo']}</span>
          <div style="line-height:1.2;">
            <div style="font-weight:700;font-size:1.1rem;color:#fff;letter-spacing:-.01em;">EMIPredict AI</div>
            <div style="font-size:.7rem;color:#8B9CB3;font-weight:500;">Risk Assessment Platform</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_gauge(percent: float, color: str, caption: str = ""):
    """Semicircular gauge (0-100%). percent is the fill fraction 0..1."""
    pct = max(0.0, min(1.0, percent))
    # Semicircle arc length for r=54 is pi*r ≈ 169.6
    arc = 169.6
    dash = arc * pct
    st.markdown(
        f"""
        <div style="text-align:center;">
          <svg width="180" height="104" viewBox="0 0 130 74">
            <path d="M11 65 A54 54 0 0 1 119 65" fill="none"
                  stroke="#E2E8F0" stroke-width="12" stroke-linecap="round"/>
            <path d="M11 65 A54 54 0 0 1 119 65" fill="none"
                  stroke="{color}" stroke-width="12" stroke-linecap="round"
                  stroke-dasharray="{dash} {arc}"/>
            <text x="65" y="60" text-anchor="middle" font-size="22"
                  font-weight="700" fill="{color}">{pct*100:.0f}%</text>
          </svg>
          <div style="color:{MUTED};font-size:.8rem;margin-top:-6px;">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def factor_rows(factors: list):
    """Render explainability factors as colored rows."""
    rows = ""
    for f in factors:
        c = STATUS_COLORS.get(f["status"], MUTED)
        rows += (
            f'<div style="display:flex;align-items:center;gap:12px;padding:10px 14px;'
            f'border:1px solid {BORDER};border-left:4px solid {c};border-radius:10px;'
            f'margin-bottom:8px;background:#fff;">'
            f'<span style="width:9px;height:9px;border-radius:50%;background:{c};flex:none;"></span>'
            f'<span style="flex:1;color:{INK};font-weight:600;font-size:.9rem;">{f["label"]}</span>'
            f'<span style="color:{c};font-weight:700;font-size:.95rem;">{f["value"]}</span>'
            f'<span style="flex-basis:100%;color:{MUTED};font-size:.78rem;'
            f'padding-left:21px;">{f["note"]}</span></div>'
        )
    st.markdown(f'<div style="margin-top:6px;">{rows}</div>', unsafe_allow_html=True)


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


def nav_row(items):
    """items: list of (page_url, icon_key, label). Renders animated SVG link cards."""
    cells = "".join(
        f'<a class="nav-card" href="{url}" target="_self">{ICONS.get(ic, "")}'
        f'<span>{label}</span></a>'
        for url, ic, label in items
    )
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;'
        f'margin-bottom:8px;">{cells}</div>',
        unsafe_allow_html=True,
    )


def callout(text: str, icon: str = "info"):
    st.markdown(
        f'<div class="emi-callout">{ICONS.get(icon, ICONS["info"])}'
        f'<span>{text}</span></div>',
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        f"""
        <hr style="border:none;border-top:1px solid {BORDER};margin:2.5rem 0 1rem;">
        <div style="text-align:center;color:{MUTED};font-size:.82rem;line-height:1.6;">
          <b style="color:{NAVY};">EMIPredict AI</b> · Financial Risk Assessment
          Platform &nbsp;•&nbsp; XGBoost + MLflow + Streamlit &nbsp;•&nbsp;
          For demonstration and educational use
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
