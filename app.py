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
span[data-baseweb="tag"] { background-color: transparent !important; border: 1.5px solid #FFD700 !important; }

/* Background Abu-abu Permanen & Garis Merah untuk Radar */
.radar-box { 
    background-color: rgba(150, 150, 150, 0.15); 
    padding: 30px; 
    border-radius: 12px; 
    margin-bottom: 30px; 
    border-left: 6px solid #D32F2F;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
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
    try:
        df = pd.read_excel(file_path, sheet_name='forecast_all')
    except:
        try:
            df = pd.read_excel(file_path)
        except Exception as ex:
            st.error(f"Gagal membaca file: {ex}")
            return pd.DataFrame()

    df.columns = [c.lower() for c in df.columns]
    if 'bulan_tahun' in df.columns:
        df['bulan_tahun'] = pd.to_datetime(df['bulan_tahun'], errors='coerce')
    return df

df_master = load_data()

if not df_master.empty:
    col_komoditas = 'komoditas' if 'komoditas' in df_master.columns else 'komoditas_pangan'
    list_komoditas = sorted(df_master[col_komoditas].dropna().unique())

    df_global_hist = df_master[df_master['actual'] > 0]
    df_global_proj = df_master[(df_master['actual'] == 0) | (df_master['actual'].isna())]
    df_global_proj = df_global_proj[df_global_proj['forecast'] > 0]

    # ==========================================
    # HALAMAN 1: BERANDA (EXECUTIVE SUMMARY)
    # ==========================================
    if st.session_state.page == 'Beranda':

        # -------------------------------------------------------------------
        # CUSTOM HEADER PROPORSIONAL
        # -------------------------------------------------------------------
        col_logo, col_text = st.columns([1.2, 8.8])
        with col_logo:
            # Logo diperbesar agar mengimbangi tinggi teks
            st.markdown('<img src="https://drive.google.com/thumbnail?id=1nAsEcJP4W8C9Qj-pLtY5278YI9iSKabY&sz=w500" style="width: 100%; max-width: 150px; margin-top: 5px;">', unsafe_allow_html=True)
        with col_text:
            # Teks diperbesar dan disesuaikan kerapatannya
            st.markdown("<h1 style='margin:0; padding:0; line-height: 1.1; font-size: 3.2rem;'>BI - RAJAWALI</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin:0; padding:0; color: #D32F2F; margin-bottom: 8px; font-size: 1.6rem;'>Radar Gejolak Harga Waspada Inflasi</h3>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 1.2rem; opacity: 0.85; margin:0;'>Dashboard Early Warning System Sumatera Selatan untuk memantau volatilitas harga dan ketersediaan pasokan secara real-time.</p>", unsafe_allow_html=True)

        st.divider()

        # -------------------------------------------------------------------
        # RADAR KETAHANAN PANGAN DENGAN BACKGROUND ABU-ABU
        # -------------------------------------------------------------------
        komoditas_bermasalah = 0
        bln_proj_terdekat_str = "-"
        if not df_global_proj.empty:
            bln_proj_terdekat = df_global_proj['bulan_tahun'].min()
            df_proj_terdekat = df_global_proj[df_global_proj['bulan_tahun'] == bln_proj_terdekat]
            komoditas_bermasalah = df_proj_terdekat['ews_status'].astype(str).str.lower().isin(['waspada', 'kritis', 'high price risk']).sum()
            bln_proj_terdekat_str = bln_proj_terdekat.strftime('%B %Y')
            
        warna_risiko = "#FF4B4B" if komoditas_bermasalah > 0 else "#21C354"

        radar_html = f"""
        <div class="radar-box">
            <h2 style="margin-top: 0; margin-bottom: 25px;">Radar Ketahanan Pangan</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                <div style="flex: 1; min-width: 200px;">
                    <p style="margin: 0; font-size: 15px; opacity: 0.7;">Status Global</p>
                    <h2 style="margin: 0; font-size: 2.2rem; color: {warna_risiko};">{komoditas_bermasalah} Berisiko</h2>
                    <p style="margin: 0; font-size: 14px; opacity: 0.6;">Bulan Depan: {bln_proj_terdekat_str}</p>
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <p style="margin: 0; font-size: 15px; opacity: 0.7;">Total Pantauan</p>
                    <h2 style="margin: 0; font-size: 2.2rem;">{len(list_komoditas)} Komoditas</h2>
                    <p style="margin: 0; font-size: 14px; opacity: 0.6;">Harga & Pasokan</p>
                </div>
                <div style="flex: 1; min-width: 200px;">
                    <p style="margin: 0; font-size: 15px; opacity: 0.7;">Sistem Prediksi</p>
                    <h2 style="margin: 0; font-size: 2.2rem;">Aktif 🟢</h2>
                    <p style="margin: 0; font-size: 14px; opacity: 0.6;">SARIMAX Terkalibrasi</p>
                </div>
            </div>
        </div>
        """
        st.markdown(radar_html, unsafe_allow_html=True)

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

        komoditas_summary = []
        for kom in list_komoditas:
            df_k = df_master[df_master[col_komoditas] == kom].sort_values('bulan_tahun')
            df_k_hist = df_k[df_k['actual'] > 0]
            df_k_proj = df_k[(df_k['actual'] == 0) | (df_k['actual'].isna())]
            df_k_proj = df_k_proj[df_k_proj['forecast'] > 0]

            harga_n = df_k_hist['actual'].iloc[-1] if not df_k_hist.empty else 0
            harga_n1 = df_k_proj['forecast'].iloc[0] if not df_k_proj.empty else harga_n
            delta_n1 = ((harga_n1 - harga_n) / harga_n) * 100 if harga_n > 0 else 0

            status_k = "Aman"
            if not df_k_proj.empty and 'ews_status' in df_k_proj.columns:
                status_k = str(df_k_proj['ews_status'].iloc[0]).title()

            if status_k.lower() == 'high price risk':
                status_k = 'Waspada'

            komoditas_summary.append({
                'nama': kom,
                'harga_n': harga_n,
                'harga_n1': harga_n1,
                'delta_n1': delta_n1,
                'status': status_k,
                'icon': get_icon(kom)
            })

        st.subheader("Papan Pantau Peringatan Dini", anchor=False)

        col_s, col_f, col_so = st.columns([4, 3, 3])
        with col_s:
            search_query = st.text_input("Pencarian Komoditas", placeholder="Ketik nama komoditas...")
        with col_f:
            filter_status = st.multiselect("Filter Status", options=["Aman", "Waspada", "Kritis"], placeholder="Semua Status")
        with col_so:
            sort_by = st.selectbox("Urutkan Berdasarkan", options=["Nama (A - Z)", "Nama (Z - A)", "Status (Kritis - Aman)", "Status (Aman - Kritis)"])

        st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px; opacity: 0.3;'>", unsafe_allow_html=True)

        if search_query:
            komoditas_summary = [k for k in komoditas_summary if search_query.lower() in k['nama'].lower()]

        if filter_status:
            komoditas_summary = [k for k in komoditas_summary if k['status'] in filter_status]

        def priority(s):
            s = s.lower()
            if s == 'kritis': return 1
            if s == 'waspada': return 2
            return 3

        if sort_by == "Nama (A - Z)":
            komoditas_summary.sort(key=lambda x: x['nama'])
        elif sort_by == "Nama (Z - A)":
            komoditas_summary.sort(key=lambda x: x['nama'], reverse=True)
        elif sort_by == "Status (Kritis - Aman)":
            komoditas_summary.sort(key=lambda x: (priority(x['status']), x['nama']))
        elif sort_by == "Status (Aman - Kritis)":
            komoditas_summary.sort(key=lambda x: (priority(x['status']), x['nama']), reverse=True)

        if len(komoditas_summary) == 0:
            st.info("Tidak ada komoditas yang sesuai dengan kriteria pencarian Anda.")
        else:
            cols = st.columns(4)
            for idx, k in enumerate(komoditas_summary):
                kom = k['nama']
                harga_n = k['harga_n']
                harga_n1 = k['harga_n1']
                delta_n1 = k['delta_n1']
                status_k = k['status']
                icon = k['icon']

                if status_k.lower() in ['kritis']:
                    warna_border = "#FF4B4B"
                    warna_bg = "rgba(255, 75, 75, 0.08)"
                elif status_k.lower() in ['waspada']:
                    warna_border = "#FFA500"
                    warna_bg = "rgba(255, 165, 0, 0.08)"
                else:
                    warna_border = "#21C354"
                    warna_bg = "rgba(33, 195, 84, 0.08)"

                warna_inflasi = "red" if delta_n1 > 0 else "green"
                tanda_inflasi = "▲" if delta_n1 > 0 else "▼" if delta_n1 < 0 else "-"

                link_foto = kamus_foto.get(str(kom).lower(), "")
                # Lebar fade gambar diubah menjadi 45% (width: 45%;)
                img_tag = f'<img src="{link_foto}" style="position: absolute; right: 0; top: 0; height: 100%; width: 45%; object-fit: cover; object-position: right center; opacity: 0.25; z-index: 0; -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 80%); mask-image: linear-gradient(to right, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 80%);">' if link_foto else ''

                card_html = f"""
                <div style="position: relative; overflow: hidden; border: 2px solid {warna_border}; border-radius: 10px; padding: 15px; background-color: {warna_bg}; margin-bottom: 10px; color: inherit;">
                    {img_tag}
                    <div style="position: relative; z-index: 1;">
                        <div style="font-size: 1.15rem; font-weight: bold; margin-top:0px; margin-bottom:10px; color: inherit;">{icon} {kom}</div>
                        <p style="margin:0px; font-size:14px; color: inherit;">Harga Saat Ini: <b>Rp {harga_n:,.0f}</b></p>
                        <p style="margin:0px; font-size:14px; color: inherit;">Prediksi (N+1): <b>Rp {harga_n1:,.0f}</b></p>
                        <p style="margin:0px; font-size:14px; font-weight:bold; color:{warna_inflasi};">{tanda_inflasi} {delta_n1:+.2f}% <span style="font-size:12px; font-weight:normal; color:gray;">(vs Bulan Ini)</span></p>
                        <hr style="margin: 10px 0px; border-color: {warna_border}; opacity: 0.3;">
                        <p style="margin:0px; font-size:14px; font-weight:bold; color:{warna_border};">Status: {status_k}</p>
                    </div>
                </div>
                """

                with cols[idx % 4]:
                    st.markdown(card_html, unsafe_allow_html=True)
                    st.button("Lihat Analisis", key=f"btn_{kom}", on_click=go_to_detail, args=(kom,), use_container_width=True)

    # ==========================================
    # HALAMAN 2: DETAIL KOMODITAS
    # ==========================================
    elif st.session_state.page == 'Detail':

        komoditas = st.session_state.selected_komoditas
        icon_detail = get_icon(komoditas)

        col_b1, col_b2 = st.columns([2, 8])
        with col_b1:
            st.button("Kembali", on_click=go_to_home, type="secondary", use_container_width=True)
        with col_b2:
            st.markdown(f"<div style='font-size:2rem; font-weight:bold; margin-top:-5px; color:inherit;'>{icon_detail} Analisis Detail EWS: {komoditas}</div>", unsafe_allow_html=True)

        df_filtered = df_master[df_master[col_komoditas] == komoditas].copy().sort_values('bulan_tahun')
        df_hist = df_filtered[df_filtered['actual'] > 0].copy()
        df_proj_all = df_filtered[(df_filtered['actual'] == 0) | (df_filtered['actual'].isna())].copy()
        df_proj_all = df_proj_all[df_proj_all['forecast'] > 0]

        max_bulan = len(df_proj_all)
        options_waktu = ['Nowcasting'] + [f"{i} Bulan" for i in range(1, max_bulan + 1)] if max_bulan > 0 else ['Nowcasting']

        st.sidebar.title("Filter Proyeksi")
        pilihan_waktu = st.sidebar.select_slider(
            "Target Prediksi Ke Depan:",
            options=options_waktu,
            value=options_waktu[-1] if max_bulan > 0 else 'Nowcasting'
        )
        filter_bulan = options_waktu.index(pilihan_waktu)
        df_proj = df_proj_all.head(filter_bulan)

        status_terkini = df_proj['ews_status'].iloc[-1] if not df_proj.empty else (df_hist['ews_status'].iloc[-1] if not df_hist.empty else "Historical")

        harga_n = df_hist['actual'].iloc[-1] if not df_hist.empty else 0
        harga_n1 = df_proj['forecast'].iloc[0] if not df_proj.empty else harga_n
        delta_n1 = ((harga_n1 - harga_n) / harga_n) * 100 if harga_n > 0 else 0

        proj_naik = 0; tgl_proj_akhir = "-"
        if not df_proj.empty and harga_n > 0:
            proj_naik = ((df_proj['forecast'].iloc[-1] - harga_n) / harga_n) * 100
            tgl_proj_akhir = df_proj['bulan_tahun'].iloc[-1].strftime('%b %Y')

        mape_val = df_filtered['mape'].dropna().iloc[0] if not df_filtered['mape'].dropna().empty else 0
        akurasi = 100 - mape_val if mape_val > 1 else (1 - mape_val) * 100

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"Status EWS ({pilihan_waktu})", str(status_terkini).upper(), delta_color="inverse" if str(status_terkini).lower() in ['waspada', 'kritis'] else "normal")
        col2.metric("Potensi Gejolak (N+1)", f"{delta_n1:+.2f}%", f"Bulan Depan vs Saat Ini")
        col3.metric(f"Tren Jangka Panjang", f"{proj_naik:+.2f}%" if tgl_proj_akhir != "-" else "N/A", f"S.d {tgl_proj_akhir}", delta_color="off")
        col4.metric("Tingkat Akurasi", f"{akurasi:.2f}%", "Akurasi Historis")
        st.divider()

        st.subheader("Tren Harga & Proyeksi Interval Risiko", anchor=False)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        if 'neraca' in df_filtered.columns:
            fig.add_trace(go.Bar(x=df_hist['bulan_tahun'], y=df_hist['neraca'], name='Neraca Aktual', marker_color='rgba(54, 162, 235, 0.4)'), secondary_y=True)
            if not df_proj.empty:
                fig.add_trace(go.Bar(x=df_proj['bulan_tahun'], y=df_proj['neraca'], name='Proyeksi Neraca', marker_color='rgba(255, 159, 64, 0.5)'), secondary_y=True)
        if not df_proj.empty and 'lower_ci' in df_proj.columns and 'upper_ci' in df_proj.columns:
            tgl_ci = pd.concat([df_hist['bulan_tahun'].tail(1), df_proj['bulan_tahun']])
            upper_ci = pd.concat([df_hist['actual'].tail(1), df_proj['upper_ci']])
            lower_ci = pd.concat([df_hist['actual'].tail(1), df_proj['lower_ci']])
            fig.add_trace(go.Scatter(x=pd.concat([tgl_ci, tgl_ci[::-1]]), y=pd.concat([upper_ci, lower_ci[::-1]]), fill='toself', fillcolor='rgba(231, 76, 60, 0.15)', line=dict(color='rgba(255,255,255,0)'), hoverinfo="skip", name='Interval Risiko (CI)'), secondary_y=False)
        fig.add_trace(go.Scatter(x=df_hist['bulan_tahun'], y=df_hist['actual'], name='Harga Aktual', mode='lines+markers', line=dict(color='blue', width=3)), secondary_y=False)
        if not df_proj.empty:
            df_proj_connected = pd.concat([df_hist.tail(1), df_proj])
            y_proj = pd.concat([df_hist['actual'].tail(1), df_proj['forecast']])
            fig.add_trace(go.Scatter(x=df_proj_connected['bulan_tahun'], y=y_proj, name='Proyeksi Harga', mode='lines+markers', line=dict(color='red', width=3, dash='dash')), secondary_y=False)
        if 'threshold_kritis_atas' in df_filtered.columns and not df_filtered['threshold_kritis_atas'].isna().all():
            thresh_val = df_filtered['threshold_kritis_atas'].dropna().iloc[0]
            all_dates = pd.concat([df_hist['bulan_tahun'], df_proj['bulan_tahun']]) if not df_proj.empty else df_hist['bulan_tahun']
            fig.add_trace(go.Scatter(x=all_dates, y=[thresh_val]*len(all_dates), name='Batas Kritis EWS', mode='lines', line=dict(color='rgba(231, 76, 60, 0.8)', width=1.5, dash='dot')), secondary_y=False)

        fig.update_layout(height=450, hovermode='x unified', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_yaxes(title_text="<b>Harga (Rp)</b>", secondary_y=False)
        if 'neraca' in df_filtered.columns: fig.update_yaxes(title_text="<b>Neraca (Ton)</b>", secondary_y=True, showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        st.subheader("Pusat Komando & Mitigasi Risiko", anchor=False)
        col_mit, col_email = st.columns([1.2, 1])

        with col_mit:
            st.markdown("<div style='font-size:1.15rem; font-weight:bold; margin-bottom:10px;'>Rekomendasi Kebijakan</div>", unsafe_allow_html=True)

            worst_status = "aman"
            worst_month = None
            worst_delta = 0

            for i, (idx, row) in enumerate(df_proj_all.iterrows()):
                s = str(row['ews_status']).lower()
                if s in ['kritis']:
                    worst_status = 'kritis'
                    worst_month = row['bulan_tahun'].strftime('%B %Y')
                    worst_delta = i + 1
                    break
                elif s in ['waspada', 'high price risk'] and worst_status == 'aman':
                    worst_status = 'waspada'
                    worst_month = row['bulan_tahun'].strftime('%B %Y')
                    worst_delta = i + 1

            if worst_status == 'kritis':
                st.error(f"**STATUS KRITIS PADA {worst_delta} BULAN KE DEPAN ({worst_month.upper()})!**")
                st.markdown("""
                * **Tindakan Darurat:** Segera jadwalkan Operasi Pasar Murah (OPM) berkoordinasi dengan Bulog daerah.
                * **Pasokan:** Lakukan inspeksi jalur distribusi untuk mencegah penimbunan (kartel).
                * **Regulasi:** Siapkan pengajuan kuota pasokan darurat ke pusat (Badan Pangan Nasional).
                """)
            elif worst_status == 'waspada':
                st.warning(f"**STATUS WASPADA PADA {worst_delta} BULAN KE DEPAN ({worst_month.upper()})!**")
                st.markdown("""
                * **Tindakan Pencegahan:** Tingkatkan frekuensi pemantauan harga harian di Pasar Induk.
                * **Pasokan:** Hubungi distributor lokal utama untuk memastikan rencana pasokan bulan depan aman.
                * **Komunikasi:** Terbitkan himbauan untuk tidak *panic buying* ke masyarakat.
                """)
            else:
                st.success("**STATUS KESELURUHAN AMAN**")
                st.markdown("""
                * **Tindakan:** Lanjutkan monitoring rutin (Mingguan).
                * Kondisi pasokan dan tren harga ke depan dinilai stabil oleh model. Tidak memerlukan intervensi darurat saat ini.
                """)

            st.markdown("---")
            arima_order = df_filtered['arima_order'].dropna().iloc[0] if 'arima_order' in df_filtered.columns and not df_filtered['arima_order'].dropna().empty else "-"
            exog_nama = df_filtered['exog_utama'].dropna().iloc[0] if 'exog_utama' in df_filtered.columns and not df_filtered['exog_utama'].dropna().empty else "Tidak ada"
            st.info(f"**Analisis Faktor Utama (Model {arima_order}):** Gejolak sangat dipengaruhi oleh variabel eksternal **{str(exog_nama).replace('Eks_','')}**.")

        with col_email:
            st.markdown("<div style='font-size:1.15rem; font-weight:bold; margin-bottom:10px;'>Surat Instruksi Pemimpin</div>", unsafe_allow_html=True)
            with st.container(border=True):
                catatan_bos = st.text_area("Catatan/Instruksi Pemimpin BI Sumsel:", placeholder="Ketik instruksi kebijakan di sini untuk dikirim ke seluruh Tim TPID...")

                with st.expander("Konfigurasi Pengirim (Wajib Diisi 1x)"):
                    st.caption("Masukkan kredensial email Anda untuk mengaktifkan fitur pengiriman.")
                    pengirim_email = st.text_input("Email Gmail Pengirim:")
                    pengirim_pass = st.text_input("App Password Gmail:", type="password")

                list_penerima = [
                    "aidandaffa2nd@gmail.com",
                    "azghisyani@gmail.com",
                    "taniariesty@gmail.com",
                    "hildaidamaharani@gmail.com"
                ]

                if st.button("Kirim Email Instruksi ke Seluruh Tim TPID", type="primary", use_container_width=True):
                    if not pengirim_email or not pengirim_pass:
                        st.error("Silakan isi Konfigurasi Pengirim terlebih dahulu.")
                    elif not catatan_bos:
                        st.error("Catatan instruksi tidak boleh kosong!")
                    else:
                        with st.spinner("Mengirim instruksi ke seluruh Tim TPID..."):
                            try:
                                msg = MIMEMultipart("alternative")
                                msg["Subject"] = f"Peringatan Dini EWS: {komoditas.upper()} ({status_terkini.upper()})"
                                msg["From"] = pengirim_email
                                msg["To"] = ", ".join(list_penerima)

                                html_template = f"""
                                <html>
                                <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                                    <div style="border:1px solid #ddd; padding:20px; border-radius:10px;">
                                        <h2 style="color: #d9534f; border-bottom: 2px solid #d9534f; padding-bottom: 10px;">
                                            Early Warning System - BI Sumsel
                                        </h2>
                                        <p>Tim TPID yang terhormat,</p>
                                        <p>Sistem EWS Pangan mendeteksi anomali pada komoditas <b>{komoditas}</b>.</p>
                                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                                            <tr>
                                                <td style="padding: 8px; border: 1px solid #ddd; background-color: #f9f9f9;"><b>Status Peringatan ({pilihan_waktu})</b></td>
                                                <td style="padding: 8px; border: 1px solid #ddd;"><b>{status_terkini.upper()}</b></td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px; border: 1px solid #ddd; background-color: #f9f9f9;"><b>Harga Saat Ini</b></td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">Rp {harga_n:,.0f}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px; border: 1px solid #ddd; background-color: #f9f9f9;"><b>Proyeksi N+1 (Bulan Depan)</b></td>
                                                <td style="padding: 8px; border: 1px solid #ddd;">Rp {harga_n1:,.0f} ({delta_n1:+.2f}%)</td>
                                            </tr>
                                        </table>
                                        <h3 style="color: #2c3e50;">Instruksi Pemimpin BI Sumsel:</h3>
                                        <blockquote style="background: #eef2f5; padding: 15px; border-left: 5px solid #3498db; font-size: 16px; font-style: italic;">
                                            "{catatan_bos}"
                                        </blockquote>
                                        <br>
                                        <p style="font-size: 12px; color: #999;">Email ini dikirim secara otomatis melalui Dashboard EIS Pangan.</p>
                                    </div>
                                </body>
                                </html>
                                """
                                msg.attach(MIMEText(html_template, "html"))

                                server = smtplib.SMTP("smtp.gmail.com", 587)
                                server.starttls()
                                server.login(pengirim_email, pengirim_pass)
                                server.sendmail(pengirim_email, list_penerima, msg.as_string())
                                server.quit()

                                st.success("Sukses! Instruksi darurat telah disiarkan ke seluruh email Tim TPID.")
                            except Exception as e:
                                st.error(f"Gagal mengirim email. Periksa kembali koneksi internet dan App Password Anda. Error: {e}")
