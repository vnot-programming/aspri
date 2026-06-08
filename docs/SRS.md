# 📋 Software Requirements Specification (SRS) — AspriAI

## 1. Pendahuluan

### 1.1 Tujuan
Dokumen ini mendefinisikan kebutuhan perangkat lunak (fungsional dan non-fungsional) untuk proyek **AspriAI (Asisten Pribadi AI)**. Tujuan dari dokumen ini adalah memastikan keselarasan fitur yang dibangun dengan kebutuhan bisnis pengguna dalam memusatkan layanan AI (Ollama, ComfyUI, YOLO/SAM2) di dalam satu gerbang API terpadu yang aman.

### 1.2 Cakupan Sistem
Sistem AspriAI terdiri atas dua subsistem utama:
1.  **AspriAI Core (Backend):** Layanan API Gateway *Stateless* berbasis FastAPI yang membungkus pemanggilan model AI di cluster Slurm menggunakan kontainer Singularity.
2.  **AspriAI Desk (Frontend):** Dasbor bermain web terpisah berbasis Laravel 13 (didukung PostgreSQL, Redis, dan MinIO di *Docker Host* eksternal) dengan antarmuka bertema *Bio-Digital Minimalism* untuk interaksi visual dan manajemen API Key.

---

## 2. Kebutuhan Fungsional (Functional Requirements)

Sistem wajib mendukung fitur-fitur fungsional berikut yang dikelompokkan ke dalam 4 modul utama:

### Modul A: API Gateway & Keamanan
*   **FR-A.1 (Autentikasi API Terpusat):** Gateway wajib menolak semua permintaan tanpa *Personal API Key* yang valid.
*   **FR-A.2 (Manajemen Pengguna & API Key):** Frontend Laravel wajib memiliki fitur registrasi/login pengguna. Pengguna dapat membuat, memantau riwayat pemanggilan, dan menghapus API Key mereka melalui antarmuka dasbor web, dengan seluruh data disimpan pada PostgreSQL di *Docker Host*.
*   **FR-A.3 (Routing API Terpadu):**
    *   `/v1/chat/completions` -> Diteruskan ke Ollama.
    *   `/v1/studio/txt2img` -> Diteruskan ke ComfyUI (Flux/SDXL).
    *   `/v1/studio/img2video` -> Diteruskan ke ComfyUI Video (SVD).
    *   `/v1/vision/detect` -> Diteruskan ke detektor gambar YOLOv11/SAM2.
*   **FR-A.4 (Integrasi Cloudflare Access):** Semua request API eksternal ke domain utama `backend-ollama.penelitian.my.id` wajib melewati otentikasi Cloudflare Access dengan menyertakan header `CF-Access-Client-Id` dan `CF-Access-Client-Secret`.

### Modul B: AspriAI Desk (Playground Dasbor)
*   **FR-B.1 (Chat Playground):** Menyajikan obrolan interaktif ala ChatGPT/Claude untuk melakukan tanya jawab bahasa, perancangan teks, atau bantuan penulisan kode program.
*   **FR-B.2 (Studio Playground):** Menyediakan form sederhana untuk memasukkan prompt teks, mengunggah gambar referensi, memilih tipe output (gambar/video), dan mengunduh hasil eksekusi generatif.
*   **FR-B.3 (Vision Playground):** Mengunggah berkas gambar untuk melihat hasil anotasi bounding box (deteksi objek) dan kontur piksel (segmentasi instance) secara visual.

### Modul C: Integrasi Slurm & Singularity (Backend Operator)
*   **FR-C.1 (Slurm Job Dispatcher):** Sistem harus mampu menyusun file sbatch peluncur secara otomatis dan mengirimkannya (`sbatch`) ke antrean Slurm ketika ada task generatif masuk.
*   **FR-C.2 (Singularity Execution):** Seluruh inferensi model wajib dieksekusi di dalam kontainer Singularity dengan binding driver NVIDIA (`--nv`) dan bind-mount folder weights.
*   **FR-C.3 (CUDA Memory Flush):** Sistem wajib memicu pembersihan cache memori GPU setelah eksekusi job selesai untuk menjaga VRAM kluster tetap optimal.

---

## 3. Kebutuhan Non-Fungsional (Non-Functional Requirements)

*   **NFR-1 (Keamanan Data - Privacy):** Semua data prompt, gambar, dan video yang diproses tidak boleh dikirim ke luar server lokal. Seluruh inferensi wajib berjalan *self-hosted*.
*   **NFR-2 (Ketersediaan - Availability):** Dasbor Frontend wajib dapat diakses 24/7 di luar jaringan lokal via Cloudflare Tunnel HTTPS dengan proteksi SSL penuh.
*   **NFR-3 (Efisiensi Sumber Daya):** Kontainer Singularity ComfyUI hanya boleh memakan alokasi GPU saat proses render aktif, dan harus melepas GPU (`scancel`) setelah selesai agar antrean Slurm tidak terhambat.
*   **NFR-4 (Estetika Antarmuka - UI/UX):** Tampilan dasbor web wajib mengadopsi standar *Bio-Digital Minimalism 2026*, mendukung mode terang/gelap secara sinkron dengan preferensi OS, ergonomis untuk layar ponsel (zona sentuh minimal 44x44px), dan aman untuk penderita buta warna.
*   **NFR-5 (Isolasi Kredensial & Pengamanan File Env):** Sistem wajib memisahkan token otentikasi administratif (SSH Deploy via GitHub Secrets) dan token API klien (API Access via `.env` lokal). Berkas kredensial lokal wajib dilindungi dengan permission ketat (`600`) di server host.
