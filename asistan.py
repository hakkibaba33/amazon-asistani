import streamlit as st
import requests
import base64

# API AYARLARI
API_KEY = "BURAYA_YENI_ALDIĞIN_ANAHTARI_YAPISTIR".strip()
MODEL_NAME = "models/gemini-1.5-flash"

def amazon_asistani(musteri_mesaji, aksiyon, ton, fotograf=None):
    # Fotoğraf varsa işle
    image_part = []
    if fotograf is not None:
        image_data = base64.b64encode(fotograf.read()).decode("utf-8")
        image_part = [{"inline_data": {"mime_type": "image/jpeg", "data": image_data}}]

    talimat = f"""
    Sen profesyonel bir Amazon satıcı asistanısın.
    Müşteri Mesajı: '{musteri_mesaji}'
    Senin Kararın: '{aksiyon}'
    Cevap Tonu: '{ton}'
    
    GÖREVİN:
    1. Eğer bir fotoğraf yüklendiyse, fotoğraftaki hasarı veya durumu analiz et ve cevaba dahil et.
    2. Müşteriye kendi dilinde '{ton}' bir tonda profesyonel cevap yaz.
    3. Cevabın altına "TÜRKÇE ÖZET:" başlığıyla ne yazdığını kısaca açıkla.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
    
    # Metin ve görseli birleştir
    contents = [{"parts": [{"text": talimat}] + image_part}]
    payload = {"contents": contents}
    
    try:
        r = requests.post(url, json=payload)
        sonuc = r.json()
        return sonuc['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Hata oluştu: {e}"

# --- ARAYÜZ (UI) ---
st.set_page_config(page_title="Amazon Pro Asistan", page_icon="📦", layout="wide")

st.title("📦 Amazon Satıcı Operasyon Merkezi")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Müşteri Bilgileri")
    mesaj = st.text_area("Müşteri Mesajı:", placeholder="Buraya mesajı yapıştırın...", height=200)
    yuklenen_dosya = st.file_uploader("Ürün Fotoğrafı (Opsiyonel):", type=["jpg", "png", "jpeg"])
    
with col2:
    st.subheader("⚙️ Aksiyon ve Ton")
    karar = st.selectbox("Alınacak Aksiyon:", 
                         ["İadeyi Kabul Et", "Hasar Kanıtı İste", "Kısmi İade/İndirim Teklif Et", "Ürünü Yeniden Gönder"])
    
    ton = st.select_slider("Cevap Tonu:", 
                           options=["Çok Nazik", "Profesyonel", "Resmi ve Mesafeli"])
    
    st.write("---")
    if st.button("🚀 Akıllı Cevap Oluştur", use_container_width=True):
        if mesaj:
            with st.spinner('Yapay zeka analiz ediyor ve yazıyor...'):
                cevap = amazon_asistani(mesaj, karar, ton, yuklenen_dosya)
                st.success("İşlem Tamamlandı!")
                st.markdown(cevap)
        else:
            st.warning("Lütfen en azından bir müşteri mesajı girin.")

st.sidebar.info("Bu asistan Gemini 1.5 Flash altyapısını kullanır ve görsel analiz yeteneğine sahiptir.")
