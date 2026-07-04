from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import requests
import random

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str

# 🌐 Proxy Pool (For initial bypass attempts)
PREMIUM_PROXIES = [
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.1.132:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.29.215:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@217.181.91.8:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@217.181.92.48:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.2.220:3129"
]

def fetch_from_cloud_bridge(url: str):
    """
    ENGINE B: The Ultimate Savior (RapidAPI / External Bypass Bridge)
    Agar saari proxies fail ho jayein, toh yeh bypass bridge 100% data nikalega.
    """
    try:
        # ⚠️ Yahan aap apni khuli hui RapidAPI ka endpoint aur key daal sakte hain:
        # Example using a common stable downloader API structure:
        api_url = "https://social-media-video-downloader.p.rapidapi.com/api/video/download"
        
        headers = {
            "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY_HERE", # <-- Yahan apni key lagayein
            "X-RapidAPI-Host": "social-media-video-downloader.p.rapidapi.com"
        }
        
        querystring = {"url": url}
        response = requests.get(api_url, headers=headers, params=querystring, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Response ko aapke standard format mein convert karna:
            return {
                "error": False,
                "url": url,
                "source": data.get("source", "social"),
                "id": data.get("id", "0000"),
                "author": data.get("uploader", "Unknown"),
                "title": data.get("title", "Social Video"),
                "thumbnail": data.get("thumbnail", ""),
                "video_url": data.get("url") # Direct downloadable link
            }
    except Exception as bridge_err:
        print(f"Cloud bridge fallback also failed: {bridge_err}")
    
    # Free Public Alt Fallback (Agar RapidAPI set up nahi hai toh yeh try karega)
    try:
        alt_url = f"https://api.cobalt.tools/api/json"
        alt_headers = {"Accept": "application/json", "Content-Type": "application/json"}
        alt_data = {"url": url, "vQuality": "720"}
        
        res = requests.post(alt_url, json=alt_data, headers=alt_headers, timeout=10)
        if res.status_code == 200:
            res_json = res.json()
            return {
                "error": False,
                "url": url,
                "source": "bypass_engine",
                "id": "extracted",
                "author": "Creator",
                "title": "Bypassed Media Video",
                "thumbnail": "",
                "video_url": res_json.get("url")
            }
    except Exception:
        pass
        
    return None

def extract_with_retry(url: str, ydl_opts: dict):
    """Primary extraction layer using yt-dlp + Proxies"""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as initial_err:
        if PREMIUM_PROXIES:
            shuffled = PREMIUM_PROXIES.copy()
            random.shuffle(shuffled)
            for proxy in shuffled[:2]: # Max 2 quick retries to maintain fast response
                try:
                    proxy_opts = ydl_opts.copy()
                    proxy_opts['proxy'] = proxy
                    with yt_dlp.YoutubeDL(proxy_opts) as ydl:
                        return ydl.extract_info(url, download=False)
                except Exception:
                    continue
        raise initial_err

@app.post("/v1/social/autolink")
def get_media_links(request: DownloadRequest):
    url_lower = request.url.lower()
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'merge_output_format': 'mp4',
        'socket_timeout': 6, 
    }
    
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        ydl_opts['extractor_args'] = {'youtube': {'player_client': ['ios', 'android'], 'skip': ['webpage']}}
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1'
        }
    elif "instagram.com" in url_lower:
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }
    else:
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
    
    try:
        # Step 1: Try Local Extraction
        info = extract_with_retry(request.url, ydl_opts)
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
        # Step 2: The Ultimate Fallback Layer (RapidAPI / Cobalt Tools Bridge Bypass)
        target_domains = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "pinterest.com", "pin.it"]
        if any(domain in url_lower for domain in target_domains):
            cloud_response = fetch_from_cloud_bridge(request.url)
            if cloud_response:
                return cloud_response

        raise HTTPException(
            status_code=400,
            detail={
                "error": True, 
                "message": f"All engines exhausted. Extraction failed. System Error: {str(e)}"
            }
        )