import re
from typing import List, Dict, Any

def parse_time_to_seconds(time_str: str) -> float:
    """
    Parses time strings like '0:06', '00:06', '1:30', '01:30', '01:30:15' into seconds.
    """
    time_str = time_str.strip().strip("[]()")
    parts = time_str.split(":")
    if len(parts) == 2:
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    elif len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 1:
        return float(parts[0])
    raise ValueError(f"Unknown time format: {time_str}")

def parse_script_text(raw_text: str) -> List[Dict[str, Any]]:
    """
    Parses scripts in formats like:
      0:00 – 0:06
      Welcome to DogfoodHack...

      or:
      [00:00 - 00:05]
      "Welcome to DogfoodHack..."

      or:
      0:00 - 0:06: Welcome to DogfoodHack...
    """
    lines = raw_text.strip().splitlines()
    segments = []
    
    # Pattern 1: [00:00 - 00:05] or 0:00 - 0:06 or 0:00 – 0:06
    # followed by optional text on same line or next line
    pattern_time = re.compile(
        r'^\s*\[?\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—~to]+\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*\]?\s*[:\-]?\s*(.*)$',
        re.IGNORECASE
    )

    current_seg = None

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        match = pattern_time.match(line_clean)
        if match:
            if current_seg:
                current_seg["text"] = current_seg["text"].strip().strip('"\'')
                if current_seg["text"]:
                    segments.append(current_seg)
                current_seg = None

            start_str, end_str, inline_text = match.groups()
            try:
                start_sec = parse_time_to_seconds(start_str)
                end_sec = parse_time_to_seconds(end_str)
            except Exception:
                continue

            current_seg = {
                "id": len(segments) + 1,
                "label": f"{start_str} – {end_str}",
                "start": start_sec,
                "end": end_sec,
                "slot": max(0.5, end_sec - start_sec),
                "text": inline_text.strip() if inline_text else ""
            }
        else:
            if current_seg:
                if current_seg["text"]:
                    current_seg["text"] += " " + line_clean
                else:
                    current_seg["text"] = line_clean

    if current_seg:
        current_seg["text"] = current_seg["text"].strip().strip('"\'')
        if current_seg["text"]:
            segments.append(current_seg)

    return segments

if __name__ == "__main__":
    sample = """
    0:00 – 0:06
    Welcome to DogfoodHack. An organizer signs in and submits a new event proposal, VIBEATHON.

    [0:06 - 0:12]
    "The Platform Admin reviews the proposal and approves or rejects it."
    """
    res = parse_script_text(sample)
    print("Parsed count:", len(res))
    for r in res:
        print(r)
