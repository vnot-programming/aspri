# 📐 Software Design Document (SDD) — AspriAI

## 1. Desain Arsitektur Sistem

Sistem **AspriAI** dirancang menggunakan arsitektur modular terpisah (*decoupled architecture*):
1.  **Frontend (AspriAI Desk):** Laravel 13 + Tailwind CSS (menggunakan Blade/Livewire/Inertia). Hosted di server web/VPS CPU (tidak memerlukan GPU).
2.  **Backend (AspriAI Core):** FastAPI (Python). Dijalankan secara lokal di master node cluster GPU.
3.  **Engine layer:** Ollama (LLM), ComfyUI API (Image/Video), dan YOLO/SAM2 (Computer Vision).

```
┌─────────────────┐             ┌─────────────────┐             ┌──────────────────┐
│  AspriAI Desk   │             │   AspriAI Core  │             │   Slurm Cluster  │
│  (Laravel Web)  │             │    (FastAPI)    │             │   (ai2 / ai3)    │
└────────┬────────┘             └────────┬────────┘             └────────┬─────────┘
         │                               │                               │
         │ 1. Request (/v1/studio)       │                               │
         ├──────────────────────────────>│                               │
         │                               │ 2. Cek Antrean GPU            │
         │                               ├──────────────────────────────>│
         │                               │    (squeue / sacct)           │
         │                               │                               │
         │                               │ 3. Buat Job Slurm (sbatch)    │
         │                               ├──────────────────────────────>│
         │                               │    (Singularity + ComfyUI)    │
         │                               │                               │
         │                               │ 4. Koneksi WebSocket & JSON   │
         │                               ├──────────────────────────────>│
         │                               │    (Kirim workflow.json)      │
         │                               │                               │
         │                               │ 5. Monitor Render Status      │
         │                               │<==============================│
         │                               │                               │
         │                               │ 6. Ambil Hasil & Lepas GPU    │
         │                               ├──────────────────────────────>│
         │                               │    (scancel / empty_cache)    │
         │                               │                               │
         │ 7. Return Image/Video URL     │                               │
         │<──────────────────────────────┤                               │
```

---

## 2. Struktur Data & Skema Penyimpanan

Sesuai dengan arsitektur *decoupled*, **AspriAI Core (Backend) bersifat 100% Stateless**. Backend tidak lagi menggunakan SQLite lokal. Seluruh manajemen state, manajemen pengguna, *Personal API Keys*, hingga log aktivitas sepenuhnya dikendalikan oleh **Frontend AspriAI Desk (Laravel)** melalui infrastruktur terpusat di Docker Host.

Infrastruktur penyimpanan (terisolasi di `docker-host`):
*   **PostgreSQL:** Basis data relasional utama untuk manajemen `users`, `api_keys`, dan `activity_logs`.
*   **Redis:** Digunakan untuk *caching*, manajemen *session*, dan antrean *job queue* (Horizon) untuk tugas asinkron di ekosistem Laravel.
*   **MinIO:** Penyimpanan objek bertipe S3 untuk menampung gambar/video hasil *generate*, log sistem, dan aset media lainnya secara terpusat.

---

## 3. Spesifikasi API Endpoints

Semua request wajib menyertakan header autentikasi: `Authorization: Bearer <PERSONAL_API_KEY>`

### 3.1 LLM Chat (Ollama Proxy)
*   **Endpoint:** POST `/v1/chat/completions`
*   **Payload:**
    ```json
    {
      "model": "llama3",
      "messages": [
        {"role": "user", "content": "Halo Aspri, bantu tulis fungsi Python."}
      ],
      "temperature": 0.7
    }
    ```
*   **Response:** Kompatibel dengan format OpenAI Chat Completions.

### 3.2 Image Generation (ComfyUI Wrapper)
*   **Endpoint:** POST `/v1/studio/txt2img`
*   **Payload:**
    ```json
    {
      "prompt": "Vibrant digital art of a neural network glowing in dark cyan color",
      "negative_prompt": "blurry, low quality, distorted",
      "aspect_ratio": "16:9",
      "steps": 25,
      "seed": -1
    }
    ```
*   **Response:**
    ```json
    {
      "task_id": "job_984712",
      "status": "SUCCESS",
      "output_url": "https://api-ai.penelitian.my.id/outputs/job_984712.png",
      "execution_time_sec": 4.8
    }
    ```

---

## 4. Arsitektur Keamanan & Jaringan

Untuk mengamankan API LLM (Ollama) yang diekspos ke internet publik tanpa membebani server lokal dengan proses otentikasi komputasional (seperti menginstal Web Server untuk memvalidasi *Bearer Token* di sisi Slurm), sistem menerapkan **Cloudflare Access Zero Trust Service Tokens** melalui **Cloudflare Named Tunnel** (bukan *Quick Tunnel* yang dinamis agar lebih aman dan persisten saat restart):

```
[ Client App (WebUI/Postman) ]
            │
            │  1. HTTP Request dengan header:
            │     - CF-Access-Client-Id: <ID>
            │     - CF-Access-Client-Secret: <SECRET>
            ▼
┌───────────────────────────────┐
│     Cloudflare Edge Proxy     │
│  (Validasi Token Zero Trust)  │
└───────────────┬───────────────┘
                │
                │  2. Lolos Autentikasi -> Diteruskan via Tunnel
                ▼
┌───────────────────────────────┐
│       Cloudflared Agent       │
│  - Rewrite Host -> localhost  │ (Opsi: --http-host-header localhost)
└───────────────┬───────────────┘
                │
                │  3. Diteruskan ke Port internal compute node
                ▼
┌───────────────────────────────┐
│      Ollama Service (SIF)     │
│    - Host Bind: 0.0.0.0       │ (Mengizinkan akses lintas domain)
└───────────────────────────────┘
```

### 4.1 Mekanisme Otentikasi Lapis Jaringan
* **Cloudflare Access Policy:** Subdomain `backend-ollama.penelitian.my.id` diproteksi secara penuh di sisi gerbang Cloudflare. Klien wajib mengirimkan header HTTP berikut untuk menembusnya:
  * `CF-Access-Client-Id`
  * `CF-Access-Client-Secret`
* **Host Header Rewrite:** Dikarenakan Ollama memproteksi request dari luar localhost ketika Host Header tidak cocok, biner `cloudflared` lokal dikonfigurasi dengan flag `--http-host-header localhost`. Flag ini menulis ulang header `Host` menjadi `localhost` sebelum diteruskan ke server Ollama lokal, meniadakan error *403 Forbidden*.
* **Ollama Host Binding:** Server Ollama di dalam kontainer Singularity diikat ke host `0.0.0.0:${OLLAMA_PORT}` untuk menerima request internal yang dirutekan oleh *agent* Cloudflared.
* **Isolasi Izin File Lokal:** Berkas konfigurasi `.env` lokal dilindungi secara ketat di server dengan permission `600` (eksklusif hanya untuk pemilik user). Kunci privat SSH administratif (`SSH_PRIVATE_KEY_BASE64`) tidak disimpan secara lokal, melainkan disimpan eksklusif pada **GitHub Secrets** untuk keamanan terisolasi.
