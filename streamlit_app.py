import streamlit as st
import pandas as pd
from utils.youtube_api import search_videos
from utils.youtube_suggest import get_suggestions

# ---- CONFIG ----
st.set_page_config(page_title="🎵 YouTube Auto Playlist Generator", layout="wide")
api_key = st.secrets["YOUTUBE_API_KEY"]

st.title("🎵 YouTube Auto Playlist Generator")
st.write("Type a topic and get suggested playlists instantly.")

# --- Dynamic Suggestions ---
query_input = st.text_input("Enter keyword", placeholder="e.g., meditation music")

if query_input:
    suggestions = get_suggestions(query_input)
    if suggestions:
        selected_keyword = st.selectbox("Suggestions:", suggestions, index=0)
    else:
        selected_keyword = query_input
else:
    st.info("Start typing to see YouTube keyword suggestions...")
    selected_keyword = None

# --- Search & Playlist Generation ---
if selected_keyword:
    df = search_videos(api_key, selected_keyword, max_results=10)
    st.subheader(f"Videos for: {selected_keyword}")
    st.dataframe(df)

    if not df.empty:
        playlist_url = "https://www.youtube.com/watch_videos?video_ids=" + ",".join(df["videoId"].tolist())
        st.markdown(f"[▶ Open Playlist in YouTube]({playlist_url})")
