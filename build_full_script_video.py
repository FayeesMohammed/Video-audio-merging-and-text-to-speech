import asyncio
import os
import wave
import subprocess
import edge_tts
import miniaudio
import imageio_ffmpeg

VOICE = "en-US-GuyNeural"
SAMPLE_RATE = 44100
CHANNELS = 2
BYTES_PER_FRAME = 4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIPS_DIR = os.path.join(BASE_DIR, "clips")

# Input video defaults to Downloads file or a local copy
DEFAULT_INPUT_VIDEO = r"C:\Users\Lenovo\Downloads\Untitled design (1).mp4"
OUTPUT_VIDEO = os.path.join(BASE_DIR, "DogfoodHack_Demo_Walkthrough.mp4")
OUTPUT_MASTER_WAV = os.path.join(BASE_DIR, "dogfoodhack_voiceover_master.wav")
TEMP_WAV = os.path.join(BASE_DIR, "temp_full_timeline.wav")

TOTAL_DURATION = 180.03  # 03:00.03

SEGMENTS = [
    {
        "id": 1,
        "label": "0:00 – 0:06",
        "start": 0.0,
        "end": 6.0,
        "rate": "+25%",
        "text": "Welcome to DogfoodHack. An organizer signs in and submits a new event proposal, VIBEATHON."
    },
    {
        "id": 2,
        "label": "0:06 – 0:12",
        "start": 6.0,
        "end": 12.0,
        "rate": "+10%",
        "text": "The Platform Admin reviews the proposal and approves or rejects it, with an optional reason."
    },
    {
        "id": 3,
        "label": "0:12 – 0:17",
        "start": 12.0,
        "end": 17.0,
        "rate": "+20%",
        "text": "The organizer then sets visibility, deadline, time zone, team size, and track mode."
    },
    {
        "id": 4,
        "label": "0:17 – 0:24",
        "start": 17.0,
        "end": 24.0,
        "rate": "+10%",
        "text": "Judges are invited by email. The roster shows each status, with options to confirm or revoke."
    },
    {
        "id": 5,
        "label": "0:24 – 0:33",
        "start": 24.0,
        "end": 33.0,
        "rate": "+0%",
        "text": "Approved events appear on the public home page, filterable by open, upcoming, or closed, with search and each event's deadline."
    },
    {
        "id": 6,
        "label": "0:33 – 0:40",
        "start": 33.0,
        "end": 40.0,
        "rate": "+10%",
        "text": "Participants sign in, open the event page with its overview, tracks, and prizes, and create a team by naming it."
    },
    {
        "id": 7,
        "label": "0:40 – 0:48",
        "start": 40.0,
        "end": 48.0,
        "rate": "+15%",
        "text": "The submission form covers basics, details and links, plus an optional thumbnail in JPEG, PNG, or WebP, under five megabytes."
    },
    {
        "id": 8,
        "label": "0:48 – 0:56",
        "start": 48.0,
        "end": 56.0,
        "rate": "+15%",
        "text": "Team owners can generate invitation links with a usage limit and expiry. Work saves as a draft or submits as final."
    },
    {
        "id": 9,
        "label": "0:56 – 1:10",
        "start": 56.0,
        "end": 70.0,
        "rate": "+0%",
        "text": "Every participant signs in with individual credentials, creates a team, and completes the same form, so each project is recorded before the deadline."
    },
    {
        "id": 10,
        "label": "1:10 – 1:30",
        "start": 70.0,
        "end": 90.0,
        "rate": "+0%",
        "text": "The same steps repeat across the platform, with each participant signing in separately, until all ten projects are submitted."
    },
    {
        "id": 11,
        "label": "1:31 – 1:43",
        "start": 91.0,
        "end": 103.0,
        "rate": "+10%",
        "text": "The organizer creates a judging round and rubric, then previews and commits the plan: ten projects, five judges, twenty assignments. Telemetry, stage closure, and exports become available."
    },
    {
        "id": 12,
        "label": "1:43 – 1:55",
        "start": 103.0,
        "end": 115.0,
        "rate": "+0%",
        "text": "Judges review their assigned projects, with details beside a rubric form, where a slider scores User Experience from zero to five."
    },
    {
        "id": 13,
        "label": "1:55 – 2:06",
        "start": 115.0,
        "end": 126.0,
        "rate": "+0%",
        "text": "Written feedback can be added. Reviews can be saved as drafts or finalized with Submit Review, and each judge repeats this for every assignment."
    },
    {
        "id": 14,
        "label": "2:06 – 2:16",
        "start": 126.0,
        "end": 136.0,
        "rate": "+0%",
        "text": "Each judge signs in with their own account and completes four reviews, so every project receives independent scores."
    },
    {
        "id": 15,
        "label": "2:16 – 2:25",
        "start": 136.0,
        "end": 145.0,
        "rate": "+0%",
        "text": "The judging dashboard shows the open round, completed reviews out of the total, and each submitted assignment with its score."
    },
    {
        "id": 16,
        "label": "2:25 – 2:44",
        "start": 145.0,
        "end": 164.0,
        "rate": "+0%",
        "text": "Further judges follow the same process. Each project in this demonstration is evaluated by two judges, and every review stays linked to its assignment."
    },
    {
        "id": 17,
        "label": "2:44 – 2:49",
        "start": 164.0,
        "end": 169.0,
        "rate": "+0%",
        "text": "Finally, the organizer signs in to review the outcome."
    },
    {
        "id": 18,
        "label": "2:49 – 2:55",
        "start": 169.0,
        "end": 175.0,
        "rate": "+10%",
        "text": "The status is valid and calibrated, with bias offsets calculated across twenty reviews."
    },
    {
        "id": 19,
        "label": "2:55 – 3:00",
        "start": 175.0,
        "end": 180.0,
        "rate": "+10%",
        "text": "Projects rank by normalized score, then the stage is finalized and published."
    }
]

async def build_full_voiceover(input_video_path=DEFAULT_INPUT_VIDEO):
    os.makedirs(CLIPS_DIR, exist_ok=True)
    total_frames = int(TOTAL_DURATION * SAMPLE_RATE)
    master_buffer = bytearray(total_frames * BYTES_PER_FRAME)

    print(f"=== Generating 19-Part Synchronized Voiceover ({VOICE}) ===")
    print(f"Total Video Timeline: {TOTAL_DURATION:.2f}s (03:00)\n")

    for seg in SEGMENTS:
        seg_id = seg["id"]
        label = seg["label"]
        start_sec = seg["start"]
        end_sec = seg["end"]
        slot = end_sec - start_sec
        rate = seg["rate"]
        text = seg["text"]

        clip_name = f"clip_{seg_id:02d}_{label.replace(':', '-').replace(' ', '').replace('–', '_')}.mp3"
        clip_path = os.path.join(CLIPS_DIR, clip_name)

        comm = edge_tts.Communicate(text, VOICE, rate=rate)
        await comm.save(clip_path)

        dec = miniaudio.decode_file(clip_path)
        raw_pcm = bytes(dec.samples)
        frames = len(dec.samples) // dec.nchannels
        duration = frames / dec.sample_rate

        status = "OK" if duration <= slot else f"EXCEEDED by {duration - slot:.2f}s"
        print(f"[{seg_id:02d}/19] [{label}] ({start_sec:.1f}s -> {end_sec:.1f}s): dur = {duration:.2f}s (slot: {slot:.1f}s) -> {status}")

        start_frame = int(start_sec * SAMPLE_RATE)
        start_byte = start_frame * BYTES_PER_FRAME
        end_byte = start_byte + len(raw_pcm)

        if end_byte > len(master_buffer):
            master_buffer.extend(bytearray(end_byte - len(master_buffer)))

        master_buffer[start_byte:end_byte] = raw_pcm

    print(f"\nWriting master timeline WAV track to {OUTPUT_MASTER_WAV}...")
    with wave.open(OUTPUT_MASTER_WAV, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(bytes(master_buffer))

    if not os.path.exists(input_video_path):
        print(f"Input video not found at: {input_video_path}")
        return

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Merging with video: {input_video_path}")

    cmd = [
        ffmpeg,
        "-i", input_video_path,
        "-i", OUTPUT_MASTER_WAV,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-y",
        OUTPUT_VIDEO
    ]
    print(f"Saving to: {OUTPUT_VIDEO}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        raise RuntimeError(f"FFmpeg error: {res.stderr}")

    print("\nSUCCESS! Merged video and audio created successfully!")

if __name__ == "__main__":
    asyncio.run(build_full_voiceover())
