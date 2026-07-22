# CrewAI Flow Trial

Proyek ini merupakan integrasi sistem otomasi kecerdasan buatan yang dibangun menggunakan **FastAPI**, **Celery**, **Redis**, dan **CrewAI**. Arsitektur ini dirancang untuk memproses tugas-tugas agen AI secara *asynchronous* di latar belakang (*background processing*). Selain itu, proyek ini dilengkapi dengan integrasi **Telegram Bot** melalui mekanisme Webhook.

---

## 🏗️ Alur Sistem (System Flow)

1. **Permintaan Pengguna (User Request)**: Pengguna berinteraksi dengan sistem melalui Endpoint API (menggunakan klien HTTP seperti Postman atau *frontend*) atau melalui Telegram Bot.
2. **FastAPI (API Gateway)**: Menerima seluruh *request* HTTP yang masuk. Untuk mengelola beban komputasi AI yang intensif dan mencegah *timeout*, FastAPI akan mendelegasikan tugas tersebut ke **Celery** dan mengembalikan `task_id` sebagai respons awal.
3. **Redis (Message Broker)**: FastAPI mengirimkan pesan tugas (*task message*) ke Redis, yang berfungsi sebagai antrean (*queue*) sementara.
4. **Celery Worker**: Komponen *worker* yang berjalan di latar belakang akan mengambil tugas dari Redis dan memulai pemrosesan agen AI melalui framework **CrewAI**.
5. **Verifikasi Status & Hasil**:
   - **Melalui API**: Pengguna dapat melakukan *polling* ke *endpoint* `/status/{task_id}` untuk memantau apakah tugas tersebut berstatus `PENDING`, `SUCCESS`, atau `FAILURE`. Jika berhasil, hasil keluaran AI akan dilampirkan dalam *response*.
   - **Melalui Telegram**: Bot akan menampilkan indikator "sedang mengetik..." (*typing action*) dan akan secara otomatis mengirimkan hasil akhir saat Celery telah menyelesaikan tugas terkait.

---

## 🛠️ Daftar API Endpoint dan Spesifikasinya

Seluruh fungsionalitas diakses melalui protokol HTTP yang dilayani oleh FastAPI.

### 1. Integrasi Webhook
- `POST /webhook`
  - **Deskripsi**: Menerima pembaruan (*update*) otomatis dari platform Telegram. Seluruh pesan dan interaksi dari Telegram Bot akan diterima oleh *endpoint* ini dan diteruskan sebagai *background task* FastAPI agar Telegram tidak melakukan panggilan ulang (*retry*).

### 2. Riset dan Rekomendasi (Berbasis Teks)
- `POST /research`
  - **Deskripsi**: Menjalankan riset komprehensif. Membutuhkan format *body JSON*: `topic` (topik riset) dan `audience` (target pembaca).
- `POST /market-research`
  - **Deskripsi**: Menjalankan analisis dan riset pasar. Membutuhkan format *body JSON*: `topic` (topik) dan `current_year` (tahun berjalan).
- `POST /tax-research`
  - **Deskripsi**: Menjalankan riset peraturan perpajakan. Membutuhkan format *body JSON*: `country` (negara) dan `year` (tahun).
- `POST /tax-advise`
  - **Deskripsi**: Memberikan rekomendasi dan konsultasi pajak spesifik suatu negara. Membutuhkan format *body JSON*: `country` (negara) dan `year` (tahun).

### 3. Pemrosesan Berkas (Berbasis Unggahan)
- `POST /file-text-analyzer`
  - **Deskripsi**: Menganalisis konten teks. Endpoint menerima *form-data* yang berisi berkas `file` dengan format teks (`text/plain`).
- `POST /anomaly-detection`
  - **Deskripsi**: Mendeteksi anomali pada sekumpulan data (dataset). Endpoint menerima unggahan berkas `file` dengan format Excel (`.xlsx`).
- `POST /forecasting`
  - **Deskripsi**: Menghasilkan proyeksi data (*forecasting*). Endpoint menerima unggahan berkas `file` dengan format Excel (`.xlsx`).
- `POST /helmet-detection`
  - **Deskripsi**: Mendeteksi penggunaan helm pada sebuah citra (gambar). Endpoint menerima unggahan berkas `image` dengan format `jpeg` atau `png`.

### 4. Manajemen Tugas (Task Management)
- `GET /status/{task_id}`
  - **Deskripsi**: Memeriksa status penyelesaian dari suatu tugas yang sedang diproses oleh Celery.
  - **Respons**: Mengembalikan status tugas (`PENDING`, `SUCCESS`, atau `FAILURE`). Jika status menunjukkan `SUCCESS`, atribut `result` akan memuat jawaban komprehensif yang dihasilkan oleh agen AI.

---

## 🚀 Panduan Instalasi dan Pengoperasian

Untuk menjalankan proyek ini secara komprehensif, diperlukan **empat (4) antarmuka terminal** yang terpisah. Pastikan terminal berada di direktori utama (*root directory*) dari proyek ini.

### 1. Instalasi Dependensi
Proyek ini dikelola menggunakan pengelola paket (*package manager*) `uv`.
```bash
uv sync
```

### 2. Menjalankan Redis (Message Broker)
Celery bergantung pada Redis sebagai *broker*. Pastikan layanan Redis telah berjalan di *port* `localhost:6379`.
Bagi pengguna sistem operasi distribusi Linux atau subsistem WSL:
```bash
sudo service redis-server start
```
Sebagai alternatif menggunakan kontainer Docker:
```bash
docker run -d -p 6379:6379 redis
```

### 3. Menjalankan Celery Worker (AI Processor)
Buka terminal baru. Eksekusi perintah berikut untuk menginisialisasi *worker* Celery yang bertugas melayani agen-agen CrewAI di latar belakang.
```bash
uv run celery -A tasks.celery_app worker --loglevel=INFO
```

### 4. Menjalankan Server Utama (FastAPI)
Buka terminal terpisah, dan jalankan server API utama.
```bash
uv run uvicorn api.main:app --reload
```
Layanan API dapat diakses melalui peramban (*browser*) pada alamat: **`http://127.0.0.1:8000`** (Dokumentasi API interaktif atau Swagger UI tersedia di `http://127.0.0.1:8000/docs`).

> **Catatan Khusus Penggunaan Telegram Bot:**
> Pastikan konfigurasi `WEBHOOK_URL` pada berkas `api/main.py` mengarah pada tautan publik (contohnya dengan menggunakan layanan *tunneling* seperti Ngrok atau Cloudflare Tunnels). Hal ini esensial agar platform Telegram dapat meneruskan *payload* pesan langsung ke lingkungan pengembangan lokal.

---

### Pengujian Lingkungan CrewAI (Tanpa Antarmuka API)
Untuk kebutuhan pengujian *flow* dan fungsionalitas agen AI secara langsung menggunakan antarmuka baris perintah (*command line interface*) tanpa perlu menginisialisasi layanan FastAPI dan Celery, perintah berikut dapat dieksekusi:
```bash
uv run kickoff
```
Atau sebagai alternatif:
```bash
uv run crewai run
```
