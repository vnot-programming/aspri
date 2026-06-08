import httpx
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
import json

router = APIRouter()

OLLAMA_BASE_URL = "http://127.0.0.1:11435"

async def _reverse_proxy(request: Request):
    client = httpx.AsyncClient()
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    
    # URL target (Ollama)
    target_url = f"{OLLAMA_BASE_URL}{url}"
    
    # Meneruskan body request
    body = await request.body()
    
    # Meneruskan headers (kecuali host agar tidak konflik)
    headers = dict(request.headers)
    headers.pop("host", None)

    # Menggunakan request stream untuk menghemat memory
    req = client.build_request(
        request.method, target_url, headers=headers, content=body
    )
    
    # Fungsi generator untuk streaming response dari Ollama ke klien
    async def stream_response():
        async with client.stream(request.method, target_url, headers=headers, content=body) as response:
            async for chunk in response.aiter_raw():
                yield chunk

    # Ambil status code dan headers dari respon target (sementara cukup manual request untuk header)
    # Untuk efisiensi, kita mulai streaming dan kembalikan response.
    # Cara lebih robust adalah menggunakan httpx send stream
    
    # Kita butuh status_code awal
    response = await client.send(req, stream=True)
    
    async def response_streamer():
        try:
            async for chunk in response.aiter_raw():
                yield chunk
        finally:
            await response.aclose()
            await client.aclose()

    return StreamingResponse(
        response_streamer(),
        status_code=response.status_code,
        headers={k: v for k, v in response.headers.items() if k.lower() != "content-encoding"}
    )

from fastapi.responses import JSONResponse

@router.api_route("/health", methods=["GET", "POST"])
async def health_check():
    """
    Mengecek secara riil (murni) apakah engine Ollama Server di port 11435 merespon.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Default root url Ollama merespon "Ollama is running" (200 OK)
            response = await client.get(OLLAMA_BASE_URL, timeout=5.0)
            if response.status_code == 200:
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "ok", 
                        "message": "AspriAI Core is healthy & Ollama is running",
                        "ollama_response": response.text
                    }
                )
            else:
                return JSONResponse(
                    status_code=502, # Bad Gateway (Ollama responds with non-200)
                    content={
                        "status": "degraded",
                        "message": f"Ollama engine returned status code {response.status_code}"
                    }
                )
        except httpx.RequestError as exc:
            return JSONResponse(
                status_code=503, # Service Unavailable (Ollama mati)
                content={
                    "status": "offline",
                    "message": "Ollama engine is unreachable or down",
                    "error": str(exc)
                }
            )

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def ollama_proxy_catch_all(request: Request, path: str):
    """
    Transparent proxy endpoint untuk menangkap semua lalu lintas (catch-all).
    Ini akan memastikan bahwa baik request ke `/api/tags`, `/api/generate`, maupun `/v1/chat/completions`
    akan diteruskan secara persis ke Ollama.
    """
    return await _reverse_proxy(request)


