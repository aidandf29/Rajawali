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
    page_icon="https://drive.google.com/uc?export=view&id=1nAsEcJP4W8C9Qj-pLtY5278YI9iSKabY", 
    layout="wide"
)

# Styling CSS 
st.markdown("""
<style>
/* 1. KONTROL PADDING STREAMLIT AGAR BANNER BISA NAIK KE ATAS */
.block-container {
    padding-top: 2rem !important; 
    padding-bottom: 0rem !important;
}

/* MENURUNKAN TOMBOL SIDEBAR AGAR TIDAK KETUTUP LOGO */
[data-testid="collapsedControl"] {
    top: 70px !important; 
}

/* 2. MENGHILANGKAN IKON RANTAI (ANCHOR LINK) STREAMLIT */
a.header-anchor, .st-emotion-cache-10trblm a, h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
    display: none !important;
    visibility: hidden !important;
}

/* 3. LOGO HEADER BAWAAN STREAMLIT (Kiri Atas) */
[data-testid="stHeader"] {
    background-image: url('https://drive.google.com/uc?export=view&id=1sbqabWaTANwaFfSd5hExupqoA_joEzBk');
    background-repeat: no-repeat;
    background-position: 20px center;
    background-size: auto 65%;
    background-color: transparent;
}

/* 4. BACKDROP PASAR (Opacity & Blend Mode Disesuaikan) */
.top-backdrop {
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    margin-top: -65px; 
    padding: 60px 10% 40px 10%; 
    /* Menggunakan background-blend-mode agar foto lebih gelap/redup */
    background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://drive.google.com/uc?export=view&id=151ji3lJmqLu_A9FyWsMQMgdYoNkpBy3E');
    background-size: cover;
    background-position: center 30%;
    color: #FFFFFF !important;
    box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    z-index: 1;
}

/* Kotak Radar Transparan di atas Backdrop Pasar */
.radar-box-transparent {
    background-color: rgba(255, 255, 255, 0.15); 
    padding: 30px; 
    border-radius: 12px; 
    margin-top: 30px;
    border-left: 6px solid #FFD700;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 5. FOOTER AMPERA */
.footer-wrapper {
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    margin-top: 60px;
    padding: 25px 0;
    text-align: center;
    border-top: 1px solid rgba(150, 150, 150, 0.2);
    font-size: 13px;
    font-weight: 600;
    color: var(--text-color);
}

/* Judul Kustom Pengganti st.subheader */
.custom-subheader {
    font-size: 1.8rem;
    font-weight: bold;
    margin-top: 25px;
    margin-bottom: 15px;
    color: inherit;
}

/* Styling Filter Emas Adaptif */
span[data-baseweb="tag"] { background-color: var(--secondary-background-color) !important; border: 1.5px solid #FFD700 !important; color: var(--text-color) !important; }
span[data-baseweb="tag"] span { color: var(--text-color) !important; }
span[data-baseweb="tag"] svg { fill: var(--text-color) !important; }

/* 6. SCROLLBAR MENYAMAR */
::-webkit-scrollbar { width: 8px; height: 8px; background-color: transparent; }
::-webkit-scrollbar-track { background-color: transparent; }
::-webkit-scrollbar-thumb { background-color: rgba(150, 150, 150, 0.4); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background-color: rgba(150, 150, 150, 0.7); }
</style>
""", unsafe_allow_html=True)

# ... (Lanjutkan sisa kode Anda di sini)
