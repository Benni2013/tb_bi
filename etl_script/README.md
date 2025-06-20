# Restaurant Reviews ETL Application

Aplikasi web Streamlit untuk proses ETL (Extract, Transform, Load) data review restoran ke database PostgreSQL dengan analisis sentimen otomatis.

## 🏗️ Struktur Proyek

```
etl_script/
├── web_ETL.py            # Aplikasi web Streamlit untuk ETL
├── etl_functions.py      # Fungsi-fungsi ETL dan analisis sentimen
├── database_config.py    # Konfigurasi database (akan dibuat otomatis)
├── requirements.txt      # Dependencies
└── README.md             # Dokumentasi
```

## 📋 Requirements

```
streamlit
pandas
sqlalchemy
psycopg2-binary
nltk
textblob
streamlit-option-menu
```

## 🚀 Instalasi & Menjalankan

### 1. Install Dependencies
```bash
cd etl_script
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi
```bash
streamlit run web_ETL.py
```

### 3. Akses Aplikasi
- Buka browser: `http://localhost:8501`
- Upload file CSV review restoran
- Klik "🚀 Lakukan ETL"
- Monitor progress dan lihat hasil

## 📊 Format CSV yang Diharapkan

```
ID, Time_GMT, Phone, Organization, OLF, Rating, NumberReview, 
Category, Country, CountryCode, State, City, Street, Building, ReviewText
```

**Contoh:**
- Time_GMT: `12/15/2023 14:30`
- Rating: `1-5`
- ReviewText: Teks review pelanggan

## 🗃️ Output Database

ETL akan membuat tabel:
- `dim_time` - Dimensi waktu
- `dim_location` - Dimensi lokasi  
- `dim_restaurant` - Dimensi restoran
- `dim_category` - Dimensi kategori
- `dim_keywords` - Keywords dari review
- `dim_sentiment` - Hasil analisis sentimen
- `bridge_sentiment_keywords` - Bridge table
- `fact_restaurant_reviews` - Tabel fakta utama

## 💡 Tips

- Dataset sample tersedia di folder `../dataset/`
- Proses ETL membutuhkan 5-15 menit tergantung ukuran data
- Gunakan mode "Pertahankan data" untuk menambah data tanpa menghapus yang lama