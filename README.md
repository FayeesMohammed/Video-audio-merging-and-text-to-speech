# 🎬 Video-Audio Merging & Text-to-Speech Studio

A complete, self-contained system to generate synchronized voiceover narrations from timestamped scripts and merge them seamlessly into video recordings.

---

## 📁 Directory Contents

| File / Folder | Purpose |
| :--- | :--- |
| **`DogfoodHack_Demo_Walkthrough.mp4`** | Final 1080p demo video merged with all 19 synchronized voiceover cues. |
| **`dogfoodhack_voiceover_master.wav`** | Master audio track (44.1kHz stereo WAV) with exact time padding and silence. |
| **`clips/`** | Directory containing all 19 individual `.mp3` voiceover segments. |
| **`index.html`** | Web player interface for video playback, clip previewing, and downloads. |
| **`server.py`** | Web server with automatic browser opening and HTTP download support. |
| **`build_full_script_video.py`** | Pipeline script to regenerate speech clips, audio timeline, and video merge. |
| **`start.bat` / `start.ps1`** | Double-click Windows launcher to start the web app. |
| **`requirements.txt`** | Python dependencies (`edge-tts`, `miniaudio`, `imageio-ffmpeg`). |

---

## 🚀 How to Run the Web App

### Option A: Double Click
Simply double-click **`start.bat`**. It will start the server and automatically launch the web interface in your browser at `http://localhost:8080`.

### Option B: Terminal Command
Run in PowerShell / Command Prompt:
```powershell
python server.py
```

---

## 🛠️ How to Re-generate or Modify Audio

If you ever want to change the script, voice, or video source:
1. Edit the `SEGMENTS` list or `VOICE` setting in `build_full_script_video.py`.
2. Run:
```powershell
python build_full_script_video.py
```
3. The new video and audio files will be automatically generated and updated in this folder.
