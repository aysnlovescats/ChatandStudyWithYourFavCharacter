import streamlit as st

st.set_page_config(page_title="Karakter Sohbeti", page_icon=None, layout="wide")

import characters as C
import config
import state
import styles
from views import chat, create, gallery, settings, study

state.init_state()
styles.inject()
ss = st.session_state

NAV = [
    ("gallery", "Karakterler"),
    ("chat", "Sohbet"),
    ("study", "Ders çalış"),
    ("create", "Karakter ekle"),
    ("settings", "Ayarlar"),
]
VIEWS = {"gallery": gallery, "chat": chat, "study": study, "create": create, "settings": settings}

with st.sidebar:
    st.markdown('<div class="side-title">Karakter Sohbeti</div>', unsafe_allow_html=True)
    for key, label in NAV:
        st.button(
            label,
            key=f"nav_{key}",
            type="primary" if ss.page == key else "secondary",
            on_click=state.go,
            args=(key,),
        )
    st.divider()
    st.button("Rastgele öner", key="nav_roll", on_click=state.roll)
    active = C.all_characters().get(ss.active)
    if active:
        st.markdown(f'<div class="side-note">Aktif karakter: {active["name"]}</div>', unsafe_allow_html=True)
    if not config.has_key(ss.cfg["provider"]):
        st.warning("API anahtarı bulunamadı. Ayarlar sayfasına bak.")

VIEWS[ss.page].render()
