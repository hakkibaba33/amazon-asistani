import streamlit as st
import requests
import base64
from fpdf import FPDF  # fpdf2 kütüphanesini kullanır

# API AYARLARI
API_KEY = st.secrets["GEMINI_KEY"]
MODEL_NAME = "models/gemini-1.5-flash"

# PDF OLUŞTURMA FONKSİYONU
def pdf_olustur(mesaj, karar, cevap):
    pdf = FPDF()
    pdf.add_page()
    
    # Standart bir font kullanalım
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, txt="Amazon Islem Formu", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Helvetica", size=12)
    # Karakter hatasını önlemek için temizleme fonksiyonu
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
    
    # --- KRİTİK DEĞİŞİKLİK BURADA: bytes() ekledik ---
    return bytes(pdf.output())

# YANIT OLUŞTURMA FONKSİYONU
def amazon_asistani(musteri_mesaji, aksiyon, ton, fotograf=None):
    image_part = []
    if fotograf is not None:
        image_data = base64.b64encode(fotograf.read()).decode("utf-8")
        image_part = [{"inline_data": {"mime_type": "image/jpeg", "data": image_data}}]

    talimat = f"Müşteri Mesajı: {musteri_mesaji}\nKarar: {aksiyon}\nTon: {ton}\nProfesyonel bir cevap yaz ve altına Türkçe özet ekle."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
    contents = [{"parts": [{"text": talimat}] + image_part}]
    
    try:
        r = requests.post(url, json={"contents": contents})
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Bir hata oluştu. API anahtarını veya bağlantını kontrol et."

# --- ARAYÜZ ---
st.set_page_config(page_title="Amazon Pro Asistan", layout="wide")
st.title("📦 Amazon Operasyon & PDF Merkezi")

if 'cevap' not in st.session_state:
    st.session_state.cevap = ""

col1, col2 = st.columns([1, 1])

with col1:
    mesaj = st.text_area("Müşteri Mesajı:", height=200, placeholder="Müşteriden gelen mesajı buraya yapıştırın...")
    yuklenen_dosya = st.file_uploader("Ürün Fotoğrafı (Opsiyonel):", type=["jpg", "png", "jpeg"])
    
with col2:
    karar = st.selectbox("Aksiyon:", ["Iadeyi Kabul Et", "Hasar Kaniti Iste", "Indirim Teklif Et"])
    ton = st.select_slider("Ton:", options=["Nazik", "Profesyonel", "Resmi"])
    
    if st.button("🚀 İşlemi Başlat", use_container_width=True):
        if mesaj:
            with st.spinner('Yapay zeka analiz ediyor...'):
                st.session_state.cevap = amazon_asistani(mesaj, karar, ton, yuklenen_dosya)
        else:
            st.warning("Lütfen bir müşteri mesajı girin.")

# SONUÇ EKRANI VE İNDİRME BUTONU
if st.session_state.cevap:
    st.markdown("---")
    st.subheader("Hazırlanan Yanıt")
    st.info(st.session_state.cevap)
    
    try:
        # PDF verisini alıyoruz
        pdf_data = pdf_olustur(mesaj, karar, st.session_state.cevap)
        
        st.download_button(
            label="📄 İşlem Formunu PDF İndir",
            data=pdf_data,  # Burası artık 'bytes' formatında olduğu için hata vermeyecek
            file_name="amazon_islem_formu.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"PDF oluşturulurken bir hata oluştu: {e}")
