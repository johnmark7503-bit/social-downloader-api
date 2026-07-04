from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import requests
import random

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str

# 🔥 PROXYSCRAPE PREMIUM PROXIES POOL
# Username aur password ke sath fully configured formatted links
PREMIUM_PROXIES = [
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.1.132:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.29.215:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@217.181.91.8:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@217.181.92.48:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.2.220:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@45.3.35.226:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.23.179:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@45.3.43.157:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@209.50.169.84:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@209.50.187.121:3129"
]

def fetch_from_cloud_bridge(url: str):
    """ENGINE B: Fallback cloud bridge structure"""
    try:
        return None
    except Exception:
        return None

def extract_with_retry(url: str, ydl_opts: dict):
    """Premium proxies ko random select aur auto-retry karne wala engine"""
    # 1. Pehle Direct Render IP se check karte hain (agar link direct chal jaye toh time bachega)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as initial_err:
        print(f"Direct connection blocked, switching to ProxyScrape Premium... Error: {initial_err}")
        
        # 2. Agar block hua, toh premium list ko shuffle karke rotate karenge
        if PREMIUM_PROXIES:
            shuffled_proxies = PREMIUM_PROXIES.copy()
            random.shuffle(shuffled_proxies)
            
            for proxy in shuffled_proxies:
                try:
                    print(f"Bypassing with premium proxy: {proxy.split('@')[-1]}") # IP safe log trace
                    proxy_opts = ydl_opts.copy()
                    proxy_opts['proxy'] = proxy
                    
                    with yt_dlp.YoutubeDL(proxy_opts) as ydl:
                        return ydl.extract_info(url, download=False)
                except Exception as proxy_err:
                    print(f"Proxy dead or rate-limited, switching to next... Error: {proxy_err}")
                    continue
        
        raise initial_err

@app.post("/v1/social/autolink")
def get_media_links(request: DownloadRequest):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'merge_output_format': 'mp4',
        'socket_timeout': 10,  # Premium proxies fast hoti hain, 10 sec ka kafi hai
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate'
        }
    }
    
    try:
        # ENGINE A: Powerful private proxy rotation technique
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
        # ENGINE B FALLBACK: Agar premium network ke baad bhi block ho (extreme edge case)
        target_domains = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "pinterest.com", "pin.it"]
        
        if any(domain in request.url.lower() for domain in target_domains):
            cloud_response = fetch_from_cloud_bridge(request.url)
            if cloud_response:
                return cloud_response

        raise HTTPException(
            status_code=400,
            detail={
                "error": True, 
                "message": f"Boom system failed. Request blocked globally. Local Error: {str(e)}"
            }
        )