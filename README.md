# 🎙️ Emerald Workstation — Video-Audio Merging & Text-to-Speech Studio

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-107B4F.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Edge-TTS](https://img.shields.io/badge/Engine-Microsoft_Edge_TTS-107B4F.svg?style=flat-square)](https://github.com/rany2/edge-tts)
[![FFmpeg](https://img.shields.io/badge/Media-FFmpeg_H.264/AAC-107B4F.svg?style=flat-square)](https://ffmpeg.org)
[![Python](https://img.shields.io/badge/Python-3.9+-107B4F.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Design](https://img.shields.io/badge/Design_System-Emerald_Workstation-107B4F.svg?style=flat-square)](#-design-system--tokens)

A commercial-grade, browser-based media production workstation and FastAPI backend for synthesizing timestamped voiceover narrations, generating sample-accurate master audio soundscapes, and multiplexing synchronized video tracks using FFmpeg.

---

## 🌟 Key Features

### 1. Studio & Script Console (Page 1)
- **Source Video Ingestion Deck:**
  - **Drag & Drop Zone:** Interactive drop well supporting MP4, WebM, and QuickTime MOV.
  - **Live Video Preview:** Embedded 16:9 player with instant Blob URL preview, detected filename, format badges, and one-click "🔄 Replace" / "✕ Remove" controls.
  - **Direct Filesystem Path:** Auto-sanitized path input that strips outer quotes and special characters from pasted paths.
- **Timestamped Voiceover Script Editor:**
  - Multi-line textarea for editing timestamped narrations (`0:00 – 0:06`).
  - Formatted placeholder hints for effortless script formatting.
  - One-click script clearing and instant timeline updates.
- **Dual Voice Synthesis Engine:**
  - **Free Microsoft Edge Neural Voices:** 6 natural neural voices (Guy, Christopher, Ryan, Jenny, Sonia, William) with zero API keys or rate limits.
  - **ElevenLabs API Integration:** Custom Voice ID and API key configuration drawer.
- **Reference Skeleton Loader (Inspired by `useless_project_temp`):**
  - Rotating dashed outer spinner ring (`spinDashed`).
  - Centered bobbing microphone avatar (`bobIcon`).
  - Dynamic cycling status subtitles with humorous and informative stage updates.
  - 4-stage pipeline stepper: `1. Parse Script` → `2. Neural Voice` → `3. Master Audio` → `4. Video Merge`.
  - Staggered triple bouncing dots and live percentage readout (`0%` → `100%`).

### 2. Production Monitor & Timeline (Page 2)
- **Multi-Track Master Sequencer Bar:**
  - High-precision timecode clock badge (`00:02:45.120`).
- **Central Preview Viewport:**
  - Framed 1080p MP4 synchronized video player (`#mainVideoPlayer`).
  - Format badge: `Canvas 1080p @ 60fps`.
- **Master 44.1kHz Stereo Soundscape:**
  - Standalone master audio player (`#mainAudioPlayer`).
  - **Interactive Waveform Visualizer (`#waveformCanvas`):**
    - 75 acoustic envelope speech bars with rounded caps.
    - Two-tone visualization: rich Emerald green (`#107B4F`) for played duration, soft sage (`#C4D9CD`) for unplayed duration.
    - Click-to-scrub seeking: clicking anywhere on the waveform immediately scrubs audio playback.
    - Real-time monospace timecodes (`#audioTimeCurrent`, `#audioTimeTotal`).
- **Speech Sync & Multi-Track Narration Cues (`#segmentsContainer`):**
  - Cue index badges (`Cue #01`, `0:00 – 0:06` in Courier Prime) clickable to seek the video player to that exact moment.
  - Full narration text display in high-legibility typography.
  - Telemetry badges: audio clip duration, allocated timeline slot, and calculated gap/headroom (`+0.8s gap`).
  - **Copy Action:** Copies cue narration text to clipboard with instant visual checkmark feedback and toast notification.
  - **Play Clip Action:** Auditions individual speech segments on demand (`playCueClip`).
  - **Live Playback Synchronization:** Cues automatically illuminate in emerald/mint as the video playhead advances through their time range.
- **Export Controls:**
  - **Export Master (FFmpeg H.264/AAC):** One-click download of the multiplexed MP4.
  - **Export Master Audio (.wav):** Download of the standalone 44.1kHz stereo master track.

### 3. Top Sticky Header & Navigation
- **Emerald WORKSTATION Branding:** High-contrast logo with Retro Floral display typography.
- **Segmented Control Navigation:** Studio and Production Monitor tabs with live synced cue counter badge (`#tabCueBadge`).
- **Session Reset Button:** Resets all inputs, video players, and script console with confirmation prompt and toast alert.

---

## 📁 Directory Structure & File Inventory

```
Video-audio-merging-and-text-to-speech/
├── fonts/                              # Local font assets
│   ├── Retro Floral.ttf                # Brand display typography font
│   └── Retro Floral.otf
├── index.html                          # Complete Emerald Workstation single-page application
├── server.py                           # FastAPI REST server & static media file router
├── pipeline.py                         # Asynchronous audio synthesis & FFmpeg video pipeline
├── script_parser.py                    # Timestamp parser and cue segment builder
├── requirements.txt                    # Python runtime package dependencies
├── start.bat                           # Windows batch launcher (starts server & opens browser)
├── start.ps1                           # Windows PowerShell launcher
└── README.md                           # Documentation & user manual
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.9 or higher
- Windows, macOS, or Linux
- Internet connection (for Microsoft Edge neural voice synthesis or ElevenLabs)

### 1. Installation
Clone or navigate to the project directory and install the required dependencies:

```powershell
pip install -r requirements.txt
```

### 2. Launch the Application

#### Option A: One-Click Windows Launcher
Double-click **`start.bat`** (or execute **`start.ps1`** in PowerShell). This starts the FastAPI server and automatically opens the interface in your default browser.

#### Option B: Terminal Command
Run directly via Python:
```powershell
python server.py
```
Then visit **`http://127.0.0.1:8080/`** in your browser.

---

## 🎙️ Timestamped Script Syntax Guide

The parser automatically detects timestamps formatted as `MM:SS – MM:SS` or `M:SS - M:SS` preceding each narration block:

```text
0:00 – 0:06
Welcome to our product showcase. An organizer signs in and submits a new proposal.

0:06 – 0:12
The platform administrator reviews the submission and approves it.

0:12 – 0:17
The team configures event visibility, timeline deadlines, and track categories.
```

- **Silence & Padding:** If the audio duration is shorter than the allotted time slot, the pipeline automatically inserts silence up to the next timestamp.
- **Overrun Protection:** If speech exceeds the slot, subsequent clips dynamically offset or compress to maintain synchronization.

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the Emerald Workstation production interface (`index.html`). |
| `POST` | `/api/generate` | Starts synthesis & video multiplexing. Accepts JSON body (`script_text`, `voice`, `elevenlabs_key`, `elevenlabs_voice_id`, `video_path`). |
| `GET` | `/api/progress` | Returns real-time pipeline status and percentage (`{"status": "...", "progress": 0.75}`). |
| `POST` | `/api/upload-video` | Handles multipart video file uploads from the Studio drag-and-drop zone. |
| `GET` | `/fonts/{font_name}` | Serves local typography files (e.g. `Retro Floral.ttf`). |
| `GET` | `/clips/{clip_name}` | Serves individual audio segment clips. |

---

## 🎨 Design System & Tokens

All interface styling is centralized via CSS custom properties in `:root`:

| Token | Value | Description |
| :--- | :--- | :--- |
| `--bg-primary` | `#F4F7F5` | Crisp light sage-gray studio canvas background |
| `--bg-panel` | `#FFFFFF` | Pure white cards and surfaces |
| `--bg-elevated` | `#EDF4F0` | Soft mint-tinted wells, inputs, and drop zones |
| `--accent-primary` | `#107B4F` | Rich Emerald green for active tabs, CTAs, and playheads |
| `--accent-hover` | `#0D6E44` | Deep emerald for hover and active pressed states |
| `--accent-mint` | `#D1F4E2` | Pastel mint for telemetry pills, cue gap tags, and waveforms |
| `--text-primary` | `#112A1F` | Deep dark forest pine for razor-sharp legibility |
| `--text-secondary` | `#4D665A` | Slate sage for subheadings, labels, and secondary metadata |
| `--border-color` | `#DCE8E1` | Precision hairline borders for cards and inputs |

---

## 📄 License & Credits

- **Author / Lead Developer:** kryPsis
- **Copyright:** © 2026 Emerald Workstation. All rights reserved.
