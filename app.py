import streamlit as st
import yt_dlp
import tempfile
import shutil
from pathlib import Path

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="YouTube Downloader & Converter",
    page_icon="🎬",
    layout="centered"
)

# ------------------ STYLES ------------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
    color: #e5e7eb;
    font-family: 'Segoe UI', sans-serif;
}
h1 {
    text-align: center;
    color: #6366f1;
}
.card {
    background-color: #020617;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.stButton > button {
    background-color: #6366f1;
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
    font-weight: bold;
}
.stProgress > div > div {
    background-color: #6366f1;
}
</style>
""", unsafe_allow_html=True)

# ------------------ UI ------------------
st.markdown("<h1>🎬 YouTube Downloader & Converter</h1>", unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

youtube_url = st.text_input("🔗 Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")

option = st.selectbox(
    "⚙️ Choose Action",
    ("Download Video (MP4)", "Download Audio (MP3)", "Convert Video to Audio (MP3)")
)

progress_bar = st.progress(0)
status_text = st.empty()

# ------------------ FUNCTIONS ------------------
def get_video_info(url):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        return ydl.extract_info(url, download=False)

def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "0%").replace("%","")
        try:
            progress_bar.progress(int(float(percent)))
            status_text.text(f"⬇️ Downloading... {percent}%")
        except:
            pass
    elif d["status"] == "finished":
        progress_bar.progress(100)
        status_text.text("🎧 Processing...")

def download_youtube(url, download_type="video"):
    """
    download_type: "video", "audio", "convert_audio"
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        ydl_opts = {}
        if download_type == "video":
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": str(Path(tmp_dir) / "%(title)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "quiet": True,
            }
        elif download_type == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": str(Path(tmp_dir) / "%(title)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "quiet": True,
            }
        elif download_type == "convert_audio":
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
            filename = ydl.prepare_filename(info)

            # Determine final file path
            if download_type == "convert_audio":
                final_file = Path(tmp_dir) / (Path(filename).stem + ".mp3")
            elif download_type == "audio":
                # Copy as mp3 if not converted
                final_file = Path(tmp_dir) / (Path(filename).stem + ".mp3")
            else:
                final_file = Path(filename)

            # Copy to permanent downloads folder for Streamlit
            downloads_dir = Path("downloads")
            downloads_dir.mkdir(exist_ok=True)
            final_path = downloads_dir / final_file.name
            shutil.copy(final_file, final_path)

            return final_path, info

# ------------------ ACTION ------------------
if st.button("⬇️ Start"):
    if not youtube_url:
        st.warning("Please enter a YouTube URL!")
    else:
        try:
            info = get_video_info(youtube_url)
            st.image(info["thumbnail"], width=300)
            st.markdown(f"**🎬 Title:** {info['title']}")
            st.markdown(f"**⏱ Duration:** {info['duration']//60} min")

            if option == "Download Video (MP4)":
                file_path, meta = download_youtube(youtube_url, "video")
            elif option == "Download Audio (MP3)":
                file_path, meta = download_youtube(youtube_url, "audio")
            else:
                file_path, meta = download_youtube(youtube_url, "convert_audio")

            st.success(f"✅ {option} ready!")

            with open(file_path, "rb") as f:
                st.download_button(
                    "⬇️ Download File",
                    data=f,
                    file_name=file_path.name,
                    mime="application/octet-stream" if option.startswith("Download Video") else "audio/mpeg"
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
