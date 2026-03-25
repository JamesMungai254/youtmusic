from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import tempfile
from pathlib import Path
import shutil
import subprocess
import logging

app = FastAPI(title="YouTube Downloader API")

# -------------------- LOGGING --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt-downloader")

# -------------------- UTILS --------------------
def ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed on the system."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

# -------------------- ROUTES --------------------
@app.get("/download")
def download_video(url: str, mode: str = "video"):
    """
    Download a YouTube video or audio.

    Parameters:
    - url: YouTube video URL
    - mode: "video" or "audio"
    """
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)

            # -------------------- YT-DLP OPTIONS --------------------
            if mode == "video":
                ydl_opts = {
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "outtmpl": str(tmp_dir_path / "%(title)s.%(ext)s"),
                    "noplaylist": True,
                    "quiet": True,
                    "merge_output_format": "mp4",
                    "http_headers": {"User-Agent": "Mozilla/5.0"},
                    "hls_prefer_native": True,  # handle SABR adaptive streams
                }
            elif mode == "audio":
                if not ffmpeg_installed():
                    logger.error("FFmpeg not found on system.")
                    raise HTTPException(status_code=500, detail="FFmpeg is required for audio conversion")

                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": str(tmp_dir_path / "%(title)s.%(ext)s"),
                    "noplaylist": True,
                    "quiet": True,
                    "http_headers": {"User-Agent": "Mozilla/5.0"},
                    "hls_prefer_native": True,
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                }
            else:
                raise HTTPException(status_code=400, detail="Invalid mode. Must be 'video' or 'audio'")

            # -------------------- DOWNLOAD --------------------
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    logger.info(f"Starting download: {url} as {mode}")
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                    # Determine final file path
                    if mode == "audio":
                        file_path = Path(filename).with_suffix(".mp3")
                    else:
                        file_path = Path(filename)

                    if not file_path.exists():
                        logger.error(f"File not found after download: {file_path}")
                        raise HTTPException(status_code=500, detail="File not found after download")

                    # Copy to safe downloads folder inside tmp_dir
                    downloads_dir = tmp_dir_path / "downloads"
                    downloads_dir.mkdir(exist_ok=True)
                    final_path = downloads_dir / file_path.name
                    shutil.copy(file_path, final_path)

                    logger.info(f"Download complete: {final_path}")
                    return FileResponse(final_path, filename=final_path.name)

            except yt_dlp.utils.DownloadError as e:
                logger.error(f"yt-dlp download error: {e}")
                raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")