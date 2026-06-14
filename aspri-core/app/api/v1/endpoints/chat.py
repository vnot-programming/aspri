import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, JSONResponse
import json
import os
from datetime import datetime

router = APIRouter()

OLLAMA_BASE_URL = "http://127.0.0.1:11435"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com"

ASPRI_KEYS_PATH = "/data/users/g6717500336/singularity/AspriAI/api_keys.json"
ASPRI_ENV_PATH = "/data/users/g6717500336/singularity/AspriAI/.env"

NVIDIA_MODELS_SET = {
    "qwen/qwen3.5-397b-a17b",
    "mistralai/mistral-large-3-675b-instruct-2512",
    "moonshotai/kimi-k2.6",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "minimaxai/minimax-m3"
}

def get_nvidia_api_key():
    if os.path.exists(ASPRI_ENV_PATH):
        with open(ASPRI_ENV_PATH, "r") as f:
            for line in f:
                if line.startswith("NVIDIA_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    return val
    return None

def validate_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized: Missing or invalid Bearer token")
    
    token = auth_header.split(" ", 1)[1].strip()
    
    if not os.path.exists(ASPRI_KEYS_PATH):
        raise HTTPException(status_code=401, detail="Unauthorized: No API keys configured")
        
    try:
        with open(ASPRI_KEYS_PATH, "r") as f:
            keys = json.load(f)
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error: Key store corrupted")
        
    if token not in keys:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")
        
    key_info = keys[token]
    if key_info.get("revoked", False):
        raise HTTPException(status_code=401, detail="Unauthorized: API Key has been revoked")
        
    expires_at = datetime.fromisoformat(key_info["expires_at"])
    if expires_at < datetime.now():
        raise HTTPException(status_code=401, detail="Unauthorized: API Key has expired")

async def _reverse_proxy(request: Request, check_auth=True):
    if check_auth:
        validate_api_key(request)

    body = await request.body()
    
    is_nvidia_route = False
    nvidia_model_id = ""
    
    if request.url.path.endswith("/v1/chat/completions") or request.url.path.endswith("/chat/completions"):
        try:
            body_json = json.loads(body)
            model = body_json.get("model", "")
            for nv_model in NVIDIA_MODELS_SET:
                if nv_model in model:
                    is_nvidia_route = True
                    nvidia_model_id = nv_model
                    break
        except:
            pass

    client = httpx.AsyncClient(timeout=300.0)
    
    headers = dict(request.headers)
    
    # Clean up headers that shouldn't be forwarded to avoid WAF/Cloudflare blocks
    keys_to_remove = []
    for k in headers.keys():
        k_lower = k.lower()
        if k_lower.startswith("cf-") or k_lower.startswith("x-forwarded-") or k_lower in ["host", "content-length", "authorization", "cdn-loop", "connection"]:
            keys_to_remove.append(k)
            
    for k in keys_to_remove:
        headers.pop(k, None)
    
    if is_nvidia_route:
        # Rewrite body to match NVIDIA expected model ID exactly
        try:
            body_json = json.loads(body)
            body_json["model"] = nvidia_model_id
            body = json.dumps(body_json).encode("utf-8")
        except:
            pass
            
        # NVIDIA NIM Smart Routing
        path = request.url.path
        if request.url.query:
            path += f"?{request.url.query}"
        target_url = f"{NVIDIA_BASE_URL}{path}"
        
        nvidia_key = get_nvidia_api_key()
        if nvidia_key:
            headers["authorization"] = f"Bearer {nvidia_key}"
    else:
        # Default Local Ollama Routing
        path = request.url.path
        if request.url.query:
            path += f"?{request.url.query}"
        target_url = f"{OLLAMA_BASE_URL}{path}"
        
    req = client.build_request(
        request.method, target_url, headers=headers, content=body
    )
    try:
        response = await client.send(req, stream=True)
    except httpx.RequestError as e:
        return JSONResponse(status_code=504, content={"error": f"Upstream connection error: {str(e)}"})
    
    if response.status_code >= 400:
        error_body = await response.aread()
        try:
            with open("/data/users/g6717500336/singularity/AspriAI/aspri-core/error_debug.log", "a") as f:
                f.write(f"--- ERROR {response.status_code} ---\n")
                f.write(f"URL: {target_url}\n")
                f.write(f"REQUEST HEADERS: {req.headers}\n")
                f.write(f"REQUEST BODY: {body.decode('utf-8', errors='ignore')}\n")
                f.write(f"RESPONSE BODY: {error_body.decode('utf-8', errors='ignore')}\n")
                f.write("---------------------\n")
        except:
            pass
            
        async def err_streamer():
            yield error_body
            
        return StreamingResponse(
            err_streamer(),
            status_code=response.status_code,
            headers={k: v for k, v in response.headers.items() if k.lower() not in ["content-encoding", "content-length"]}
        )
    
    async def response_streamer():
        try:
            if not is_nvidia_route:
                async for chunk in response.aiter_raw():
                    yield chunk
                return

            content_type = response.headers.get("content-type", "")
            
            if "application/json" in content_type:
                body_bytes = await response.aread()
                try:
                    data = json.loads(body_bytes)
                    for k in ["prompt_logprobs", "prompt_token_ids", "prompt_text", "kv_transfer_params"]:
                        data.pop(k, None)
                    if "usage" in data and isinstance(data["usage"], dict):
                        data["usage"].pop("prompt_tokens_details", None)
                    if "choices" in data and isinstance(data["choices"], list):
                        for choice in data["choices"]:
                            choice.pop("routed_experts", None)
                            if "message" in choice and isinstance(choice["message"], dict):
                                msg = choice["message"]
                                for mk in ["refusal", "annotations", "audio", "function_call", "reasoning", "reasoning_content"]:
                                    msg.pop(mk, None)
                    yield json.dumps(data).encode("utf-8")
                except:
                    yield body_bytes
            
            elif "text/event-stream" in content_type:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        payload = line[6:]
                        if payload.strip() == "[DONE]":
                            yield f"{line}\n".encode("utf-8")
                            continue
                        try:
                            data = json.loads(payload)
                            for k in ["prompt_logprobs", "prompt_token_ids", "prompt_text", "kv_transfer_params"]:
                                data.pop(k, None)
                            if "usage" in data and isinstance(data["usage"], dict):
                                data["usage"].pop("prompt_tokens_details", None)
                            if "choices" in data and isinstance(data["choices"], list):
                                for choice in data["choices"]:
                                    choice.pop("routed_experts", None)
                                    if "delta" in choice and isinstance(choice["delta"], dict):
                                        delta = choice["delta"]
                                        for mk in ["refusal", "annotations", "audio", "function_call", "reasoning", "reasoning_content"]:
                                            delta.pop(mk, None)
                            yield f"data: {json.dumps(data)}\n".encode("utf-8")
                        except:
                            yield f"{line}\n".encode("utf-8")
                    else:
                        yield f"{line}\n".encode("utf-8")
            else:
                async for chunk in response.aiter_raw():
                    yield chunk

        finally:
            await response.aclose()
            await client.aclose()

    return StreamingResponse(
        response_streamer(),
        status_code=response.status_code,
        headers={k: v for k, v in response.headers.items() if k.lower() not in ["content-encoding", "content-length"]}
    )

@router.api_route("/health", methods=["GET", "POST"])
async def health_check():
    """
    Mengecek secara riil (murni) apakah engine Ollama Server di port 11435 merespon.
    """
    async with httpx.AsyncClient() as client:
        try:
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
                    status_code=502,
                    content={
                        "status": "degraded",
                        "message": f"Ollama engine returned status code {response.status_code}"
                    }
                )
        except httpx.RequestError as exc:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "offline",
                    "message": "Ollama engine is unreachable or down",
                    "error": str(exc)
                }
            )
@router.get("/tags")
async def get_tags(request: Request):
    """
    Menggabungkan model lokal Ollama dengan model external (NVIDIA NIM)
    agar bisa muncul di endpoint native Ollama API.
    """
    validate_api_key(request)
    
    # 1. Ambil model dari Ollama lokal
    models = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("models", [])
        except:
            pass
            
    # 2. Tambahkan model eksternal NVIDIA ke dalam list
    now_iso = datetime.now().astimezone().isoformat()
    for nv_model in NVIDIA_MODELS_SET:
        family = "nvidia-nim"
        if "qwen" in nv_model:
            family = "qwen"
        elif "mistral" in nv_model:
            family = "mistral"
        elif "nemotron" in nv_model:
            family = "nemotron"
            
        param_size = "Unknown"
        if "397b" in nv_model.lower(): param_size = "397B"
        elif "675b" in nv_model.lower(): param_size = "675B"
        elif "550b" in nv_model.lower(): param_size = "550B"
        elif "moonshotai" in nv_model.lower() or "minimaxai" in nv_model.lower(): param_size = "Proprietary"

        models.append({
            "name": nv_model,
            "model": nv_model,
            "modified_at": now_iso,
            "size": 0,
            "digest": "external-api",
            "details": {
                "parent_model": "",
                "format": "api",
                "family": family,
                "families": [family],
                "parameter_size": param_size,
                "quantization_level": "API"
            }
        })
        
    return JSONResponse(status_code=200, content={"models": models})

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def ollama_proxy_catch_all(request: Request, path: str):
    """
    Transparent proxy endpoint untuk menangkap semua lalu lintas (catch-all).
    Smart Routing akan meneruskan ke NVIDIA NIM atau Ollama berdasarkan 'model'.
    API Key (api_keys.json) divalidasi.
    """
    # Bypass OPTIONS preflight checking for CORS
    if request.method == "OPTIONS":
        return await _reverse_proxy(request, check_auth=False)
    return await _reverse_proxy(request, check_auth=True)
