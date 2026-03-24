import streamlit as st
import yt_dlp
import tempfile
import shutil
from pathlib import Path
import subprocess
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="YouTube Downloader Pro",
    page_icon="🎬",
    layout="centered"
)

# ------------------ SESSION STATE ------------------
if "file_ready" not in st.session_state:
    st.session_state.file_ready = None
if "info" not in st.session_state:
    st.session_state.info = None

# ------------------ STYLES ------------------
st.markdown("""
<style>
body {background-color: #0f172a; color: #e5e7eb;}
h1 {text-align: center; color: #6366f1;}
.card {background-color: #020617; padding: 25px; border-radius: 16px;}
.stButton > button {background-color: #6366f1; color: white; border-radius: 10px; height: 45px; width: 100%; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎬 YouTube Downloader Pro</h1>", unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

# ------------------ TABS ------------------
tab1, tab2 = st.tabs(["📥 YouTube Downloader", "🎧 Video → MP3 Converter"])

# ------------------ PROGRESS HOOK ------------------
def progress_hook(d):
    if d["status"] == "downloading":
        percent_str = d.get("_percent_str", "0%").strip().replace("%", "")
        speed = d.get("_speed_str", "0 KB/s")
        try:
            percent = float(percent_str)
            progress_bar.progress(min(int(percent), 100))
            status_text.text(f"⬇️ {percent:.1f}% | ⚡ {speed}")
        except:
            pass
    elif d["status"] == "finished":
        progress_bar.progress(100)
        status_text.text("🎧 Processing...")

# ------------------ TAB 1 ------------------
with tab1:
    youtube_url = st.text_input("🔗 YouTube URL")

    col1, col2 = st.columns(2)
    with col1:
        download_type = st.selectbox("Type", ["Video", "Audio (MP3)"])
    with col2:
        resolution = st.selectbox("Resolution", ["best", "1080", "720", "480", "360"])

    progress_bar = st.progress(0)
    status_text = st.empty()

    def download_video(url, mode, res):
        with tempfile.TemporaryDirectory() as tmp_dir:

            if mode == "Video":
                format_str = f"bestvideo[height<={res}]+bestaudio/best" if res != "best" else "bestvideo+bestaudio/best"

                ydl_opts = {
                    "format": format_str,
                    "outtmpl": str(Path(tmp_dir) / "%(title).50s.%(ext)s"),
                    "merge_output_format": "mp4",
                    "progress_hooks": [progress_hook],
                    "quiet": True,
                }

            else:
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": str(Path(tmp_dir) / "%(title).50s.%(ext)s"),
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

                if mode == "Audio (MP3)":
                    final_file = Path(filename).with_suffix(".mp3")
                else:
                    final_file = Path(filename).with_suffix(".mp4")

                downloads_dir = Path("downloads")
                downloads_dir.mkdir(exist_ok=True)
                final_path = downloads_dir / final_file.name

                shutil.copy(final_file, final_path)

                return final_path, info

    if st.button("⬇️ Download"):
        if not youtube_url:
            st.warning("Enter a valid URL")
        else:
            try:
                file_path, info = download_video(youtube_url, download_type, resolution)

                st.session_state.file_ready = file_path
                st.session_state.info = info

            except Exception as e:
                st.error("Download failed")
                st.exception(e)

    # -------- SHOW RESULT --------
    if st.session_state.file_ready:
        info = st.session_state.info
        file_path = st.session_state.file_ready

        st.image(info["thumbnail"], width=300)
        st.markdown(f"**🎬 {info['title']}**")
        st.markdown(f"⏱ {info['duration']//60} min")

        mime = "audio/mpeg" if file_path.suffix == ".mp3" else "video/mp4"

        with open(file_path, "rb") as f:
            st.download_button(
                "⬇️ Download File",
                data=f.read(),
                file_name=file_path.name,
                mime=mime
            )

# ------------------ TAB 2 ------------------
with tab2:
    uploaded_file = st.file_uploader("Upload Video", type=["mp4", "mov", "avi", "mkv"])
    progress_bar2 = st.progress(0)
    status_text2 = st.empty()

    if uploaded_file and st.button("🎧 Convert to MP3"):
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                video_path = Path(tmp_dir) / uploaded_file.name

                with open(video_path, "wb") as f:
                    f.write(uploaded_file.read())

                output_audio = Path(tmp_dir) / (video_path.stem + ".mp3")

                status_text2.text("🎬 Converting...")

                command = [
                    "ffmpeg",
                    "-i", str(video_path),
                    "-vn",
                    "-ab", "192k",
                    "-ar", "44100",
                    "-y",
                    str(output_audio)
                ]

                subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                downloads_dir = Path("downloads")
                downloads_dir.mkdir(exist_ok=True)
                final_path = downloads_dir / output_audio.name

                shutil.copy(output_audio, final_path)

                progress_bar2.progress(100)
                status_text2.text("✅ Done!")

                with open(final_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download MP3",
                        data=f.read(),
                        file_name=final_path.name,
                        mime="audio/mpeg"
                    )

        except Exception as e:
            st.error("Conversion failed")
            st.exception(e)

st.markdown('</div>', unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("""
---
<p style="text-align:center;color:#9ca3af;">
Built with ❤️ by <b>James Mungai</b> | Streamlit • yt-dlp • FFmpeg
</p>
""", unsafe_allow_html=True)