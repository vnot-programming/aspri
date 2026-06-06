# 🔗 Software Requirements and Design (SRD) — AspriAI

## 1. Pemetaan Kebutuhan ke Desain (Requirements-to-Design Mapping)

Untuk menjamin setiap kebutuhan fungsional (FR) yang didefinisikan dalam SRS diimplementasikan dengan benar dalam arsitektur teknis SDD, berikut adalah tabel pemetaannya:

| ID Kebutuhan (SRS) | Modul Desain Terkait (SDD) | Komponen Teknis Realisasi |
|:---|:---|:---|
| **FR-A.1** (Autentikasi API Key) | Bab 2 (Tabel `api_keys`) & Bab 3 (Header Auth) | FastAPI `Security` dependency injection dengan validasi token hash SHA-256 dari SQLite. |
| **FR-A.2** (Manajemen Key di UI) | Bab 1 & Bab 2 (Tabel `api_keys`) | Dasbor Playground React/Next.js memanggil route `POST /v1/keys` dan `DELETE /v1/keys`. |
| **FR-A.3** (Routing API Terpadu) | Bab 3 (Spesifikasi Endpoints) | Pustaka `httpx` di FastAPI bertindak sebagai HTTP client asinkron untuk meneruskan payload. |
| **FR-B.1** (Chat Playground) | Bab 1 (Playground UI) | Komponen UI Next.js yang mendukung streaming token teks menggunakan pustaka Markdown renderer. |
| **FR-B.2** (Studio Playground) | Bab 1 & Bab 3.2 (ComfyUI Wrapper) | Form parameter Next.js mengirim data ke backend, yang memodifikasi node JSON workflow ComfyUI. |
| **FR-C.1** (Slurm Dispatcher) | Bab 1 (Slurm Integration) | Eksekusi utilitas sistem Python `subprocess.run(["sbatch", "job.sbatch"])` di backend FastAPI. |
| **FR-C.2** (Singularity Execution)| Bab 1 (Engine Layer) | Script wrapper sbatch memanggil `singularity exec --nv` dari direktori `/data/programs/`. |
| **FR-C.3** (CUDA Memory Flush) | Bab 1 (Engine Layer) | Python script memicu garbage collection dan `torch.cuda.empty_cache()` secara terjadwal setelah inferensi selesai. |

---

## 2. Justifikasi Pilihan Teknologi & Desain Sistem

### 2.1 Mengapa Memilih FastAPI untuk Backend (AspriAI Core)?
*   **Asynchronous Native:** FastAPI dibangun di atas Starlette dan Uvicorn, mendukung operasi asinkron (`async/await`) secara native. Ini sangat penting karena proses menunggu respon rendering gambar/video dari ComfyUI atau token teks dari Ollama memakan waktu beberapa detik. Operasi asinkron mencegah backend mengalami deadlock saat melayani banyak request paralel.
*   **Auto-Generated Documentation:** FastAPI secara otomatis memproduksi dokumentasi Swagger OpenAPI di `/docs`. Hal ini memudahkan developer eksternal saat ingin mengintegrasikan API Key AspriAI ke dalam bot pribadi atau editor kode.

### 2.2 Mengapa Memisahkan Frontend (AspriAI Desk) ke Lokasi Berbeda?
*   **Efisiensi VRAM:** Menyimpan antarmuka pengguna pada mesin terpisah (seperti VPS Azure) menjamin node GPU murni hanya terbebani proses rendering matematis model AI, menjaga stabilitas VRAM 32GB Tesla V100.
*   **Keamanan Jaringan:** Cluster GPU terlindungi di balik Tailscale/Intranet. Cloudflare Tunnel bertindak sebagai filter terdepan yang hanya membuka port API Gateway asinkron ke internet umum.

### 2.3 Mekanisme Integrasi ComfyUI Tanpa GUI
*   Untuk menjaga fleksibilitas, AspriAI Core tidak menulis ulang logika graf node di Python. Ia **mengonsumsi workflows JSON** hasil ekspor dari UI ComfyUI. Hal ini memudahkan kita jika di kemudian hari ingin mengganti model (misal dari Stable Diffusion ke Flux.1-Dev atau SVD ke CogVideoX) cukup dengan mengekspor file JSON alur kerja baru dari GUI dan meletakkannya di folder `workflows/` tanpa perlu membongkar kode backend FastAPI.
