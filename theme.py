"""
theme.py
Premium 3D glassmorphism FinTech CSS theme, injected once per page render.
Kept separate from app.py so the visual language stays consistent and easy
to tune across every page (auth, dashboard, forms, tables, charts, chat).
"""

CSS = """
<style>
:root {
    --bg-0: #05070f;
    --bg-1: #0b0f1e;
    --bg-2: #10152a;
    --surface: rgba(255, 255, 255, 0.045);
    --surface-strong: rgba(255, 255, 255, 0.07);
    --border: rgba(255, 255, 255, 0.09);
    --border-strong: rgba(255, 255, 255, 0.16);
    --text-0: #eef1ff;
    --text-1: #c7cef0;
    --text-2: #8a91b8;
    --accent-1: #7C9CFF;
    --accent-2: #5EE6C8;
    --accent-3: #B98BFF;
    --danger: #F27F7F;
    --radius-lg: 22px;
    --radius-md: 16px;
    --radius-sm: 10px;
    --shadow-deep: 0 30px 60px -20px rgba(0,0,0,0.65), 0 2px 0 rgba(255,255,255,0.03) inset;
    --shadow-soft: 0 18px 40px -18px rgba(0,0,0,0.55);
}

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background:
        radial-gradient(1200px 700px at 12% -10%, rgba(124,156,255,0.14), transparent 60%),
        radial-gradient(1000px 700px at 110% 10%, rgba(94,230,200,0.10), transparent 55%),
        radial-gradient(900px 900px at 50% 120%, rgba(185,139,255,0.10), transparent 55%),
        linear-gradient(180deg, var(--bg-0), var(--bg-1) 45%, var(--bg-2));
    background-attachment: fixed;
    color: var(--text-0);
}

/* Animated depth-grid background layer */
.sf-bg-grid {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(124,156,255,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124,156,255,0.05) 1px, transparent 1px);
    background-size: 46px 46px;
    transform: perspective(600px) rotateX(55deg) scale(1.6) translateY(-10%);
    transform-origin: center top;
    opacity: 0.35;
    animation: sf-grid-float 18s ease-in-out infinite;
}
@keyframes sf-grid-float {
    0%, 100% { transform: perspective(600px) rotateX(55deg) scale(1.6) translateY(-10%); }
    50% { transform: perspective(600px) rotateX(55deg) scale(1.65) translateY(-6%); }
}

.sf-orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.35;
    z-index: 0;
    pointer-events: none;
    animation: sf-orb-drift 14s ease-in-out infinite;
}
.sf-orb-1 { width: 360px; height: 360px; top: -80px; left: -60px; background: var(--accent-1); }
.sf-orb-2 { width: 420px; height: 420px; bottom: -120px; right: -100px; background: var(--accent-3); animation-delay: -6s; }
.sf-orb-3 { width: 280px; height: 280px; top: 40%; left: 60%; background: var(--accent-2); animation-delay: -3s; }
@keyframes sf-orb-drift {
    0%, 100% { transform: translate(0,0) scale(1); }
    50% { transform: translate(20px,-16px) scale(1.06); }
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1200px; }

/* ---------------------------------------------------------------- */
/* Glass surface primitive                                          */
/* ---------------------------------------------------------------- */
.sf-glass {
    position: relative;
    background: linear-gradient(160deg, var(--surface-strong), var(--surface));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-deep);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    transform-style: preserve-3d;
    transition: transform 0.35s ease, box-shadow 0.35s ease, border-color 0.35s ease;
}
.sf-glass:hover {
    transform: perspective(900px) rotateX(1.4deg) rotateY(-1.4deg) translateZ(6px);
    border-color: var(--border-strong);
}

/* ---------------------------------------------------------------- */
/* Brand header                                                      */
/* ---------------------------------------------------------------- */
.sf-brand-row { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.sf-logo-mark {
    width: 40px; height: 40px; border-radius: 12px;
    background: linear-gradient(135deg, var(--accent-1), var(--accent-3));
    box-shadow: 0 10px 24px -8px rgba(124,156,255,0.55), inset 0 1px 0 rgba(255,255,255,0.4);
    transform: perspective(300px) rotateY(-12deg) rotateX(8deg);
    display: flex; align-items: center; justify-content: center;
}
.sf-logo-mark svg { width: 22px; height: 22px; }
.sf-brand-title {
    font-size: 1.35rem; font-weight: 800; letter-spacing: 0.06em;
    background: linear-gradient(90deg, #ffffff, var(--text-1));
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.sf-brand-sub { color: var(--text-2); font-size: 0.82rem; letter-spacing: 0.03em; margin-top: -4px; }

.sf-page-title { font-size: 1.7rem; font-weight: 800; color: var(--text-0); margin-bottom: 2px; }
.sf-page-sub { color: var(--text-2); font-size: 0.92rem; margin-bottom: 1.2rem; }

/* ---------------------------------------------------------------- */
/* Metric cards                                                       */
/* ---------------------------------------------------------------- */
.sf-metric-card {
    padding: 22px 22px 18px 22px;
    border-radius: var(--radius-md);
    background: linear-gradient(155deg, var(--surface-strong), var(--surface));
    border: 1px solid var(--border);
    box-shadow: var(--shadow-soft);
    transform-style: preserve-3d;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    height: 100%;
}
.sf-metric-card:hover {
    transform: perspective(700px) rotateX(3deg) rotateY(-3deg) translateZ(10px) translateY(-2px);
    border-color: var(--border-strong);
    box-shadow: 0 26px 46px -18px rgba(124,156,255,0.28);
}
.sf-metric-label {
    font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text-2); font-weight: 600; margin-bottom: 10px;
}
.sf-metric-value { font-size: 1.7rem; font-weight: 800; color: var(--text-0); }
.sf-metric-icon {
    width: 34px; height: 34px; border-radius: 10px; margin-bottom: 14px;
    background: linear-gradient(135deg, rgba(124,156,255,0.25), rgba(94,230,200,0.18));
    border: 1px solid var(--border-strong);
    display: flex; align-items: center; justify-content: center;
}

/* ---------------------------------------------------------------- */
/* Sidebar                                                            */
/* ---------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(12,16,32,0.96), rgba(8,11,22,0.98));
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }

.sf-nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 11px 14px; margin-bottom: 6px;
    border-radius: var(--radius-sm);
    border: 1px solid transparent;
    color: var(--text-1);
    font-weight: 600; font-size: 0.92rem;
}
.sf-nav-item.active {
    background: linear-gradient(135deg, rgba(124,156,255,0.18), rgba(185,139,255,0.10));
    border-color: var(--border-strong);
    color: var(--text-0);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
}

.sf-sidebar-user {
    margin-top: 10px; padding: 14px; border-radius: var(--radius-md);
    background: var(--surface); border: 1px solid var(--border);
}
.sf-sidebar-user-name { font-weight: 700; color: var(--text-0); font-size: 0.95rem; }
.sf-sidebar-user-email { color: var(--text-2); font-size: 0.78rem; }

/* ---------------------------------------------------------------- */
/* Buttons                                                            */
/* ---------------------------------------------------------------- */
div.stButton > button, .stFormSubmitButton > button {
    width: 100%;
    background: linear-gradient(135deg, var(--accent-1), #5b7ce0);
    color: #05070f;
    font-weight: 700;
    letter-spacing: 0.04em;
    border: none;
    border-radius: var(--radius-sm);
    padding: 0.65rem 1rem;
    box-shadow: 0 14px 30px -10px rgba(124,156,255,0.55), inset 0 1px 0 rgba(255,255,255,0.35);
    transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}
div.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: perspective(600px) translateZ(6px) translateY(-2px);
    box-shadow: 0 20px 38px -12px rgba(124,156,255,0.65);
    filter: brightness(1.05);
    color: #05070f;
}
div.stButton > button:active { transform: translateY(0px) scale(0.98); }

.sf-secondary-btn button {
    background: var(--surface) !important;
    color: var(--text-0) !important;
    border: 1px solid var(--border-strong) !important;
    box-shadow: none !important;
}

/* ---------------------------------------------------------------- */
/* Inputs                                                             */
/* ---------------------------------------------------------------- */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.045) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-0) !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.35);
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus {
    border-color: var(--accent-1) !important;
    box-shadow: 0 0 0 3px rgba(124,156,255,0.22), inset 0 2px 8px rgba(0,0,0,0.35) !important;
}
label, .stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label, .stTextArea label {
    color: var(--text-1) !important; font-weight: 600 !important; font-size: 0.85rem !important;
}

/* ---------------------------------------------------------------- */
/* Tables / dataframes                                                */
/* ---------------------------------------------------------------- */
div[data-testid="stDataFrame"] {
    border-radius: var(--radius-md);
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-soft);
}

/* ---------------------------------------------------------------- */
/* Auth screen                                                        */
/* ---------------------------------------------------------------- */
.sf-auth-hero {
    padding: 40px 34px;
    height: 100%;
}
.sf-auth-hero-badge {
    display: inline-block; padding: 6px 14px; border-radius: 999px;
    background: var(--surface); border: 1px solid var(--border-strong);
    color: var(--accent-2); font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase;
    margin-bottom: 22px;
}
.sf-auth-hero-title {
    font-size: 2.5rem; font-weight: 800; line-height: 1.1; margin-bottom: 14px;
    background: linear-gradient(100deg, #ffffff 20%, var(--accent-1) 60%, var(--accent-3) 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.sf-auth-hero-desc { color: var(--text-1); font-size: 1.02rem; line-height: 1.6; max-width: 420px; }

.sf-auth-section {
    padding: 24px 12px;
    max-width: 640px;
    margin: 0 auto;
}
.sf-form-section, .sf-table-section, .sf-chart-section, .sf-chat-section {
    position: relative;
    width: 100%;
}
.sf-form-section { max-width: 720px; }
.sf-table-section { overflow-x: auto; }
.sf-chart-section { padding: 4px 0; }
.sf-chat-section {
    min-height: 0;
    padding: 4px 0;
}

.sf-auth-card-title { font-size: 1.5rem; font-weight: 800; color: var(--text-0); margin-bottom: 4px; }
.sf-auth-card-sub { color: var(--text-2); font-size: 0.88rem; margin-bottom: 22px; }

.sf-auth-switch { text-align: center; margin-top: 16px; color: var(--text-2); font-size: 0.88rem; }

.sf-visual-shape {
    width: 100%; height: 210px; border-radius: var(--radius-lg);
    background: linear-gradient(135deg, rgba(124,156,255,0.22), rgba(94,230,200,0.14));
    border: 1px solid var(--border-strong);
    margin-top: 26px;
    position: relative;
    overflow: hidden;
    transform: perspective(900px) rotateX(8deg) rotateY(-6deg);
    box-shadow: var(--shadow-deep);
}
.sf-visual-shape::before, .sf-visual-shape::after {
    content: ""; position: absolute; border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.18);
    background: rgba(255,255,255,0.04);
}
.sf-visual-shape::before { width: 120px; height: 80px; top: 26px; left: 24px; transform: rotate(-8deg); }
.sf-visual-shape::after { width: 90px; height: 60px; bottom: 22px; right: 30px; transform: rotate(10deg); }

/* ---------------------------------------------------------------- */
/* Chat                                                                */
/* ---------------------------------------------------------------- */
.sf-chat-row { display: flex; margin-bottom: 14px; }
.sf-chat-row.user { justify-content: flex-end; }
.sf-chat-bubble {
    max-width: 72%;
    padding: 14px 18px;
    border-radius: 16px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-soft);
    backdrop-filter: blur(14px);
    animation: sf-bubble-in 0.25s ease;
    white-space: pre-wrap;
    line-height: 1.55;
}
@keyframes sf-bubble-in {
    from { opacity: 0; transform: translateY(6px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
.sf-chat-bubble.user {
    background: linear-gradient(135deg, rgba(124,156,255,0.28), rgba(124,156,255,0.14));
    border-color: rgba(124,156,255,0.4);
}
.sf-chat-bubble.ai {
    background: var(--surface-strong);
}
.sf-chat-label {
    font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text-2); margin-bottom: 6px; font-weight: 700;
}

/* Misc */
.sf-empty-state {
    padding: 54px 20px; text-align: center; color: var(--text-2);
    border-radius: var(--radius-md);
    border: 1px dashed rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.018);
    max-width: 760px;
    margin: 18px auto 24px;
}
.sf-chat-section .sf-chat-row:first-child { margin-top: 4px; }
.sf-chat-bubble { word-break: break-word; }
@media (max-width: 768px) {
    .sf-chat-bubble { max-width: 92%; }
    .sf-auth-section { padding: 16px 4px; }
}
.sf-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border-strong), transparent); margin: 18px 0; }
.sf-badge {
    display: inline-block; padding: 3px 10px; border-radius: 999px;
    background: rgba(94,230,200,0.14); color: var(--accent-2);
    font-size: 0.72rem; font-weight: 700; border: 1px solid rgba(94,230,200,0.3);
}
</style>

<div class="sf-bg-grid"></div>
<div class="sf-orb sf-orb-1"></div>
<div class="sf-orb sf-orb-2"></div>
<div class="sf-orb sf-orb-3"></div>
"""


def inject_css(st) -> None:
    st.markdown(CSS, unsafe_allow_html=True)
