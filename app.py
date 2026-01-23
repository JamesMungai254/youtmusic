import streamlit as st
import yt_dlp
import tempfile
import shutil
from pathlib import Path
import os
from moviepy.editor import VideoFileClip

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="YouTube Downloader & Video-to-Audio Converter",
    page_icon="🎬",
    layout="centered"
)

# ------------------ STYLES ------------------
st.markdown("""
<style>
body {background-color: #0f172a; color: #e5e7eb; font-family: 'Segoe UI', sans-serif;}
h1 {text-align: center; color: #6366f1;}
.card {background-color: #020617; padding: 25px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);}
.stButton > button {background-color: #6366f1; color: white; border-radius: 10px; height: 45px; width: 100%; font-weight: bold;}
.stProgress > div > div {background-color: #6366f1;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎬 YouTube Downloader & Video-to-Audio Converter</h1>", unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

# ------------------ OPTIONS ------------------
tab1, tab2 = st.tabs(["YouTube Downloader", "Video-to-Audio Converter"])

# ------------------ TAB 1: YouTube Downloader ------------------
with tab1:
    youtube_url = st.text_input("🔗 Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
    option = st.selectbox("⚙️ Choose Download Type", ("Video (MP4)", "Audio (MP3)"))
    progress_bar = st.progress(0)
    status_text = st.empty()

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
                final_file = Path(tmp_dir) / (Path(filename).stem + (".mp3" if download_type=="audio" else ".mp4"))

                # Copy to permanent downloads folder
                downloads_dir = Path("downloads")
                downloads_dir.mkdir(exist_ok=True)
                final_path = downloads_dir / final_file.name
                shutil.copy(final_file, final_path)

                return final_path, info

    if st.button("⬇️ Start Download (YouTube)"):
        if not youtube_url:
            st.warning("Please enter a YouTube URL!")
        else:
            try:
                download_type = "video" if option=="Video (MP4)" else "audio"
                file_path, info = download_youtube(youtube_url, download_type)

                st.image(info["thumbnail"], width=300)
                st.markdown(f"**🎬 Title:** {info['title']}")
                st.markdown(f"**⏱ Duration:** {info['duration']//60} min")

                st.success(f"✅ {option} ready!")
                with open(file_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download File",
                        data=f,
                        file_name=file_path.name,
                        mime="audio/mpeg" if download_type=="audio" else "video/mp4"
                    )

            except Exception as e:
                st.error("❌ Failed to download video.")
                st.exception(e)

# ------------------ TAB 2: Video-to-Audio Converter ------------------
with tab2:
    uploaded_file = st.file_uploader("📂 Upload a video file", type=["mp4", "mov", "mkv", "avi"])
    if uploaded_file:
        progress_bar2 = st.progress(0)
        status_text2 = st.empty()

        if st.button("🎧 Convert to MP3"):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_video:
                    tmp_video.write(uploaded_file.read())
                    tmp_video_path = tmp_video.name

                # Convert to MP3 using moviepy
                status_text2.text("🎬 Converting video to audio...")
                clip = VideoFileClip(tmp_video_path)
                output_audio_path = Path("downloads") / (Path(uploaded_file.name).stem + ".mp3")
                clip.audio.write_audiofile(output_audio_path, logger=None)
                clip.close()
                os.remove(tmp_video_path)  # Delete temp video

                progress_bar2.progress(100)
                status_text2.text("✅ Conversion complete!")

                with open(output_audio_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download MP3",
                        data=f,
                        file_name=output_audio_path.name,
                        mime="audio/mpeg"
                    )

            except Exception as e:
                st.error("❌ Conversion failed.")
                st.exception(e)

st.markdown('</div>', unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("""
---
<p style="text-align:center;color:#9ca3af;">
Built with ❤️ by <b>James Mungai</b> | Streamlit • yt-dlp • FFmpeg • MoviePy
</p>
""", unsafe_allow_html=True)
