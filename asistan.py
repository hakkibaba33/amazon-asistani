import streamlit as st
import requests
import base64
from fpdf import FPDF

# API AYARLARI
API_KEY = "BURAYA_API_ANAHTARINI_YAPISTIR".strip()
MODEL_NAME = "models/gemini-1.5-flash"

# PDF OLUŞTURMA FONKSİYONU
def pdf_olustur(mesaj, karar, cevap):
    pdf = FPDF()
    pdf.add_page()
    
    # Başlık
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Amazon Islem Formu", ln=True, align='C')
    pdf.ln(10)
    
    # İçerik
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Karar: {karar}", ln=True)
    pdf.ln(5)
    
    pdf.multi_cell(0, 10, txt=f"Musteri Mesaji: {mesaj[:100]}...") # Mesajın özeti
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Hazirlanan Cevap:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 5, txt=cevap.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')

def amazon_asistani(musteri_mesaji, aksiyon, ton, fotograf=None):
    image_part = []
    if fotograf is not None:
        image_data = base64.b64encode(fotograf.read()).decode("utf-8")
        image_part = [{"inline_data": {"mime_type": "image/jpeg", "data": image_data}}]

    talimat = f"Müşteri Mesajı: {musteri_mesaji}\nKarar: {aksiyon}\nTon: {ton}\nProfesyonel cevap yaz ve altına Türkçe özet ekle."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
    contents = [{"parts": [{"text": talimat}] + image_part}]
    
    try:
        r = requests.post(url, json={"contents": contents})
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Bir hata oluştu."

# --- ARAYÜZ ---
st.set_page_config(page_title="Amazon Pro Asistan", layout="wide")
st.title("📦 Amazon Operasyon & PDF Merkezi")

col1, col2 = st.columns([1, 1])

with col1:
    mesaj = st.text_area("Müşteri Mesajı:", height=200)
    yuklenen_dosya = st.file_uploader("Ürün Fotoğrafı:", type=["jpg", "png"])
    
with col2:
    karar = st.selectbox("Aksiyon:", ["İadeyi Kabul Et", "Hasar Kanıtı İste", "İndirim Teklif Et"])
    ton = st.select_slider("Ton:", options=["Nazik", "Profesyonel", "Resmi"])
    
    if st.button("🚀 İşlemi Başlat", use_container_width=True):
        if mesaj:
            st.session_state.cevap = amazon_asistani(mesaj, karar, ton, yuklenen_dosya)
        else:
            st.warning("Mesaj giriniz.")

# Sonuç ve PDF İndirme Alanı
if 'cevap' in st.session_state:
    st.markdown("---")
    st.subheader("Hazırlanan Yanıt")
    st.info(st.session_state.cevap)
    
    # PDF OLUŞTURMA BUTONU
    pdf_data = pdf_olustur(mesaj, karar, st.session_state.cevap)
    st.download_button(
        label="📄 İade/İşlem Formunu PDF Olarak İndir",
        data=pdf_data,
        file_name="amazon_islem_formu.pdf",
        mime="application/pdf",
        use_container_width=True
    )
