# 📋 Software Development Plan (SDP) — AspriAI

## 1. Fase Pengembangan & Milestone

Proyek **AspriAI (Asisten Pribadi AI)** direncanakan berjalan dalam 4 fase pengembangan yang terstruktur:

```mermaid
gantt
    title Peta Jalan Pengembangan AspriAI (2026)
    dateFormat  YYYY-MM-DD
    section Fase 1: Core API Gateway
    Inisiasi Proyek & Dokumentasi docs/   :active, des1, 2026-06-07, 1d
    Pembangunan FastAPI Core & Integrasi SQLite : des2, after des1, 3d
    Konektivitas Ollama & YOLO Routing          : des3, after des2, 2d
    section Fase 2: ComfyUI API Wrapper
    Eksport & Integrasi JSON workflows         : des4, after des3, 3d
    WebSocket Listener untuk Render Progress    : des5, after des4, 2d
    section Fase 3: Slurm Orchestrator
    Sbatch Script generator & Job Queuer        : des6, after des5, 3d
    CUDA Memory Cleanup daemon                  : des7, after des6, 1d
    section Fase 4: Playground UI (AspriDesk)
    Next.js Setup & UI Design System            : des8, after des7, 3d
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
