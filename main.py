from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import requests
import random

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str

# 🌐 Proxy Pool from your ProxyScrape Premium List
PREMIUM_PROXIES = [
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.1.132:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.29.215:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@217.181.91.8:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@217.181.92.48:3129",
    "http://qjsg7xkke2re:xhdagjlq33ozvj6@65.111.2.220:3129"
]

def fetch_from_cloud_bridge(url: str):
    """
    ENGINE B: The Ultimate Savior (Bypass Bridge Engine)
    Jab local yt-dlp aur saari datacenter proxies fail ho jayein, to yeh bypass layer hit hogi.
    """
    # Try Public High-Bypass Infrastructure First (Cobalt Network API)
    try:
        alt_url = "https://api.cobalt.tools/api/json"
        alt_headers = {
            "Accept": "application/json", 
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        alt_data = {"url": url, "vQuality": "720"}
        
        res = requests.post(alt_url, json=alt_data, headers=alt_headers, timeout=8)
        if res.status_code == 200:
            res_json = res.json()
            if res_json.get("url"):
                return {
                    "error": False,
                    "url": url,
                    "source": "bypass_bridge",
                    "id": "extracted",
                    "author": "Creator",
                    "title": "Social Media Video (Bypassed)",
                    "thumbnail": "",
                    "video_url": res_json.get("url")
                }
    except Exception as e:
        print(f"Bypass Bridge Layer 1 failed: {str(e)}")

    # Try RapidAPI Fallback (Since you have the Social Media Downloader tab open)
    try:
        # Apni RapidAPI key yahan lagayein agar aapke paas active subscription hai
        api_url = "https://social-media-video-downloader.p.rapidapi.com/api/video/download"
        headers = {
            "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY_HERE", 
            "X-RapidAPI-Host": "social-media-video-downloader.p.rapidapi.com"
        }
        response = requests.get(api_url, headers=headers, params={"url": url}, timeout=8)
        if response.status_code == 200:
            data = response.json()
            return {
                "error": False,
                "url": url,
                "source": data.get("source", "social"),
                "id": data.get("id", "extracted"),
                "author": data.get("uploader", "Unknown"),
                "title": data.get("title", "Social Video"),
                "thumbnail": data.get("thumbnail", ""),
                "video_url": data.get("url")
            }
    except Exception as e:
        print(f"RapidAPI Bypass Layer failed: {str(e)}")
        
    return None

def extract_with_retry(url: str, ydl_opts: dict):
    """Primary extraction layer using yt-dlp + Proxies"""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as initial_err:
        # Rotate through premium proxies immediately if direct request fails
        shuffled = PREMIUM_PROXIES.copy()
        random.shuffle(shuffled)
        for proxy in shuffled[:2]:
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
        'socket_timeout': 5, 
    }
    
    # Platform-specific optimization
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        ydl_opts['extractor_args'] = {'youtube': {'player_client': ['ios', 'android'], 'skip': ['webpage']}}
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15'
        }
    else:
        ydl_opts['http_headers'] = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    try:
        # Step 1: Attempt standard yt-dlp path
        info = extract_with_retry(request.url, ydl_opts)
        return {
            "error": False,
            "url": request.url,
            "source": info.get("extractor_key", "").lower(),
            "id": info.get("id"),
            "author": info.get("uploader") or "Unknown",
            "title": info.get("title") or "Social Media Video",
            "thumbnail": info.get("thumbnail"),
            "video_url": info.get("url")
        }
    except Exception as e:
        # Step 2: Global Bypass Fallback for YouTube, Instagram, Pinterest, etc.
        print(f"Local extraction blocked by platform. Triggering Bypass Bridge... Error: {str(e)}")
        cloud_response = fetch_from_cloud_bridge(request.url)
        if cloud_response:
            return cloud_response

        raise HTTPException(
            status_code=400,
            detail={
                "error": True, 
                "message": "Extraction failed on all available engines. Link may be private or heavily protected."
            }
        )