# 1. Official Python lightweight image use karein
FROM python:3.11-slim

# 2. Server ke andar working directory set karein
WORKDIR /app

# 3. System dependencies install karein (agar yt-dlp ko ffmpeg chahiye ho)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# 4. requirements.txt copy karke install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Saara code server par copy karein
COPY . .

# 6. Port expose karein
EXPOSE 8000

# 7. Uvicorn production command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]