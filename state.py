"""Oturum durumu ve sayfa geçişleri."""
import streamlit as st

import characters as C
from storage import load_json, save_json

DEFAULT_CFG = {
    "provider": "Groq (ücretsiz)",
    "model": "openai/gpt-oss-120b",
    "temperature": 0.9,
    "length": "Orta",
    "memory": 20,
}


def init_state():
    ss = st.session_state
    if "cfg" not in ss:
        ss.cfg = {**DEFAULT_CFG, **load_json("settings.json", {})}
    ss.setdefault("page", "gallery")
    ss.setdefault("active", None)
    ss.setdefault("chats", {})
    ss.setdefault("study", None)
    ss.setdefault("suggested", None)
    ss.setdefault("form_n", 0)


def save_cfg():
    save_json("settings.json", st.session_state.cfg)


def go(page):
    st.session_state.page = page


def ensure_chat(cid):
    ss = st.session_state
    if cid not in ss.chats:
        char = C.lookup(cid)
        ss.chats[cid] = [{"role": "assistant", "content": char["greeting"]}]


def reset_chat(cid):
    st.session_state.chats.pop(cid, None)
    ensure_chat(cid)


def start_chat(cid):
    ss = st.session_state
    ss.active = cid
    ensure_chat(cid)
    ss.page = "chat"


def start_study(cid):
    ss = st.session_state
    if ss.study and ss.study["char"] != cid:
        ss.study = None
    ss["st_char"] = cid
    ss.page = "study"


def add_and_chat(cid):
    C.add_custom(dict(C.lookup(cid)))
    start_chat(cid)


def roll():
    ss = st.session_state
    ss.suggested = C.random_pick()["id"]
    ss.page = "gallery"


def close_suggestion():
    st.session_state.suggested = None


def toggle_fav(cid):
    C.toggle_fav(cid)
