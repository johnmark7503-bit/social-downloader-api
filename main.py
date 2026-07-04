from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import requests

app = FastAPI()

# Request model validation ke liye
class DownloadRequest(BaseModel):
    url: str

def fetch_from_cloud_bridge(url: str):
    """
    ENGINE B: Cloud Bridge Bypass Engine.
    Agar aapka koi specific Third-Party API Endpoint ya bypass bridge setup hai,
    toh uski logic aap yahan rakh sakte hain.
    """
    try:
        # NOTE: Yahan apna actual cloud bridge API URL aur headers lazmi check kar lein
        # api_url = f"https://your-cloud-bridge-api.com/bypass?url={url}"
        # response = requests.get(api_url, timeout=10)
        # if response.status_code == 200:
        #     return response.json()
        
        # Filhal yeh fallback structure return karega agar custom API config hai:
        return None
    except Exception:
        return None

@app.post("/v1/social/autolink")
def get_media_links(request: DownloadRequest):
    # yt-dlp ki global configurations
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'merge_output_format': 'mp4',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }
    
    try:
        # ENGINE A: Primary extraction using local/container yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            # Response formatting jo frontend ko chahiye
            return {
                "error": False,
                "url": request.url,
                "source": info.get("extractor_key", "").lower(),
                "id": info.get("id"),
                "author": info.get("uploader") or info.get("artist") or "Unknown",
                "title": info.get("title") or "Social Media Video",
                "thumbnail": info.get("thumbnail"),
                "video_url": info.get("url")
            }
            
    except Exception as e:
        # ENGINE B FALLBACK: Agar local system/Render ka IP block ho jaye, toh cloud bypass use karein
        # Ab isme TikTok, Instagram, YouTube, aur Pinterest sab domains check hote hain
        target_domains = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "pinterest.com", "pin.it"]
        
        if any(domain in request.url.lower() for domain in target_domains):
            cloud_response = fetch_from_cloud_bridge(request.url)
            if cloud_response:
                return cloud_response

        # Agar dono engines fail ho jayein tab hi final error display hoga
        raise HTTPException(
            status_code=400,
            detail={
                "error": True, 
                "message": f"Extraction failed on all available engines. Link may be private or broken. Local Error: {str(e)}"
            }
        )