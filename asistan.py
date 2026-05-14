import streamlit as st
import requests

# API ANAHTARIN (Değiştirme, bu haliyle kalsın)
API_KEY = "AIzaSyDlKJ6BWXEin7HvEccD3_nx-Wk1KuBu1f0".strip()

# 1. Google'dan senin için çalışan en doğru model adını bulan fonksiyon
def dogru_modeli_bul():
    versiyonlar = ["v1beta", "v1"]
    for v in versiyonlar:
        try:
            url = f"https://generativelanguage.googleapis.com/{v}/models?key={API_KEY}"
            res = requests.get(url).json()
            if "models" in res:
                for m in res["models"]:
                    if "generateContent" in m["supportedGenerationMethods"]:
                        return m["name"], v
        except:
            continue
    return None, None

# 2. Akıllı Amazon Asistanı Fonksiyonu
def amazon_asistani(musteri_mesaji, aksiyon, model_yolu, versiyon):
    # BURASI ÖNEMLİ: Talimatı güncelledik
    talimat = f"""
    Sen profesyonel bir Amazon satıcı asistanısın. 
    Müşteriden gelen mesaj şu dilde olabilir: Türkçe, İngilizce, İsveççe veya herhangi bir dil.
    
    Gelen Mesaj: '{musteri_mesaji}'
    Satıcının Kararı: '{aksiyon}'
    
    GÖREVİN:
    1. Gelen mesajın hangi dilde olduğunu tespit et.
    2. Müşteriye KENDİ DİLİNDE (örneğin İsveççe yazdıysa İsveççe) çok nazik ve profesyonel bir cevap yaz.
    3. Bu cevabın hemen altına, satıcının ne yazdığını anlaması için "TÜRKÇE ÇEVİRİ:" başlığıyla Türkçesini ekle.
    """
    
    url = f"https://generativelanguage.googleapis.com/{versiyon}/{model_yolu}:generateContent?key={API_KEY}"
    data = {"contents": [{"parts": [{"text": talimat}]}]}
    
    try:
        r = requests.post(url, json=data).json()
        return r['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Hata oluştu: {e}"

# --- ARAYÜZ (GÖRSEL KISIM) ---
st.set_page_config(page_title="Küresel Amazon Asistanı", page_icon="🌍")
st.title("🌍 Küresel Amazon Satıcı Paneli")
st.markdown("---")

# Arka planda model kontrolü
if 'calisan_model' not in st.session_state:
    with st.spinner("Sistem yapılandırılıyor..."):
        m_ad, v_ad = dogru_modeli_bul()
        st.session_state.calisan_model = m_ad
        st.session_state.versiyon = v_ad

if st.session_state.calisan_model:
    mesaj = st.text_area("Müşteriden gelen mesajı yapıştırın (Herhangi bir dilde):", height=150)
    karar = st.selectbox("Alınacak Karar:", 
                         ["İadeyi kabul et ve özür dile", 
                          "Ürünün fotoğrafını çekip göndermesini iste", 
                          "Kısmi iade (indirim) teklif et",
                          "Kargonun yolda olduğunu nazikçe belirt"])

    if st.button("Profesyonel Cevap Oluştur"):
        if mesaj:
            with st.spinner('Dil algılanıyor ve cevap hazırlanıyor...'):
                cevap = amazon_asistani(mesaj, karar, st.session_state.calisan_model, st.session_state.versiyon)
                st.success("Müşteriye Gönderilecek Yanıt:")
                st.info(cevap)
        else:
            st.warning("Lütfen işlem yapmak için bir mesaj girin.")
else:
    st.error("API bağlantısı kurulamadı. Lütfen internetini veya API anahtarını kontrol et.")
