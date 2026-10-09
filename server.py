import os
import sys
import asyncio
import webbrowser
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

import script_parser
import pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Video-Audio Merging & Text-to-Speech Studio")

current_progress = {"status": "Idle", "progress": 0.0}

class GenerateRequest(BaseModel):
    script_text: str
    voice: Optional[str] = "en-US-GuyNeural"
    elevenlabs_key: Optional[str] = None
    elevenlabs_voice_id: Optional[str] = None
    video_path: Optional[str] = None

@app.get("/")
@app.head("/")
async def get_index():
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "Server running"})

@app.get("/api/progress")
async def get_progress():
    return current_progress

@app.post("/api/generate")
async def generate_voiceover(req: GenerateRequest):
    global current_progress
    if not req.script_text or not req.script_text.strip():
        raise HTTPException(status_code=400, detail="Script text cannot be empty.")

    segments = script_parser.parse_script_text(req.script_text)
    if not segments:
        raise HTTPException(
            status_code=400,
            detail="Could not detect any timestamped segments. Please format like: '0:00 – 0:06 Your text here'"
        )

    def on_progress(msg: str, pct: float):
        global current_progress
        current_progress = {"status": msg, "progress": round(pct, 2)}

    try:
        current_progress = {"status": "Starting generation...", "progress": 0.05}
        result = await pipeline.process_script(
            segments=segments,
            voice=req.voice or "en-US-GuyNeural",
            elevenlabs_key=req.elevenlabs_key.strip() if req.elevenlabs_key else None,
            elevenlabs_voice_id=req.elevenlabs_voice_id.strip() if req.elevenlabs_voice_id else None,
            video_path=req.video_path.strip() if req.video_path else None,
            progress_callback=on_progress
        )
        current_progress = {"status": "Ready", "progress": 1.0}
        return result
    except Exception as e:
        current_progress = {"status": f"Error: {str(e)}", "progress": 0.0}
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files to serve clips, videos, and wav files
app.mount("/", StaticFiles(directory=BASE_DIR), name="static")

def run():
    port = 8080
    url = f"http://localhost:{port}"
    print("\n========================================================")
    print("  Video-Audio Merging & Text-to-Speech Studio")
    print(f"  Running at: {url}")
    print("========================================================\n")
    print("Opening web app in your default browser...")
    webbrowser.open(url)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    run()
