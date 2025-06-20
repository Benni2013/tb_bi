# Restaurant Analytics: ETL & Dashboard Application

Proyek ini adalah aplikasi web berbasis Streamlit yang dirancang untuk memfasilitasi proses ETL (Extract, Transform, Load) data review restoran dan menyediakan dashboard analitik yang komprehensif. Aplikasi ini memungkinkan pengguna untuk memproses data CSV review restoran, memuatnya ke database PostgreSQL dari Supabase, dan menganalisis data melalui dashboard interaktif.

## 🏗️ Struktur Proyek

```
tb_bi/
├── etl_script/
│   ├── web_ETL.py              # Aplikasi web Streamlit untuk proses ETL
│   ├── etl_functions.py        # Fungsi-fungsi ETL untuk pemrosesan data
│   ├── requirements.txt        # Dependensi untuk ETL
│   └── README.md               # Dokumentasi ETL
├── dashboard/
│   ├── main_dashboard.py       # Dashboard Utama
│   ├── dashboard_*.py          # Modul dashboard spesifik
│   ├── shared_utils.py         # Utilitas bersama
│   └── requirements.txt        # Dependensi untuk dashboard
|   └── README.md               # Dokumentasi dashboard
├── dataset/
│   └── yelp_database_with_advanced_reviews.csv  # Dataset contoh
└── README.md                   # Dokumentasi utama proyek
```

## ✨ Fitur Utama

### ETL Module
- Upload dan validasi file CSV
- Ekstraksi dan transformasi data review restoran
- Analisis sentimen otomatis menggunakan NLP
- Loading data ke PostgreSQL dengan skema data warehouse
- Monitoring proses ETL real-time

### Dashboard Module
- **Segmentasi Pelanggan & Analisis Performa**: Analisis performa restoran dengan segmentasi berdasarkan rating
- **Performa Lokasi & Tren Rating**: Visualisasi performa berdasarkan lokasi geografis dan tren waktu
- **Sentimen & Suara Pelanggan**: Analisis sentimen review dan word cloud

## 📋 Requirements

### Untuk ETL Application
```
streamlit>=1.28.0
pandas>=2.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
nltk>=3.8.0
textblob>=0.17.0
streamlit-option-menu>=0.3.0
```

### Untuk Dashboard Application
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

## 🚀 Setup dan Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd tb_bi
```


## 🔄 Menjalankan ETL Application

### 1. Install Dependencies ETL
```bash
cd etl_script
pip install -r requirements.txt
```

### 2. Jalankan ETL Application
```bash
streamlit run web_ETL.py
```

### 3. Proses ETL
1. Buka browser dan akses aplikasi di `http://localhost:8501`
2. Upload file CSV yang berisi data review restoran
3. Pilih opsi untuk mempertahankan data existing (jika ada)
4. Klik "Execute ETL Process"
5. Monitor progress dan lihat summary hasil ETL

### 4. Format Data CSV yang Diharapkan
File CSV harus memiliki kolom berikut:
- `Time_GMT`: Timestamp review
- `Phone`: Nomor telepon restoran
- `Organization`: Nama organisasi/restoran
- `OLF`: Online listing format
- `Rating`: Rating review (1-5)
- `NumberReview`: Jumlah review
- `Category`: Kategori restoran
- `Country`: Negara
- `CountryCode`: Kode negara
- `State`: Provinsi/negara bagian
- `City`: Kota
- `Street`: Alamat jalan
- `Building`: Nomor bangunan
- `ReviewText`: Teks review

## 📊 Menjalankan Dashboard Application

### 1. Install Dependencies Dashboard
```bash
cd dashboard
pip install -r requirements.txt
```

### 2. Jalankan Dashboard Application
```bash
streamlit run main_dashboard.py
```

### 3. Menggunakan Dashboard
1. Buka browser dan akses dashboard di `http://localhost:8501`
2. Pilih dashboard yang ingin digunakan dari sidebar:
   - **Segmentasi Pelanggan & Analisis Performa Gabungan**
   - **Performa Lokasi & Tren Rating**
   - **Sentimen & Suara Pelanggan**
3. Gunakan filter di sidebar untuk menyesuaikan analisis
4. Eksplorasi visualisasi interaktif yang tersedia

## 💡 Tips Penggunaan

1. **Jalankan ETL terlebih dahulu** sebelum menggunakan dashboard untuk memastikan data tersedia
2. **Gunakan dataset sample** di folder `dataset/` untuk testing
3. **Monitor performa database** saat memproses dataset besar
4. **Backup database** secara berkala untuk menghindari kehilangan data

### Error Dependencies
```bash
# Update pip terlebih dahulu
pip install --upgrade pip

# Install ulang dependencies
pip install -r requirements.txt --force-reinstall
```

### Error NLTK Data
```python
import nltk
nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab')
```

## 🎯 Fitur Dashboard

### 1. Segmentasi Pelanggan & Analisis Performa
- Scatter plot rating vs total reviews
- Segmentasi lokasi berdasarkan rating
- Clustering performa restoran
- Top dan bottom performers

### 2. Performa Lokasi & Tren Rating
- Analisis performa per kota
- Tren rating bulanan
- Tren rating untuk top organizations
- Metrik performa lokasi

### 3. Sentimen & Suara Pelanggan
- Distribusi sentimen (positif, negatif, netral)
- Sentimen per lokasi
- Word cloud dari review
- Tren sentimen dari waktu ke waktu
- Sample review per kategori sentimen

## 📄 Lisensi

Proyek ini dikembangkan untuk keperluan akademis dan pembelajaran.