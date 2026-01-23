import streamlit as st
import yt_dlp
import tempfile
import shutil
from pathlib import Path
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="YouTube → Audio",
    page_icon="🎵",
    layout="centered"
)

# ------------------ STYLES ------------------
st.markdown("""
<style>
.main {
    background-color: #0f172a;
}
h1, h2, h3, p, label {
    color: #e5e7eb;
}
.stButton > button {
    background-color: #6366f1;
    color: white;
    border-radius: 10px;
    height: 45px;
}
.stProgress > div > div {
    background-color: #6366f1;
}
.card {
    background-color: #020617;
    padding: 20px;
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)

# ------------------ UI ------------------
st.markdown("<h1 style='text-align:center;'>🎵 YouTube → Audio Converter</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Convert YouTube videos to high-quality MP3</p>", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

youtube_url = st.text_input("🔗 YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

progress_bar = st.progress(0)
status_text = st.empty()

# ------------------ FUNCTIONS ------------------
def get_video_info(url):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        return ydl.extract_info(url, download=False)

def download_audio(url, progress_hook):
    # Create a temporary folder for video download
    with tempfile.TemporaryDirectory() as tmp_dir:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(Path(tmp_dir) / "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # yt-dlp converts and saves MP3 in the same tmp_dir
            filename = ydl.prepare_filename(info)
            audio_file = filename.rsplit(".", 1)[0] + ".mp3"

            # Copy the MP3 to the "downloads" folder for Streamlit download
            output_dir = Path("downloads")
            output_dir.mkdir(exist_ok=True)
            final_path = output_dir / Path(audio_file).name
            shutil.copy(audio_file, final_path)

            # The temporary folder is automatically deleted here
            return final_path, info

def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "0%").replace("%", "")
        try:
            progress_bar.progress(int(float(percent)))
            status_text.text(f"⬇️ Downloading... {percent}%")
        except:
            pass
    elif d["status"] == "finished":
        progress_bar.progress(100)
        status_text.text("🎧 Converting to audio...")

# ------------------ ACTION ------------------
if st.button("🎧 Convert to MP3"):
    if not youtube_url:
        st.warning("Please enter a YouTube link.")
    else:
        try:
            info = get_video_info(youtube_url)

            # Thumbnail
            st.image(info["thumbnail"], width=300)

            # Video info
            st.markdown(f"**🎬 Title:** {info['title']}")
            st.markdown(f"**⏱ Duration:** {info['duration']//60} min")

            audio_file, metadata = download_audio(youtube_url, progress_hook)

            st.success("✅ Audio ready!")

            with open(audio_file, "rb") as f:
                st.download_button(
                    "⬇️ Download MP3",
                    data=f,
                    file_name=audio_file.name,
                    mime="audio/mpeg"
                )

        except Exception as e:
            st.error("❌ Failed to process the video.")
            st.exception(e)

st.markdown('</div>', unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("""
---
<p style="text-align:center;color:#9ca3af;">
Built with ❤️ by <b>James Mungai</b> | Streamlit • yt-dlp • FFmpeg
</p>
""", unsafe_allow_html=True)
