import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 0. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="BI - RAJAWALI", 
    page_icon="https://drive.google.com/thumbnail?id=1nAsEcJP4W8C9Qj-pLtY5278YI9iSKabY&sz=w128", 
    layout="wide"
)

st.markdown("""
<style>
/* Styling Filter Emas */
span[data-baseweb="tag"] { 
    background-color: transparent !important; 
    border: 1.5px solid #FFD700 !important; 
}
/* Styling Kotak Abu-abu Radar */
.radar-box { 
    background-color: rgba(211, 211, 211, 0.2); 
    padding: 20px; 
    border-radius: 12px; 
    margin-bottom: 20px; 
    border: 1px solid rgba(200, 200, 200, 0.3); 
}
</style>
""", unsafe_allow_html=True)

# State Management
if 'page' not in st.session_state: st.session_state.page = 'Beranda'
if 'selected_komoditas' not in st.session_state: st.session_state.selected_komoditas = None

def go_to_detail(komoditas):
    st.session_state.selected_komoditas = komoditas
    st.session_state.page = 'Detail'

def go_to_home():
    st.session_state.page = 'Beranda'
    st.session_state.selected_komoditas = None

def get_icon(nama_komoditas):
    nama = str(nama_komoditas).lower()
    if 'telur' in nama: return '🥚'
    elif 'cabai rawit' in nama or 'cabe rawit' in nama: return '🔥'
    elif 'cabai' in nama or 'cabe' in nama: return '🌶️'
    elif 'beras' in nama: return '🍚'
    elif 'bawang merah' in nama: return '🧅'
    elif 'bawang putih' in nama: return '🧄'
    elif 'ayam' in nama: return '🍗'
    elif 'sapi' in nama or 'daging' in nama: return '🥩'
    elif 'minyak' in nama: return '🍳'
    elif 'gula' in nama: return '🧂'
    elif 'jagung' in nama: return '🌽'
    elif 'kedelai' in nama: return '🫘'
    return '🌾'

# ==========================================
# 1. LOAD DATA SOURCE
# ==========================================
@st.cache_data
def load_data():
    file_path = 'Forecast_EWS_10_Komoditas_2024_2026-3 Terbaru.xlsx'
    df = pd.read_excel(file_path)
    df.columns = [c.lower() for c in df.columns]
    if 'bulan_tahun' in df.columns:
        df['bulan_tahun'] = pd.to_datetime(df['bulan_tahun'], errors='coerce')
    return df

df_master = load_data()
col_komoditas = 'komoditas' if 'komoditas' in df_master.columns else 'komoditas_pangan'
list_komoditas = sorted(df_master[col_komoditas].dropna().unique())
df_global_proj = df_master[(df_master['actual'] == 0) | (df_master['actual'].isna())]
df_global_proj = df_global_proj[df_global_proj['forecast'] > 0]

# ==========================================
# HALAMAN BERANDA
# ==========================================
if st.session_state.page == 'Beranda':
    col_logo, col_mascot = st.columns([7, 3])
    with col_logo:
        st.markdown('<img src="https://drive.google.com/thumbnail?id=1sbqabWaTANwaFfSd5hExupqoA_joEzBk&sz=w1000" style="max-height: 80px; margin-bottom: 10px;">', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.15rem; color: #666; margin-top: -5px;'>Dashboard Early Warning System Sumatera Selatan untuk memantau volatilitas harga dan ketersediaan pasokan secara real-time.</p>", unsafe_allow_html=True)
    with col_mascot:
        st.markdown('<img src="https://drive.google.com/thumbnail?id=1ZdFZWG6StfwCk7R9AdUP6lVYVhKvafiK&sz=w800" style="max-height: 120px; float: right; border-radius: 12px; object-fit: cover;">', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown('<div class="radar-box">', unsafe_allow_html=True)
    st.subheader("Radar Ketahanan Pangan", anchor=False)
    
    komoditas_bermasalah = 0
    bln_proj_terdekat = df_global_proj['bulan_tahun'].min() if not df_global_proj.empty else "-"
    if not df_global_proj.empty:
        df_proj_terdekat = df_global_proj[df_global_proj['bulan_tahun'] == bln_proj_terdekat]
        komoditas_bermasalah = df_proj_terdekat['ews_status'].astype(str).str.lower().isin(['waspada', 'kritis', 'high price risk']).sum()

    col_g1, col_g2, col_g3 = st.columns(3)
    col_g1.metric("Status Global", f"{komoditas_bermasalah} Berisiko", f"Bulan Depan: {bln_proj_terdekat.strftime('%b %Y') if bln_proj_terdekat != '-' else '-'}")
    col_g2.metric("Total Pantauan", f"{len(list_komoditas)} Komoditas", "Harga & Pasokan")
    col_g3.metric("Sistem Prediksi", "Aktif 🟢", "SARIMAX Terkalibrasi")
    st.markdown('</div>', unsafe_allow_html=True)

    # Dictionary Gambar
    kamus_foto = {
        "beras": "https://drive.google.com/thumbnail?id=1u-NKeYa2kDo8EWvIsqWqk3YmE38D6mi1&sz=w800",
        "cabai merah": "https://drive.google.com/thumbnail?id=1SxPyn-4Ib8nsn4-bdbR3S8jxAeqj3paN&sz=w800",
        "cabai rawit": "https://drive.google.com/thumbnail?id=12AvNJA9f20B64DrRp1rmpMLecrLvDxHa&sz=w800",
        "telur ayam": "https://drive.google.com/thumbnail?id=1uFGm8hueEjZp0fmc23uSdUmUc4E9F95P&sz=w800",
        "daging ayam": "https://drive.google.com/thumbnail?id=1koQ53csAw90x11A_kq6M513oDmI8vaU7&sz=w800",
        "daging sapi": "https://drive.google.com/thumbnail?id=1jLWp5gR6dUH6pp7CcIFYDQmi-24rSjLK&sz=w800",
        "bawang putih": "https://drive.google.com/thumbnail?id=1DX-EKXX-2ugC9i60xWAqT8KbiQHrWVQW&sz=w800",
        "bawang merah": "https://drive.google.com/thumbnail?id=1jgF0fysWvYAzgidQrZTvhE2NfrTkPL9e&sz=w800",
        "gula pasir": "https://drive.google.com/thumbnail?id=1IBT08J_OzlGmx8MCko1kCh_-5WCxC5uR&sz=w800",
        "minyak goreng": "https://drive.google.com/thumbnail?id=154WnytfQKYGNHoJpk_SAoOS4oQHI04vd&sz=w800"
    }

    # Data Processing
    komoditas_summary = []
    for kom in list_komoditas:
        df_k = df_master[df_master[col_komoditas] == kom].sort_values('bulan_tahun')
        df_k_hist = df_k[df_k['actual'] > 0]
        df_k_proj = df_k[(df_k['actual'] == 0) | (df_k['actual'].isna())]
        df_k_proj = df_k_proj[df_k_proj['forecast'] > 0]

        harga_n = df_k_hist['actual'].iloc[-1] if not df_k_hist.empty else 0
        harga_n1 = df_k_proj['forecast'].iloc[0] if not df_k_proj.empty else harga_n
        delta_n1 = ((harga_n1 - harga_n) / harga_n) * 100 if harga_n > 0 else 0
        status_k = str(df_k_proj['ews_status'].iloc[0]).title() if not df_k_proj.empty else "Aman"
        if status_k.lower() == 'high price risk': status_k = 'Waspada'
        
        komoditas_summary.append({'nama': kom, 'harga_n': harga_n, 'harga_n1': harga_n1, 'delta_n1': delta_n1, 'status': status_k, 'icon': get_icon(kom)})

    # Toolbar
    st.subheader("Papan Pantau Peringatan Dini", anchor=False)
    col_s, col_f, col_so = st.columns([4, 3, 3])
    with col_s: search_query = st.text_input("Pencarian Komoditas", placeholder="Ketik nama komoditas...")
    with col_f: filter_status = st.multiselect("Filter Status", options=["Aman", "Waspada", "Kritis"], placeholder="Semua Status")
    with col_so: sort_by = st.selectbox("Urutkan Berdasarkan", options=["Nama (A - Z)", "Nama (Z - A)", "Status (Kritis - Aman)", "Status (Aman - Kritis)"])

    st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px; opacity: 0.3;'>", unsafe_allow_html=True)

    if search_query: komoditas_summary = [k for k in komoditas_summary if search_query.lower() in k['nama'].lower()]
    if filter_status: komoditas_summary = [k for k in komoditas_summary if k['status'] in filter_status]
    
    def priority(s):
        s = s.lower()
        if s == 'kritis': return 1
        if s == 'waspada': return 2
        return 3

    if sort_by == "Nama (A - Z)": komoditas_summary.sort(key=lambda x: x['nama'])
    elif sort_by == "Nama (Z - A)": komoditas_summary.sort(key=lambda x: x['nama'], reverse=True)
    elif sort_by == "Status (Kritis - Aman)": komoditas_summary.sort(key=lambda x: (priority(x['status']), x['nama']))
    elif sort_by == "Status (Aman - Kritis)": komoditas_summary.sort(key=lambda x: (priority(x['status']), x['nama']), reverse=True)

    # Render Cards
    cols = st.columns(4)
    for idx, k in enumerate(komoditas_summary):
        warna_border = "#FF4B4B" if k['status'].lower() == 'kritis' else ("#FFA500" if k['status'].lower() == 'waspada' else "#21C354")
        warna_bg = "rgba(255, 75, 75, 0.08)" if k['status'].lower() == 'kritis' else ("rgba(255, 165, 0, 0.08)" if k['status'].lower() == 'waspada' else "rgba(33, 195, 84, 0.08)")
        link_foto = kamus_foto.get(str(k['nama']).lower(), "")
        img_tag = f'<img src="{link_foto}" style="position: absolute; right: 0; top: 0; height: 100%; width: 35%; object-fit: cover; object-position: right center; opacity: 0.25; z-index: 0; -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 80%); mask-image: linear-gradient(to right, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 80%);">' if link_foto else ''

        card_html = f"""
        <div style="position: relative; overflow: hidden; border: 2px solid {warna_border}; border-radius: 10px; padding: 15px; background-color: {warna_bg}; margin-bottom: 10px; color: inherit;">
            {img_tag}
            <div style="position: relative; z-index: 1;">
                <div style="font-size: 1.15rem; font-weight: bold; margin-bottom:10px;">{k['icon']} {k['nama']}</div>
                <p style="margin:0px; font-size:14px;">Harga Saat Ini: <b>Rp {k['harga_n']:,.0f}</b></p>
                <p style="margin:0px; font-size:14px;">Prediksi (N+1): <b>Rp {k['harga_n1']:,.0f}</b></p>
                <hr style="margin: 10px 0px; border-color: {warna_border}; opacity: 0.3;">
                <p style="margin:0px; font-size:14px; font-weight:bold; color:{warna_border};">Status: {k['status']}</p>
            </div>
        </div>
        """
        with cols[idx % 4]:
            st.markdown(card_html, unsafe_allow_html=True)
            st.button("Lihat Analisis", key=f"btn_{k['nama']}", on_click=go_to_detail, args=(k['nama'],), use_container_width=True)

# ==========================================
# HALAMAN 2: DETAIL KOMODITAS
# ==========================================
elif st.session_state.page == 'Detail':
    # Halaman detail tidak perlu perubahan, kode di bawah ini standar
    st.write("Halaman Detail...") # Anda bisa menempelkan logika halaman detail Anda di sini
