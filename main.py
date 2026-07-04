from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import urllib.request
import urllib.parse
import json

app = FastAPI(
    title="Enterprise Hybrid Downloader API",
    description="Production-ready scraper with silent error suppression and CORS protection.",
    version="4.0.0"
)

# 1. CORS MIDDLEWARE (Zaroori hai taake frontend/apps se direct call ho sake)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Production mein yahan apni website ka domain daal sakte hain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. SILENT LOGGER (Terminal se laal rang ke 403 errors ko chupane ke liye)
class SuppressYtdlLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass # Yeh line local terminal par error print hone se rokegi

class DownloadRequest(BaseModel):
    url: str

# --- ENGINE B: CLOUD BRIDGE ENGINE ---
def fetch_from_cloud_bridge(target_url: str):
    try:
        api_endpoint = "https://www.tikwm.com/api/"
        encoded_data = urllib.parse.urlencode({'url': target_url}).encode('utf-8')
        
        req = urllib.request.Request(
            api_endpoint, 
            data=encoded_data, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        with urllib.request.urlopen(req, timeout=12) as response:
            res = json.loads(response.read().decode('utf-8'))
            if res.get('code') == 0 and 'data' in res:
                d = res['data']
                medias = []
                
                if d.get('play'):
                    medias.append({"url": d.get('play'), "data_size": d.get('size', 0), "width": 0, "height": 0, "quality": "no_watermark", "extension": "mp4", "type": "video"})
                if d.get('wmplay'):
                    medias.append({"url": d.get('wmplay'), "data_size": 0, "width": 0, "height": 0, "quality": "watermark", "extension": "mp4", "type": "video"})
                if d.get('music'):
                    medias.append({"url": d.get('music'), "data_size": 0, "width": 0, "height": 0, "quality": "audio", "extension": "mp3", "type": "audio"})

                return {
                    "url": target_url, "source": "tiktok (cloud-fallback)", "id": d.get('id'),
                    "author": d.get('author', {}).get('nickname', 'unknown'), "title": d.get('title', 'Social Media Video'),
                    "thumbnail": d.get('cover'), "duration": d.get('duration', 0),
                    "statistics": {"play_count": d.get('play_count', 0), "digg_count": d.get('digg_count', 0), "comment_count": d.get('comment_count', 0), "share_count": d.get('share_count', 0)},
                    "medias": medias, "type": "multiple" if len(medias) > 1 else "single", "error": False
                }
    except Exception:
        return None
    return None

# --- MAIN API ROUTE ---
@app.post("/v1/social/autolink")
def get_media_links(request: DownloadRequest):
    
    # Engine A Configuration with Custom Silent Logger
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'logger': SuppressYtdlLogger(),  # Ugly terminal errors ko handle karega
        'extract_flat': False,
        'check_formats': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    
    try:
        # TRY ENGINE A (Local Scraper)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            medias_list = []
            
            for f in info.get('formats', []):
                if f.get('url'):
                    vcodec = f.get('vcodec', 'none')
                    quality_type = "video" if vcodec != 'none' and vcodec is not None else "audio"
                    quality_label = f.get('format_note') or f.get('resolution') or "standard"
                    
                    quality_tag = "watermark" if "watermark" in quality_label.lower() else ("audio" if quality_type == "audio" else "no_watermark")

                    medias_list.append({
                        "url": f.get('url'), "data_size": f.get('filesize') or f.get('filesize_approx') or 0,
                        "width": f.get('width') or 0, "height": f.get('height') or 0,
                        "quality": quality_tag, "extension": f.get('ext', 'mp4'), "type": quality_type
                    })

            medias_list.reverse()
            return {
                "url": request.url, "source": info.get('extractor', 'unknown').lower(), "id": info.get('id'),
                "author": info.get('uploader'), "title": info.get('title'), "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration', 0),
                "statistics": {"play_count": info.get('view_count', 0), "digg_count": info.get('like_count', 0), "comment_count": info.get('comment_count', 0), "share_count": info.get('share_count', 0)},
                "medias": medias_list, "type": "multiple" if len(medias_list) > 1 else "single", "error": False
            }

    except Exception:
        # TRIGGER ENGINE B (Cloud Backup) - Bina terminal par error show kiye silent switch
        if "tiktok.com" in request.url.lower():
            cloud_response = fetch_from_cloud_bridge(request.url)
            if cloud_response:
                return cloud_response
        
        raise HTTPException(
            status_code=400, 
            detail={"error": True, "message": "Extraction failed on all available engines. Link may be private or broken."}
        )