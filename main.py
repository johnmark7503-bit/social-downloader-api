from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str

@app.post("/v1/social/autolink")
def get_media_links(request: DownloadRequest):
    # 🎯 Direct high-reputation open infrastructure endpoint (Cobalt Architecture)
    # Yeh API standard networks ke requests ko block nahi hone deti
    bypass_gateway = "https://api.cobalt.tools/api/json"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    
    # Payload requirements for high-bypass engine
    payload = {
        "url": request.url,
        "vQuality": "720",      # Default high quality stream
        "isAudioOnly": False,
        "filenamePattern": "classic"
    }
    
    try:
        # Request timeout set to 15 seconds to handle extraction processing
        response = requests.post(bypass_gateway, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            res_data = response.json()
            
            # Agar engine stream URL return karta hai
            stream_url = res_data.get("url")
            
            if not stream_url:
                raise Exception("Engine parsed the link but did not return a valid stream URL.")
            
            # Auto-detect source platform from the provided URL
            source_platform = "social"
            url_lower = request.url.lower()
            if "youtube.com" in url_lower or "youtu.be" in url_lower:
                source_platform = "youtube"
            elif "instagram.com" in url_lower:
                source_platform = "instagram"
            elif "tiktok.com" in url_lower:
                source_platform = "tiktok"
            elif "pinterest.com" in url_lower or "pin.it" in url_lower:
                source_platform = "pinterest"

            # Mapping perfectly to your app's frontend response format
            return {
                "error": False,
                "url": request.url,
                "source": source_platform,
                "id": "extracted_stream",
                "author": "Content Creator",
                "title": "Extracted Social Video Stream",
                "thumbnail": "",
                "video_url": stream_url  # Direct downloadable high-speed link
            }
        
        elif response.status_code == 400:
            # Platform explicit handling for error messages
            error_data = response.json()
            raise Exception(error_data.get("text", "Invalid video URL or unsupported platform link."))
        else:
            raise Exception(f"Gateway rejected the connection with status code: {response.status_code}")
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": True, 
                "message": f"Bypass engine failed to extract this link. Details: {str(e)}"
            }
        )