# Restaurant Analytics Dashboard

Dashboard interaktif berbasis Streamlit untuk analisis data review restoran dengan visualisasi komprehensif dan insights bisnis.

## 🏗️ Struktur Dashboard

```
dashboard/
├── main_dashboard.py          # Dashboard utama dengan navigasi
├── dashboard_segmentation.py  # Modul segmentasi pelanggan
├── dashboard_location.py      # Modul analisis lokasi & tren
├── dashboard_sentiment.py     # Modul analisis sentimen
├── shared_utils.py           # Utilitas dan koneksi database
├── requirements.txt          # Dependencies
└── README.md                # Dokumentasi
```

## 📋 Requirements

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
plotly>=5.15.0
matplotlib>=3.7.0
wordcloud>=1.9.0
folium>=0.14.0
streamlit-folium>=0.13.0
requests>=2.31.0
nltk>=3.8.0
python-dateutil>=2.8.0
```

## 🚀 Instalasi & Menjalankan

### 1. Install Dependencies
```bash
cd dashboard
pip install -r requirements.txt
```

### 2. Jalankan Dashboard Utama
```bash
streamlit run main_dashboard.py
```

### 3. Akses Dashboard
- Buka browser: `http://localhost:8501`
- Pilih dashboard dari dropdown sidebar:
  - **Segmentasi Pelanggan & Analisis Performa**
  - **Performa Lokasi & Tren Rating**
  - **Sentimen & Suara Pelanggan**

## 📊 Fitur Dashboard

### 1. Segmentasi Pelanggan & Analisis Performa
- Performance metrics dan KPI cards
- Scatter plot rating vs total reviews
- Segmentasi rating dengan treemap visualization
- Tren rating untuk top organizations

### 2. Performa Lokasi & Tren Rating
- Performance matrix dengan quadrant analysis
- Peta interaktif rating per state
- Analisis competitive landscape
- Seasonal performance insights

### 3. Sentimen & Suara Pelanggan
- Distribusi sentimen dengan pie chart
- Analisis sentimen per lokasi
- Word cloud dari review text
- Sample reviews per kategori sentimen

## 💡 Tips Penggunaan

- **Jalankan ETL terlebih dahulu** untuk memastikan data tersedia
- Dashboard memiliki **mode demo** jika data belum tersedia
- Gunakan **filter di sidebar** untuk analisis spesifik
- Dashboard menggunakan **caching** untuk performa optimal
- Semua visualisasi **interaktif** dengan hover details

## 🔧 Troubleshooting

### Error Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Error Port
```bash
streamlit run main_dashboard.py --server.port 8502
```

### Error Database Connection
- Pastikan ETL sudah dijalankan
- Cek koneksi database di `shared_utils.py`
- Verifikasi tabel sudah terbuat di database