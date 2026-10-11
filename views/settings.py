"""Ayarlar ekranı."""
import streamlit as st

import characters as C
import config
import images
import llm
import state
import styles


def _set(key, wkey):
    st.session_state.cfg[key] = st.session_state[wkey]
    state.save_cfg()


def _provider_changed():
    ss = st.session_state
    ss.cfg["provider"] = ss["w_provider"]
    ss.cfg["model"] = config.PROVIDERS[ss["w_provider"]]["model"]
    ss["w_model"] = ss.cfg["model"]
    state.save_cfg()


def _test():
    ss = st.session_state
    try:
        out = llm.complete(ss.cfg, "Kısa cevap ver.", "Sadece 'tamam' yaz.")
        ss.api_test = ("ok", f"Bağlantı çalışıyor. Model cevabı: {out[:40]}")
    except Exception as e:
        ss.api_test = ("err", llm.friendly_error(e))


def _save_image():
    ss = st.session_state
    up = ss.get("img_up")
    if up is None:
        ss.img_msg = ("err", "Önce bir resim seç.")
        return
    images.save_upload(ss["img_char"], up)
    ss.img_msg = ("ok", "Resim kaydedildi.")


def _clear_chats():
    st.session_state.chats = {}
    st.session_state.study = None


def render():
    ss = st.session_state
    cfg = ss.cfg
    styles.title("Ayarlar", "Model, üslup ve resimler.")

    st.subheader("Model")
    ss.setdefault("w_provider", cfg["provider"])
    ss.setdefault("w_model", cfg["model"])
    ss.setdefault("w_temp", cfg["temperature"])
    ss.setdefault("w_len", cfg["length"])
    ss.setdefault("w_mem", cfg["memory"])

    st.selectbox("Sağlayıcı", list(config.PROVIDERS), key="w_provider", on_change=_provider_changed)
    st.text_input("Model adı", key="w_model", on_change=_set, args=("model", "w_model"))
    st.caption(
        "API anahtarı: "
        + ("bulundu" if config.has_key(cfg["provider"]) else f".env içinde {config.PROVIDERS[cfg['provider']]['env']} yok")
    )
    st.button("Bağlantıyı test et", on_click=_test)
    if res := ss.get("api_test"):
        (st.success if res[0] == "ok" else st.error)(res[1])

    st.subheader("Üslup")
    st.slider("Yaratıcılık", 0.0, 1.5, step=0.1, key="w_temp", on_change=_set, args=("temperature", "w_temp"))
    st.radio("Cevap uzunluğu (sohbet)", list(llm.LENGTH), key="w_len", horizontal=True,
             on_change=_set, args=("length", "w_len"))
    st.slider("Hafıza (modele gönderilen son mesaj sayısı)", 4, 40, key="w_mem",
              on_change=_set, args=("memory", "w_mem"))

    st.subheader("Karakter resimleri")
    chars = C.all_characters()
    ss.setdefault("img_char", next(iter(chars)))
    if ss["img_char"] not in chars:
        ss["img_char"] = next(iter(chars))
    st.selectbox("Karakter", list(chars), key="img_char", format_func=lambda i: chars[i]["name"])
    st.file_uploader("Resim yükle (mevcut resmin yerine geçer)", type=list(images.EXTS), key="img_up")
    st.button("Resmi kaydet", on_click=_save_image)
    if res := ss.pop("img_msg", None):
        (st.success if res[0] == "ok" else st.error)(res[1])
    st.button("İndirilen resim önbelleğini temizle", on_click=images.clear_cache)
    st.caption("İpucu: assets/ klasörüne karakter-kimligi.jpg adıyla resim atmak da yeterli (örn. assets/cassius-au-bellona.jpg).")

    st.subheader("Veriler")
    st.button("Tüm sohbetleri ve dersi sil", on_click=_clear_chats)
