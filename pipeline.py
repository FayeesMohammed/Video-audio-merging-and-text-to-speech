import asyncio
import os
import wave
import subprocess
import urllib.request
import json
import edge_tts
import miniaudio
import imageio_ffmpeg
from typing import List, Dict, Any, Callable, Optional

SAMPLE_RATE = 44100
CHANNELS = 2
BYTES_PER_FRAME = 4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIPS_DIR = os.path.join(BASE_DIR, "clips")
DEFAULT_VIDEO = r"C:\Users\Lenovo\Downloads\Untitled design (1).mp4"

async def synthesize_elevenlabs(text: str, voice_id: str, api_key: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=pcm_44100"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    loop = asyncio.get_event_loop()
    def _fetch():
        with urllib.request.urlopen(req) as resp:
            return resp.read()
    return await loop.run_in_executor(None, _fetch)

async def synthesize_edge(text: str, voice: str, rate: str = "+0%") -> tuple[bytes, float, bytes]:
    """
    Returns (raw_pcm_stereo, duration_seconds, mp3_bytes)
    """
    comm = edge_tts.Communicate(text, voice, rate=rate)
    mp3_chunks = []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            mp3_chunks.append(chunk["data"])
    
    mp3_data = b"".join(mp3_chunks)
    dec = miniaudio.decode(mp3_data)
    frames = len(dec.samples) // dec.nchannels
    duration = frames / dec.sample_rate
    raw_pcm = bytes(dec.samples)
    return raw_pcm, duration, mp3_data

async def process_script(
    segments: List[Dict[str, Any]],
    voice: str = "en-US-GuyNeural",
    elevenlabs_key: Optional[str] = None,
    elevenlabs_voice_id: Optional[str] = None,
    video_path: Optional[str] = None,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> Dict[str, Any]:
    os.makedirs(CLIPS_DIR, exist_ok=True)

    if not segments:
        raise ValueError("No segments provided")

    max_end = max(s["end"] for s in segments)
    total_timeline_sec = max(max_end, 5.0)

    # If video path is valid, match video length if greater
    if video_path and os.path.exists(video_path):
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        probe = subprocess.run([ffmpeg_exe, "-i", video_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        for line in probe.stderr.splitlines():
            if "Duration:" in line:
                try:
                    dur_str = line.split("Duration:")[1].split(",")[0].strip()
                    parts = dur_str.split(":")
                    vid_dur = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
                    total_timeline_sec = max(total_timeline_sec, vid_dur)
                except Exception:
                    pass
                break

    total_frames = int(total_timeline_sec * SAMPLE_RATE)
    master_buffer = bytearray(total_frames * BYTES_PER_FRAME)

    results = []
    total_segs = len(segments)

    for idx, seg in enumerate(segments, 1):
        seg_id = seg["id"]
        label = seg["label"]
        start_sec = seg["start"]
        slot_sec = seg["slot"]
        text = seg["text"]

        if progress_callback:
            progress_callback(f"Synthesizing [{idx}/{total_segs}]: {label}", (idx / total_segs) * 0.7)

        clip_filename = f"clip_{seg_id:02d}.mp3"
        clip_filepath = os.path.join(CLIPS_DIR, clip_filename)

        if elevenlabs_key and elevenlabs_voice_id:
            pcm_data = await synthesize_elevenlabs(text, elevenlabs_voice_id, elevenlabs_key)
            duration = len(pcm_data) / (SAMPLE_RATE * 2) # mono 16-bit
            # Convert mono PCM to stereo
            stereo_buf = bytearray(len(pcm_data) * 2)
            for i in range(0, len(pcm_data), 2):
                sample = pcm_data[i:i+2]
                stereo_buf[i*2 : i*2+2] = sample
                stereo_buf[i*2+2 : i*2+4] = sample
            raw_pcm = bytes(stereo_buf)
            # Save as WAV for clip
            clip_filename = f"clip_{seg_id:02d}.wav"
            clip_filepath = os.path.join(CLIPS_DIR, clip_filename)
            with wave.open(clip_filepath, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(raw_pcm)
        else:
            # First pass at natural rate
            raw_pcm, duration, mp3_data = await synthesize_edge(text, voice, rate="+0%")
            
            # If duration exceeds slot by more than 0.2s, auto-scale rate
            if duration > (slot_sec + 0.1):
                over_ratio = duration / slot_sec
                speed_pct = min(60, int((over_ratio - 1.0) * 100) + 8)
                rate_str = f"+{speed_pct}%"
                raw_pcm, duration, mp3_data = await synthesize_edge(text, voice, rate=rate_str)

            with open(clip_filepath, "wb") as f:
                f.write(mp3_data)

        # Place in master buffer
        start_frame = int(start_sec * SAMPLE_RATE)
        start_byte = start_frame * BYTES_PER_FRAME
        end_byte = start_byte + len(raw_pcm)

        if end_byte > len(master_buffer):
            master_buffer.extend(bytearray(end_byte - len(master_buffer)))

        master_buffer[start_byte:end_byte] = raw_pcm

        results.append({
            "id": seg_id,
            "label": label,
            "start": start_sec,
            "end": seg["end"],
            "duration": round(duration, 2),
            "text": text,
            "clip_url": f"/clips/{clip_filename}"
        })

    if progress_callback:
        progress_callback("Stitching master audio timeline...", 0.8)

    master_wav_path = os.path.join(BASE_DIR, "dogfoodhack_voiceover_master.wav")
    with wave.open(master_wav_path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(bytes(master_buffer))

    video_url = None
    merged_video_path = os.path.join(BASE_DIR, "DogfoodHack_Demo_Walkthrough.mp4")

    # If video path provided or default video exists
    chosen_video = video_path if (video_path and os.path.exists(video_path)) else (DEFAULT_VIDEO if os.path.exists(DEFAULT_VIDEO) else None)
    
    if chosen_video:
        if progress_callback:
            progress_callback("Merging audio into video with FFmpeg...", 0.9)

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_exe,
            "-i", chosen_video,
            "-i", master_wav_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-y",
            merged_video_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            video_url = "/DogfoodHack_Demo_Walkthrough.mp4"

    if progress_callback:
        progress_callback("Completed!", 1.0)

    return {
        "success": True,
        "total_duration": round(total_timeline_sec, 2),
        "segments": results,
        "master_audio_url": "/dogfoodhack_voiceover_master.wav",
        "video_url": video_url
    }
