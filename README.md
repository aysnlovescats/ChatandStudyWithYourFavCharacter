# Karakter Sohbeti

Kitap, dizi ve anime karakterleriyle sohbet edebildiğin, onlarla ders çalışabildiğin bir Streamlit uygulaması. Karakterin kişiliği system prompt ile tanımlanır; cevaplar bir LLM tarafından (Groq ya da OpenAI) üretilir.

**Özellikler**
- Karakter kartları, arama ve favoriler
- Karakterle sohbet, sohbeti indirme
- Ders çalışma modu: konu anlatımı, quiz, Feynman yöntemi, hızlı tekrar; notlarını (.txt, .md, .pdf) yükleyebilirsin
- Kendi karakterini ekleme (kişiliği yapay zekâ yazabilir)
- Groq ve OpenAI desteği

**Kurulum**
1. `pip install -r requirements.txt`
2. `.env.example` dosyasını `.env` olarak kopyala ve API anahtarını yaz
3. `streamlit run app.py`
