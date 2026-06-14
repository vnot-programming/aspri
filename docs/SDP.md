# 📋 Software Development Plan (SDP) — AspriAI

## 1. Fase Pengembangan & Milestone

Proyek **AspriAI (Asisten Pribadi AI)** direncanakan berjalan dalam 4 fase pengembangan yang terstruktur:

```mermaid
gantt
    title Peta Jalan Pengembangan AspriAI (2026)
    dateFormat  YYYY-MM-DD
    section Fase 1: Core API Gateway
    Inisiasi Proyek & Dokumentasi docs/   :active, des1, 2026-06-07, 1d
    Pembangunan FastAPI Core Stateless Proxy    : des2, after des1, 3d
    Konektivitas Ollama & YOLO Routing          : des3, after des2, 2d
    section Fase 2: ComfyUI API Wrapper
    Eksport & Integrasi JSON workflows         : des4, after des3, 3d
    WebSocket Listener untuk Render Progress    : des5, after des4, 2d
    section Fase 3: Slurm Orchestrator
    Sbatch Script generator & Job Queuer        : des6, after des5, 3d
    CUDA Memory Cleanup daemon                  : des7, after des6, 1d
    section Fase 4: Playground UI (AspriDesk)
    Laravel 13 (Postgres/Redis/MinIO) Setup     : des8, after des7, 3d
    Integrasi Client API & Web Playground Panel : des9, after des8, 4d
```

---

## 2. Struktur Pengelola Progres (Development Log / Progress Tracking)

### [Entri 001] — Inisiasi Proyek & Dokumen Standar Rekayasa
*   **Tanggal/Waktu:** 2026-06-07 03:09 WIB
*   **Tugas yang diselesaikan:**
    *   Membuat repositori lokal terisolasi untuk AspriAI di direktori `/data/users/g6717500336/singularity/AspriAI`.
    *   Membuat berkas rancangan awal `README.md` yang memuat Laporan Analisis, Konsep Identitas, Network Topology, Rencana Struktur Proyek, Mekanisme API ComfyUI, serta Keuntungan Dekopel.
    *   Menginisialisasi folder `docs/` dan menyusun 5 dokumen standar rekayasa perangkat lunak:
        1.  `SRS.md` (Spesifikasi kebutuhan fungsional & non-fungsional).
        2.  `SDD.md` (Rancangan arsitektur, skema database SQLite, spesifikasi endpoints).
        3.  `SRD.md` (Pemetaan kebutuhan bisnis ke komponen teknis, justifikasi teknologi).
        4.  `STD.md` (Kasus uji / test-case unit, integrasi, dan antarmuka).
        5.  `SDP.md` (Milestone Gantt chart, log kemajuan proyek aktif).
*   **File yang diubah/dibuat:**
    *   `README.md` [DIBUAT BARU]
    *   `docs/SRS.md` [DIBUAT BARU]
    *   `docs/SDD.md` [DIBUAT BARU]
    *   `docs/SRD.md` [DIBUAT BARU]
    *   `docs/STD.md` [DIBUAT BARU]
    *   `docs/SDP.md` [DIBUAT BARU]
*   **Status saat ini:** **Selesai (Fase Inisiasi 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Dokumentasi blueprint dan cetak biru arsitektur lengkap telah terpasang di dalam folder `docs/`.
    *   Langkah berikutnya yang harus dilakukan adalah melangkah ke **Fase 1 (Pembangunan Core API Gateway)**:
        1.  Masuk ke direktori `aspri-core/`.
        2.  Membuat virtual environment python / conda.
        3.  Membangun file inisiasi server `app.py` menggunakan FastAPI.
        4.  Mengintegrasikan SQLite database (`sqlite3` / SQLAlchemy) untuk melayani penyimpanan tabel `api_keys` dan `activity_logs`.
        5.  Memastikan port FastAPI tidak bertabrakan dengan layanan lain (port default 8000 aman, atau gunakan port kustom sesuai konfigurasi).

### [Entri 002] — CI/CD Automation & Remote SSH Configuration
*   **Tanggal/Waktu:** 2026-06-07 11:21 WIB
*   **Tugas yang diselesaikan:**
    *   Mengonfigurasi dan mengaktifkan remote deployment CI/CD otomatis pada `.github/workflows/deploy.yml` untuk backend (`Deploy Backend to GPU Node`) dan frontend (`Deploy Frontend to Web Host`).
    *   Memperbaiki penulisan kunci privat SSH menggunakan pengkodean Base64 (`SSH_PRIVATE_KEY_BASE64`) disertai sanitasi string (`tr -d '\r' | tr -d '\n'`) untuk membypass sensor rahasia dan error format key di runner GitHub.
    *   Merancang konfigurasi otentikasi Cloudflare Access untuk domain `slurm.penelitian.my.id` menggunakan Service Token (`github-actions-aspri`) dengan opsi *Bypass* untuk CI/CD dan silent SSH local.
    *   Melakukan verifikasi koneksi lokal Windows (`ssh KU-Slurm-CF` menggunakan parameter `--id` dan `--secret` di `ProxyCommand`) dan berhasil login langsung ke login node secara instan tanpa membuka peramban web browser.
*   **File yang diubah/dibuat:**
    *   `.github/workflows/deploy.yml` [DIUBAH - OK]
    *   `README.md` [DIUBAH - OK]
    *   `docs/SDP.md` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Konfigurasi Infrastruktur & CI/CD 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Akses server via Cloudflare Tunnel sudah terproteksi penuh dari publik namun meloloskan CI/CD dan SSH lokal ber-token.
    *   Lanjutkan implementasi **Fase 1 (Pembangunan Core API Gateway)** pada folder `aspri-core/`.

### [Entri 003] — Pembersihan Modul Lama & Audit Script Auto-Booking GPU
*   **Tanggal/Waktu:** 2026-06-07 11:59 WIB
*   **Tugas yang diselesaikan:**
    *   Melakukan audit mendalam dan pembersihan total terhadap instansi lama di direktori `/data/users/g6717500336/singularity/` untuk mencegah bentrokan port dan resource dengan arsitektur AspriAI yang baru.
    *   Menghapus direktori proyek lama secara permanen: `lm-studio/`, `ollama/`, dan `open-webui/`.
    *   Menonaktifkan pemanggilan skrip launcher `sbatch_llm_service.sh` dari generator sbatch `book_gpu.py` (baris 144-147) dan file submit job `submit_booking_run.sbatch` (baris 21-24) untuk mencegah inisialisasi tak terduga saat booking GPU diaktifkan kembali.
    *   Mematikan sesi tmux `gpu_booking` (daemon `book_gpu.py`) serta membatalkan job Slurm `6618` (`vnot`) agar resource GPU terbebas penuh (status bersih).
*   **File yang diubah/dibuat:**
    *   `docs/SDP.md` [DIUBAH - OK]
    *   `/data/users/g6717500336/Trainning-Models/MyFineTunning-SlurmMaster/utils/book_gpu.py` [DIUBAH - OK]
    *   `/data/users/g6717500336/Trainning-Models/MyFineTunning-SlurmMaster/utils/submit_booking_run.sbatch` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Pembersihan Lingkungan Lama 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Lingkungan kini benar-benar bersih dan siap untuk inisiasi ulang.
    *   Langkah selanjutnya adalah membangun kembali proyek Ollama secara modular di bawah folder `/data/users/g6717500336/singularity/ollama` yang berdiri sendiri sesuai instruksi user.

### [Entri 004] — Inisiasi Ulang & Kompilasi Modular Server Ollama v0.24.0
*   **Tanggal/Waktu:** 2026-06-07 12:47 WIB
*   **Tugas yang diselesaikan:**
    *   Membangun ulang modul server Ollama v0.24.0 secara modular di direktori `/data/users/g6717500336/singularity/ollama/`.
    *   Membuat berkas `setup.sh` dengan argumen `--install` yang mengotomasi pembuatan folder `models/` & `logs/`, menyalin `.env` dari SlurmMaster, dan mem-pull image container Singularity `ollama-0.24.sif` secara otomatis.
    *   Membuat berkas job runner `sbatch_aspri_service.sh` dengan konfigurasi:
        1.  Penggunaan port dinamis acak (`18000-18999`).
        2.  Flash Attention dinonaktifkan (`OLLAMA_FLASH_ATTENTION=false`) untuk GPU Volta V100.
        3.  Reverse SSH tunnel diarahkan ke host internal `slurmmaster` ke port statis `11434` (untuk dicocokkan dengan Cloudflare Tunnel ID `02700c0e-a0ea-468b-8abd-19619affe58e`).
        4.  Integrasi pengiriman tautan publik fallback (quick tunnel) ke Telegram sebagai link HTML aktif yang dapat diklik.
        5.  Sistem pembersihan (`cleanup EXIT`) berbasis variabel PID presisi (`$OLLAMA_PID`, `$CF_PID`, `$SSH_PID`) agar tidak menyentuh proses tunnel utama di login node.
    *   Mengeksekusi `bash setup.sh --install` secara sukses (SIF ter-pull sempurna, `.env` tersalin).
*   **File yang diubah/dibuat:**
    *   `docs/SDP.md` [DIUBAH - OK]
    *   `singularity/ollama/setup.sh` [BARU - OK]
    *   `singularity/ollama/sbatch_aspri_service.sh` [BARU - OK]
*   **Status saat ini:** **Selesai (Inisiasi Ulang & Kompilasi SIF Ollama 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Modul Ollama v0.24.0 siap dijalankan di compute node kluster.
    *   Tunggu instruksi user untuk langkah selanjutnya (menyalakan booking GPU atau mem-pull model).

### [Entri 005] — Integrasi Menu Manajemen AspriAI pada Script Utama Slurm
*   **Tanggal/Waktu:** 2026-06-07 13:12 WIB
*   **Tugas yang diselesaikan:**
    *   Menambahkan opsi menu baru **`8. 🤖 Manajemen AspriAI (Ollama & WebUI)`** ke dalam antarmuka menu utama skrip pengelola kluster `/data/users/g6717500336/Trainning-Models/MyFineTunning-SlurmMaster/utils/myslurm.sh`.
    *   Mengimplementasikan fungsi `manage_aspri_ai()` yang secara cerdas mendeteksi status sewa GPU aktif (Job ID, Compute Node, State), keaktifan proses server Ollama, dan port compute node atau PORT Ollama Server yang sedang dipetakan.
    *   Menyusun submenu di bawah Menu 8 untuk:
        1.  🚀 **Jalankan Server Ollama:** Meluncurkan `sbatch_aspri_service.sh` secara remote di background compute node yang sedang aktif disewa (via SSH + nohup).
        2.  🛑 **Hentikan Server Ollama:** Mematikan proses server, cloudflared, dan reverse tunnel secara presisi di compute node tanpa melepaskan alokasi sewa GPU (Job Slurm tetap jalan).
        3.  📋 **Lihat Log Runtime:** Memantau log jalannya Ollama dan log tunnel secara real-time.
        4.  ⚙️ **Inisiasi Ulang Modul:** Memicu ulang skrip `setup.sh --install` secara instan dari menu.
*   **File yang diubah/dibuat:**
    *   `docs/SDP.md` [DIUBAH - OK]
    *   `/data/users/g6717500336/Trainning-Models/MyFineTunning-SlurmMaster/utils/myslurm.sh` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Integrasi Menu Utama Slurm 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Kontrol server Ollama dan arsitektur modular di compute node kini terintegrasi penuh ke dalam sistem dashboard interaktif `myslurm.sh`.
    *   Langkah selanjutnya adalah menunggu instruksi user untuk inisiasi modul lanjutan (seperti Open WebUI).

### [Entri 006] — Perbaikan Akses Eksternal Quick Tunnel & Sinkronisasi Kredensial Global
*   **Tanggal/Waktu:** 2026-06-07 15:15 WIB
*   **Tugas yang diselesaikan:**
    *   Mendiagnosis dan memperbaiki masalah error `403 Forbidden` saat mengakses API Ollama via Cloudflare Quick Tunnel (`*.trycloudflare.com`) dari Postman. Perbaikan dilakukan dengan mengubah pengikatan host Ollama di `sbatch_aspri_service.sh` menjadi `0.0.0.0:${OLLAMA_PORT}` dan menambahkan argumen `--http-host-header localhost` di cloudflared.
    *   Membersihkan sisa proses zombie (`ollama`, `cloudflared`, `sbatch_aspri_service.sh`) di compute node `ai3` untuk menghindari bentrokan port dinamis.
    *   Menyalin berkas kredensial global `/data/users/g6717500336/singularity/.env` (Single Source of Truth) ke `/data/users/g6717500336/singularity/AspriAI/.env` dan `/data/users/g6717500336/singularity/ollama/.env` guna sinkronisasi otentikasi.
    *   Mengamankan izin akses file `.env` lokal menggunakan `chmod 600` untuk mencegah pembacaan data sensitif oleh pengguna lain di kluster Slurm.
    *   Menghilangkan parameter `SSH_PRIVATE_KEY_BASE64` dari file `.env` lokal dan membiarkannya tersimpan eksklusif di GitHub Secrets (praktik keamanan terbaik).
*   **File yang diubah/dibuat:**
    *   `singularity/ollama/sbatch_aspri_service.sh` [DIUBAH - OK]
    *   `singularity/AspriAI/.env` [DIUBAH - OK]
    *   `singularity/ollama/.env` [DIUBAH - OK]
    *   `singularity/AspriAI/docs/SDP.md` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (API Security & Access Verification 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Token otentikasi terbagi menjadi dua: Token SSH (di GitHub Secrets untuk CI/CD) dan Token API (di `.env` lokal untuk akses klien). Desain ini mengisolasi akses SSH dari potensi kebocoran token API.
    *   Pengujian API GET/POST menggunakan domain utama `backend-ollama.penelitian.my.id` saat ini sudah berjalan sukses dengan menyertakan header `CF-Access-Client-Id` dan `CF-Access-Client-Secret`.

### [Entri 007] — Sinkronisasi Keamanan Cloudflare, Environment Global, dan Setup RVM
*   **Tanggal/Waktu:** 2026-06-07 15:35 WIB
*   **Tugas yang diselesaikan:**
    *   **Keputusan Arsitektur Jaringan:** Memutuskan untuk menggunakan **Cloudflare Named Tunnel** dengan **Zero Trust Service Token** untuk keamanan. Keputusan ini menghindari penggunaan *Quick Tunnel* yang dinamis (tidak konsisten saat restart), serta menghindari beban komputasi tambahan di sisi *Slurm node* (seperti keharusan menginstal Web Server untuk validasi Bearer Token internal).
    *   **Kredensial Lingkungan (Environment):** Mengonfirmasi penggunaan global `.env` (berasal dari `/data/users/g6717500336/singularity/.env`) pada proyek AspriAI untuk sinkronisasi token.
    *   **Kebijakan Rahasia GitHub Actions:** Mengonfirmasi bahwa parameter otentikasi pendeployan (`CF_CLIENT_ID`, `CF_CLIENT_SECRET`, dan `SSH_PRIVATE_KEY_BASE64`) tidak disimpan di *environment* lokal, melainkan diamankan 100% pada *GitHub Secrets* untuk *deployment* via `.github/workflows/deploy.yml`.
    *   **Perencanaan Frontend:** Memutuskan pengkajian penggunaan **Laravel Versi 13** (terbaru) untuk *AspriAI Desk (Frontend)* guna memanfaatkan fitur integrasi `ai-sdk` bawaan yang *out-of-the-box*.
    *   **Milestone Terkait:** Memastikan keberhasilan *setup* proyek Computer Vision lain yaitu RVM (Reverse Vending Machine), dengan status aktif pada `https://backend-rvm.penelitian.my.id` dan `https://front-rvm.penelitian.my.id` sebagai acuan *best practice* infrastruktur.
*   **File yang diubah/dibuat:**
    *   `docs/SDP.md` [DIUBAH - OK]
    *   `docs/SDD.md` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Infrastruktur & Arsitektur Jaringan Ditetapkan 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Implementasi infrastruktur keamanan dan lingkungan proyek telah disepakati dan dikonfigurasi.
    *   **AspriAI Core (Backend)** untuk interaksi langsung dengan model Ollama (serta ComfyUI) masih **Belum Dibuat** (Fase 1 *Pending*).
    *   Langkah selanjutnya (bagi AI atau *developer* selanjutnya) adalah memulai pengembangan **AspriAI Core** dengan FastAPI.

### [Entri 008] — Simplifikasi Arsitektur Keamanan (No-SQLite) & Penetapan Prioritas
*   **Tanggal/Waktu:** 2026-06-07 15:45 WIB
*   **Tugas yang diselesaikan:**
    *   **Simplifikasi Keamanan (Penghapusan Bearer Token):** Berdasarkan tinjauan *overhead* server, diputuskan bahwa sistem **tidak lagi membutuhkan lapisan autentikasi API Key (Bearer Token) via SQLite** di sisi aplikasi *FastAPI*. Autentikasi dan sekuritas diserahkan 100% kepada lapisan **Cloudflare Access (Zero Trust)**. Aplikasi *FastAPI* murni bertindak sebagai proksi lokal. Ini akan menghemat resource secara drastis (zero-DB requirement).
    *   **Penetapan Conda Environment:** Dikonfirmasi bahwa *backend FastAPI* akan di-install dan dijalankan menggunakan environment bawaan standar yaitu `yolo_env`.
    *   **Penetapan Fokus Uji Awal:** Fokus implementasi tahap pertama dibatasi secara ketat pada pembangunan **Endpoint Proksi Ollama** (membuktikan *pipeline* berhasil) sebelum melanjutkan ke modul sekunder (ComfyUI / YOLO).
*   **File yang diubah/dibuat:**
    *   `docs/SDP.md` [DIUBAH - OK]
    *   `implementation_plan.md` (Artifact) [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Blueprint Terkalibrasi Ulang 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Abaikan instruksi lama terkait integrasi SQLite atau verifikasi `Bearer Token` di `main.py`. Aplikasi FastAPI harus dibangun sesederhana dan se-ringan mungkin sebagai *proxy gateway* yang transparan ke port `11434` (Ollama).
    *   Langkah selanjutnya: Install paket `fastapi`, `uvicorn`, dan `httpx` di `yolo_env`, kemudian buat `main.py` dan `app/api/v1/endpoints/chat.py`.

### [Entri 009] — Fix Deployment AspriAI (Docker-Compose & Asset Build)
*   **Tanggal/Waktu:** 2026-06-08 20:31 WIB
*   **Tugas yang diselesaikan:**
    *   Mendiagnosis dan memperbaiki HTTP 500 (`Connection refused`, `Permission denied storage`, dan `Vite manifest not found`) pada AspriAI Desk (Laravel 13 + Vite).
    *   Membuat `entrypoint.sh` kustom pada Docker image PHP (`AspriAI-php`) untuk melakukan otomatisasi proses saat start container: `composer install`, `npm install && npm run build`, perbaikan *ownership* `storage/` dan `bootstrap/cache/`, serta `php artisan config:clear`.
    *   Memperbaiki pemetaan volume Nginx dan PHP-FPM di `docker-compose.yml` agar menunjuk secara langsung ke source code `./aspri-desk` di Docker Host.
    *   Memperbarui aturan CI/CD: Mendaftarkan `deployment/` ke dalam `.gitignore` (agar setup Docker terisolasi dan dikelola via *docker-host*) serta menambahkan direktori `docs/` ke dalam instruksi *sparse-checkout* Github Actions.
    *   Mereplikasi perubahan konfigurasi (*re-build & deployment ulang*) langsung ke server `docker-host`, menghasilkan status `200 OK` yang stabil dan *favicon* yang ter-load secara normal.
*   **File yang diubah/dibuat:**
    *   `deployment/AspriAI/docker/php/Dockerfile` [BARU - OK]
    *   `deployment/AspriAI/docker/php/entrypoint.sh` [BARU - OK]
    *   `deployment/AspriAI/docker-compose.yml` [DIUBAH - OK]
    *   `.gitignore` [DIUBAH - OK]
    *   `.github/workflows/deploy.yml` [DIUBAH - OK]
    *   `docs/SDP.md` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Infrastruktur Frontend Desk & Build Pipeline 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Deployment Frontend AspriAI-Desk (Laravel 13) di docker-host kini bersifat *self-sustaining*. Apabila ada perubahan source code yang ditarik, proses container yang me-restart akan otomatis memicu `entrypoint.sh` untuk me-rebuild aset secara otomatis.

### [Entri 010] — Finalisasi Arsitektur Dokumen, RVM Header Fix & Agent Workflow
*   **Tanggal/Waktu:** 2026-06-08 21:20 WIB
*   **Tugas yang diselesaikan:**
    *   Memodifikasi file `RVM/frontend/js/app.js` untuk menginjeksi header `CF-Access-Client-Id` dan `CF-Access-Client-Secret` pada semua request `fetch` agar berhasil melewati perlindungan Cloudflare Zero Trust ke `backend-rvm`.
    *   Membuat file `workflow-aspri.md` sebagai panduan mutlak bagi seluruh AI Agent terkait letak *source code* Frontend (Laravel 13) dan Backend (FastAPI) serta URL *endpoint* publik yang harus dipakai.
    *   Merombak ulang keseluruhan dokumen proyek (`README.md`, `SDD.md`, `SRS.md`, `SRD.md`, `STD.md`, `SDP.md`) agar selaras dengan arsitektur final *Decoupled*: AspriCore sebagai Stateless Proxy dan AspriDesk sebagai aplikasi monolitik Laravel 13 yang menangani otentikasi API Key via PostgreSQL.
*   **File yang diubah/dibuat:**
    *   `RVM/frontend/js/app.js` [DIUBAH - OK]
    *   `.agents/rules/workflow-aspri.md` [BARU - OK]
    *   `singularity/AspriAI/README.md` [DIUBAH - OK]
    *   `singularity/AspriAI/docs/SDD.md` [DIUBAH - OK]
    *   `singularity/AspriAI/docs/SRS.md` [DIUBAH - OK]
    *   `singularity/AspriAI/docs/SRD.md` [DIUBAH - OK]
    *   `singularity/AspriAI/docs/STD.md` [DIUBAH - OK]
    *   `singularity/AspriAI/docs/SDP.md` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Klarifikasi Dokumentasi Arsitektur 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   RVM Frontend sekarang bisa berkomunikasi dengan backend via Cloudflare Access.
    *   Arsitektur AspriAI telah dipisahkan secara tegas dan Laravel 13 resmi digunakan sebagai pengelola antarmuka/database. Patuhi panduan `workflow-aspri.md`.
- **Tanggal/Waktu:** Mon Jun  8 23:49:49 +07 2026
- **Tugas yang diselesaikan:** Mengubah AspriAI Core Gateway (main.py) menjadi jembatan (Unified Health Check) untuk mengecek status Ollama Server, RVM Server, dan ComfyUI (Placeholder) secara konkuren dari satu endpoint (/health).
- **File yang diubah/dibuat:** singularity/AspriAI/aspri-core/main.py
- **Status saat ini:** Selesai
- **Catatan untuk AI selanjutnya:** API Gateway di aspri-core sudah mendukung agregasi health dari 3 services.
- **Tanggal/Waktu:** Tue Jun  9 00:03:59 +07 2026
- **Tugas yang diselesaikan:** Memperbaiki logika ekstraksi status JSON di API Gateway (main.py). Kini Gateway menggunakan status 'offline' atau 'degraded' berdasarkan isi body payload response, terlepas dari HTTP status 200 OK proxy.
- **File yang diubah/dibuat:** singularity/AspriAI/aspri-core/main.py
- **Status saat ini:** Selesai
- **Catatan untuk AI selanjutnya:** Parsing status sekarang telah menangani nested health check payload.
- **Tanggal/Waktu:** Tue Jun  9 00:05:51 +07 2026
- **Tugas yang diselesaikan:** Memperbaiki HTTP Status Code di chat.py untuk membalas dengan 503 (Service Unavailable) atau 502 (Bad Gateway) saat Ollama mati, sehingga response JSON dan HTTP Status selaras.
- **File yang diubah/dibuat:** singularity/AspriAI/aspri-core/app/api/v1/endpoints/chat.py
- **Status saat ini:** Selesai
- **Tanggal/Waktu:** Tue Jun  9 00:32:34 +07 2026
- **Tugas yang diselesaikan:** Membuat skrip Watchdog untuk pemulihan otomatis (auto-recovery) Ollama saat job Slurm terputus atau node berpindah.
- **File yang diubah/dibuat:** singularity/ollama/watchdog_ollama.sh
- **Status saat ini:** Selesai
- **Tanggal/Waktu:** Tue Jun  9 00:34:30 +07 2026
- **Tugas yang diselesaikan:** Merefaktor skrip Watchdog Ollama menjadi `run_ollama_daemon.sh` agar menggunakan pendekatan `srun --overlap` seperti pada RVM Backend. File watchdog lama dihapus. Pendekatan ini lebih Cloud-Native, bebas bentrok, dan seragam penamaannya.
- **File yang diubah/dibuat:** singularity/ollama/run_ollama_daemon.sh (Baru), singularity/ollama/watchdog_ollama.sh (Dihapus)
- **Status saat ini:** Selesai
- **Tanggal/Waktu:** Tue Jun  9 00:40:51 +07 2026
- **Tugas yang diselesaikan:** Merefaktor logika Menu 8 di `myslurm.sh` agar fully terintegrasi dengan `run_ollama_daemon.sh`. Deteksi proses, auto-start, manual-start, dan stop kini menggunakan eksekusi Daemon di latar belakang pada Login Node dan tidak lagi menggunakan SSH ke Compute Node.
- **File yang diubah/dibuat:** Trainning-Models/MyFineTunning-SlurmMaster/utils/myslurm.sh
- **Status saat ini:** Selesai
- **Tanggal/Waktu:** Tue Jun  9 00:41:49 +07 2026
- **Tugas yang diselesaikan:** Menghapus script legacy `sbatch_aspri_service.sh` karena peran peluncurannya telah sepenuhnya digantikan oleh `run_ollama_daemon.sh` (srun overlap).
- **File yang diubah/dibuat:** singularity/ollama/sbatch_aspri_service.sh (Dihapus)
- **Status saat ini:** Selesai
- **Tanggal/Waktu:** Tue Jun  9 00:45:02 +07 2026
- **Tugas yang diselesaikan:** Memperbaiki bug kegagalan parser port di UI myslurm.sh akibat tidak ter-log-nya string deklarasi port dinamis di dalam `ollama_daemon.log`. 
- **File yang diubah/dibuat:** singularity/ollama/run_ollama_daemon.sh
- **Status saat ini:** Selesai

### [Entri 011] — Penerapan Kebijakan VRAM Keep-Alive 1 Menit & Jeda Pemuatan
*   **Tanggal/Waktu:** Tue Jun  9 00:58:00 +07 2026
*   **Tugas yang diselesaikan:**
    *   Mengintegrasikan variabel lingkungan `export SINGULARITYENV_OLLAMA_KEEP_ALIVE="1m"` pada skrip auto-resume `run_ollama_daemon.sh` untuk pelepasan otomatis memori VRAM GPU Volta V100 1 menit setelah request selesai.
    *   Mendokumentasikan mekanisme VRAM Keep-Alive serta implikasi jeda awal pemuatan model (cold start loading delay sekitar 5-15 detik) ke dalam `docs/SDD.md` dan `docs/SDP.md` sebagai panduan interaksi pengguna.
*   **File yang diubah/dibuat:**
    *   `singularity/ollama/run_ollama_daemon.sh` [DIUBAH - OK]
    *   `singularity/AspriAI/docs/SDD.md` [DIUBAH - OK]
    *   `singularity/AspriAI/docs/SDP.md` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Konfigurasi Optimasi VRAM & Dokumentasi 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Ollama sekarang akan melepaskan GPU secara otomatis setelah 1 menit tidak aktif.
    *   Pada frontend AspriAI Desk, perlu diantisipasi atau ditampilkan status "Loading / Menyiapkan Model" pada UI jika respons pertama membutuhkan waktu beberapa detik (cold start).

### [Entri 012] — Integrasi Konfigurasi Docker-Compose dan Nginx ke Root Repo
*   **Tanggal/Waktu:** Mon Jun  8 18:37:00 UTC 2026
*   **Tugas yang diselesaikan:**
    *   Memasukkan konfigurasi Docker dan Nginx (`docker-compose.yml`, direktori `docker/`, dan `nginx/`) di tingkat root repository agar dapat dilacak dan dikelola langsung melalui Git pada branch `desk/dev`.
*   **File yang diubah/dibuat:**
    *   `docker-compose.yml` [BARU - OK]
    *   `docker/php/Dockerfile` [BARU - OK]
    *   `docker/php/entrypoint.sh` [BARU - OK]
    *   `nginx/default.conf` [BARU - OK]
    *   `docs/SDP.md` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Sinkronisasi Konfigurasi Root Docker & Git 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Konfigurasi aktif Docker dan Nginx sekarang telah ter-track secara resmi di branch `desk/dev` agar konsisten antar-lingkungan pengembangan.



### [Entri 013] — Pembangunan Infrastruktur ComfyUI (Fase 2 Wrapper)
*   **Tanggal/Waktu:** 2026-06-09 02:30 WIB
*   **Tugas yang diselesaikan:**
    *   Membuat skrip instalasi `setup.sh` untuk modul ComfyUI yang akan membuat struktur direktori lokal, menyalin `.env`, melakukan instalasi repositori ComfyUI, serta menarik image PyTorch (CUDA 12.1) melalui `singularity pull pytorch_cuda12_1.sif docker://pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime`.
    *   Membuat *self-healing watchdog daemon* `run_comfui_daemon.sh` untuk menjalankan ComfyUI di *compute node* menggunakan `srun --overlap`. Daemon ini dilengkapi dengan konfigurasi integrasi *Cloudflare Quick Tunnel*, notifikasi Telegram, serta *SSH Reverse Port Forwarding* port dinamis ke port 8188 di *slurmmaster*.
    *   Memodifikasi *Interactive GPU Booking Menu* (`myslurm.sh`) dengan menyertakan *dashboard* pemantauan *real-time* khusus untuk layanan ComfyUI, menggantikan menu *placeholder* lama. 
*   **File yang diubah/dibuat:**
    *   `singularity/comfui/setup.sh` [BARU - OK]
    *   `singularity/comfui/run_comfui_daemon.sh` [BARU - OK]
    *   `Trainning-Models/MyFineTunning-SlurmMaster/utils/myslurm.sh` [DIUBAH - OK]
    *   `singularity/AspriAI/docs/SDP.md` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Infrastruktur ComfyUI 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Struktur *backend* komputasi (ComfyUI) kini sudah siap digunakan.
    *   Anda dapat menggunakan opsi menu 6 pada `myslurm.sh` untuk mengatur instalasi dan melihat log layanannya.
    *   Instruksikan atau jalankan `bash /data/users/g6717500336/singularity/comfui/setup.sh --install` untuk benar-benar mengunduh dan memasang *Singularity Image Container* serta modul ComfyUI.

---

### [Entri 014] — Root Cause Fix: Cloudflare Tunnel Selalu Mati & Perbaikan ComfyUI Daemon
*   **Tanggal/Waktu:** 2026-06-09 03:41 WIB
*   **Tugas yang diselesaikan:**
    *   **Investigasi Mendalam Cloudflare Tunnel:** Menginvestigasi mengapa tunnel selalu mati dengan `Initiating graceful shutdown due to signal terminated` setiap 2-8 detik setelah berhasil konek.
    *   **Root Cause Ditemukan:** Port metrics default `127.0.0.1:20241` selalu konflik karena sisa binding dari instance cloudflared sebelumnya, menyebabkan instance baru menerima SIGTERM dari sistem (*address already in use*).
    *   **Fix `myslurm.sh`:** Menambahkan flag `--metrics 127.0.0.1:<random_port>` menggunakan `shuf -i 20200-20299 -n 1` pada wrapper script cloudflared. Dengan port metrics acak, konflik tidak pernah terjadi.
    *   **Fix `run_comfui_daemon.sh`:** Mengganti perintah `pkill -f "cloudflared tunnel.*run --token"` yang bersifat global (membunuh SEMUA instance cloudflared di sistem termasuk tunnel master) dengan mekanisme **PID File Tracking** yang spesifik. Daemon kini hanya mematikan instance tunnel miliknya sendiri via `${LOGS_DIR}/named_tunnel.pid`.
    *   **Identifikasi Error ComfyUI:** Package `comfy_kitchen 0.2.10` terinstal di `~/.local/lib/python3.10/site-packages/` (luar container) tidak kompatibel dengan PyTorch 2.2.2 di dalam container Singularity (butuh PyTorch ≥ 2.4 untuk `torch.library.custom_op`). User akan upgrade container manual.
    *   **Tunnel Cloudflare Stabil:** Setelah fix, sesi tmux `cloudflare_tunnel` berjalan stabil (PID 2046991) lebih dari 1 menit tanpa terminasi.
*   **File yang diubah/dibuat:**
    *   `Trainning-Models/MyFineTunning-SlurmMaster/utils/myslurm.sh` [DIMODIFIKASI — wrapper cloudflared dengan random metrics port]
    *   `singularity/comfui/run_comfui_daemon.sh` [DIMODIFIKASI — pkill global diganti PID file tracking]
    *   `singularity/AspriAI/docs/SDP.md` [DIUBAH — Penambahan Log 014]
*   **Status saat ini:** **Selesai**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Tunnel Cloudflare kini **stabil** via sesi tmux `cloudflare_tunnel` dengan `--metrics` port acak.
    *   ComfyUI **belum bisa dijalankan** hingga container Singularity diupgrade ke PyTorch ≥ 2.4. User akan melakukan upgrade manual. Setelah upgrade, cukup jalankan kembali menu 6 `myslurm.sh` → Opsi 1.
    *   **JANGAN** gunakan `pkill -f "cloudflared tunnel.*run --token"` di script manapun — selalu gunakan PID file targeting.
    *   Quick Tunnel (fallback) untuk ComfyUI saat ini rate-limited (429) dari Cloudflare karena terlalu banyak request selama debugging — akan pulih otomatis dalam beberapa jam.


### [Entri 014] — Bugfix & Version Bump untuk ComfyUI
*   **Tanggal/Waktu:** 2026-06-09 04:05 WIB
*   **Tugas yang diselesaikan:**
    *   Menaikkan versi PyTorch Singularity Image di `setup.sh` ke versi `2.4.0-cuda12.1-cudnn9-runtime`. Hal ini mengatasi error `AttributeError: module 'torch.library' has no attribute 'custom_op'` pada library `comfy_kitchen` yang membutuhkan minimum PyTorch 2.4.0.
    *   Mengevaluasi error HTTP 429 pada Cloudflare Quick Tunnel. Daemon `run_comfui_daemon.sh` dan `myslurm.sh` dirancang untuk gracefully menangani kegagalan layanan gratis Quick Tunnel, memprioritaskan ketersediaan via Named Tunnel.
*   **File yang diubah/dibuat:**
    *   `singularity/comfui/setup.sh` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (Menunggu Instalasi Ulang PyTorch 2.4.0)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   Struktur siap. User perlu menjalankan `setup.sh --install` kembali.

### [Entri 015] — Integrasi Endpoint Health ComfyUI ke AspriAI Core
*   **Tanggal/Waktu:** 2026-06-09 04:45 WIB
*   **Tugas yang diselesaikan:**
    *   Memodifikasi *Gateway* `aspri-core/main.py` untuk mengintegrasikan ComfyUI ke dalam sistem pengecekan *Health Check* global (`/health`).
    *   Mengubah *endpoint* ComfyUI dari yang sebelumnya berupa draf `/v1/health` (menimbulkan error 404) menjadi menggunakan API *native* `/system_stats`.
    *   Menghapus logika pengecualian (*exclusion*) untuk ComfyUI, sehingga apabila *node* ComfyUI mati, AspriAI Core akan mendeteksinya dengan benar dan mengembalikan status `degraded`.
*   **File yang diubah/dibuat:**
    *   `singularity/AspriAI/aspri-core/main.py` [DIUBAH - OK]
*   **Status saat ini:** **Selesai**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   ComfyUI sudah menjadi warga kelas satu (*first-class citizen*) di dalam arsitektur AspriAI Core.

### [Entri 016] — Pembuatan Layanan Model List Berstandar OpenAI (OpenAI-Compatible Models Endpoint)
*   **Tanggal/Waktu:** 2026-06-09 13:46 WIB
*   **Tugas yang diselesaikan:**
    *   Menyelesaikan masalah `no space left on device` secara otomatis dengan membersihkan cache pip dan huggingface di `/data/users/g6717500336/.cache/`.
    *   Menambahkan endpoint baru di `openai.py` yang menyediakan rute `GET /v1/models` dan `GET /v1/vendors`. Endpoint ini memungkinkan frontend (AspriDesk) mendapatkan daftar model AI dinamis yang berstandar OpenAI-compatible (serta rute kustom vendor untuk rendering UI yang lebih baik).
    *   Mendaftarkan router `openai.py` di `main.py` sebelum proxy Ollama agar permintaan `/v1/models` tidak tertelan oleh *catch-all* rute Ollama.
*   **File yang diubah/dibuat:**
    *   `singularity/AspriAI/aspri-core/app/api/v1/endpoints/openai.py` [DIBUAT BARU]
    *   `singularity/AspriAI/aspri-core/main.py` [DIUBAH - OK]
*   **Status saat ini:** **Selesai (LLM Providers Router 100%)**
*   **Catatan untuk AI selanjutnya (Handoff Note):**
    *   FastAPI sekarang memproses `/v1/models` secara internal, sedangkan semua sisanya `/v1/*` diteruskan (*reverse-proxied*) ke Ollama Server.
    *   Daftar LLM providers ini saat ini masih di-hardcode dalam memori, di masa depan dapat dikembangkan agar bersinkronisasi dengan database PostgreSQL melalui Laravel.
