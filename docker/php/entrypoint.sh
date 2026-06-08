#!/bin/sh
set -e

echo "🚀 [entrypoint] Memulai setup AspriAI..."

# Tunggu source code tersedia (volume mount mungkin butuh waktu)
if [ ! -f "/var/www/html/artisan" ]; then
    echo "⚠️  [entrypoint] Menunggu source code (artisan tidak ditemukan)..."
    sleep 3
fi

cd /var/www/html

# =============================================================================
# 1. Install Composer Dependencies
# =============================================================================
if [ -f "composer.json" ]; then
    echo "📦 [entrypoint] Menjalankan composer install..."
    composer install --no-interaction --optimize-autoloader --no-dev 2>&1 || \
    composer install --no-interaction --optimize-autoloader 2>&1
    echo "✅ [entrypoint] composer install selesai."
fi

# =============================================================================
# 2. Build Frontend Assets (Vite)
#    Hanya build jika public/build/manifest.json belum ada atau src berubah
# =============================================================================
if [ -f "package.json" ]; then
    if [ ! -f "public/build/manifest.json" ]; then
        echo "🎨 [entrypoint] Menjalankan npm install & npm run build..."
        npm install --silent 2>&1
        npm run build 2>&1
        echo "✅ [entrypoint] Frontend build selesai."
    else
        echo "ℹ️  [entrypoint] public/build/manifest.json sudah ada, skip npm build."
    fi
fi

# =============================================================================
# 3. Perbaiki Permission Storage dan Bootstrap Cache
# =============================================================================
echo "🔐 [entrypoint] Memperbaiki permission storage & bootstrap/cache..."
chown -R www-data:www-data storage bootstrap/cache 2>/dev/null || true
chmod -R 775 storage bootstrap/cache 2>/dev/null || true
echo "✅ [entrypoint] Permission selesai."

# =============================================================================
# 4. Clear Config Cache (pastikan membaca .env terbaru)
# =============================================================================
echo "🔄 [entrypoint] Clear config cache..."
php artisan config:clear 2>&1 || true

# =============================================================================
# 5. Jalankan PHP-FPM (proses utama)
# =============================================================================
echo "✅ [entrypoint] Setup selesai. Menjalankan PHP-FPM..."
exec php-fpm
