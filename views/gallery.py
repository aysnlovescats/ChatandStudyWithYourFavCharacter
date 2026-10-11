"""Karakter kartları ekranı."""
import html

import streamlit as st

import characters as C
import images
import state
import styles


def _card(char):
    st.markdown(
        '<div class="char-card">'
        f"{images.avatar_html(char, 260)}"
        '<div class="char-body">'
        f'<div class="char-name">{html.escape(char["name"])}</div>'
        f'<div class="char-uni">{html.escape(char.get("universe", ""))}</div>'
        f'<div class="char-tag">{html.escape(char.get("tagline", ""))}</div>'
        "</div></div>",
        unsafe_allow_html=True,
    )


def _suggestion(chars):
    cid = st.session_state.suggested
    char = C.lookup(cid) if cid else None
    if not char:
        return
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown(images.avatar_html(char, 200), unsafe_allow_html=True)
    with c2:
        st.markdown(
            '<div class="suggest-box"><div class="suggest-label">Sana bir öneri</div>'
            f'<div class="char-name">{html.escape(char["name"])}</div>'
            f'<div class="char-uni">{html.escape(char.get("universe", ""))}</div>'
            f'<div class="char-tag">{html.escape(char.get("tagline", ""))}</div></div>',
            unsafe_allow_html=True,
        )
        b1, b2, b3 = st.columns(3)
        if cid in chars:
            b1.button("Konuş", key="sg_chat", type="primary", on_click=state.start_chat, args=(cid,))
        else:
            b1.button("Ekle ve konuş", key="sg_add", type="primary", on_click=state.add_and_chat, args=(cid,))
        b2.button("Başka öner", key="sg_next", on_click=state.roll)
        b3.button("Kapat", key="sg_close", on_click=state.close_suggestion)
    st.divider()


def render():
    styles.title("Karakterler", "Kiminle konuşmak ya da ders çalışmak istersin?")
    chars = C.all_characters()
    favs = C.load_favs()

    _suggestion(chars)

    f1, f2 = st.columns([3, 1])
    q = f1.text_input("Karakter ara", key="gal_q", placeholder="İsim, dizi ya da kitap yaz")
    only_fav = f2.toggle("Sadece favoriler", key="gal_fav")

    items = [
        c
        for c in chars.values()
        if (not q or q.lower() in f'{c["name"]} {c.get("universe", "")} {c.get("tagline", "")}'.lower())
        and (not only_fav or c["id"] in favs)
    ]
    if not items:
        st.info("Eşleşen karakter yok. Sol menüden yeni karakter ekleyebilir ya da rastgele öneri alabilirsin.")
        return

    for i in range(0, len(items), 3):
        cols = st.columns(3)
        for col, ch in zip(cols, items[i : i + 3]):
            cid = ch["id"]
            with col:
                _card(ch)
                b1, b2, b3 = st.columns([2, 2, 3])
                b1.button("Konuş", key=f"c_{cid}", type="primary", on_click=state.start_chat, args=(cid,))
                b2.button("Ders", key=f"s_{cid}", on_click=state.start_study, args=(cid,))
                b3.button("Favoride" if cid in favs else "Favori", key=f"f_{cid}",
                          on_click=state.toggle_fav, args=(cid,))
