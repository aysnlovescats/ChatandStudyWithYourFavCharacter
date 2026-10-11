"""Sohbet ekranı."""
import html

import streamlit as st

import characters as C
import images
import llm
import state
import styles


def _transcript(char, msgs):
    return "\n\n".join(
        f"{'Sen' if m['role'] == 'user' else char['name']}: {m['content']}" for m in msgs
    )


def render():
    ss = st.session_state
    chars = C.all_characters()
    cid = ss.active

    if cid not in chars:
        styles.title("Sohbet", "Önce bir karakter seçmen gerekiyor.")
        st.button("Karakterlere git", on_click=state.go, args=("gallery",))
        return

    char = chars[cid]
    state.ensure_chat(cid)
    msgs = ss.chats[cid]

    h1, h2 = st.columns([1, 6])
    with h1:
        st.markdown(images.avatar_html(char, 96, thumb=True), unsafe_allow_html=True)
    with h2:
        st.markdown(
            f'<div class="page-title">{html.escape(char["name"])}</div>'
            f'<div class="char-uni">{html.escape(char.get("universe", ""))}</div>'
            f'<div class="char-tag">{html.escape(char.get("tagline", ""))}</div>',
            unsafe_allow_html=True,
        )

    b1, b2, b3, b4 = st.columns(4)
    b1.button("Sohbeti sıfırla", on_click=state.reset_chat, args=(cid,))
    b2.download_button("İndir", _transcript(char, msgs), file_name=f"{cid}-sohbet.txt")
    b3.button("Bununla ders çalış", on_click=state.start_study, args=(cid,))
    b4.button("Karakter değiştir", on_click=state.go, args=("gallery",))

    bot_avatar = images.chat_avatar(char)
    for m in msgs:
        with st.chat_message(m["role"], avatar=bot_avatar if m["role"] == "assistant" else "user"):
            st.write(m["content"])

    if prompt := st.chat_input(f"{char['name']}'e bir şey söyle..."):
        msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="user"):
            st.write(prompt)
        system = llm.chat_system(char, ss.cfg["length"])
        with st.chat_message("assistant", avatar=bot_avatar):
            try:
                reply = st.write_stream(llm.stream_reply(ss.cfg, system, msgs))
            except Exception as e:
                msgs.pop()
                st.error(llm.friendly_error(e))
                return
        msgs.append({"role": "assistant", "content": reply or "..."})
