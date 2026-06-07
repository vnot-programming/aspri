# 🧪 Software Test Document (STD) — AspriAI

## 1. Rencana Pengujian (Testing Plan)

Strategi pengujian AspriAI berfokus pada jaminan keandalan pengiriman instruksi (*job dispatching*) ke GPU cluster, keakuratan autentikasi API, serta stabilitas pembersihan cache memori CUDA untuk mencegah kegagalan *Out-Of-Memory* (OOM).

### Tingkat Pengujian:
1.  **Unit Testing:** Validasi logika pembuatan hash token API, parser JSON workflow ComfyUI, dan routing request di FastAPI.
2.  **Integration Testing:** Pengujian koneksi asinkron FastAPI ke port Ollama (11434), ComfyUI WebSocket (8188), dan pengiriman job ke Slurm Manager (`sbatch`).
3.  **UI/UX Accessibility Testing:** Pengujian responsivitas dasbor di layar ponsel dan simulasi visual dual-theme (terang/gelap) serta buta warna.
4.  **Load/Stress Testing:** Simulasi 10 request generatif gambar secara simultan untuk memvalidasi performa antrean job Slurm.

---

## 2. Kasus Uji (Test Cases)

### 2.1 Pengujian Unit & Integrasi Backend API

| ID Test | Kategori | Deskripsi Uji | Input yang Diberikan | Hasil yang Diharapkan | Status Target |
|:---|:---|:---|:---|:---|:---|
| **TC-B-01** | Keamanan | Akses API tanpa menyertakan API Key. | `GET /v1/chat` (tanpa Header) | HTTP 401 Unauthorized, dengan pesan `"Missing API Key"`. | Wajib Lolos |
| **TC-B-02** | Keamanan | Akses API dengan kunci palsu/salah. | `GET /v1/chat` (Header: `Bearer salah_key`) | HTTP 403 Forbidden, dengan pesan `"Invalid API Key"`. | Wajib Lolos |
| **TC-B-03** | Integrasi | Proxy chat ke Ollama dengan model valid. | `POST /v1/chat/completions` (model: "llama3") | HTTP 200 OK, mengembalikan token teks bahasa secara streaming. | Wajib Lolos |
| **TC-B-04** | Integrasi | Trigger render gambar ke ComfyUI via API JSON. | `POST /v1/studio/txt2img` (prompt: "cat") | HTTP 200 OK, server mengembalikan status `SUCCESS` dan file URL gambar. | Wajib Lolos |
| **TC-B-05** | Keamanan | Akses domain utama tanpa header Cloudflare Access. | `GET https://backend-ollama.penelitian.my.id/api/tags` | HTTP 403 Forbidden (Ditolak oleh Cloudflare Access Edge). | Wajib Lolos |
| **TC-B-06** | Keamanan | Akses domain utama dengan header Cloudflare Access valid. | `GET https://backend-ollama.penelitian.my.id/api/tags` (Header: `CF-Access-*` valid) | HTTP 200 OK, server mengembalikan status JSON daftar model. | Wajib Lolos |

### 2.2 Pengujian Integrasi Slurm & Singularity

| ID Test | Kategori | Deskripsi Uji | Input yang Diberikan | Hasil yang Diharapkan | Status Target |
|:---|:---|:---|:---|:---|:---|
| **TC-S-01** | Slurm | Pembuatan job otomatis via sbatch. | Memicu render dari API | Sistem FastAPI berhasil menjalankan perintah `sbatch` dan melacak JobID Slurm. | Wajib Lolos |
| **TC-S-02** | Singularity| Eksekusi terisolasi di dalam kontainer. | Menjalankan kontainer comfyui | Model berjalan lancar dengan flag `--nv` tanpa menghasilkan CUDA driver error. | Wajib Lolos |
| **TC-S-03** | Memori | Pembersihan CUDA memori pasca eksekusi. | Job selesai | Sistem otomatis memicu script pembersih cache, memori bebas kembali ke >90%. | Wajib Lolos |

### 2.3 Pengujian Dasbor Playground (Frontend UI)

| ID Test | Kategori | Deskripsi Uji | Langkah Pengujian | Hasil yang Diharapkan | Status Target |
|:---|:---|:---|:---|:---|:---|
| **TC-U-01** | UI/UX | Responsivitas Tampilan Seluler. | Perkecil lebar layar browser ke <450px | Menu navigasi tebal tersembunyi ke dalam drawer, semua tombol sentuh berukuran min 44x44px. | Wajib Lolos |
| **TC-U-02** | UI/UX | Transisi Tema Gelap/Terang. | Klik tombol toggle tema di sudut kanan atas | Semua warna latar dan teks berubah harmonis (flicker-free) mengikuti preferensi. | Wajib Lolos |
| **TC-U-03** | A11y | Mitigasi Spektrum Buta Warna. | Aktifkan mode `partial-color-blind` | Skema warna peringatan/sukses bergeser dari merah-hijau ke biru-oranye kontras tinggi. | Wajib Lolos |

---

## 3. Eksekusi Pengujian Otomatis

Untuk menjalankan unit test backend secara berkala, developer dapat menggunakan pustaka `pytest` di dalam lingkungan virtual Python:
```bash
# Di dalam folder aspri-core
source /data/programs/anaconda3/bin/activate yolo_env
pip install pytest httpx
pytest -v tests/
```
