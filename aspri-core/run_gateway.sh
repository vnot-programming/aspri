#!/bin/bash
# Script untuk menjalankan AspriAI Core (FastAPI Gateway)

source /data/programs/anaconda3/bin/activate yolo_env
cd /data/users/g6717500336/singularity/AspriAI/aspri-core

echo "Memulai AspriAI Core API Gateway di port 11434..."
echo "(Port ini mendengarkan request dari Cloudflare Tunnel dan mem-proxy ke Ollama di 11435)"

# Jalankan uvicorn di port 11434
uvicorn main:app --host 127.0.0.1 --port 11434 --reload
