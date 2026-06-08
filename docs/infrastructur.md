Berikut adalah konfigurasi lengkap untuk **Proyek Infrastruktur (Shared)** agar dapat digunakan secara global oleh Aplikasi A dan Aplikasi B di `docker-host`.

Konsep kuncinya adalah: **Satu folder infrastruktur** yang menjalankan database/layanan, dan **Aplikasi AspriAI & B hanya "menumpang"** jaringan tersebut tanpa menjalankan database sendiri.

### 1. Struktur Folder
Buatlah struktur direktori seperti ini di `docker-host` Anda:

```text
/home/my/
├── utils/
│   └── infrastructure/          # <-- PUSAT KENDALI (Database, Redis, Minio)
│       ├── docker-compose.yml
│       └── .env
├── apps/
│   └── AspriAI/                # <-- Aplikasi A (PHP 8.5)
│       ├── docker-compose.yml
│       └── .env
└── apps/
    └── ProyekB/                # <-- Aplikasi B (PHP 8.5)
        ├── docker-compose.yml
        └── .env
```

---

### 2. Konfigurasi Proyek Infrastruktur (Shared)
File ini bertugas membuat **Network Global** dan menjalankan layanan bersama.

**Lokasi:** `/home/my/utils/infrastructure/docker-compose.yml`

```yaml
version: '3.8'

services:
  # --- POSTGRES GLOBAL ---
  postgres:
    image: postgres:15-alpine
    container_name: shared-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${GLOBAL_DB_NAME}
      POSTGRES_USER: ${GLOBAL_DB_USER}
      POSTGRES_PASSWORD: ${GLOBAL_DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - global-net
    # TIDAK ADA PORTS (Lebih aman, hanya bisa diakses container lain)
    # Jika butuh akses dari luar (DBeaver), buka port: - "5432:5432"

  # --- REDIS GLOBAL ---
  redis:
    image: redis:7-alpine
    container_name: shared-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redisdata:/data
    networks:
      - global-net

  # --- MINIO GLOBAL ---
  minio:
    image: minio/minio:latest
    container_name: shared-minio
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    volumes:
      - miniodata:/data
    networks:
      - global-net
    # Opsional: Expose port jika perlu upload manual dari luar
    # ports:
    #   - "9000:9000"
    #   - "9001:9001"

  # --- NGINX PROXY (Opsional, untuk routing domain) ---
  # Jika Anda ingin satu Nginx depan untuk semua aplikasi
  nginx-proxy:
    image: nginx:alpine
    container_name: shared-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
    networks:
      - global-net
    depends_on:
      - postgres # Hanya contoh dependensi

networks:
  global-net:
    name: global-net       # Nama network PENTING, harus sama di semua proyek
    driver: bridge

volumes:
  pgdata:
  redisdata:
  miniodata:
```

**Lokasi:** `/home/my/utils/infrastructure/.env`
```bash
GLOBAL_DB_NAME=mydb_global
GLOBAL_DB_USER=admin_global
GLOBAL_DB_PASSWORD=rahasia_sangat_kuat_123
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=rahasia_minio_123
```

---

### 3. Konfigurasi Aplikasi A (PHP 8.2)
Aplikasi ini **TIDAK** punya service postgres/redis sendiri. Ia hanya konek ke network `global-net`.

**Lokasi:** `/home/my/apps/AspriAI/docker-compose.yml`

```yaml
version: '3.8'

services:
  app-php:
    image: php:8.5-fpm-alpine
    container_name: AspriAI-php
    restart: unless-stopped
    working_dir: /var/www/html
    volumes:
      - ./src:/var/www/html
    networks:
      - global-net  # Masuk ke network shared
    environment:
      # Host DB adalah NAMA SERVICE di infrastruktur (shared-postgres)
      DB_HOST: shared-postgres
      DB_NAME: ${GLOBAL_DB_NAME}
      DB_USER: ${GLOBAL_DB_USER}
      DB_PASS: ${GLOBAL_DB_PASSWORD}
      REDIS_HOST: shared-redis
      MINIO_ENDPOINT: shared-minio:9000

  nginx-app:
    image: nginx:alpine
    container_name: AspriAI-nginx
    restart: unless-stopped
    ports:
      - "8081:80" # Akses aplikasi A via port 8081
    volumes:
      - ./src:/var/www/html
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
    networks:
      - global-net
    depends_on:
      - app-php

networks:
  global-net:
    external: true  # PENTING: Memberitahu Docker ini network yang sudah ada
    name: global-net
```

---

### 4. Konfigurasi Aplikasi B (PHP 8.2)
Sama seperti Aplikasi A, tapi menggunakan image PHP 8.5 dan port berbeda.

**Lokasi:** `/home/my/apps/ProyekB/docker-compose.yml`

```yaml
version: '3.8'

services:
  app-php:
    image: php:8.2-fpm-alpine
    container_name: proyekB-php
    restart: unless-stopped
    working_dir: /var/www/html
    volumes:
      - ./src:/var/www/html
    networks:
      - global-net
    environment:
      # Tetap konek ke container yang SAMA dengan Aplikasi A
      DB_HOST: shared-postgres
      DB_NAME: ${GLOBAL_DB_NAME}
      DB_USER: ${GLOBAL_DB_USER}
      DB_PASS: ${GLOBAL_DB_PASSWORD}
      REDIS_HOST: shared-redis
      MINIO_ENDPOINT: shared-minio:9000

  nginx-app:
    image: nginx:alpine
    container_name: proyekB-nginx
    restart: unless-stopped
    ports:
      - "8082:80" # Akses aplikasi B via port 8082
    volumes:
      - ./src:/var/www/html
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
    networks:
      - global-net
    depends_on:
      - app-php

networks:
  global-net:
    external: true
    name: global-net
```

---

### 5. Cara Menjalankan (Urutan Wajib)

Anda harus menjalankan **Infrastruktur terlebih dahulu** agar network `global-net` tercipta.

1.  **Start Infrastruktur:**
    ```bash
    cd /home/my/utils/infrastructure
    docker compose up -d
    ```
    *Cek apakah network sudah jadi:* `docker network ls | grep global-net`

2.  **Start Aplikasi AspriAI:**
    ```bash
    cd /home/my/apps/AspriAI
    docker compose up -d
    ```

3.  **Start Aplikasi B:**
    ```bash
    cd /home/my/apps/ProyekB
    docker compose up -d
    ```

### Verifikasi Koneksi
Coba ping database dari dalam container Aplikasi A:
```bash
docker exec AspriAI-php ping -c 3 shared-postgres
```
Jika berhasil (ada reply), berarti Aplikasi A dan B sudah terhubung secara global ke database yang sama tanpa duplikasi.
