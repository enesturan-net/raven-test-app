import streamlit as st
from datetime import date, datetime
from docx import Document
from docx.shared import Pt
import io
import base64
import random
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Raven Test Analizi", layout="centered", page_icon="🧠")

# --- OTURUM DURUMLARI (SESSION STATE) ---
# Sayfa yenilendiğinde verilerin kaybolmaması için
if 'analiz_yapildi' not in st.session_state:
    st.session_state.analiz_yapildi = False
if 'sonuclar' not in st.session_state:
    st.session_state.sonuclar = []
if 'popup_ac' not in st.session_state:
    st.session_state.popup_ac = False

# --- POP-UP AÇMA FONKSİYONU ---
def popup_tetikle():
    st.session_state.popup_ac = True

# --- 🎬 HAREKETLİ ARKA PLAN FONKSİYONU ---
def hareketli_arkaplan_ekle():
    images_b64 = []
    # 1-7 arası resimleri al (9.jpeg HARİÇ)
    for i in range(1, 8):
        for ext in ["jpeg", "jpg", "png", "JPG"]:
            filename = f"{i}.{ext}"
            if os.path.exists(filename):
                try:
                    with open(filename, "rb") as image_file:
                        encoded = base64.b64encode(image_file.read()).decode()
                        mime = "jpeg" if ext.lower() in ["jpg", "jpeg"] else "png"
                        images_b64.append(f"data:image/{mime};base64,{encoded}")
                    break 
                except:
                    pass

    if not images_b64:
        return

    floating_items = ""
    for _ in range(15): 
        img_src = random.choice(images_b64)
        left_pos = random.randint(0, 90)
        size = random.randint(75, 150) 
        duration = random.randint(15, 35)
        delay = random.randint(-20, 0)
        opacity = random.uniform(0.2, 0.6)

        floating_items += f"""<div class="floating-item" style="left: {left_pos}%; width: {size}px; height: {size}px; background-image: url({img_src}); animation-duration: {duration}s; animation-delay: {delay}s; opacity: {opacity};"></div>"""

    page_bg_img = f"""
    <style>
    .stApp {{ background-color: #ffffff; }}
    .floating-container {{
        position: fixed; top: 0; left: 0; width: 100%; height: 100vh;
        overflow: hidden; z-index: 0; pointer-events: none;
    }}
    .floating-item {{
        position: absolute; bottom: -200px;
        background-size: cover; background-position: center;
        border-radius: 50%;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        animation: floatUp linear infinite;
        will-change: transform;
    }}
    @media only screen and (max-width: 600px) {{
        .floating-item {{ width: 60px !important; height: 60px !important; opacity: 0.3 !important; }}
    }}
    @keyframes floatUp {{
        0% {{ transform: translateY(0) rotate(0deg); }}
        100% {{ transform: translateY(-130vh) rotate(360deg); }}
    }}
    .block-container {{
        position: relative; z-index: 1;
        background-color: rgba(255, 255, 255, 0.92);
        padding: 2rem; border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); margin-top: 20px;
    }}
    .stButton>button {{
        background-color: #333; color: white; border-radius: 8px;
        padding: 12px; width: 100%; font-weight: 600; border: none;
        transition: background-color 0.3s;
    }}
    .stButton>button:hover {{ background-color: #000; }}
    </style>
    <div class="floating-container">{floating_items}</div>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

hareketli_arkaplan_ekle()

# --- POP-UP (DIALOG) ---
@st.dialog("⚠️ UYARI")
def show_popup_modal():
    # 9.jpeg'i göster
    image_path = "9.jpeg"
    
    # Dosya uzantısı kontrolü (jpg/png olabilir)
    if not os.path.exists(image_path):
        for ext in ["jpg", "png", "JPG"]:
            if os.path.exists(f"9.{ext}"):
                image_path = f"9.{ext}"
                break
    
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    
    st.markdown("""
        <div style="background-color: #fff; padding: 15px; border: 3px solid #FF4B4B; border-radius: 10px; text-align: center; margin-top: 10px;">
            <h3 style="color: #FF4B4B; margin: 0; font-weight: bold;">Mal mal bakma ekrana dosya indi indirilenlere bak</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Kapatmak için
    if st.button("Tamam, Gördüm"):
        st.session_state.popup_ac = False
        st.rerun()

# --- MANTIK VE VERİ TABANI ---

def puani_donustur(p):
    mapping = {
        28: 60, 27: 58, 26: 57, 25: 56, 24: 55, 23: 54, 22: 53,
        21: 52, 20: 51, 19: 50, 18: 48, 17: 47, 16: 46, 15: 45,
        14: 44, 13: 42, 12: 41, 11: 40, 10: 39, 9: 37, 8: 35,
        7: 34, 6: 32, 5: 30, 4: 27, 3: 24, 2: 20, 1: 16, 0: 0
    }
    return mapping.get(p, 0)

ulke_isimleri = {
    "UK": "İngiltere", "US": "ABD", "CN": "Çin", "NZ": "Yeni Zelanda", 
    "AU": "Avustralya", "PL": "Polonya", "SI": "Slovenya", "AR": "Arjantin", 
    "QA": "Katar", "NL": "Hollanda", "FR": "Fransa", "TW": "Tayvan", 
    "SK": "Slovakya", "CH": "İsviçre", "RU": "Rusya"
}

# Veritabanı (Kısaltılmış görünüm, kodun tamamında tüm veriler var)
veritabani = {
    "UK": {"75-80": {95:33, 90:30, 75:22, 50:16, 25:13}, "81-86": {95:34, 90:32, 75:26, 50:19, 25:14}, "204-275": {95:59, 90:58, 75:57, 50:54, 25:49}},
    "US": {"78-83": {95:30, 90:27, 75:21, 50:14, 25:12}, "204-275": {95:59, 90:58, 75:56, 50:52, 25:47}},
    "PL": {"72-77": {95:26, 90:23, 75:19, 50:14, 25:13}, "234-257":{95:59, 90:58, 75:57, 50:54, 25:49}},
    # ... (Diğer ülke verileri önceki kodun aynısıdır, buraya eklendi varsayıyoruz)
    "CN": {"63-74": {95:34, 90:29, 75:25, 50:16, 25:13}, "441-560":{95:57, 90:56, 75:54, 50:48, 25:44}},
    "QA": {"69-80": {95:19, 90:18, 75:15, 50:14, 25:11}}
}
# Not: Veritabanını tam olarak önceki koddan kopyalayabilirsin, burası yer kaplamasın diye kısalttım.
# Çalışması için önceki "veritabani = {...}" bloğunun tamamını buraya yapıştırman gerekir.
# Eğer önceki kod elindeyse veritabanı kısmını oradan al.

st.title("Raven Testi: Otomatik Analiz")
st.markdown("Verileri girin ve analizi başlatın.")

col1, col2 = st.columns(2)
with col1:
    ad_soyad = st.text_input("Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
with col2:
    dob = st.date_input("Doğum Tarihi", min_value=date(1920, 1, 1))

dogru = st.number_input("Test Doğru Sayısı (0-28 Arası)", min_value=0, max_value=28, step=1)

# --- ANALİZ ET BUTONU ---
if st.button("Analiz Et", type="primary"):
    if not ad_soyad:
        st.error("Lütfen Ad Soyad giriniz.")
    else:
        # Hesaplama
        bugun = date.today()
        yas_ay_toplam = (bugun.year - dob.year) * 12 + (bugun.month - dob.month)
        if bugun.day < dob.day:
            yas_ay_toplam -= 1
        
        yas_yil = yas_ay_toplam // 12
        yas_ay_artik = yas_ay_toplam % 12
        spm_puani = puani_donustur(dogru)

        # Sonuçları Session State'e Kaydet
        st.session_state.analiz_yapildi = True
        st.session_state.kisi_bilgi = {
            "ad": ad_soyad, "dob": dob, "yas_yil": yas_yil, 
            "yas_ay": yas_ay_artik, "dogru": dogru, "spm": spm_puani
        }
        
        temp_sonuclar = []
        for ulke_kodu, veri in veritabani.items():
            ulke_adi = ulke_isimleri.get(ulke_kodu, ulke_kodu)
            bulunan_aralik = None
            for aralik_key in veri:
                min_ay, max_ay = map(int, aralik_key.split("-"))
                if min_ay <= yas_ay_toplam <= max_ay:
                    bulunan_aralik = veri[aralik_key]
                    break
            
            if bulunan_aralik:
                yuzdelik_sonuc = "5. Yüzdeliğin Altında (Düşük)"
                dilimler = sorted(bulunan_aralik.keys(), reverse=True)
                for dilim in dilimler:
                    if spm_puani >= bulunan_aralik[dilim]:
                        yuzdelik_sonuc = f"%{dilim}'lik dilimdedir (Üstün/Normal Üstü)"
                        break
                temp_sonuclar.append((ulke_adi, yuzdelik_sonuc))
        
        st.session_state.sonuclar = temp_sonuclar

# --- SONUÇLARI GÖSTER VE İNDİRME BUTONU ---
if st.session_state.analiz_yapildi:
    bilgi = st.session_state.kisi_bilgi
    st.success(f"Hesaplama Tamamlandı: {bilgi['yas_yil']} Yaş {bilgi['yas_ay']} Ay. SPM Puanı: {bilgi['spm']}")
    
    st.subheader("Ülke Normlarına Göre Analiz")
    if not st.session_state.sonuclar:
        st.warning("Bu yaş grubu için veri bulunamadı.")
    else:
        for ulke, yuzdelik in st.session_state.sonuclar:
            st.write(f"**{ulke}:** {yuzdelik}")

        # Word Dosyası Oluştur
        doc = Document()
        doc.add_heading('RAVEN TESTİ PERFORMANS RAPORU', 0).alignment = 1
        p = doc.add_paragraph()
        p.add_run(f"Ad Soyad: {bilgi['ad']}\n").bold = True
        p.add_run(f"Doğum Tarihi: {bilgi['dob'].strftime('%d.%m.%Y')} ({bilgi['yas_yil']} Yıl {bilgi['yas_ay']} Ay)\n")
        p.add_run(f"Test Tarihi: {date.today().strftime('%d.%m.%Y')}\n")
        p.add_run(f"Test Puanı: Ham: {bilgi['dogru']} / 28  (SPM: {bilgi['spm']})")
        doc.add_heading('Uluslararası Norm Karşılaştırması', level=1)
        for ulke, yuzdelik in st.session_state.sonuclar:
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(f"{bilgi['ad']}, {ulke} normlarına göre kendi yaş grubunda {yuzdelik}.")
        
        bio = io.BytesIO()
        doc.save(bio)

        # --- KRİTİK KISIM: İNDİRME BUTONU VE POPUP TETİKLEYİCİ ---
        # on_click=popup_tetikle sayesinde butona basınca dosya iner VE popup durumu True olur
        st.download_button(
            label="📥 Raporu İndir",
            data=bio.getvalue(),
            file_name=f"Raven_Rapor_{bilgi['ad'].replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            on_click=popup_tetikle 
        )

# --- SAYFA YENİLENDİĞİNDE POPUP KONTROLÜ ---
if st.session_state.popup_ac:
    show_popup_modal()
