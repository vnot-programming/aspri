import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# Static list of NVIDIA NIM models
NVIDIA_MODELS = [
    {"id": "qwen/qwen3.5-397b-a17b", "name": "Qwen 3.5 397B (NVIDIA NIM)"},
    {"id": "mistralai/mistral-large-3-675b-instruct-2512", "name": "Mistral Large 3 (NVIDIA NIM)"},
    {"id": "moonshotai/kimi-k2.6", "name": "Kimi k2.6 (NVIDIA NIM)"},
    {"id": "nvidia/nemotron-3-ultra-550b-a55b", "name": "Nemotron 3 Ultra 550B (NVIDIA NIM)"},
    {"id": "minimaxai/minimax-m3", "name": "MiniMax M3 (NVIDIA NIM)"}
]

async def _fetch_ollama_models():
    """Fetch available models from the local Ollama instance via SSH reverse tunnel."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get("http://127.0.0.1:11435/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = []
                for m in data.get("models", []):
                    models.append({"id": m.get("name"), "name": f"{m.get('name')} (Local)"})
                return models
    except Exception as e:
        print(f"[Ollama Fetch Error] {e}")
    return []

@router.get("/vendors")
async def get_vendors():
    """
    Mengembalikan struktur data Vendor beserta array model-nya.
    Cocok dikonsumsi oleh UI untuk membuat dropdown berjenjang (Select Vendor -> Select Model).
    """
    ollama_models = await _fetch_ollama_models()
    
    providers = [
        {
            "vendor": "NVIDIA",
            "models": NVIDIA_MODELS
        },
        {
            "vendor": "Ollama",
            "models": ollama_models
        }
    ]
    return JSONResponse(status_code=200, content={"data": providers})

@router.get("/models")
async def get_models():
    """
    OpenAI-compatible /v1/models endpoint.
    Menerjemahkan list provider ke format flat yang kompatibel dengan standar library OpenAI.
    """
    ollama_models = await _fetch_ollama_models()
    
    providers = [
        {
            "vendor": "NVIDIA",
            "models": NVIDIA_MODELS
        },
        {
            "vendor": "Ollama",
            "models": ollama_models
        }
    ]
    
    openai_models = []
    for provider in providers:
        for model in provider["models"]:
            openai_models.append({
                "id": model["id"],
                "object": "model",
                "created": 1718000000,
                "owned_by": provider["vendor"].lower(),
                "name": model["name"]
            })
    
    return JSONResponse(status_code=200, content={"object": "list", "data": openai_models})

