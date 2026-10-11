"""Karakter resimleri: önce assets/ klasörü, sonra Wikipedia/URL, yoksa emoji."""
import base64
import html
from pathlib import Path

import requests
import streamlit as st

ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)
EXTS = ("png", "jpg", "jpeg", "webp")
HEADERS = {"User-Agent": "talkwithchar/1.0 (ogrenci projesi)"}


def local_image(cid):
    for ext in EXTS:
        p = ASSETS / f"{cid}.{ext}"
        if p.exists():
            return p
    return None


def save_upload(cid, uploaded):
    ext = uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else "png"
    ext = ext if ext in EXTS else "png"
    for e in EXTS:
        old = ASSETS / f"{cid}.{e}"
        if old.exists():
            old.unlink()
    (ASSETS / f"{cid}.{ext}").write_bytes(uploaded.getvalue())


def _wiki_thumb(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    r = requests.get(url, headers=HEADERS, timeout=8)
    r.raise_for_status()
    data = r.json()
    img = data.get("thumbnail") or data.get("originalimage")
    return img["source"] if img else None


@st.cache_data(show_spinner=False)
def _fetch_remote(cid, wiki, image_url):
    """Resmi bir kez indirip assets/ içine kaydeder. Başarısızsa None döner."""
    try:
        url = image_url or (_wiki_thumb(wiki) if wiki else None)
        if not url:
            return None
        r = requests.get(url, headers=HEADERS, timeout=8)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "")
        ext = "png" if "png" in ctype else "webp" if "webp" in ctype else "jpg"
        path = ASSETS / f"{cid}.{ext}"
        path.write_bytes(r.content)
        return str(path)
    except Exception:
        return None


def clear_cache():
    _fetch_remote.clear()


def find_image(char):
    p = local_image(char["id"])
    if p:
        return p
    found = _fetch_remote(char["id"], char.get("wiki"), char.get("image_url"))
    return Path(found) if found else None


@st.cache_data(show_spinner=False)
def _data_uri(path, mtime):
    raw = Path(path).read_bytes()
    ext = Path(path).suffix.lstrip(".").lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return f"data:image/{mime};base64,{base64.b64encode(raw).decode()}"


def initials(char):
    return "".join(w[0] for w in char["name"].split()[:2]).upper()


def avatar_html(char, height=220, thumb=False):
    p = find_image(char)
    size = f"width:{height}px;height:{height}px;" if thumb else f"height:{height}px;"
    if p:
        uri = _data_uri(str(p), p.stat().st_mtime)
        cls = "char-thumb" if thumb else "char-img"
        return f'<img class="{cls}" src="{uri}" style="{size}">'
    cls = "char-ph-thumb" if thumb else "char-ph"
    fs = int(height * (0.38 if thumb else 0.34))
    return f'<div class="{cls}" style="{size}font-size:{fs}px;">{html.escape(initials(char))}</div>'


def chat_avatar(char):
    p = find_image(char)
    return str(p) if p else "assistant"
