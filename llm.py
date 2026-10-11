"""Model çağrıları ve prompt'lar."""
from config import get_client

LENGTH = {
    "Kısa": "Cevapların 1-2 cümleyi geçmesin.",
    "Orta": "Cevapların 2-4 cümleyi geçmesin.",
    "Uzun": "Cevapların 5-8 cümle olabilir, daha ayrıntılı anlat.",
}

RULES = (
    "Genel kurallar:\n"
    "- Daima Türkçe konuş ve asla karakterden çıkma.\n"
    "- Yapay zeka olduğunu söyleme; kendi dünyanın içinden cevap ver.\n"
    "- Karakterin bilmeyeceği modern şeyleri kendi dünyasına uyarlayarak yorumla."
)


def chat_system(char, length):
    return f"{char['prompt']}\n\n{RULES}\n- {LENGTH[length]}"


MODES = {
    "Konu anlatımı": {
        "rules": "Konuyu küçük parçalara bölerek, sırayla anlat. Her parçanın sonunda kısa bir anlama kontrolü sorusu sor ve cevabı bekle.",
        "opener": "Derse başla: kısa bir girişle konuyu tanıt, ilk küçük parçayı anlat ve bir kontrol sorusu sor.",
    },
    "Quiz (soru-cevap)": {
        "rules": (
            "Öğrenciye tek seferde yalnızca BİR soru sor. Cevabı değerlendir: doğruysa kısaca pekiştir, "
            "yanlışsa doğrusunu nazikçe açıkla, sonra bir sonraki soruya geç. Zorluğu yavaş yavaş artır "
            "ve arada kaç doğru yaptığını söyle."
        ),
        "opener": "Quiz'e başla: kısa bir giriş yap ve ilk soruyu sor.",
    },
    "Feynman yöntemi (ben anlatayım)": {
        "rules": (
            "Öğrenci konuyu kendi cümleleriyle sana anlatacak. Sen meraklı bir öğrenci gibi eksik ve yanlış yerleri "
            "sorularla yakala. Doğru cevabı hemen verme, önce yönlendir; öğrenci takılırsa ipucu ver."
        ),
        "opener": "Öğrenciden konuyu kendi cümleleriyle anlatmasını iste ve nereden başlayabileceği konusunda küçük bir ipucu ver.",
    },
    "Sınav öncesi hızlı tekrar": {
        "rules": "Önce konunun en önemli noktalarını kısa maddelerle özetle, sonra hızlı tekrar soruları sor. Tek tek ilerle.",
        "opener": "Konunun en önemli noktalarını kısa maddelerle özetle ve ilk hızlı tekrar sorusunu sor.",
    },
}

LEVELS = ["Ortaokul", "Lise", "Üniversite", "İleri seviye"]


def study_system(char, study):
    notes = study["notes"].strip()[:12000]
    notes_block = (
        f"\n\nÖğrencinin ders notları (önce bunlara dayan; notlarda olmayan bir şey sorulursa bunu belirt):\n---\n{notes}\n---"
        if notes
        else ""
    )
    return (
        f"{char['prompt']}\n\n"
        f"Şu an bir öğretmen/çalışma arkadaşı rolündesin. Konu: {study['topic'] or 'öğrencinin notları'}. "
        f"Öğrenci seviyesi: {study['level']}.\n"
        f"Yöntem: {MODES[study['mode']]['rules']}\n\n"
        "Kurallar:\n"
        "- Karakterinin üslubunu ve kişiliğini koru ama doğruluktan ve öğretici olmaktan ödün verme.\n"
        "- Emin olmadığın bir şeyi uydurma; bilmediğini söyle.\n"
        "- Daima Türkçe konuş. Kısa paragraflar ve gerekirse sade madde işaretleri kullan.\n"
        "- Cevapların en fazla 8-10 cümle olsun."
        f"{notes_block}"
    )


def _clean(messages):
    return [{"role": m["role"], "content": m["content"]} for m in messages]


def stream_reply(cfg, system, messages):
    client = get_client(cfg["provider"])
    history = _clean(messages)[-int(cfg["memory"]):]
    stream = client.chat.completions.create(
        model=cfg["model"],
        messages=[{"role": "system", "content": system}] + history,
        temperature=cfg["temperature"],
        stream=True,
    )
    for part in stream:
        if part.choices and part.choices[0].delta.content:
            yield part.choices[0].delta.content


def complete(cfg, system, user):
    client = get_client(cfg["provider"])
    r = client.chat.completions.create(
        model=cfg["model"],
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.8,
    )
    return (r.choices[0].message.content or "").strip()


def friendly_error(e):
    t = str(e).lower()
    if "insufficient_quota" in t or "credit" in t:
        return "Hesapta kredi yok. Ayarlar'dan başka bir sağlayıcı seç ya da kredi yükle."
    if "model_not_found" in t or "does not exist" in t:
        return "Bu model bulunamadı. Ayarlar'dan model adını güncelle (Groq için openai/gpt-oss-120b dene)."
    if "401" in t or "invalid_api_key" in t or "incorrect api key" in t:
        return "API anahtarı geçersiz. .env dosyasındaki anahtarı kontrol et."
    if "429" in t or "rate" in t:
        return "İstek sınırına takıldın. Birkaç saniye bekleyip tekrar dene."
    if "bulunamadı" in t:
        return str(e)
    return f"Bir hata oluştu: {e}"
