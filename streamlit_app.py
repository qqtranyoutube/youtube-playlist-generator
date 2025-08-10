import streamlit as st
import pandas as pd
from utils.youtube_api import search_videos

# ---- CONFIG ----
st.set_page_config(page_title="🎵 YouTube Auto Playlist Generator", layout="wide")

api_key = st.secrets["YOUTUBE_API_KEY"]

# ---- UI ----
st.title("🎵 YouTube Auto Playlist Generator")
st.write("Type a topic and get suggested playlists instantly.")

# --- Keyword Suggestions ---
suggested_keywords = ["meditation music", "432Hz sleep", "study music", "lofi beats", "relaxing piano"]

keyword = st.text_input("Enter keyword", placeholder="e.g., meditation music")

if keyword:
    df = search_videos(api_key, keyword, max_results=10)
    st.subheader(f"Videos for: {keyword}")
    st.dataframe(df)

    playlist_url = "https://www.youtube.com/watch_videos?video_ids=" + ",".join(df["videoId"].tolist())
    st.markdown(f"[▶ Open Playlist in YouTube]({playlist_url})")

else:
    st.info("Try one of these: " + ", ".join(suggested_keywords))
