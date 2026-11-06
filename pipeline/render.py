import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
API_KEY = os.environ.get("GEMINI_API_KEY", "")
NARRATION = Path(os.environ.get("NARRATION_FILE", "assets/narration.mp3"))
SCENES_FILE = Path(os.environ.get("SCENES_FILE", "pipeline/scenes.json"))
TITLE = os.environ.get("VIDEO_TITLE", "KILAS FAKTA")
OUT_DIR = Path("output")
CLIPS_DIR = OUT_DIR / "clips"


def run(command):
    subprocess.run(command, check=True)


def generate_clip(scene, config):
    prompt = (
        config["visual_style"]
        + "\nHistorical scene direction: " + scene["prompt"]
        + "\nCreate a continuous moving shot. Show clear movement by people, horses, cloth, smoke, weather or camera. "
          "Keep the same illustrated documentary art direction. No abstract geometric shapes, no static slideshow, "
          "no modern objects, no text, no logos, and no subtitles inside the generated footage."
    )
    payload = {
        "model": config.get("model", "gemini-omni-1.2-flash"),
        "input": prompt,
        "response_format": {
            "type": "video",
            "aspect_ratio": config.get("aspect_ratio", "9:16"),
            "resolution": config.get("resolution", "720p"),
            "duration": f'{config.get("duration_seconds", 10)}s'
        }
    }
    headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}

    for attempt in range(3):
        response = requests.post(API_URL, headers=headers, json=payload, timeout=900)
        if response.ok:
            data = response.json()
            if data.get("status") not in (None, "completed"):
                raise RuntimeError(f"Gemini interaction status: {data.get('status')}")
            for step in data.get("steps", []):
                if step.get("type") == "model_output":
                    for item in step.get("content", []):
                        if item.get("type") == "video" and item.get("data"):
                            return base64.b64decode(item["data"])
                        if item.get("type") == "video" and item.get("uri"):
                            video_response = requests.get(item["uri"], timeout=900)
                            video_response.raise_for_status()
                            return video_response.content
            raise RuntimeError("Gemini returned no video. Check model access, quota and API response.")
        if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
            time.sleep(20 * (attempt + 1))
            continue
        raise RuntimeError(f"Gemini API error {response.status_code}: {response.text[:1200]}")

    raise RuntimeError("Video generation failed after retries.")


def main():
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it in GitHub Settings > Secrets and variables > Actions.")
    if not NARRATION.is_file():
        raise FileNotFoundError(f"Narration audio not found: {NARRATION}")

    config = json.loads(SCENES_FILE.read_text(encoding="utf-8"))
    scenes = config.get("scenes", [])
    if not scenes:
        raise RuntimeError("The scenes JSON contains no scenes.")

    OUT_DIR.mkdir(exist_ok=True)
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    concat_file = OUT_DIR / "clips.txt"
    generated = []

    for index, scene in enumerate(scenes, start=1):
        clip_path = CLIPS_DIR / f"scene_{index:02d}.mp4"
        print(f"Generating scene {index}/{len(scenes)}: {scene['id']}", flush=True)
        clip_path.write_bytes(generate_clip(scene, config))
        generated.append(clip_path)

    normalized = []
    for index, clip in enumerate(generated, start=1):
        normalized_path = CLIPS_DIR / f"normalized_{index:02d}.mp4"
        run([
            "ffmpeg", "-y", "-i", str(clip), "-an", "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24,setsar=1",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", str(normalized_path)
        ])
        normalized.append(normalized_path)

    concat_file.write_text(
        "".join(f"file '{p.resolve()}'\n" for p in normalized),
        encoding="utf-8"
    )
    joined = OUT_DIR / "joined.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(joined)])

    duration = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(NARRATION)
    ], text=True).strip())

    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    safe_title = TITLE.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    video_filter = (
        f"drawtext=fontfile={font}:text='{safe_title}':"
        "fontcolor=white:fontsize=38:borderw=3:bordercolor=black@0.8:"
        "x=(w-text_w)/2:y=h*0.12:enable='between(t,0,3)',"
        f"drawtext=fontfile={font}:text='KILAS FAKTA':"
        "fontcolor=white@0.9:fontsize=28:borderw=2:bordercolor=black@0.7:"
        "x=w-text_w-42:y=45"
    )

    subtitle = Path("assets/subtitles.srt")
    if subtitle.is_file():
        video_filter += (
            f",subtitles={subtitle.as_posix()}:"
            "force_style='FontName=DejaVu Sans,FontSize=18,Outline=2,Shadow=1,Alignment=2,MarginV=150'"
        )

    music = Path("assets/music.mp3")
    output = OUT_DIR / "KILAS_FAKTA.mp4"

    if music.is_file():
        filter_complex = (
            f"[0:v]{video_filter}[v];"
            "[1:a]volume=1.0[narr];[2:a]volume=0.10[music];"
            "[narr][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        command = [
            "ffmpeg", "-y", "-i", str(joined), "-i", str(NARRATION), "-i", str(music),
            "-filter_complex", filter_complex, "-map", "[v]", "-map", "[aout]",
            "-t", str(duration), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output)
        ]
    else:
        command = [
            "ffmpeg", "-y", "-i", str(joined), "-i", str(NARRATION),
            "-vf", video_filter, "-map", "0:v:0", "-map", "1:a:0",
            "-t", str(duration), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output)
        ]

    run(command)
    print(f"Finished: {output}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"PIPELINE FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
