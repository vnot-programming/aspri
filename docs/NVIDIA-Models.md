1. `qwen/qwen3.5-397b-a17b`
```py
import requests, base64

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
stream = False

def read_b64(path):
  with open(path, "rb") as f:
    return base64.b64encode(f.read()).decode()

headers = {
  "Authorization": "Bearer $NVIDIA_API_KEY",
  "Accept": "text/event-stream" if stream else "application/json"
}

payload = {
  "model": "qwen/qwen3.5-397b-a17b",
  "messages": [{"role":"user","content":""}],
  "max_tokens": 16384,
  "temperature": 0.60,
  "top_p": 0.95,
  "top_k": 20,
  "presence_penalty": 0,
  "repetition_penalty": 1,
  "stream": stream,
  
}

response = requests.post(invoke_url, headers=headers, json=payload, stream=stream)
if stream:
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
else:
    print(response.json())
```

2. `mistralai/mistral-large-3-675b-instruct-2512`
```py
import requests, base64

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
stream = False


headers = {
  "Authorization": "Bearer $NVIDIA_API_KEY",
  "Accept": "text/event-stream" if stream else "application/json"
}

payload = {
  "model": "mistralai/mistral-large-3-675b-instruct-2512",
  "messages": [{"role":"user","content":""}],
  "max_tokens": 2048,
  "temperature": 0.15,
  "top_p": 1.00,
  "frequency_penalty": 0.00,
  "presence_penalty": 0.00,
  "stream": stream
}

response = requests.post(invoke_url, headers=headers, json=payload)

if stream:
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
else:
    print(response.json())
```

3. `moonshotai/kimi-k2.6`
```py
import requests, base64

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
stream = False

def read_b64(path):
  with open(path, "rb") as f:
    return base64.b64encode(f.read()).decode()

headers = {
  "Authorization": "Bearer $NVIDIA_API_KEY",
  "Accept": "text/event-stream" if stream else "application/json"
}

payload = {
  "model": "moonshotai/kimi-k2.6",
  "messages": [{"role":"user","content":""}],
  "max_tokens": 16384,
  "temperature": 1.00,
  "top_p": 1.00,
  "stream": stream,
  
}

response = requests.post(invoke_url, headers=headers, json=payload, stream=stream)
if stream:
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
else:
    print(response.json())
```

4. `nvidia/nemotron-3-ultra-550b-a55b`
```py
from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "$NVIDIA_API_KEY"
)


completion = client.chat.completions.create(
  model="nvidia/nemotron-3-ultra-550b-a55b",
  messages=[{"role":"user","content":""}],
  temperature=1,
  top_p=0.95,
  max_tokens=16384,
  extra_body={"chat_template_kwargs":{"enable_thinking":True},"reasoning_budget":16384},
  stream=True
)

for chunk in completion:
  if not chunk.choices:
    continue
  reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
  if reasoning:
    print(reasoning, end="")
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")
```

5. `minimaxai/minimax-m3`
```py
import requests

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
stream = False

headers = {
  "Authorization": "Bearer $NVIDIA_API_KEY",
  "Accept": "text/event-stream" if stream else "application/json"
}

payload = {
  "model": "minimaxai/minimax-m3",
  "messages": [{"role":"user","content":""}],
  "max_tokens": 8192,
  "temperature": 1.00,
  "top_p": 0.95,
  "stream": stream,
  
}

# MiniMax-M3 is multimodal. To send images or video, set a message's
# "content" to a list of parts (a public URL or a base64 data URI):
#   payload["messages"] = [{"role": "user", "content": [
#       {"type": "text", "text": "Describe this."},
#       {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}},
#       {"type": "video_url", "video_url": {"url": "https://example.com/video.mp4"}},
#   ]}]
# To use base64 instead of a URL:
#   import base64
#   b64 = base64.b64encode(open("image.png", "rb").read()).decode()
#   {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}

response = requests.post(invoke_url, headers=headers, json=payload, stream=stream)
if stream:
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
else:
    print(response.json())
```