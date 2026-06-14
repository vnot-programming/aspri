from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import chat, openai

app = FastAPI(
    title="AspriAI Core API Gateway",
    description="API Gateway for AspriAI services, acting as a lightweight proxy.",
    version="1.0.0",
)

# Konfigurasi CORS agar bisa diakses dari frontend (AspriAI Desk)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Bisa diperketat nanti, tapi karena sudah di belakang Cloudflare Access, aman.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mendaftarkan router untuk Provider & Models (Harus didaftarkan sebelum proxy catch-all Ollama)
app.include_router(openai.router, prefix="/v1", tags=["LLM Providers"])

# Mendaftarkan router untuk format OpenAI (/v1)
app.include_router(chat.router, prefix="/v1", tags=["Ollama OpenAI Proxy"])

# Mendaftarkan router untuk format Native Ollama (/api)
app.include_router(chat.router, prefix="/api", tags=["Ollama Native Proxy"])

import asyncio
import httpx

@app.api_route("/health", methods=["GET", "POST"])
async def global_health_check():
    """
    Unified Health Check: Menjembatani pengecekan status dari seluruh layanan AI.
    Mengecek: Ollama Server, RVM Server, dan ComfyUI Server.
    """
    services_to_check = [
        {"name": "Ollama Server", "url": "https://backend-ollama.penelitian.my.id/v1/health", "method": "POST"},
        {"name": "RVM Server", "url": "https://backend-rvm.penelitian.my.id/api/health", "method": "GET"},
        {"name": "ComfyUI Server", "url": "https://backend-comfui.penelitian.my.id/system_stats", "method": "GET"}
    ]
    
    # Injeksi Cloudflare Headers untuk RVM Server (agar tidak terhalang 403 Forbidden)
    import os
    cf_headers = {}
    env_path = "/data/users/g6717500336/Trainning-Models/MyFineTunning-SlurmMaster/RVM/.env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("CF-Access-Client-Id="):
                    cf_headers["CF-Access-Client-Id"] = line.split("=", 1)[1]
                elif line.startswith("CF-Access-Client-Secret="):
                    cf_headers["CF-Access-Client-Secret"] = line.split("=", 1)[1]

    async def check_service(client, name, url, method):
        try:
            if method.upper() == "POST":
                # Some APIs require empty JSON body for POST health
                response = await client.post(url, timeout=5.0, json={})
            else:
                response = await client.get(url, timeout=5.0)
                
            try:
                data = response.json()
                # Mengekstrak status dari body response jika ada (menangani nested health check)
                internal_status = data.get("status", "").lower() if isinstance(data, dict) else ""
            except Exception:
                data = response.text[:100]
                internal_status = ""
                
            # Evaluasi status gabungan (Network Code vs Internal Payload Code)
            if response.status_code >= 400:
                final_status = "offline" if response.status_code >= 500 else "degraded"
            elif internal_status in ["offline", "degraded", "error", "unhealthy"]:
                final_status = internal_status
            else:
                final_status = "online"
                
            return {
                "name": name,
                "url": url,
                "status": final_status,
                "status_code": response.status_code,
                "response": data
            }
        except Exception as e:
            return {
                "name": name,
                "url": url,
                "status": "offline",
                "error": str(e)
            }

    # Gunakan httpx Client dengan bypass SSL & headers
    async with httpx.AsyncClient(headers=cf_headers, verify=False) as client:
        tasks = [check_service(client, s["name"], s["url"], s.get("method", "GET")) for s in services_to_check]
        results = await asyncio.gather(*tasks)
        
    # Evaluasi status gabungan
    all_online = all(r["status"] == "online" for r in results)
    
    return {
        "status": "ok" if all_online else "degraded",
        "status_code": 200,
        "gateway": "AspriAI Core Unified Gateway",
        "services": results
    }

@app.get("/")
async def root():
    return await global_health_check()
