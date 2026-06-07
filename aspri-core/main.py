from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import chat

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

# Mendaftarkan router untuk format OpenAI (/v1)
app.include_router(chat.router, prefix="/v1", tags=["Ollama OpenAI Proxy"])

# Mendaftarkan router untuk format Native Ollama (/api)
app.include_router(chat.router, prefix="/api", tags=["Ollama Native Proxy"])

@app.get("/")
async def root():
    return {"message": "Welcome to AspriAI Core API Gateway"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
