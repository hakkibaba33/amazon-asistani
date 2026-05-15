import streamlit as st
import requests
import base64
from fpdf import FPDF

# --- API AYARLARI ---
# ÖNEMLİ: Eğer Streamlit Secrets kullanıyorsan alttaki satırı aktif et:
# API_KEY = st.secrets["GEMINI_KEY"]
# Şimdilik senin anahtarını direkt buraya tanımlıyorum:
API_KEY = "AIzaSyD2Dz4eG1yZaQUMCl1v7hEur_zis1w-7RA".strip()
MODEL_NAME = "models/gemini-1.5-flash"

# PDF OLUŞTURMA FONKSİYONU
def pdf_olustur(mesaj, karar, cevap):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, txt="Amazon Islem Formu", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Helvetica", size=12)
        def temizle(metin):
            return str(metin).encode('ascii', 'ignore').decode('ascii')

        pdf.cell(0, 10, txt=f"Karar: {temizle(karar)}", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt=f"Musteri Mesaji Ozeti: {temizle(mesaj[:100])}")
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, txt="Hazirlanan Cevap:", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 5, txt=temizle(cevap))
        
        return bytes(pdf.output())
    except Exception as e:
        return None

# ANA ASİSTAN FONKSİYONU
def amazon_asistani(musteri_mesaji, aksiyon, ton, fotograf=None):
    image_part = []
    if fotograf is not None:
        image_data = base64.b64encode(fotograf.read()).decode("utf-8")
        image_part = [{"inline_data": {"mime_type": "image/jpeg", "data": image_data}}]

    talimat = f"""
    Sen profesyonel bir Amazon satıcı asistanısın.
    Müşteri Mesajı: '{musteri_mesaji}'
    Alınacak Karar: '{aksiyon}'
    Cevap Tonu: '{ton}'
    
    GÖREVİN:
    1. Eğer fotoğraf varsa analiz et. 
    2. Müşterinin dilinde profesyonel bir cevap yaz.
    3. Altına 'TÜRKÇE ÖZET:' ekle.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": talimat}] + image_part}]}
    
    try:
        r = requests.post(url, json=payload)
        response_json = r.json()
        if 'candidates' in response_json:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"API Hatası: {response_json.get('error', {}).get('message', 'Bilinmeyen hata')}"
    except Exception as e:
        return f"Bağlantı Hatası: {e}"

# --- ARAYÜZ (GÖRSEL) ---
st.set_page_config(page_title="Amazon Operasyon Merkezi", layout="wide")
st.title("📦 Amazon Operasyon & PDF Merkezi")

if 'cevap_gecmisi' not in st.session_state:
    st.session_state.cevap_gecmisi = ""

col1, col2 = st.columns([1, 1])

with col1:
    mesaj = st.text_area("Müşteri Mesajı:", height=200, placeholder="Mesajı buraya yapıştırın...")
    yuklenen_dosya = st.file_uploader("Fotoğraf Yükle (Opsiyonel):", type=["jpg", "png", "jpeg"])
    
with col2:
    karar = st.selectbox("Aksiyon:", ["İadeyi Kabul Et", "Hasar Kanıtı İste", "İndirim Teklif Et", "Kargo Bilgisi Ver"])
    ton = st.select_slider("Cevap Tonu:", options=["Nazik", "Profesyonel", "Resmi"])
    
    if st.button("🚀 İşlemi Başlat", use_container_width=True):
        if mesaj:
            with st.spinner('Analiz ediliyor...'):
                st.session_state.cevap_gecmisi = amazon_asistani(mesaj, karar, ton, yuklenen_dosya)
        else:
            st.warning("Lütfen bir mesaj girin.")

if st.session_state.cevap_gecmisi:
    st.markdown("---")
    st.subheader("🤖 Hazırlanan Yanıt")
    st.info(st.session_state.cevap_gecmisi)
    
    pdf_data = pdf_olustur(mesaj, karar, st.session_state.cevap_gecmisi)
    if pdf_data:
        st.download_button(
            label="📄 İşlem Formunu PDF İndir",
            data=pdf_data,
            file_name="amazon_form.pdf",
            mime="application/pdf",
            use_container_width=True
        )
