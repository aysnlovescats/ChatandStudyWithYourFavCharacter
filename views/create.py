"""Yeni karakter ekleme ekranı."""
import html

import streamlit as st

import characters as C
import images
import llm
import state
import styles


def _k(name):
    return f"{name}_{st.session_state.form_n}"


def _gen_persona():
    ss = st.session_state
    name = ss.get(_k("new_name"), "").strip()
    if not name:
        ss.create_error = "Önce karakterin adını yaz."
        return
    uni = ss.get(_k("new_universe"), "").strip()
    try:
        text = llm.complete(
            ss.cfg,
            "Rol yapma botları için karakter tanımı yazarsın. Türkçe, 4-5 cümle, ikinci tekil şahısla ('Sen ...sın') yaz: "
            "kişilik, konuşma tarzı, değerler ve küçük huylar. Yalnızca tanımı yaz.",
            f"Karakter: {name}" + (f" ({uni})" if uni else ""),
        )
        ss[_k("new_persona")] = text
    except Exception as e:
        ss.create_error = llm.friendly_error(e)


def _save():
    ss = st.session_state
    name = ss.get(_k("new_name"), "").strip()
    persona = ss.get(_k("new_persona"), "").strip()
    if not name or not persona:
        ss.create_error = "Ad ve kişilik alanları boş olamaz."
        return
    cid = C.slugify(name)
    char = {
        "id": cid,
        "name": name,
        "universe": ss.get(_k("new_universe"), "").strip() or "Özel karakter",
        "tagline": ss.get(_k("new_tagline"), "").strip() or "Senin yarattığın karakter",
        "greeting": ss.get(_k("new_greeting"), "").strip() or f"Merhaba, ben {name}.",
        "prompt": f"Sen {name} karakterisin. {persona}",
        "wiki": ss.get(_k("new_wiki"), "").strip() or None,
        "image_url": ss.get(_k("new_url"), "").strip() or None,
    }
    C.add_custom(char)
    up = ss.get(_k("new_img"))
    if up is not None:
        images.save_upload(cid, up)
    ss.flash = f"{name} eklendi! Karakterler sayfasında seni bekliyor."
    ss.form_n += 1


def _delete(cid):
    ss = st.session_state
    C.delete_custom(cid)
    ss.chats.pop(cid, None)
    if ss.active == cid:
        ss.active = None


def render():
    ss = st.session_state
    styles.title("Karakter ekle", "Sevdiğin bir karakteri ekle; kişiliğini sen yaz ya da yapay zekâya bırak.")
    if msg := ss.pop("flash", None):
        st.success(msg)
    if err := ss.pop("create_error", None):
        st.error(err)

    c1, c2 = st.columns(2)
    c1.text_input("Karakter adı", key=_k("new_name"))
    c2.text_input("Nereden? (dizi, kitap, anime...)", key=_k("new_universe"))
    st.text_input("Kısa slogan", key=_k("new_tagline"))
    st.text_area("Kişilik ve konuşma tarzı", key=_k("new_persona"), height=140,
                 placeholder="Nasıl biri? Nasıl konuşur? Nelere tepki verir?")
    st.button("Kişiliği yapay zekâ yazsın", on_click=_gen_persona)
    st.text_input("İlk cümlesi (boşsa otomatik)", key=_k("new_greeting"))

    st.markdown("**Resim** (üçünden birini kullanabilirsin)")
    st.file_uploader("Bilgisayardan yükle", type=list(images.EXTS), key=_k("new_img"))
    r1, r2 = st.columns(2)
    r1.text_input("veya Wikipedia sayfa başlığı", key=_k("new_wiki"), placeholder="Örn. Sasuke_Uchiha")
    r2.text_input("veya resim linki", key=_k("new_url"), placeholder="https://...")
    st.button("Karakteri ekle", type="primary", on_click=_save)

    customs = C.load_custom()
    if customs:
        st.divider()
        st.subheader("Eklediklerin")
        for c in customs:
            a, b, d = st.columns([1, 6, 2])
            a.markdown(images.avatar_html(c, 56, thumb=True), unsafe_allow_html=True)
            b.markdown(f"**{html.escape(c['name'])}**  \n{html.escape(c.get('universe', ''))}")
            d.button("Sil", key=f"del_{c['id']}", on_click=_delete, args=(c["id"],))
