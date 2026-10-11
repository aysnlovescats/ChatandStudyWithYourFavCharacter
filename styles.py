"""Mor + turuncu tema: düz renkler, köşeli çizgiler, sert başlıklar."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@700;800&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
    --ink: #120B1C; --panel: #1C1230; --line: #3A2A5C;
    --purple: #7C3AED; --orange: #FF6A13; --text: #EDE6F7; --muted: #A99BC4;
}
.stApp { background: var(--ink); font-family: 'IBM Plex Sans', 'Segoe UI', sans-serif; }
h1, h2, h3 { font-family: 'Bricolage Grotesque', 'Segoe UI', sans-serif; font-weight: 800; letter-spacing: -0.01em; }

[data-testid="stSidebar"] { background: #0D0716; border-right: 1px solid var(--line); }
[data-testid="stSidebar"] .stButton > button {
    width: 100%; justify-content: flex-start; border-color: transparent;
}
.side-title {
    font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.45rem;
    color: #fff; letter-spacing: -0.02em; margin: .2rem 0 1.4rem 0;
}
.side-note { color: var(--muted); font-size: .85rem; margin-top: .6rem; }

.page-title {
    font-family: 'Bricolage Grotesque', 'Segoe UI', sans-serif; font-weight: 800;
    font-size: 2.7rem; line-height: 1.05; letter-spacing: -0.02em; color: #fff; margin: 0;
}
.page-sub { color: var(--muted); margin: .45rem 0 0 0; }
.page-rule { border-bottom: 1px solid var(--line); margin: 1.1rem 0 1.5rem 0; }

.stButton > button, .stDownloadButton > button {
    border-radius: 0; border: 1px solid var(--line); background: transparent;
    color: var(--text); font-weight: 500;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--orange); color: var(--orange); background: transparent;
}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--orange); border-color: var(--orange); color: var(--ink); font-weight: 600;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: #FF8540; border-color: #FF8540; color: var(--ink);
}

.char-card { background: var(--panel); border: 1px solid var(--line); margin-bottom: .5rem; }
.char-card:hover { border-color: var(--orange); }
.char-img { width: 100%; object-fit: cover; object-position: top; display: block; }
.char-ph, .char-ph-thumb {
    display: flex; align-items: center; justify-content: center; background: #2A1658;
    color: var(--orange); font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
}
.char-ph { width: 100%; }
.char-ph-thumb { border: 1px solid var(--line); }
.char-thumb { object-fit: cover; object-position: top; display: block; border: 1px solid var(--line); }
.char-body { padding: .85rem 1rem 1rem 1rem; border-top: 3px solid var(--purple); }
.char-name {
    font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.3rem;
    line-height: 1.1; color: #fff; letter-spacing: -0.01em;
}
.char-uni { color: var(--orange); font-size: .9rem; font-weight: 500; margin-top: .2rem; }
.char-tag { color: var(--muted); font-size: .9rem; margin-top: .35rem; }

.suggest-box { border-left: 4px solid var(--orange); padding: .1rem 0 .1rem 1rem; margin-bottom: .8rem; }
.suggest-label { color: var(--orange); font-weight: 600; margin-bottom: .3rem; }

[data-testid="stChatMessage"] {
    background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--purple);
    border-radius: 0;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) { border-left-color: var(--orange); }
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def title(text, sub=""):
    html = f'<div class="page-title">{text}</div>'
    if sub:
        html += f'<div class="page-sub">{sub}</div>'
    html += '<div class="page-rule"></div>'
    st.markdown(html, unsafe_allow_html=True)
