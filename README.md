# 💧 SimAntrian – Simulasi Sistem Antrian Depot Air Minum

> **Pemodelan dan Simulasi** | Universitas Muhammadiyah Malang

Dashboard interaktif berbasis **Streamlit** untuk mensimulasikan dan menganalisis sistem antrian depot air minum isi ulang menggunakan **Agent-Based Modeling (ABM)**, **SimPy**, dan pengujian **Monte Carlo**.

---

## 📌 Deskripsi Project

Project ini memodelkan perilaku pelanggan di depot air minum sebagai agen cerdas yang:
- Memiliki tingkat kecemasan (*anxiety*) yang berubah seiring waktu tunggu
- Mengambil keputusan mandiri: **tetap menunggu** atau **pergi**
- Menerapkan strategi **Coping CBT** untuk mengelola kecemasan

Simulasi dapat dijalankan dengan **dataset berbeda** tanpa mengubah kode — cukup upload file CSV baru.

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 📂 Upload Dataset | Upload CSV dengan validasi otomatis |
| 🔬 Simulasi ABM | Setiap pelanggan sebagai agen independen (SimPy) |
| 😰 Anxiety Model | Kecemasan dihitung: `A(t+1) = A(t) + S·D - R·P` |
| 🧠 Coping CBT | 4 strategi: None, Reactive, Preventive, Adaptive |
| ⚙️ Multi-Skenario | 8 skenario: 1/2 mesin × 4 coping |
| 🎲 Monte Carlo | Hingga 1000 iterasi per skenario |
| 📊 Visualisasi | Line chart, histogram, boxplot, scatter (Plotly interaktif) |
| 💡 Insight Otomatis | Analisis dan temuan otomatis berbasis hasil simulasi |
| 🔬 Uji t | Perbandingan statistik dua skenario |
| ⬇️ Export | Download hasil simulasi dan Monte Carlo sebagai CSV |

---

## 🛠️ Teknologi

- **Python 3.10+**
- **Streamlit** – Framework dashboard web
- **SimPy** – Discrete-event simulation engine
- **Pandas / NumPy** – Manipulasi data
- **Plotly** – Visualisasi interaktif
- **SciPy** – Uji statistik (t-test, CI)
- **Matplotlib / Seaborn** – Visualisasi tambahan

---

## 📁 Struktur Project

```
project/
│
├── app.py                  # Entri utama Streamlit
├── requirements.txt        # Dependensi Python
├── README.md               # Dokumentasi ini
├── .gitignore
│
├── datasets/
│   └── dataset_contoh.csv  # Dataset sampel 50 pelanggan
│
├── assets/                 # Gambar, logo (opsional)
│
└── modules/
    ├── __init__.py
    ├── simulation.py       # Kelas Pelanggan, SimPy engine
    ├── montecarlo.py       # Monte Carlo + uji t
    ├── visualization.py    # Semua fungsi Plotly
    ├── insights.py         # Generator insight otomatis
    └── utils.py            # Validasi, loader, helper
```

---

## 📋 Format Dataset

File CSV harus memiliki **4 kolom wajib**:

```csv
pelanggan,kedatangan,layanan,sabar
P001,0,8,12
P002,3,6,10
P003,7,9,15
```

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `pelanggan` | string | ID unik pelanggan |
| `kedatangan` | float | Waktu kedatangan (urut naik) |
| `layanan` | float | Durasi layanan yang dibutuhkan |
| `sabar` | float | Batas maksimal waktu tunggu |

---

## 🚀 Cara Install & Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/USERNAME/simantrian.git
cd simantrian
```

### 2. Buat Virtual Environment (Direkomendasikan)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

### 4. Jalankan Dashboard

```bash
streamlit run app.py
```

Dashboard akan terbuka di browser: `http://localhost:8501`

---

## 🌐 Cara Deploy ke Streamlit Cloud

### Langkah 1 – Persiapkan GitHub Repository

```bash
# Inisialisasi git (jika belum)
git init

# Tambahkan semua file
git add .

# Commit pertama
git commit -m "feat: initial dashboard SimAntrian"

# Buat repository di GitHub (via web atau CLI)
# Lalu hubungkan:
git remote add origin https://github.com/USERNAME/simantrian.git
git branch -M main
git push -u origin main
```

### Langkah 2 – Deploy di Streamlit Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Login dengan akun GitHub
3. Klik **"New app"**
4. Pilih repository: `USERNAME/simantrian`
5. Branch: `main`
6. Main file path: `app.py`
7. Klik **"Deploy!"**

Streamlit Cloud akan otomatis install `requirements.txt` dan deploy dashboard.

---

## 🎯 Cara Penggunaan Dashboard

1. **Upload Dataset** → Sidebar kiri, pilih file CSV
2. **Atur Parameter** → Pilih jumlah mesin dan strategi coping
3. **Jalankan Simulasi** → Klik "▶ Simulasi" (satu skenario) atau "🔄 Semua" (8 skenario)
4. **Lihat Visualisasi** → Tab "📈 Visualisasi"
5. **Monte Carlo** → Atur iterasi, klik "▶ Jalankan Monte Carlo"
6. **Baca Insight** → Tab "💡 Insight" untuk analisis otomatis
7. **Export** → Download hasil sebagai CSV

---

## 📊 Model Matematika

**Waktu Tunggu:**
```
WT_i = t_layani - t_datang
```

**Kondisi Pergi:**
```
Jika WT_i > W_i_efektif → agen pergi
W_i_efektif = W_i - (A_i × ANXIETY_IMPACT)
```

**Persamaan Anxiety:**
```
A(t+1) = A(t) + S × D
```
Kemudian dimodifikasi oleh strategi coping.

**Strategi Coping:**
- `none` : tidak ada pengurangan anxiety
- `reactive` : kurangi 0.8 jika anxiety > 1.5
- `preventive` : kurangi 0.2 setiap langkah waktu
- `adaptive` : pengurangan bertingkat sesuai level anxiety

---

## 👤 Author

**Project – Pemodelan dan Simulasi**  
Universitas Muhammadiyah Malang  
Tahun Akademik 2025/2026

---

## 📄 Lisensi

MIT License – bebas digunakan untuk keperluan akademik.
