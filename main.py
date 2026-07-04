from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str

# 🌐 Active Open Infrastructure Nodes
COBALT_NODES = [
    "https://cobalt.api.v0.nexus",
    "https://api.cobalt.tools",
    "https://cobalt-api.kwi.sk"
]

@app.post("/v1/social/autolink")
def get_media_links(request: DownloadRequest):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    
    payload = {
        "url": request.url,
        "vQuality": "720",
        "isAudioOnly": False
    }

    # Auto-detect source platform for the response schema
    url_lower = request.url.lower()
    source_platform = "social"
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        source_platform = "youtube"
    elif "instagram.com" in url_lower:
        source_platform = "instagram"
    elif "tiktok.com" in url_lower:
        source_platform = "tiktok"
    elif "pinterest.com" in url_lower or "pin.it" in url_lower:
        source_platform = "pinterest"

    # Try nodes one by one until one works
    for base_url in COBALT_NODES:
        try:
            # Constructing path dynamically for compatibility
            target_endpoint = f"{base_url.rstrip('/')}/api/json" if "v0" not in base_url else base_url
            
            response = requests.post(target_endpoint, json=payload, headers=headers, timeout=8)
            
            if response.status_code == 200:
                res_data = response.json()
                stream_url = res_data.get("url")
                
                if stream_url:
                    return {
                        "error": False,
                        "url": request.url,
                        "source": source_platform,
                        "id": "extracted_stream",
                        "author": "Content Creator",
                        "title": "Extracted Social Video Stream",
                        "thumbnail": "",
                        "video_url": stream_url
                    }
        except Exception as node_err:
            print(f"Node {base_url} failed or timed out. Trying next...")
            continue

    # If all open infrastructure routes fail
    raise HTTPException(
        status_code=400,
        detail={
            "error": True, 
            "message": "All open bypass nodes are currently exhausted. Please try again in a few moments."
        }
    )