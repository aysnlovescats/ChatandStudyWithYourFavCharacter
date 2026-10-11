"""Karakterle ders çalışma ekranı."""
import html

import streamlit as st

import characters as C
import images
import llm
import state
import styles

QUICK = {
    "Beni test et": "Beni bu konudan 3 soruyla test et. Soruları tek tek sor.",
    "Özetle": "Şimdiye kadar anlattıklarını kısa maddelerle özetle.",
    "Flashcard çıkar": "Bu konudan 5 flashcard çıkar (her biri için ön yüz: soru, arka yüz: cevap).",
    "Daha basit anlat": "Bunu daha basit, günlük hayattan örneklerle tekrar anlat.",
}


def _read_upload(f):
    name = f.name.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        return "\n".join((p.extract_text() or "") for p in PdfReader(f).pages)
    return f.getvalue().decode("utf-8", errors="ignore")


def _start():
    ss = st.session_state
    notes = ss.get("st_notes", "")
    f = ss.get("st_file")
    if f is not None:
        try:
            notes = (notes + "\n\n" + _read_upload(f)).strip()
        except Exception as e:
            ss.study_error = f"Dosya okunamadı: {e}"
            return
    topic = ss.get("st_topic", "").strip()
    if not topic and not notes:
        ss.study_error = "Bir konu yaz ya da not ekle."
        return
    ss.study = {
        "char": ss["st_char"],
        "topic": topic,
        "level": ss["st_level"],
        "mode": ss["st_mode"],
        "notes": notes,
        "messages": [],
    }


def _new_lesson():
    st.session_state.study = None


def _quick(text):
    st.session_state.study_pending = text


def _setup(chars):
    ss = st.session_state
    styles.title("Ders çalış", "Bir karakter seç, konuyu yaz; ders onun üslubuyla ilerlesin.")
    if err := ss.pop("study_error", None):
        st.error(err)

    if ss.get("st_char") not in chars:
        ss["st_char"] = ss.active if ss.active in chars else next(iter(chars))
    ss.setdefault("st_level", llm.LEVELS[1])
    ss.setdefault("st_mode", list(llm.MODES)[0])

    c1, c2 = st.columns(2)
    c1.selectbox(
        "Hocan kim olsun?",
        list(chars),
        key="st_char",
        format_func=lambda i: chars[i]["name"],
    )
    c2.text_input("Konu", key="st_topic", placeholder="Örn. Fotosentez, Newton yasaları, SQL join...")
    c3, c4 = st.columns(2)
    c3.selectbox("Seviye", llm.LEVELS, key="st_level")
    c4.selectbox("Çalışma biçimi", list(llm.MODES), key="st_mode")
    st.text_area("Ders notların (isteğe bağlı)", key="st_notes", height=140,
                 placeholder="Notlarını buraya yapıştır; karakter önce bunlara dayansın.")
    st.file_uploader("veya not dosyası yükle (.txt, .md, .pdf)", type=["txt", "md", "pdf"], key="st_file")
    st.button("Dersi başlat", type="primary", on_click=_start)


def _generate(char, study, system):
    ss = st.session_state
    msgs = study["messages"]
    with st.chat_message("assistant", avatar=images.chat_avatar(char)):
        try:
            reply = st.write_stream(llm.stream_reply(ss.cfg, system, msgs))
        except Exception as e:
            msgs.pop()
            st.error(llm.friendly_error(e))
            return
    msgs.append({"role": "assistant", "content": reply or "..."})


def render():
    ss = st.session_state
    chars = C.all_characters()
    study = ss.study

    if not study or study["char"] not in chars:
        ss.study = None
        _setup(chars)
        return

    char = chars[study["char"]]
    msgs = study["messages"]
    system = llm.study_system(char, study)

    h1, h2 = st.columns([1, 6])
    with h1:
        st.markdown(images.avatar_html(char, 96, thumb=True), unsafe_allow_html=True)
    with h2:
        topic = study["topic"] or "Notlarım"
        st.markdown(
            f'<div class="page-title">{html.escape(topic)}</div>'
            f'<div class="char-uni">Hoca: {html.escape(char["name"])}</div>'
            f'<div class="char-tag">{html.escape(study["mode"])}, {html.escape(study["level"])}</div>',
            unsafe_allow_html=True,
        )

    q = st.columns(4)
    for col, (label, text) in zip(q, QUICK.items()):
        col.button(label, key=f"q_{label}", on_click=_quick, args=(text,))
    m1, m2, _ = st.columns([1, 1, 2])
    m1.button("Yeni ders", on_click=_new_lesson)
    transcript = "\n\n".join(
        f"{'Sen' if m['role'] == 'user' else char['name']}: {m['content']}"
        for m in msgs
        if not m.get("hidden")
    )
    m2.download_button("Notları indir", transcript, file_name="ders-notlari.txt")

    bot_avatar = images.chat_avatar(char)
    for m in msgs:
        if m.get("hidden"):
            continue
        with st.chat_message(m["role"], avatar=bot_avatar if m["role"] == "assistant" else "user"):
            st.write(m["content"])

    if not msgs:
        msgs.append({"role": "user", "content": llm.MODES[study["mode"]]["opener"], "hidden": True})
        _generate(char, study, system)
        if msgs and msgs[-1]["role"] == "assistant":
            st.rerun()
        return

    prompt = st.chat_input("Sorunu yaz ya da cevabını gönder...") or ss.pop("study_pending", None)
    if prompt:
        msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="user"):
            st.write(prompt)
        _generate(char, study, system)
