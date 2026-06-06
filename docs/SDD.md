# 📐 Software Design Document (SDD) — AspriAI

## 1. Desain Arsitektur Sistem

Sistem **AspriAI** dirancang menggunakan arsitektur modular terpisah (*decoupled architecture*):
1.  **Frontend (AspriAI Desk):** Next.js (App Router) + Tailwind CSS. Hosted di server web/VPS CPU (tidak memerlukan GPU).
2.  **Backend (AspriAI Core):** FastAPI (Python). Dijalankan secara lokal di master node cluster GPU.
3.  **Engine layer:** Ollama (LLM), ComfyUI API (Image/Video), dan YOLO/SAM2 (Computer Vision).

```
┌─────────────────┐             ┌─────────────────┐             ┌──────────────────┐
│  AspriAI Desk   │             │   AspriAI Core  │             │   Slurm Cluster  │
│  (Next.js Web)  │             │    (FastAPI)    │             │   (ai2 / ai3)    │
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

Untuk mengelola autentikasi *Personal API Keys* dan riwayat aktivitas secara ringan, AspriAI Core menggunakan database relasional berbasis **SQLite** (lokal di server):

### Tabel: `api_keys`
Menyimpan data API Key pengguna untuk keperluan otentikasi eksternal.

| Nama Kolom | Tipe Data | Atribut | Deskripsi |
|:---|:---|:---|:---|
| `id` | INTEGER | Primary Key, Auto Increment | ID unik record |
| `key_name` | VARCHAR(50) | Not Null | Label/nama pengenal API Key (misal: "VSCode-Cline") |
| `api_key` | VARCHAR(64) | Not Null, Unique | Hash API Key untuk validasi request |
| `created_at` | TIMESTAMP | Default Current | Waktu pembuatan kunci |
| `last_used_at`| TIMESTAMP | Nullable | Waktu terakhir pemanggilan API |
| `is_active` | BOOLEAN | Default True | Status keaktifan kunci |

### Tabel: `activity_logs`
Mencatat riwayat eksekusi task untuk monitoring kuota dan analisis performa GPU.

| Nama Kolom | Tipe Data | Atribut | Deskripsi |
|:---|:---|:---|:---|
| `id` | INTEGER | Primary Key, Auto Increment | ID unik record |
| `api_key_id` | INTEGER | Foreign Key -> `api_keys.id` | Kunci yang digunakan |
| `task_type` | VARCHAR(20) | Not Null | Jenis tugas (`llm_chat`, `txt2img`, `img2video`, `cv`) |
| `prompt` | TEXT | Nullable | Input teks prompt yang dikirim |
| `status` | VARCHAR(15) | Not Null | Status job (`SUCCESS`, `FAILED`, `RUNNING`) |
| `duration_ms` | INTEGER | Nullable | Lama waktu rendering dalam milidetik |
| `gpu_id` | INTEGER | Nullable | Indeks GPU Slurm yang memproses job |

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
