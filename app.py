import streamlit as st
import requests

# 🔥 CHANGE THIS if deployed
BACKEND_URL = "http://0.0.0.0:8000/download"

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="YouTube Downloader Pro",
    page_icon="🎬",
    layout="centered"
)

# ------------------ UI ------------------
st.markdown(
    "<h1 style='text-align:center;color:#6366f1;'>🎬 YouTube Downloader Pro</h1>",
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["📥 YouTube Downloader", "🎧 Video → MP3 Converter"])

# ------------------ TAB 1 ------------------
with tab1:

    youtube_url = st.text_input("🔗 Enter YouTube URL")

    col1, col2 = st.columns(2)
    with col1:
        download_type = st.selectbox("Download Type", ["Video", "Audio (MP3)"])
    with col2:
        resolution = st.selectbox("Resolution", ["best", "1080", "720", "480", "360"])

    if st.button("⬇️ Download"):

        if not youtube_url:
            st.warning("⚠️ Please enter a YouTube URL")
        else:
            try:
                mode = "video" if download_type == "Video" else "audio"

                with st.spinner("⏳ Downloading from backend... Please wait"):

                    response = requests.get(
                        BACKEND_URL,
                        params={
                            "url": youtube_url,
                            "mode": mode,
                            "res": resolution
                        },
                        stream=True,
                        timeout=300
                    )

                if response.status_code == 200:

                    file_name = (
                        "video.mp4" if mode == "video" else "audio.mp3"
                    )

                    st.success("✅ File ready!")

                    st.download_button(
                        label="⬇️ Download File",
                        data=response.content,
                        file_name=file_name,
                        mime="video/mp4" if mode == "video" else "audio/mpeg"
                    )

                else:
                    st.error(f"❌ Backend error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Is FastAPI running?")
            except requests.exceptions.Timeout:
                st.error("⏳ Request timed out. Try a smaller video.")
            except Exception as e:
                st.error("❌ Unexpected error")
                st.exception(e)

# ------------------ TAB 2 ------------------
with tab2:
    st.info("🎧 Video to MP3 conversion works locally only (no backend needed).")

# ------------------ FOOTER ------------------
st.markdown("""
---
<p style="text-align:center;color:#9ca3af;">
Built with ❤️ by <b>James Mungai</b>
</p>
""", unsafe_allow_html=True)