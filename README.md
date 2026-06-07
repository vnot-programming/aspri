# 🤖 AspriAI (Asisten Pribadi AI)

> **Your Private GPU Cluster, Your Personal Assistant.**
> 
> *Satu pintu gerbang cerdas untuk semua kebutuhan AI Anda—Bahasa, Generasi Visual, dan Visi Komputer.*

---

## 1. Laporan Analisis, Konsep Identitas & Slogan

### Laporan Analisis
Dalam ekosistem komputasi berbasis GPU yang dinamis, terdapat kebutuhan mendesak untuk memanfaatkan berbagai model kecerdasan buatan (LLM, Computer Vision, dan Generative Image/Video) secara efisien dan terpusat. Masalah utama yang sering dihadapi adalah fragmentasi layanan, konsumsi VRAM GPU yang tidak terpantau, serta kompleksitas integrasi ke aplikasi klien seperti Telegram, Discord, Line, atau editor kode. 

**AspriAI** dirancang untuk menyelesaikan fragmentasi ini dengan bertindak sebagai **Personal AI API Gateway & Playground** mandiri yang berjalan di atas kluster GPU Slurm (menggunakan kontainer Singularity).

### Konsep Identitas
*   **Aman & Terisolasi:** Berjalan penuh secara mandiri (*self-hosted*) tanpa mengirimkan data ke pihak ketiga.
*   **API-First & Modular:** Mengekspos API terpadu yang kompatibel dengan berbagai integrasi eksternal.
*   **Visual-Friendly:** Menyembunyikan kompleksitas komputasi belakang layar (seperti alur kerja node ComfyUI) dengan menghadirkan dasbor bermain (*Playground*) yang bersih dan minimalis.

### Slogan
> *"Your Private GPU Cluster, Your Personal Assistant."*

---

## 2. Network Topology & Ecosystem Map

Sistem ini memisahkan secara ketat (*decoupled*) antara penyedia komputasi berat (GPU cluster) dan antarmuka interaksi pengguna (Frontend):

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PUBLIC INTERNET (WAN)                           │
│              (Akses luar via Cloudflare Tunnel SSL HTTPS)              │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTPS
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND: AspriAI Desk (UI)                       │
│ • Hosted di VPS Azure (VPS-4C56G - 100.70.118.53)                      │
│ • Atau Docker Host (vm100 - 100.90.5.60)                               │
│ • Teknologi: Next.js + Tailwind CSS (Bio-Digital Minimalism Style)     │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTP/WebSockets (Cloudflare Tunnel)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 BACKEND GATEWAY: AspriAI Core                          │
│ • Hosted di Login/Compute Node GPU Slurm (ai2 / ai3 - 100.111.139.127)  │
│ • Teknologi: FastAPI (Python) di dalam Singularity Container           │
└────────────────┬─────────────────┼──────────────────┬──────────────────┘
                 │                 │                  │
                 ▼                 ▼                  ▼
   ┌───────────────────┐    ┌───────────────┐   ┌──────────────┐
   │    Ollama (LLM)   │    │  ComfyUI API  │   │   YOLO/SAM2  │
   │   (Port 11434)    │    │  (Port 8188)  │   │ (Port 8502)  │
   └───────────────────┘    └───────────────┘   └──────────────┘
```

---

## 3. Rencana Struktur Proyek

Proyek ini dipisahkan menjadi dua repositori/folder mandiri untuk menyederhanakan siklus hidup pengembangan:

```
/data/users/g6717500336/singularity/AspriAI/
├── aspri-core/               # Python FastAPI (Backend API Gateway)
│   ├── app.py                # Server entry point
│   ├── config.py             # Konfigurasi port, path Singularity, dll.
│   ├── requirements.txt      # Dependensi python FastAPI
│   ├── routers/              # Endpoint routing
│   │   ├── chat.py           # Endpoint proxy ke Ollama
│   │   ├── studio.py         # Endpoint eksekusi workflow ComfyUI
│   │   └── vision.py         # Endpoint deteksi gambar (YOLO/SAM2)
│   └── workflows/            # Kumpulan file JSON API ComfyUI
│       ├── txt2img_flux.json
│       └── img2video_svd.json
│
├── aspri-desk/               # Next.js App (Frontend Playground)
│   ├── package.json          # Dependensi Next.js & Tailwind CSS
│   ├── tailwind.config.js    # Konfigurasi token visual Bio-Digital
│   └── src/
│       └── app/              # Struktur folder Next.js App Router
│
└── docs/                     # Dokumentasi Standar Rekayasa Perangkat Lunak
    ├── SRS.md                # Software Requirements Specification
    ├── SDD.md                # Software Design Document
    ├── SRD.md                # Software Requirements and Design
    ├── STD.md                # Software Test Document
    └── SDP.md                # Software Development Plan
```

---

## 4. Bagaimana ComfyUI Bekerja sebagai API Engine (Tanpa GUI)?

ComfyUI tidak hanya menyediakan antarmuka visual berupa graf node, melainkan dapat bertindak sebagai API Engine murni tanpa GUI (*headless*). Alur kerjanya adalah sebagai berikut:

1.  **Ekspor Alur Kerja (Workflow):** Developer mengaktifkan *"Dev mode"* di pengaturan ComfyUI dan mengekspor alur kerja node menjadi berkas JSON dengan menekan tombol **"Save (API Format)"**.
2.  **Pemetaan Parameter:** Backend FastAPI Kortex akan memuat file JSON tersebut ke memori. Saat pengguna mengirimkan prompt baru dari dasbor/klien:
    *   Backend mencari ID node bertipe *CLIPTextEncode* (Prompt) dan mengubah input teksnya.
    *   Backend mencari ID node bertipe *KSampler* (Seed/Langkah) dan menyesuaikan nilainya.
3.  **Pengiriman Request:** Backend mengirimkan payload JSON yang telah dimodifikasi melalui HTTP POST ke endpoint `/prompt` milik server ComfyUI (Port 8188).
4.  **Dengarkan WebSocket:** Backend membuka koneksi WebSocket ke ComfyUI untuk mendengarkan kemajuan eksekusi (*progress tracking*) secara real-time.
5.  **Pengambilan Output:** Begitu ComfyUI mengirimkan status *Execution Success*, backend mengunduh gambar/video yang dihasilkan dari endpoint `/view` dan mengirimkannya kembali ke dasbor pengguna atau bot pesan.

---

## 5. Tugas Utama Dasbor AspriAI

*   **Penyedia Kunci API Kustom (Personal API Keys):**
    Menyediakan halaman dasbor untuk memproduksi, melacak, dan menghapus *Personal API Keys*. API Key ini digunakan sebagai pembungkus autentikasi yang aman ketika bot Telegram, Discord, Line, atau ekstensi VS Code Anda memanggil API Gateway AspriAI Core.
*   **Playground Interaktif Multi-Model:**
    Menyajikan antarmuka visual yang menawan untuk:
    *   *Chat Arena:* Berinteraksi secara kontekstual dengan LLM (Ollama).
    *   *Creative Studio:* Membuat gambar (Flux/SDXL) dan video (SVD/CogVideoX) secara terpadu.
    *   *Vision Lab:* Menguji deteksi/segmentasi gambar secara real-time.
*   **Antrean Job GPU Slurm Otomatis:**
    Dasbor memantau utilisasi GPU server. Ketika sebuah instruksi generatif dipicu, sistem akan secara dinamis menyusun dan mengirimkan job Slurm (`sbatch`) di balik layar, mengarahkan kontainer Singularity ke GPU yang menganggur, dan membersihkan memori CUDA sesaat setelah job selesai.

---

## 6. Keuntungan Memisahkan Frontend dan Backend

1.  **Proteksi Sumber Daya GPU:** Rendering halaman antarmuka Next.js tidak menyedot memori VRAM GPU. Dengan pemisahan ini, kapasitas 32GB VRAM GPU Tesla V100 sepenuhnya dialokasikan untuk inferensi model generatif.
2.  **Isolasi Jaringan (Security):** GPU Node yang berada di jaringan lokal privat tidak langsung terekspos ke internet. Akses luar hanya dijembatani oleh Cloudflare Tunnel menuju API Gateway, sedangkan Frontend dapat ditempatkan pada VPS luar yang aman.
3.  **Kemandirian Deployment:** Anda bebas melakukan pembaruan antarmuka web, merancang ulang gaya visual CSS, atau menambahkan fitur UI di Next.js tanpa perlu mengganggu stabilitas jalannya layanan Ollama dan ComfyUI di GPU cluster.

---
*Last updated: 2026-06-07*
