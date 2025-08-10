import streamlit as st
import pandas as pd
import plotly.express as px
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🧘 Meditation YouTube Analyzer — PRO", layout="wide")

# ---------------- API KEY SETUP ----------------
API_KEY = st.secrets.get("YOUTUBE_API_KEY", None)

if not API_KEY:
    st.error("❌ Missing `YOUTUBE_API_KEY` in Streamlit secrets. Please set it in `Secrets`.")
    st.stop()  # Stop execution so we don’t crash later

# Build YouTube API client only after key exists
YOUTUBE = build("youtube", "v3", developerKey=API_KEY)

# ---------------- FUNCTIONS ----------------
def search_meditation_videos_today():
    try:
        published_after = (datetime.utcnow() - timedelta(days=1)).isoformat("T") + "Z"
        request = YOUTUBE.search().list(
            part="snippet",
            maxResults=50,
            q="meditation",
            publishedAfter=published_after,
            type="video",
            order="date"
        )
        response = request.execute()
        videos = [
            {
                "videoId": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channelTitle": item["snippet"]["channelTitle"],
                "publishedAt": item["snippet"]["publishedAt"]
            }
            for item in response.get("items", [])
        ]
        return pd.DataFrame(videos)
    except HttpError as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error in search: {e}")
        return pd.DataFrame()

def get_video_stats(video_ids):
    if not video_ids:
        return pd.DataFrame()
    try:
        request = YOUTUBE.videos().list(
            part="statistics,snippet",
            id=",".join(video_ids)
        )
        response = request.execute()
        stats = [
            {
                "videoId": item["id"],
                "title": item["snippet"]["title"],
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "comments": int(item["statistics"].get("commentCount", 0)),
                "channelTitle": item["snippet"]["channelTitle"],
                "publishedAt": item["snippet"]["publishedAt"]
            }
            for item in response.get("items", [])
        ]
        return pd.DataFrame(stats)
    except HttpError as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error in get_video_stats: {e}")
        return pd.DataFrame()

# ---------------- APP ----------------
st.title("🧘 Meditation YouTube Analyzer — PRO")
st.markdown("Analyze today's **meditation videos** on YouTube.")

df_search = search_meditation_videos_today()

if df_search.empty:
    st.warning("No videos found for today.")
else:
    st.subheader("📊 Search Results (Past 24h)")
    st.dataframe(df_search)

    video_ids = df_search["videoId"].tolist()
    df_stats = get_video_stats(video_ids)

    if not df_stats.empty:
        st.subheader("🔥 Video Stats")
        st.dataframe(df_stats)

        # Top 10 by views
        top_videos = df_stats.sort_values("views", ascending=False).head(10)
        fig = px.bar(
            top_videos,
            x="views",
            y="title",
            orientation="h",
            title="Top 10 Meditation Videos (by views)",
            text="views"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Views over time
        df_stats["publishedAt"] = pd.to_datetime(df_stats["publishedAt"])
        fig_time = px.scatter(
            df_stats,
            x="publishedAt",
            y="views",
            size="views",
            color="channelTitle",
            title="Views vs. Publish Time"
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.warning("No stats available for these videos.")
